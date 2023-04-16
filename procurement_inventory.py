import configparser
import datetime
import json
import sys

from login import Login
from common import Common

class ProcurementInventory:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.common = Common(config_file)
        self.get_budgeturl = self.config.get("ProcurementInventoryAPI", "get_budgeturl")
        self.get_filters = json.loads(self.config.get("ProcurementInventoryAPI", "filters"))
        #采购订单
        # self.purchaseOrderUrl = self.config.get("ProcurementInventoryAPI", "purchaseOrderUrl")
        # self.purchaseOrderFilters = json.loads(self.config.get("ProcurementInventoryFilters", "purchaseOrder"))
        #库存列表
        # self.inventoryUrl = self.config.get("ProcurementInventoryAPI", "inventoryUrl")
        # self.inventoryFilters = json.loads(self.config.get("ProcurementInventoryFilters", "inventoryFilters"))
        self.month_mapping = json.loads(self.config.get("MonthMapping", "mapping"))
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()
        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")

    #采购预算
    def get_budget(self, departmentId):
        self.get_filters['filters'][0]['value'] = departmentId
        end_time = self.common.get_month_start_end_dates("END_ALL")
        formatted_date_year = end_time.strftime("%Y")
        self.get_filters['filters'][1]['value'] = formatted_date_year
        response = self.session.post(self.get_budgeturl, json=self.get_filters)
        if response.status_code == 200:
            data = response.json()['data']['rows']

            return self.get_budget_process_data(data)
        else:
            print(f"Error fetching data from {self.get_budgeturl}")
            return None

    # def purchase_order(self):
    #     response = self.session.post(self.purchaseOrderUrl, json=self.purchaseOrderFilters)
    #     if response.status_code == 200:
    #         data = response.json()
    #         return data
    #     else:
    #         print(f"Error fetching data from {self.purchaseOrderUrl}")
    #         return None
    # #库存列表
    # def inventory(self):
    #     response = self.session.post(self.inventoryUrl, json=self.inventoryFilters)
    #     if response.status_code == 200:
    #         data = response.json()
    #         return data
    #     else:
    #         print(f"Error fetching data from {self.inventoryUrl}")
    #         return None

    def get_budget_process_data(self, data):
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        previous_month_str = start_time.strftime("%m")
        month_key = self.month_mapping.get(previous_month_str, '')
        result = data[0].get(month_key, 0)

        return result

    def process_data(self):
        departments = self.common.get_department_data()['result']
        result = [
            {
                'area': department['area'],
                'communityName': department['communityName'],
                'budget': self.get_budget(department['departmentId']),
                "date": self.previous_month_str
            }
            for department in departments
        ]

        return result
