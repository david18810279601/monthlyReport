import configparser
import datetime
import json
import sys
from ESHData import ESHData
from login import Login
from common import Common
from DB import DB

class ProcurementInventory:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.common = Common(config_file)
        self.get_budgeturl = self.config.get("ProcurementInventoryAPI", "get_budgeturl")
        self.get_filters = json.loads(self.config.get("ProcurementInventoryAPI", "filters"))
        #采购订单
        self.get_extraListUrl = self.config.get("ProcurementInventoryAPI", "get_extraListUrl")
        self.get_extraListFilters = json.loads(self.config.get("ProcurementInventoryAPI", "get_extraListFilters"))
        #库存列表
        self.get_property_stock_url = self.config.get("ProcurementInventoryAPI", "property_stock_url")
        self.get_property_stock_filters = json.loads(self.config.get("ProcurementInventoryAPI", "property_stock_filters"))

        self.month_mapping = json.loads(self.config.get("MonthMapping", "mapping"))
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()
        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")

    def get_esh_contractManagement(self):
        #e生活
        esh_data = ESHData(self.config, 'eshenghuo')
        eshenghuo_data = esh_data.ESHprocurement_inventory()
        data = eshenghuo_data
        return data

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

    def get_extraList(self, departmentId):
        extraListUrl = f"{self.get_extraListUrl}?departmentId={departmentId}&filterKeyword="

        end_time = self.common.get_month_start_end_dates("END_ALL")
        formatted_date_year = end_time.strftime("%Y-%m")
        self.get_extraListFilters['filters'][0]['value'] = formatted_date_year

        response = self.session.post(extraListUrl, json=self.get_extraListFilters)
        if response.status_code == 200:
            data = response.json()
            if data['resultCode'] == '00000' and data['data']['rowCount'] != 0:
                total_money = 0
                for row in data['data']['rows']:
                    total_money += row['money']
                return total_money
            else:
                return 0
        else:
            print(f"Error fetching data from {self.get_extraListUrl}")
            return None

    #库存列表
    def get_property_stock(self, companyId):
        self.get_property_stock_filters['filters'][0]['value'] = companyId
        response = self.session.post(self.get_property_stock_url, json=self.get_property_stock_filters)
        if response.status_code == 200:
            data = response.json()['data']['rows']
            total_money = 0
            if data:
                for item in data:
                    avg_price = item['avgPrice']
                    current_stock_qty = item['currentStockQty']
                    total_money += round(avg_price * current_stock_qty, 2)
                return total_money
            else:
                return 0
        else:
            print(f"Error fetching data from {self.get_property_stock_url}")
            return None

    def get_budget_process_data(self, data):
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        previous_month_str = start_time.strftime("%m")
        month_key = self.month_mapping.get(previous_month_str, '')
        if len(data) > 0:
            result = data[0].get(month_key, 0)
        else:
            print("Error: data list is empty.")
            result = 0  # Or any other default value you prefer

        return result

    def process_data(self):
        departments = self.common.get_department_data()['result']
        result = [
            {
                'area': department['area'],
                'communityName': department['communityName'],
                'budget': self.get_budget(department['departmentId']),
                'extraList': self.get_extraList(department['departmentId']),
                'property_stock': self.get_property_stock(department['departmentId']),
                "date": self.previous_month_str
            }
            for department in departments
        ]

        return result

    #合并数据
    def combine_data(self):
        esh_data = self.get_esh_contractManagement()
        procurement_inventory_data = self.process_data()
        result = procurement_inventory_data + esh_data
        return result

    def insert_or_update_data(self, data):
        db = DB()
        for record in data:
            community_name = record['communityName']
            date = record['date']
            query = "SELECT * FROM procurement_inventory WHERE communityName = %s AND date = %s"
            result = db.select(query, (community_name, date))

            if result:
                record_id = result[0][0]
                update_data = {
                    'budget': record['budget'],
                    'extraList': record['extraList'],
                    'toDayList': record['extraList'],
                    'property_stock': record['property_stock'],
                }
                condition = f"id = {record_id} AND communityName = '{community_name}' AND date = '{date}'"
                db.update('procurement_inventory', update_data, condition)
                print(f"{community_name} on {date}: updated {len(result)} rows")
            else:
                insert_data = {
                    'area': record['area'],
                    'communityName': community_name,
                    'budget': record['budget'],
                    'extraList': record['extraList'],
                    'toDayList': record['extraList'],
                    'property_stock': record['property_stock'],
                    'date': date
                }
                db.insert('procurement_inventory', insert_data)
                print(f"{community_name} on {date}: inserted 1 row")
