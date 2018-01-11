# -*- coding: utf-8 -*-
# 获取代理ip 存入mongodb
#对mongodb 内的数据进行帅选加入is alive 字段,并删除
#如果总数小于10,再次进行爬取
#
import thread
import re
import random
import time
import urllib2
from pymongo import MongoClient
import pymongo
import DBHelper as GlobalVar
from selenium import webdriver
import selenium
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  
from selenium.webdriver.common.proxy import ProxyType  
import threadpool
import logging
import datetime

logging.basicConfig(level=logging.INFO)
'''
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='ip_pool.log',
                filemode='w')
'''



def url1_parse_ip(content):
    return re.findall(r'<td.*?>(\d+\.\d+\.\d+\.\d+)</td>.*?>(\d+)</td>',
                        content, re.S)
def url2_parse_ip(content):
    return re.findall(r'<td.*?>(\d+\.\d+\.\d+\.\d+)</td>.*?>(\d+)</td>',
                        content, re.S)

free_url_dict = {"http://www.xicidaili.com/nn/":url1_parse_ip,"https://www.kuaidaili.com/free/inha/":url2_parse_ip}
#free_url_dict = {"https://www.kuaidaili.com/free/inha/":url2_parse_ip}
#free_url_dict = {"http://www.xicidaili.com/nn/":url1_parse_ip}


def do_check_ips_thread(selfs):
    while(selfs.alived):
        res =  GlobalVar.get_db_handle()[selfs.collection_name].find({}).sort('datetime', 1).limit(1)
        if res.count()>0:
            if selfs.is_alive_ip_port([res[0]['ip'], res[0]['port']]) == 0:
                GlobalVar.get_db_handle()[selfs.collection_name].remove(res[0])
                continue
            GlobalVar.get_db_handle()[selfs.collection_name].update({'ip': res[0]['ip']},{'$set': {'datetime': datetime.datetime.now()}},True)         
        else :
            time.sleep(600)
def do_get_ips_thread(selfs, url):
    while(selfs.alived):
        #if GlobalVar.get_db_handle()[selfs.collection_name].find({}).count() >20 :
        #   time.sleep(100)
        #    continue
        #GlobalVar.get_db_handle()[selfs.collection_name].remove({})    
        for i in range(1, 1000):
            logging.info("start %s page" % (i))
            selfs.get_one_page_ip(i, url)
            logging.info("end %s page" % (i))
            time.sleep(3)
                            
class IP_POLL():
    def __init__(self):
        self.user_agent = [
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
        '''
        MONGODB_SERVER = '192.168.8.115'
        MONGODB_PORT = 27017
        MONGODB_DB = 'movies'
        MONGODB_INFO_COLLECTION = 'information'
        '''
        self.header = {"User-Agent": self.user_agent[0]}
        self.db_name = 'movies'
        self.collection_name = 'ip_pool'
        self.client = MongoClient('192.168.7.115', 27017)
        self.db = self.client[self.db_name]
        GlobalVar.set_mq_client(self.client)
        GlobalVar.set_db_handle(self.db)
        self.alived = 0
    
    def close(self):
        self.client.close()
    def get_one_page_ip(self, num, url):
        func = free_url_dict[url]
        nn_url = url + str(num)
        print nn_url
        #国内高匿名
        self.header["User-Agent"] = random.choice(self.user_agent)
        opener2 = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        req = urllib2.Request(nn_url, headers=self.header)
        resp = opener2.open(req, timeout=10)
        #resp = urllib2.urlopen(req, timeout=3)
        content = resp.read()
        ips = func(content)
        #ips = re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td>.*?(\d+)</td>',
        #                 content, re.S)
        logging.info(ips)
        ip_list = map(lambda x:list(x), ips)
        pool = threadpool.ThreadPool(5)
        #requests = threadpool.makeRequests(self.is_alive_ip_port, ips)
        requests = threadpool.makeRequests(self.is_alive_ip_port, ip_list)
        
        [pool.putRequest(req) for req in requests] 
        pool.wait()
        #insert db

    def is_alive_ip_port(self, ip_port):
        logging.info("%s"%(ip_port))
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        #从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
        dcap["phantomjs.page.settings.userAgent"] = (random.choice(self.user_agent))
        # 不载入图片，爬页面速度会快很多
        dcap["phantomjs.page.settings.loadImages"] = False
        # 设置代理
        service_args = ['--proxy=%s:%s'%(ip_port[0],ip_port[0]),'--proxy-type=socks5']
        driver = webdriver.PhantomJS("/usr/bin/phantomjs", desired_capabilities=dcap,service_args=service_args)                

        # 隐式等待5秒，可以自己调节  
        #driver.implicitly_wait(5)  
        # 设置10秒页面超时返回，类似于requests.get()的timeout选项，driver.get()没有timeout选项  
        # 以前遇到过driver.get(url)一直不返回，但也不报错的问题，这时程序会卡住，设置超时选项能解决这个问题。  
        driver.set_page_load_timeout(10)
        # 设置10秒脚本超时时间  
        driver.set_script_timeout(10) 
        '''
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=http://%s:%s'%(ip_port[0],ip_port[1]))
        prefs = {"profile.managed_default_content_settings.images":2}
        chrome_options.add_experimental_option("prefs",prefs)
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.implicitly_wait(6) 
        driver.set_page_load_timeout(15)
        driver.set_script_timeout(15)
        '''
        #定义判断此代理可用的条件      
        try:
            driver.get("https://movie.douban.com")
            time.sleep(5)
            driver.find_element_by_link_text(u'关于豆瓣')
            driver.close()
            driver.quit()
            GlobalVar.get_db_handle()[self.collection_name].update({'ip': ip_port[0]},{'$set': {'ip': ip_port[0], 'port':ip_port[1], 'datetime': datetime.datetime.now()}},True)
            logging.info("OK")
            return True
        except selenium.common.exceptions.WebDriverException:
            driver.close()
            driver.quit()
            logging.info( "failed!")
            return False

    
    def start_get_ips(self):
        if self.alived == 1:
            return
        try:
            self.alived = 1
            for (d,x) in free_url_dict.items():
                print "key:"+d+",value:"+str(x)
                thread.start_new_thread( do_get_ips_thread, (self,d,) )
            thread.start_new_thread( do_check_ips_thread, (self,) )
        except:
            self.alived = 0
            logging.info("Error: unable to start thread")
    def stop_get_ips(self):
        self.alived = 0
    def get_one_alive_ip(self):
        while(1):
            res =  GlobalVar.get_db_handle()[self.collection_name].find({}).sort('datetime', -1).limit(1)
            if res.count()>0:
                if self.is_alive_ip_port([res[0]['ip'], res[0]['port']]) == 0:
                    GlobalVar.get_db_handle()[self.collection_name].remove(res[0])
                    continue
                GlobalVar.get_db_handle()[self.collection_name].update({'ip': res[0]['ip']},{'$set': {'datetime': datetime.datetime.now()}},True)         
                return res[0]
        return 0
