# -*- coding: utf-8 -*-

# 获取豆瓣电影的所以条目ID并每天同步更新
#
from selenium import webdriver
import selenium
import time
import os
import sys
import logging
import random
import string
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pymongo import MongoClient
import pymongo
import DBHelper as GlobalVar

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='ip_pool.log',
                filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

os.environ["LANG"] = "en_US.UTF-8"
user_agent = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]


class DowBanID:
    def __init__(self):
       

        self.db_name = 'other_movies'
        self.url_collection_name = 'douban_url'
        self.ids_collection_name = 'douban_ids'
        self.client = MongoClient('192.168.7.115', 27017)
        self.db = self.client[self.db_name]
        GlobalVar.set_mq_client(self.client)
        GlobalVar.set_db_handle(self.db)

    def quit(self):
        self.driver.close()
        self.driver.quit()
    def init_phantomJS_driver(self):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        #从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
        dcap["phantomjs.page.settings.userAgent"] = random.choice(user_agent)
        # 不载入图片，爬页面速度会快很多
        dcap["phantomjs.page.settings.loadImages"] = False
        self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
        
    def init_chrome_driver(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images":2}
        chrome_options.add_experimental_option("prefs",prefs)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(20)
        # 设置10秒脚本超时时间  
        self.driver.set_script_timeout(20)
    def get_all_category(self):
        places = []
        self.driver.get("https://movie.douban.com/tag/#/")
        self.cookies = self.driver.get_cookies()
        logging.info(self.cookies)
        elements = self.driver.find_elements_by_xpath(
            '//div[@class="tags"]/ul')
        for element in elements:
            categorys = element.find_elements_by_xpath('./li/span')
            if categorys[0].text == u'全部地区':
                places = list(map(lambda x: x.text, categorys[1:]))
            #for category in categorys:
        return places

    def get_all_link(self):
        "https://movie.douban.com/tag/#/?sort=T&range=0,10&tags=剧情,电影,大陆"
        urls = []
        places = self.get_all_category()
        for i in range(0, 10, 1):
            #for type in types:
            for place in places:
                url = u'https://movie.douban.com/tag/#/?sort=R&range=%s,%s&tags=电影,%s'%(i, i + 1,  place)
                #url2 = u'https://movie.douban.com/tag/#/?sort=R&range=%s,%s&tags=电影,%s'%(i, i + 1,  place)
                urls.append(url)
                #GlobalVar.get_db_handle()[self.url_collection_name].update({'url': url},{'$setOnInsert': {'complete': 0}, '$set':{'url':url2}},True)
                GlobalVar.get_db_handle()[self.url_collection_name].update({'url': url},{'$setOnInsert': {'complete': 0}}, True)                
        return urls

    def update_driver_cookies(self):
        self.driver.delete_all_cookies()
        for cookie in self.cookies:
            # fix the problem-> "errorMessage":"Unable to set Cookie"
            for k in ('name', 'value', 'domain', 'path', 'expiry'):
                if k not in list(cookie.keys()):
                    if k == 'expiry':
                        t = time.time()
                        cookie[k] = int(t)  # 时间戳 秒
            if cookie['name'] == 'bid':
                cookie['value'] = "%s" % "".join(
                    random.sample(string.ascii_letters + string.digits, 11))
            # fix the problem-> "errorMessage":"Can only set Cookies for the current domain"
            try:
                self.driver.add_cookie({
                    k: cookie[k]
                    for k in ('name', 'value', 'domain', 'path', 'expiry')
                    if k in cookie
                })
            except selenium.common.exceptions.WebDriverException:
                pass

    def get_one_page_all_id(self, url):
        obj_ids = []
        logging.info(url)
        self.update_driver_cookies()
        self.driver.get(url)
        #self.update_driver_cookies()
        self.driver.refresh()
        time.sleep(10)
        if self.driver.find_elements_by_link_text('关于豆瓣') is None:
            logging.info("没找到关于豆瓣")
            self.update_driver_cookies()
            self.driver.refresh()
            time.sleep(20)

        retry_num = 0
        more_number = 0;
        sleep_number = 10;
        while retry_num < 3:
            retry_num += 1
            try:
                while 1:
                    if len(self.driver.window_handles) > 1:
                        self.driver.switch_to_window(
                            self.driver.window_handles[-1])
                        self.driver.close()
                        self.driver.switch_to_window(
                            self.driver.window_handles[0])
                    #js = "var q=document.documentElement.scrollTop=100000"
                    #self.driver.execute_script(js)
                    more_number +=1
                    if more_number == 15 and sleep_number < 30:
                        more_number = 0
                        sleep_number+=5
                    nt = time.time()
                    time.sleep(sleep_number)                    
                    element = self.driver.find_element_by_xpath(
                        '//a[@class="more"]')
                    #self.update_driver_cookies()
                    element.click()
                    retry_num = 0
                    print time.time()-nt
            except selenium.common.exceptions.WebDriverException:
                try:
                    self.driver.find_element_by_xpath('//div[@class="empty"]')
                    break
                except selenium.common.exceptions.WebDriverException:
                    time.sleep(4)
                #print "exceptin"

        elements = self.driver.find_elements_by_xpath(
            '//div[@class="cover-wp"]')
        for element in elements:
            obj_id = element.get_attribute("data-id")
            obj_ids.append(obj_id)
            GlobalVar.get_db_handle()[self.ids_collection_name].update({'obj_id': obj_id},{'$setOnInsert': {'url': url}},True)
        logging.info("id个数 %s" % (len(obj_ids)))
        return obj_ids

    def get_all_id(self):
        self.init_chrome_driver()
        all_ids = []
        wait_update_urls = []
        links = self.get_all_link()
        while(1):
            res =  GlobalVar.get_db_handle()[self.url_collection_name].find_one({'complete': 0})
            if res is None:
                return
            wait_update_urls.append(res['url'])
            all_ids = self.get_one_page_all_id(res['url'])
            if len(all_ids) >= 0:
                GlobalVar.get_db_handle()[self.url_collection_name].update_many({'url': {'$in':wait_update_urls}}, {'$set':{'complete':1}}, True)
            GlobalVar.get_db_handle()[self.url_collection_name].update({'url': res['url']}, {'$set':{'id_count':len(all_ids)}}, True)
        
    def get_repet_number(self, pre_obj_ids):
        obj_ids = []
        repet_number = 0
        elements = self.driver.find_elements_by_xpath(
            '//div[@class="cover-wp"]')
        for element in elements:
            obj_id = element.get_attribute("data-id")
            obj_ids.append(obj_id)
            if obj_id in pre_obj_ids:
                continue
            res = GlobalVar.get_db_handle()[self.ids_collection_name].find_one({'obj_id': obj_id})
            if res is not None:
                 repet_number+=1
            else:
                self.new_ids.append(obj_id)
                logging.info(obj_id)        
        logging.info("id个数 %s 重复个数%s" % (len(obj_ids), repet_number))
        return obj_ids, repet_number

    def update_new_id(self):
        #self.init_phantomJS_driver()
        self.new_ids = []
        urls = []
        self.init_chrome_driver()
        places = ["大陆","美国","香港","台湾","日本","韩国","英国","法国","德国","意大利"
        ,"西班牙","印度","泰国","俄罗斯","伊朗","加拿大","澳大利亚","爱尔兰","瑞典","巴西","丹麦"]
        for place in places:
            urls.append("https://movie.douban.com/tag/#/?sort=R&range=0,10&tags=电影,%s"%(place))
        urls.append("https://movie.douban.com/tag/#/?sort=R&range=0,10&tags=%E7%94%B5%E5%BD%B1")
        urls.append("https://movie.douban.com/explore#!type=movie&tag=%E7%83%AD%E9%97%A8&sort=time&page_limit=20&page_start=0")        
        for url in urls:
            logging.info(url)
            self.driver.get(url)
            self.driver.refresh()
            time.sleep(10)
            if self.driver.find_elements_by_link_text('关于豆瓣') is None:
                logging.info("没找到关于豆瓣")
                self.update_driver_cookies()
                self.driver.refresh()
                time.sleep(20)
            pre_obj_ids = []
            stop_num = 0
            while(1):
                obj_ids,repet_number = self.get_repet_number(pre_obj_ids)
                if repet_number == 20:
                    break
                else:
                    try:
                        element = self.driver.find_element_by_xpath('//a[@class="more"]')
                        element.click()
                        time.sleep(20)
                    except selenium.common.exceptions.WebDriverException:
                        break
                pre_obj_ids = obj_ids
            #insert
            for obj_id in self.new_ids:
                GlobalVar.get_db_handle()[self.ids_collection_name].update({'obj_id': obj_id},{'$setOnInsert': {'url': url}},True)
        #self.quit()
    
if sys.argv[1] == "getall":
    demo = DowBanID()
    demo.get_all_id()
elif sys.argv[1] == "update":
    demo = DowBanID()
    demo.update_new_id()
else:
    print "input getall or update"