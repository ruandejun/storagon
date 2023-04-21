import json, re
from django.conf import settings
import top.api, requests
from http.cookiejar import CookieJar


appkey = settings.TAOBAO_APPKEY
secret = settings.TAOBAO_SECRET
adzone_id = settings.TAOBAO_ADZONE_ID

# 获取淘宝客商品优惠券
def get_tbk_coupon(keyword):
    req = top.api.TbkDgItemCouponGetRequest()
    req.set_app_info(top.appinfo(appkey, secret))

    req.adzone_id = adzone_id
    # 商品的平台：1为PC端，2为无线端，默认为1
    req.platform = 2
    # 商品的类目ID
    req.cat = "16,18"
    # 每页返回的商品数量
    req.page_size = 5
    # 商品的搜索词
    req.q = keyword
    # 返回商品的页数
    req.page_no = 1
    try:
        resp = req.getResponse()
        for r in resp['tbk_dg_item_coupon_get_response']['results']['tbk_coupon']:
            coupon_url = r['coupon_click_url']
            coupon_text = r['title']
            print(">>>商品标题：", coupon_text)
            print(">>>优惠券链接：", coupon_url)
            generate_ttoken(coupon_url, coupon_text)
            print()
    except Exception as e:
        print(e)

# 生成淘口令
def generate_ttoken(url, text):
    req = top.api.TbkTpwdCreateRequest()
    req.set_app_info(top.appinfo(appkey, secret))

    req.text = text
    req.url = url
    #req.logo = "http://ozuz7s0lj.bkt.clouddn.com/avas.webp"
    try:
        resp = req.getResponse()
        print(resp)
        return resp['tbk_tpwd_create_response']['data']['model']
    except Exception as e:
        print(e)

def get_tao_kou_ling(text: str) -> str:
    pattern = "؋‎฿₿¢₡₵$₫֏€₲₾₴₭₺₼₥₦₱£﷼‎៛₽₨௹₹৲৳૱₪₸₮₩¥₳₠₢₯₣₤₶₧₰₷￥"
    pattern = "([" + pattern + "])" + "(\\w+)\\1"
    result = re.compile(pattern).findall(text)
    try:
        result = result[0][0] + result[0][1] + result[0][0]  # 取匹配到的第一个
    except IndexError:
        result = ""
    return result
    pass

def sclick_extract(url):
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
    sclick_refer_re = re.search("var real_jump_address = '(.+?)'", r.text)
    if sclick_refer_re:
        r = browser.get(sclick_refer_re.group(1).replace('amp;',''),allow_redirects=False)
        if 'Location' in r.headers:
            return r.headers['Location']
    return

def tbcn_extract(url):
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
    r = browser.get(url, allow_redirects=True)
    taobao_url_re = re.search(r"var url = '(.+?)'", r.text)
    if taobao_url_re:
        return taobao_url_re.group(1)
    return

def taokouling_extract(text):
    taokouling = get_tao_kou_ling(text)
    if taokouling:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br',
            # 'Authorization': 'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMTU2NSwidXNlcm5hbWUiOiJ0dW5nYmsiLCJleHAiOjE1NjYyNTg4MzUsImVtYWlsIjoidHR1bmcuYmtAZ21haWwuY29tIiwib3JpZ19pYXQiOjE1NjYyNTg1MzV9.lnFHG5j1i2QrtvbhNyVCUchsrei4hYp8M6plfYYLbAM',
            # 'Connection': 'keep-alive',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'host': 'hifiorder.com',
            # 'origin': 'https://hifiorder.com',
            # 'x-requested-with': 'XMLHttpRequest',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'cookie': 't=564aa35983396ee479cd02c8a1bfacea; cna=r8srFf9761kCASpxrb8j8rpG; tracknick=%5Cu4E00%5Cu731B%5Cu4E00%5Cu8282%5Cu9047%5Cu4E00%5Cu7EDD; tg=0; hng=CN%7Czh-CN%7CCNY%7C156; thw=cn; enc=6rC9VK%2BEHtOt5n%2Fmn37J26iNvoe3SNR9sv8ULC69Je0M%2F90zhj1Ye2JTXX4utAYUy%2BzlJfnO225WVOSs7S0qCQ%3D%3D; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; _cc_=UtASsssmfA%3D%3D; v=0; cookie2=16d65ec1905a870f9e36ce486f5cf9ce; _tb_token_=5ea1e631b87b5; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; mt=ci%3D-1_0; _m_h5_tk=1262ca9cade86569397591cea8512079_1567666298042; _m_h5_tk_enc=0072e95645d0f7d5b28fea3207d0a625; JSESSIONID=8AE4D417E9B7ED9E4257EA47A9548893; l=cBx7NywVv-TyJIhABOfwIurza77t6Idf1iNzaNbMiICPOL5p4UffWZU_3_T9CnMNp6bWR3Wba70LBeYBqt4RWdav2j-la; isg=BOrqQKFGQ9y7R87teaTOdsxxO1BM83HOjAjWQnSiYj33p4lhXO8UxXaBN4seYOZN',
            'referer': 'https://s.taobao.com/search?q=&imgfile=&js=1&stats_click=search_radio_all%253A1&initiative_id=staobaoz_20190911&ie=utf8&tfsid=O1CN01l4HBdh250YnDayppA_!!0-imgsearch.jpg&app=imgsearch',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        browser = requests.session()
        browser.headers = headers
        browser.cookies = CookieJar()
        r = browser.get('https://api.taokouling.com/tkl/tkljm?apikey=UbNCmCPbav&tkl=' + taokouling)
        result = json.loads(r.text)
        if 'url' in result:
            url = result['url']
            list_urls = [url]
            return list_urls

