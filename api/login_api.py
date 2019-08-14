import hashlib
import json
import threading

import requests
import time
from bs4 import BeautifulSoup
from flask_restplus import Namespace, Resource
from selenium import webdriver

from gl import DRIVER_MAP, COOKIES

headers = {
 "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
}
def get_cookie(key):
    cookie = DRIVER_MAP[key].get_cookies()
    print(cookie)
    cookies = {}

    for item in cookie:
        cookies[item['name']] = item['value']
    # for line in cookie.split(';'):  # 按照字符：进行划分读取
    #     # 其设置为1就会把字符串拆分成2份
    #     if len(line.split("=")) == 2:
    #         name, value = line.strip().split('=', 1)
    #         cookies[name] = value
    #     else:
    #         cookies[line[0:line.find("=")]] = line[line.find("=") + 1:len(line)]
    print(cookies)

    r = requests.post('https://bank.pingan.com.cn/rmb/brop/acct/cust/mgt/qryAccountBindList.do', data={
        'acconutFlag': 111000,
        'qryType': 111,
        'channelCode': 'C0012',
        'channelType': 'd',
        'access_source': 'PC'
    }, cookies=cookies)
    print(r.text)
    response_dict = json.loads(r.text)
    print(response_dict)
    if r.status_code == 200 and 'data' in response_dict:
        bank_list = response_dict['data']['bankCardList']
        print(bank_list)
        print(len(bank_list))
        if len(bank_list) > 0:
            s = threading.Timer(10, request_transfer, (cookies,bank_list,0))
            s.start()


def request_transfer(cookies,bank_list,lastTransferTime):
    query_time = time.strftime("%Y%m%d", time.localtime())
    query_time_1 = time.strftime("%Y%m%d", time.localtime(time.time() - 24 * 60 * 60))
    r = requests.post('https://bank.pingan.com.cn/rmb/brop/acct/cust/qry/qryTranList.do', data={
        'bankType': 0,
        'currType': 'RMB',
        'pageIndex': 1,
        'queryAccType': 1,
        'channelType': 'd',
        'startDate': query_time_1,
        'endDate': query_time,
        'qry_accType': '',
        'fixedDepositSN': '',
        'agreementNo': '',
        'accNum': bank_list[0]['bankCardSign'],
        'accNumSelected': bank_list[0]['bankCardSign']
    }, cookies=cookies)
    response_data = json.loads(r.text)
    print(response_data)
    data = []
    if 'data' in response_data:

        for item in response_data['data']['result_value']:
            trans_time = time.mktime(time.strptime(item['tranTime'], '%Y-%m-%d %H:%M:%S'))
            data_item = {}
            if time.time() - trans_time < 60 * 60 * 5:
                if lastTransferTime >= trans_time:
                    continue
                data_item['dt'] = trans_time
                data_item['no'] = item['tranSysNo']
                data_item['money'] = item['balance']
                data_item['mUserId'] = ''
                data_item['mTUserid'] = item['toAcctNo']
                sign_str = ''.join((str(trans_time), '', str(item['balance']), item['tranSysNo'],
                                    'alipay78cfed2222ec290fe37332cee4c35d07', item['toAcctNo']))
                m2 = hashlib.md5()
                m2.update(sign_str.encode('utf-8'))
                data_item['sign'] = m2.hexdigest()
                print('sign : ' + data_item['sign'])
                data_item['remark'] = item['userRemark']
                data_item['type'] = 'alipay2bank'
                data.append(data_item)
        print(data)
        for item in data:
            if lastTransferTime < item['dt']:
                lastTransferTime = trans_time
            r = requests.post('https://gematong.com/v1/monitor/callback', data=item, headers=headers)
            print(r.text)

    s = threading.Timer(10, request_transfer, (cookies,bank_list,lastTransferTime))
    s.start()


api = Namespace('verify','登录')
verify_api_parser = api.parser()
verify_api_parser.add_argument('id',required=True,type=str,help='ID',location='form')
verify_api_parser.add_argument('verify_code',required=True,type=str,help='验证吗',location='form')
@api.route('/update')
class VerifyResource(Resource):
    @api.expect(verify_api_parser)
    def post(self):
        '''
        登录
        '''
        args = verify_api_parser.parse_args()

        response_data = {}
        print(args['id'])
        print(args['id'] in DRIVER_MAP)
        if args['id'] in DRIVER_MAP:
            browser = DRIVER_MAP[args['id']]
            elem = browser.find_element_by_id('otp_password')
            elem.send_keys(args['verify_code'])
            btn = browser.find_element_by_xpath("//div[@class='fl']/a[@class='btn-login']")
            btn.click()

            response_data['code'] = 1
            response_data['msg'] = '登录成功'
            s = threading.Timer(10, get_cookie(args['id']), ())
            s.start()

        else:
            response_data['code'] = -1
            response_data['msg'] = '请先扫描二维码'

        return response_data