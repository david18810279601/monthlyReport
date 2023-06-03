import configparser
import datetime as dt
import sys
import requests
import inflect
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

        #合同付款
        self.get_actionTrackerUrl = self.config.get("ContractManagementAPI", "actionTrackerUrl")
        self.get_actionTrackerFilters = json.loads(self.config.get("ContractManagementAPI", "actionTrackerFilters"))

        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")


    def get_esh_contractManagement(self):
        #e生活
        esh_data = ESHData(self.config, 'eshenghuo')
        eshenghuo_data = esh_data.get_esh_process_data()
        data = eshenghuo_data
        return data

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
            print(f"Error contractManagement data from {self.get_contractManagementUrl}")
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
            print(f"Error maturity data from {departmentId}")
            return 0

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

    from datetime import datetime

    def get_actionTracker(self, companyId):
        self.get_actionTrackerFilters['companyId'] = companyId
        response = self.session.post(self.get_actionTrackerUrl, json=self.get_actionTrackerFilters)
        if response.status_code == 200:
            data = response.json()
            payable_data = {'payable': 0, 'payment': 0}

            if 'rows' in data['data']:
                current_date = datetime.datetime.now()
                previous_month = (current_date.month - 1) if current_date.month > 1 else 12
                p = inflect.engine()
                month_word = p.number_to_words(previous_month).capitalize()
                payable_key = f'payable{month_word}'
                payment_key = f'payment{month_word}'

                for row in data['data']['rows']:
                    payable_value = row.get(payable_key, 0)
                    payment_value = row.get(payment_key, 0)
                    payable_data['payable'] += payable_value
                    payable_data['payment'] += payment_value

            return payable_data
        else:
            print(f"Error fetching data from {self.get_actionTrackerUrl}")
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
                'communityName': department['community'],
                'new_contract': self.get_contractManagement(department['departmentId']),
                'maturity': self.get_maturity(department['departmentId']),
                'contract_progress': self.get_contractManagement(department['departmentId']),
                'actual_payment': self.get_actual_payment(department['departmentId']),
                'tangible_receipts': self.get_tangible_receipts(department['departmentId']),
                'payment_plan': self.get_actionTracker(department['departmentId'])['payable'],
                'collection_plan': self.get_actionTracker(department['departmentId'])['payment'],
                "date": self.previous_month_str
            }
            for department in departments
        ]
        print(result)
        sys.exit(0)
        cobmo_data = result + self.get_esh_contractManagement()
        return cobmo_data

    def insert_or_update_data(self, data):
        db = DB()
        for record in data:
            community_name = record['communityName']
            date = record['date']
            query = "SELECT * FROM contract_management WHERE communityName = %s AND date = %s"
            result = db.select(query, (community_name, date))

            if result:
                record_id = result[0][0]
                update_data = {
                    'area': record['area'],
                    'new_contract': record['new_contract'],
                    'maturity': record['maturity'],
                    'contract_progress': record['contract_progress'],
                    'actual_payment': record['actual_payment'],
                    'tangible_receipts': record['tangible_receipts'],
                    'payment_plan': record['payment_plan'],
                    'collection_plan': record['collection_plan']
                }
                condition = f"id = {record_id} AND communityName = '{community_name}' AND date = '{date}'"
                db.update('contract_management', update_data, condition)
                print(f"{community_name} on {date}: updated {len(result)} rows")
            else:
                insert_data = {
                    'area': record['area'],
                    'communityName': community_name,
                    'new_contract': record['new_contract'],
                    'maturity': record['maturity'],
                    'contract_progress': record['contract_progress'],
                    'actual_payment': record['actual_payment'],
                    'tangible_receipts': record['tangible_receipts'],
                    'payment_plan': record['payment_plan'],
                    'collection_plan': record['collection_plan'],
                    'date': date
                }
                db.insert('contract_management', insert_data)
                print(f"{community_name} on {date}: inserted 1 row")