# 获取淘宝客商品优惠券
def get_material_optional(keyword, external_id='',start_tk_rate=None, end_tk_rate=None, cat=None, start_dsr=None, end_price=None, start_price=None):
    req = top.api.TbkDgMaterialOptionalRequest()
    req.set_app_info(top.appinfo(appkey, secret))
    req.page_size = 300
    # req.page_no = 1
    # req.platform = 1
    # req.promotion_type = 2
    # req.is_overseas = 'false'
    # req.is_tmall = 'false'
    req.q = keyword
    req.adzone_id = adzone_id
    req.cat = cat
    req.external_id = external_id
    req.end_tk_rate = end_tk_rate
    req.start_tk_rate = start_tk_rate
    req.start_dsr = start_dsr
    req.start_price = start_price
    req.end_price = end_price
    try:
        resp = req.getResponse()
        # print(resp)
        # if len(resp['tbk_dg_material_optional_response']['result_list']['map_data']) == 1:
        return resp['tbk_dg_material_optional_response']['result_list']['map_data']
        # else:
        #     return
        # print(resp)
    except Exception as e:
        if str(e).find('subcode=50001') != -1:
            return
        else:
            print('===error===', e)
            return

def get_optimus_optional(material_id,page_no=1,page_size=20):
    req = top.api.TbkDgOptimusMaterialRequest()
    req.set_app_info(top.appinfo(appkey, secret))
    # san pham:6708
    # ban chay:28026
    # flash sale:4094
    # ifashion:4093
    req.page_size = page_size
    req.page_no = page_no
    req.material_id = material_id
    req.platform = 1
    req.adzone_id = adzone_id
    req.device_encrypt = "MD5"
    req.device_value = "xxx"
    req.device_type = "IMEI"
    resp = req.getResponse()
    if resp['tbk_dg_optimus_material_response']['result_list']['map_data']:
        return resp['tbk_dg_optimus_material_response']['result_list']['map_data']
    else:
        return

def get_taobao_commission(keyword, external_id=''):
    # print(keyword)
    data_item_by_urls = get_material_optional(keyword, external_id)
    if data_item_by_urls:
        item_data = data_item_by_urls[0]
        print(item_data)
        short_title = item_data['short_title']
        item_title = item_data['title']
        pict_url = item_data['pict_url']
        seller_id = item_data['seller_id']
        category_id = item_data['category_id']
        if 'shop_dsr' in item_data:
            shop_dsr = int(item_data['shop_dsr'])-1
        else:
            shop_dsr = None
        zk_final_price = int(float(item_data['zk_final_price']))
        zk_final_price_end = zk_final_price+1
        print(short_title)
        data_items = get_material_optional(short_title, external_id)
        if not data_items:
            print('==search error===', short_title)
            return
        data_item = None
        for line_data_item in data_items:
            short_title_item = line_data_item['short_title']
            pict_url_item = line_data_item['pict_url']
            seller_id_item = line_data_item['seller_id']
            print(short_title_item)
            # print(pict_url, pict_url_item)
            # print(seller_id, seller_id_item)
            if pict_url == pict_url_item and seller_id == seller_id_item:
                # data_item = line_data_item
                print('===found===')
                data_item = line_data_item
                return line_data_item
        # if not data_item:
        #     print('===Find by title===', item_title)
        #     data_items = get_material_optional(item_title, external_id,cat=str(category_id),start_dsr=str(shop_dsr), start_price=str(zk_final_price))
        #     data_item = None
        #     for line_data_item in data_items:
        #         short_title_item = line_data_item['short_title']
        #         pict_url_item = line_data_item['pict_url']
        #         seller_id_item = line_data_item['seller_id']
        #         # print(pict_url, pict_url_item)
        #         # print(seller_id, seller_id_item)
        #         if pict_url == pict_url_item and seller_id == seller_id_item:
        #             # data_item = line_data_item
        #             print('===found===')
        #             data_item = line_data_item
        #             return line_data_item
        if data_item:
            return data_item
