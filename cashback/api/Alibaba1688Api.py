import re
from django.conf import settings
import aop.api
from hashlib import sha1
import hmac
import time, requests
from http.cookiejar import CookieJar
import urllib.parse

APP_KEY_1688 = settings.APP_KEY_1688
APP_SECRET_1688 = settings.APP_SECRET_1688
ACCESS_TOKEN_1688 = settings.ACCESS_TOKEN_1688
MEDIAID_1688 = settings.MEDIAID_1688
MEDIAZONEID_1688 = settings.MEDIAZONEID_1688

def alibaba_1688_extract(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        # 'Authorization': 'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMTU2NSwidXNlcm5hbWUiOiJ0dW5nYmsiLCJleHAiOjE1NjYyNTg4MzUsImVtYWlsIjoidHR1bmcuYmtAZ21haWwuY29tIiwib3JpZ19pYXQiOjE1NjYyNTg1MzV9.lnFHG5j1i2QrtvbhNyVCUchsrei4hYp8M6plfYYLbAM',
        # 'Connection': 'keep-alive',
        'Accept-Language': 'en-US,en;q=0.9',
        # 'host': 'www.mapprouter.com',
        # 'origin': 'https://hifiorder.com',
        # 'x-requested-with': 'XMLHttpRequest',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'cookie': 't=564aa35983396ee479cd02c8a1bfacea; cna=r8srFf9761kCASpxrb8j8rpG; tracknick=%5Cu4E00%5Cu731B%5Cu4E00%5Cu8282%5Cu9047%5Cu4E00%5Cu7EDD; tg=0; hng=CN%7Czh-CN%7CCNY%7C156; thw=cn; enc=6rC9VK%2BEHtOt5n%2Fmn37J26iNvoe3SNR9sv8ULC69Je0M%2F90zhj1Ye2JTXX4utAYUy%2BzlJfnO225WVOSs7S0qCQ%3D%3D; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; _cc_=UtASsssmfA%3D%3D; v=0; cookie2=16d65ec1905a870f9e36ce486f5cf9ce; _tb_token_=5ea1e631b87b5; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; mt=ci%3D-1_0; _m_h5_tk=1262ca9cade86569397591cea8512079_1567666298042; _m_h5_tk_enc=0072e95645d0f7d5b28fea3207d0a625; JSESSIONID=8AE4D417E9B7ED9E4257EA47A9548893; l=cBx7NywVv-TyJIhABOfwIurza77t6Idf1iNzaNbMiICPOL5p4UffWZU_3_T9CnMNp6bWR3Wba70LBeYBqt4RWdav2j-la; isg=BOrqQKFGQ9y7R87teaTOdsxxO1BM83HOjAjWQnSiYj33p4lhXO8UxXaBN4seYOZN',
        'referer': url,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    browser = requests.session()
    browser.headers = headers
    browser.cookies = CookieJar()
    r = browser.get(url, allow_redirects=False)
    sclick_refer_re = re.search("androidWapUrl=decodeURIComponent\('(.+?)'\)", r.text)
    if sclick_refer_re:
        return urllib.parse.unquote(sclick_refer_re.group(1).strip())
    return

def current_time():
    return int(round(time.time() * 1000))

def sign(key, value):
    key = bytes(key, encoding='utf8')
    value = bytes(value, encoding='utf8')
    val = hmac.new(key, value, sha1).hexdigest()
    return val.upper()

def invoke(api, params):
    # http://gw.open.1688.com/openapi/param2/1/com.alibaba.product/alibaba.product.get/8384550
    url = 'param2/1/{}/{}'.format(api, APP_KEY_1688)

    # 签名
    pstr = ''
    for key, value in params.items():
        pstr += key
        pstr += str(value)
    # 通用参数
    # print(url)
    # print(pstr)
    # print(url + pstr)

    sign_str = sign(APP_SECRET_1688, url + pstr)
    # print(sign_str)
    base = {
        # 签名
        '_aop_signature': sign_str,
    }
    gw = 'http://gw.open.1688.com/openapi'
    reqUrl = '{}/{}'.format(gw, url)

    for key, value in params.items():
        base[key] = str(value)

    # 发起请求
    # r = requests.post(url=reqUrl, data=base)
    r = requests.get(url=reqUrl, params=base)
    rs = r.json()
    if 'exception' in rs:
        raise RuntimeError(rs.get('error_message') + '\n error detail:' + r.text)

    return rs

class Api:
    def __init__(self, namespace):
        self.namespace = namespace

    def call(self, api, params):
        return invoke(self.namespace + '/' + api, params)

class Get_link:
    def __init__(self):
        self.api = Api('com.alibaba.p4p')

    def get(self, product_id, ext=None):
        '''
           获取产品详情 https://open.1688.com/api/apidocdetail.htm?aopApiCategory=product_new&id=com.alibaba.product:alibaba.product.get-1
           :param product_id:
           :return:
           '''

        return self.api.call('alibaba.cps.genClickUrl', {
            'mediaId': MEDIAID_1688,
            'mediaZoneId': MEDIAZONEID_1688,
            'objectValueList': product_id,
            'type': '0',
        })
    def get_info(self, product_id):
        '''
           获取产品详情 https://open.1688.com/api/apidocdetail.htm?aopApiCategory=product_new&id=com.alibaba.product:alibaba.product.get-1
           :param product_id:
           :return:
           '''

        return self.api.call('alibaba.cps.listOfferPageQuery', {
            # 'mediaId': mediaId,
            # 'mediaZoneId': mediaZoneId,
            'feedInfo': product_id,
            'pageNo': 1,
            'pageSize': 100
        })

def GenClickUrl_1688(item_id,ext=None):


    aop.set_default_server('gw.open.1688.com')

    aop.set_default_appinfo(APP_KEY_1688, APP_SECRET_1688)  # default

    req = aop.api.AlibabaCpsGenClickUrlParam()

    req.access_token = ''
    req.ext = ext
    req.mediaId = MEDIAID_1688
    req.mediaZoneId = MEDIAZONEID_1688
    req.objectValueList = item_id
    req.type = '0'
    resp = req.get_response()
    return resp

def search_item_1688(key,pageNo=1,pageSize=100):


    aop.set_default_server('gw.open.1688.com')

    aop.set_default_appinfo(APP_KEY_1688, APP_SECRET_1688)  # default

    req = aop.api.AlibabaCpsListOfferPageQueryParam()


    req.access_token = ''
    req.feedInfo = key
    req.pageNo = pageNo
    req.pageSize = pageSize
    resp = req.get_response()
    return resp        
        
def get_1688_commission(item_url,ext=None):
    link_re = re.search('offer\/(\d+)\.html',item_url)
    if link_re:
        offer_id = link_re.group(1).strip()
        # product = Get_link()
        info_items = search_item_1688(offer_id)
        print(info_items['result'])
        # info_commission = json.loads(info_items)

        if 'result' in info_items:
            result = info_items['result']
            if result:
                link_commissions = GenClickUrl_1688(offer_id,ext)
                return {'item_info':result,'link_commissions':link_commissions}
            else:
                return
    return

def get_1688_link(item_url):
    # https://detail.1688.com/offer/595415883603.html?spm=a2615.7691456.autotrace-offerGeneral.1.4cae3fba1f8DzW
    link_re = re.search('offer\/(\d+)\.html', item_url)
    if link_re:
        offer_id = link_re.group(1).strip()
        product = Get_link()
        # 替换成自己的产品id
        info_link = product.get(offer_id)
        print(info_link)
        if str(info_link).find('error_message') != -1:
            return

        if info_link['result']:
            link_1688 = info_link['result'][0]['longClickUrl']
            return link_1688
        else:
            return
