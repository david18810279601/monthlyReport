import json
import sys

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

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
        # Set up session with retries
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

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

    #3、E生活缴费管理报告
    def eshenghuo_cost_data(self, url):
        session = requests.Session()
        if self.login_type == "eshenghuo":
            eshenghuo_response = session.post(self.login_url, data=self.payload)
            if eshenghuo_response.status_code == 200:
                payload = {
                    'order': 'asc',
                    'offset': 0,
                    'limit': 100,
                    'filters[0][field]': 'startDate',
                    'filters[0][oper]': 'GreaterThenEq',
                    'filters[0][value]': '2023-03-01',
                    'filters[0][sourceValue]': '2023-03-01',
                    'filters[1][field]': 'endDate',
                    'filters[1][oper]': 'LessThenEq',
                    'filters[1][value]': '2023-03-31',
                    'filters[1][type]': 'date',
                    'filters[1][sourceValue]': '2023-03-31',
                    'filters[2][field]': 'resourceItem',
                    'filters[2][oper]': 'Custom',
                    'filters[2][value]': 'department,A003f7f09862d9384310afe8953935109460',
                    'filters[2][sourceValue]': 'department,A003f7f09862d9384310afe8953935109460',
                    'statType': 3
                }
                eshenghuo_cost_data = session.post(url, data=payload)
                return eshenghuo_cost_data.json()
            else:
                raise Exception("Login failed")

    def eshenghuoProperty_CostsData(self, url, communityId, feeItemId):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            payload = {
                'resourceItem': f'community,{communityId}',
                'feeItemIds': feeItemId,
                'feeMethodIds': '',
                'receivedDateStart': '2023-03-01',
                'receivedDateEnd': '2023-03-31'
            }
            try:
                eshenghuoProperty_CostsData = self.session.post(url, data=payload, timeout=10)
                eshenghuoProperty_CostsData.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            response_data = eshenghuoProperty_CostsData.json()
            amount_paid = response_data.get("obj").get("amountPaid")
            return amount_paid

    def eshenghuoParking_FeeData(self, url, communityId, feeItemId):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            payload = {
                'resourceItem': f'community,{communityId}',
                'feeItemIds': feeItemId,
                'feeMethodIds': '',
                'receivedDateStart': '2023-03-01',
                'receivedDateEnd': '2023-03-31'
            }
            try:
                eshenghuoParking_FeeUrl = self.session.post(url, data=payload, timeout=10)
                eshenghuoParking_FeeUrl.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            response_data = eshenghuoParking_FeeUrl.json()
            amount_paid = response_data.get("obj").get("amountPaid")
            return amount_paid

