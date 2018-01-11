# -*- coding: utf-8 -*-

# 获取豆瓣电影的所以条目ID并每天同步更新
#
from selenium import webdriver
import selenium
import time
import os
import urllib2

user_agent = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)"
header = {"User-Agent": user_agent}
os.environ["LANG"] = "en_US.UTF-8"


class DowBanID:
    def __init__(self):
        #self.driver = webdriver.Chrome()
        pass

    def quit(self):
        self.driver.close()
        self.driver.quit()

    def get_driver(self, url):
        while (1):
            req = urllib2.Request('http://127.0.0.1:5000', headers=header)
            resp = urllib2.urlopen(req, timeout=40)
            content = resp.read()
            if content == '':
                continue
            print '--proxy-server=http://%s' % (content)
            '''
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--proxy-server=http://%s'%(content))
            prefs = {"profile.managed_default_content_settings.images":2}
            chrome_options.add_experimental_option("prefs",prefs)
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
            self.driver.get(url)
            '''
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            #从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
            dcap["phantomjs.page.settings.userAgent"] = user_agent
            # 不载入图片，爬页面速度会快很多
            dcap["phantomjs.page.settings.loadImages"] = False
            # 设置代理
            service_args = ['--proxy=%s' % (content), '--proxy-type=socks5']
            self.driver = webdriver.PhantomJS(
                "C:\\ProgramData\\Anaconda2\\Scripts\\phantomjs.exe",
                desired_capabilities=dcap,
                service_args=service_args)

            # 隐式等待5秒，可以自己调节
            self.driver.implicitly_wait(5)
            # 设置10秒页面超时返回，类似于requests.get()的timeout选项，driver.get()没有timeout选项
            # 以前遇到过driver.get(url)一直不返回，但也不报错的问题，这时程序会卡住，设置超时选项能解决这个问题。
            self.driver.set_page_load_timeout(20)
            # 设置10秒脚本超时时间
            self.driver.set_script_timeout(20)
            #定义判断此代理可用的条件
            self.driver.get(url)
            time.sleep(5)
            try:
                self.driver.find_element_by_link_text(u'关于豆瓣')
                return
            except selenium.common.exceptions.WebDriverException:
                self.quit()

    def get_all_category(self):
        types = []
        places = []

        self.get_driver("https://movie.douban.com/tag/#/")
        #self.driver.get("https://movie.douban.com/tag/#/")
        elements = self.driver.find_elements_by_xpath(
            '//div[@class="tags"]/ul')
        for element in elements:
            categorys = element.find_elements_by_xpath('./li/span')
            if categorys[0].text == u'全部类型':
                types = list(map(lambda x: x.text, categorys[1:]))
            if categorys[0].text == u'全部地区':
                places = list(map(lambda x: x.text, categorys[1:]))
            #for category in categorys:
        return types, places

    def get_all_link(self):
        "https://movie.douban.com/tag/#/?sort=S&range=0,10&tags=剧情,电影,大陆"
        urls = []
        types, places = self.get_all_category()
        for type in types:
            for place in places:
                for i in range(0, 9, 1):
                    urls.append(
                        u'https://movie.douban.com/tag/#/?sort=S&range=%s,%s&tags=%s,电影,%s'
                        % (i, i + 1, type, place))
        return urls

    def get_one_page_all_id(self, url):
        #self.quit()
        obj_ids = []
        print url
        self.get_driver(url)
        #self.driver.get(url)
        self.driver.refresh()
        time.sleep(15)
        retry_num = 0
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
                    time.sleep(5)
                    element = self.driver.find_element_by_xpath(
                        '//a[@class="more"]')
                    element.click()
                    retry_num = 0
            except selenium.common.exceptions.WebDriverException:
                time.sleep(3)
                #print "exceptin"

        elements = self.driver.find_elements_by_xpath(
            '//div[@class="cover-wp"]')
        for element in elements:
            obj_ids.append(element.get_attribute("data-id"))
        print "id个数", len(obj_ids)
        return obj_ids

    def get_all_id(self):
        all_ids = []
        links = self.get_all_link()
        for link in links:
            all_ids = all_ids + self.get_one_page_all_id(link)
            print "总数:%d" % (len(all_ids))
        print len(list(set(all_ids)))
        print "END!!"
