# -*- coding: utf-8 -*-
# 获取代理ip 存入mongodb
#对mongodb 内的数据进行帅选加入is alive 字段,并删除
#如果总数小于10,再次进行爬取
#
import  re
import  random
import  time
import  urllib2
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
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52", ]
        self.header = {"User-Agent": self.user_agent[0]}
    def get_one_page_ip(self, num):
        #one = [1,2,3,4,5,6,7,8]
        #print [x for x in one if x % 2 == 0]
        nn_url = "http://www.xicidaili.com/nn/"+str(num)
        #国内高匿名
        self.header["User-Agent"] = random.choice(self.user_agent)
        req = urllib2.Request(nn_url, headers=self.header)
        resp = urllib2.urlopen(req, timeout=1000)
        content = resp.read()
        ips = re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td>.*?(\d+)</td>', content,re.S)
        print ips
        for ip,port in ips:
            if self.is_alive_ip_port(ip, port):
                print  ip,port
        #insert db
    def get_num_page_ips(self,num):
        for i in range(1,num):
            print "start %d page"%(i)
            self.get_one_page_ip(i)
            print "end %d page" % (i)
            time.sleep(3)

    def is_alive_ip_port(self,ip, port):
        proxy = {'http':ip + ':' + port}
        #print proxy

        # 使用这个方式是全局方法。
        proxy_support = urllib2.ProxyHandler(proxy)
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
        # 使用代理访问腾讯官网，进行验证代理是否有效
        test_url = "https://movie.douban.com"
        req = urllib2.Request(test_url, headers=self.header)
        try:
            # timeout 设置为10，如果你不能忍受你的代理延时超过10，就修改timeout的数字
            resp = urllib2.urlopen(req, timeout=3)

            if resp.code == 200:
                print "work"
                return True
            else:
                #print "not work"
                return False
        except:
            #print "Not work"
            return False


