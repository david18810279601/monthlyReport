import configparser
import datetime as dt
import sys
import requests
import datetime
import json
from login import Login
from ESHData import ESHData
from DB import DB
from common import Common

class ContractManagement:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.common = Common(config_file)
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()
        #新增合同
        self.get_contractManagementUrl = self.config.get("ContractManagementAPI", "ContractManagementUrl")
        self.get_ontractManagementFilters = json.loads(self.config.get("ContractManagementAPI", "ContractManagementFilters"))
        self.get_actual_paymentUrl = self.config.get("ContractManagementAPI", "actual_paymentUrl")
        self.get_actual_paymentFilters = json.loads(self.config.get("ContractManagementAPI", "actual_paymentFilters"))
        self.get_payment_planUrl = self.config.get("ContractManagementAPI", "payment_planUrl")
        self.get_payment_planFilters = json.loads(self.config.get("ContractManagementAPI", "payment_planFilters"))
        self.get_collection_planUrl = self.config.get("ContractManagementAPI", "collection_planUrl")
        self.get_collection_planFilters = json.loads(self.config.get("ContractManagementAPI", "collection_planFilters"))
        self.get_maturityFilter = json.loads(self.config.get("ContractManagementAPI", "maturityFilter"))

        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")


    def get_contractManagement(self, departmentId):
        self.get_ontractManagementFilters['filters'][0]['value'] = departmentId
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = self.common.get_month_start_end_dates("END_ALL")
        formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

        self.get_ontractManagementFilters['filters'][2]['value'] = formatted_start_time
        self.get_ontractManagementFilters['filters'][3]['value'] = formatted_end_time
        response = self.session.post(self.get_contractManagementUrl, json=self.get_ontractManagementFilters)
        if response.status_code == 200:
            data = response.json()
            return data['data']['total']
        else:
            print(f"Error fetching data from {self.get_contractManagementUrl}")
            return None
    def get_maturity(self, departmentId):
        self.get_maturityFilter['filters'][0]['value'] = departmentId
        end_time = self.common.get_month_start_end_dates("END_ALL")
        formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
        self.get_maturityFilter['filters'][2]['value'] = formatted_end_time
        response = self.session.post(self.get_contractManagementUrl, json=self.get_maturityFilter)
        if response.status_code == 200:
            data = response.json()
            return data['data']['total']
        else:
            print(f"Error fetching data from {self.get_contractManagementUrl}")
            return None

    # 实际付款
    def get_actual_payment(self, departmentId):
        self.get_actual_paymentFilters['filters'][1]['value'] = departmentId
        response = self.session.post(self.get_actual_paymentUrl, json=self.get_actual_paymentFilters)
        if response.status_code == 200:
            data = response.json()
            return data['data']['rowCount']
        else:
            print(f"Error fetching data from {self.get_actual_paymentUrl}")
            return None

    # 实际收款
    def get_tangible_receipts(self, departmentId):
        self.get_actual_paymentFilters['filters'][1]['value'] = departmentId
        self.get_actual_paymentFilters['filters'][4]['value'] = 1
        response = self.session.post(self.get_actual_paymentUrl, json=self.get_actual_paymentFilters)
        if response.status_code == 200:
            data = response.json()
            return data['data']['rowCount']
        else:
            print(f"Error fetching data from {self.get_actual_paymentUrl}")
            return None
    # 付款计划
    def get_payment_plan(self, departmentId):
        self.get_payment_planFilters['filters'][1]['value'] = departmentId
        response = self.session.post(self.get_payment_planUrl, json=self.get_payment_planFilters)
        if response.status_code == 200:
            data = response.json()
            return data['data']['rowCount']
        else:
            print(f"Error fetching data from {self.get_payment_planUrl}")
            return None
    def get_collection_plan(self, departmentId):
        self.get_collection_planFilters['filters'][1]['value'] = departmentId
        response = self.session.post(self.get_collection_planUrl, json=self.get_collection_planFilters)
        if response.status_code == 200:
            data = response.json()
            return data['data']['rowCount']
        else:
            print(f"Error fetching data from {self.get_collection_planUrl}")
            return None

    def get_contractManagement_data(self):
        departments = self.common.get_department_data()['result']
        result = [
            {
                'area': department['area'],
                'community': department['community'],
                'new_contract': self.get_contractManagement(department['departmentId']),
                'maturity': self.get_maturity(department['departmentId']),
                'contract_progress': self.get_contractManagement(department['departmentId']),
                'actual_payment': self.get_actual_payment(department['departmentId']),
                'tangible_receipts': self.get_tangible_receipts(department['departmentId']),
                'payment_plan': self.get_payment_plan(department['departmentId']),
                'collection_plan': self.get_collection_plan(department['departmentId']),
                "date": self.previous_month_str
            }
            for department in departments
        ]

        return result