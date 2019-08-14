
from bs4 import BeautifulSoup
from flask_restplus import Namespace, Resource
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from gl import DRIVER_MAP

api = Namespace('login','获取二维码')
qr_api_parser = api.parser()
qr_api_parser.add_argument('id',required=True,type=str,help='ID',location='args')

@api.route('/qr')
class QRResource(Resource):
    @api.expect(qr_api_parser)
    def get(self):
        '''
        获取二维码
        '''
        args = qr_api_parser.parse_args()

        response_data = {}
        if args['id'] in DRIVER_MAP:
            browser = DRIVER_MAP[args['id']]
            browser.quit()
            print('browser is exist')
        browser = webdriver.Remote(command_executor="http://127.0.0.1:4444/wd/hub",desired_capabilities=DesiredCapabilities.CHROME)
        DRIVER_MAP[args['id']] = browser
        browser.get('https://bank.pingan.com.cn/m/main/index.html')
        browser.switch_to_frame(browser.find_element_by_id("newbankframe"))
        soup = BeautifulSoup(browser.page_source)
        trs = soup.findAll("img")
        length = len(trs)
        for i in range(length):
            if 'alt' in trs[i].attrs and 'Scan me!' == trs[i].attrs["alt"]:
                response_data['code'] = 1
                response_data['msg'] = '获取成功'
                data = {}
                data['id'] = args['id']
                data['qr_img'] = trs[i].attrs["src"]
                response_data['data'] = data
                return response_data
        response_data['code'] = -1
        response_data['msg'] = '获取失败'
        return response_data

@api.route('/echo')
class EchoResource(Resource):
    def get(self):
        return {'code':1,'msg':'hello'}