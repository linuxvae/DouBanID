from collect_douban_id import DowBanID

from get_proxy_ip import IP_POLL
from flask import Flask
from flask import request
import time


ip_pool = IP_POLL()
ip_pool.start_get_ips()

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def home():
    res = ip_pool.get_one_alive_ip()
    return res['ip']+':'+res['port']
    #return  '<h1>Home</h1>'

if __name__ == '__main__':
    app.run()

#demo = DowBanID()
#demo.get_all_id()
#demo.quit()
