# -*- coding: utf-8 -*-

# 获取豆瓣电影的所以条目ID并每天同步更新
#
from selenium import webdriver
import  selenium
import  time
import os
os.environ["LANG"] = "en_US.UTF-8"

class DowBanID:
    def __init__(self):
        self.driver = webdriver.Chrome()
    def quit(self):
        self.driver.close()
        self.driver.quit()
    def get_all_category(self):
        types = []
        places = []
        self.driver.get("https://movie.douban.com/tag/#/")
        elements = self.driver.find_elements_by_xpath('//div[@class="tags"]/ul')
        for element in elements:
            categorys = element.find_elements_by_xpath('./li/span')
            if categorys[0].text == u'全部类型':
                types = list(map(lambda  x:x.text, categorys[1:]))
            if categorys[0].text == u'全部地区':
                places = list(map(lambda  x:x.text, categorys[1:]))
            #for category in categorys:
        return  types, places
    def get_all_link(self):
        "https://movie.douban.com/tag/#/?sort=S&range=0,10&tags=剧情,电影,大陆"
        urls = []
        types, places = self.get_all_category()
        for type in types:
            for place in places:
                for i in range(0,9,1):
                    urls.append(u'https://movie.douban.com/tag/#/?sort=S&range=%s,%s&tags=%s,电影,%s' %(i,i+1,type,place))
        return  urls
    def get_one_page_all_id(self,url):
        obj_ids=[]
        print url
        self.driver.get(url)
        self.driver.refresh()
        time.sleep(10)
        retry_num = 0
        while retry_num < 3:
            retry_num += 1
            try:
                while 1:
                    if len(self.driver.window_handles) > 1:
                        self.driver.switch_to_window(self.driver.window_handles[-1])
                        self.driver.close()
                        self.driver.switch_to_window(self.driver.window_handles[0])
                    js = "var q=document.documentElement.scrollTop=100000"
                    self.driver.execute_script(js)
                    time.sleep(4)
                    element = self.driver.find_element_by_xpath('//a[@class="more"]')
                    element.click()
                    retry_num = 0
            except selenium.common.exceptions.WebDriverException:
                time.sleep(3)
                #print "exceptin"

        elements = self.driver.find_elements_by_xpath('//div[@class="cover-wp"]')
        for element in elements:
            obj_ids.append(element.get_attribute("data-id"))
        print "id个数", len(obj_ids)
        return obj_ids

    def get_all_id(self):
        all_ids = []
        links = self.get_all_link()
        for link in links:
            all_ids= all_ids +self.get_one_page_all_id(link)
            print "总数:%d"%(len(all_ids))
        print len(list(set(all_ids)))
        print  "END!!"
