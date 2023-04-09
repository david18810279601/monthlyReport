import json
import sys

import requests


class ESHData:
    def __init__(self, config, login_type):
        self.login_type = login_type
        if login_type == "eshenghuo":
            self.login_url = config.get("LOGIN", "eshenghuo_url")
            eshenghuo_login_data = json.loads(config.get("EshenghuoLoginInformation", "EshenghuoLoginData"))
            self.payload = {
                "j_username": eshenghuo_login_data["j_username"],
                "j_password": eshenghuo_login_data["j_password"],
            }

    def platform_index_report(self, url, filters):
        session = requests.Session()
        if self.login_type == "eshenghuo":
            eshenghuo_response = session.post(self.login_url, data=self.payload)
            if eshenghuo_response.status_code == 200:
                platform_index_report = session.post(url, filters)
                return platform_index_report.json()
            else:
                raise Exception("Login failed")

    #2、E生活客服报告
    def eshenghuoComplaintCount(self, url):
        session = requests.Session()
        if self.login_type == "eshenghuo":
            eshenghuo_response = session.post(self.login_url, data=self.payload)
            if eshenghuo_response.status_code == 200:
                payload = {
                    'resourceItem': 'department,A003f7f09862d9384310afe8953935109460',
                    'startDate': '2023-03-01',
                    'endDate': '2023-03-31',
                    'selectType': '2',
                    'filters[0][field]': 'resourceItem',
                    'filters[0][oper]': 'Custom',
                    'filters[0][value]': 'department,A003f7f09862d9384310afe8953935109460',
                    'filters[0][sourceValue]': 'department,A003f7f09862d9384310afe8953935109460',
                }
                EshenghuoComplaintCount = session.post(url, data=payload)
                data = EshenghuoComplaintCount.json()
                return data['list']
            else:
                raise Exception("Login failed")
