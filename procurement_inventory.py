import configparser
import datetime
import json
from login import Login


class ProcurementInventory:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.url = self.config.get("ProcurementInventoryAPI", "url")
        self.filters = json.loads(self.config.get("ProcurementInventoryFilters", "filters"))
        #采购订单
        self.purchaseOrderUrl = self.config.get("ProcurementInventoryAPI", "purchaseOrderUrl")
        self.purchaseOrderFilters = json.loads(self.config.get("ProcurementInventoryFilters", "purchaseOrder"))
        #库存列表
        self.inventoryUrl = self.config.get("ProcurementInventoryAPI", "inventoryUrl")
        self.inventoryFilters = json.loads(self.config.get("ProcurementInventoryFilters", "inventoryFilters"))
        self.month_mapping = json.loads(self.config.get("MonthMapping", "mapping"))
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()

    def fetch_data(self):
        response = self.session.post(self.url, json=self.filters)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching data from {self.url}")
            return None

    def purchase_order(self):
        response = self.session.post(self.purchaseOrderUrl, json=self.purchaseOrderFilters)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching data from {self.purchaseOrderUrl}")
            return None
    #库存列表
    def inventory(self):
        response = self.session.post(self.inventoryUrl, json=self.inventoryFilters)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching data from {self.inventoryUrl}")
            return None

    def process_data(self, data):
        department_id_mapping = json.loads(self.config.get("WisdomTicketCommunities", "community_list"))
        today = datetime.date.today()
        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
        previous_month_str = last_day_of_previous_month.strftime("%Y%m")
        month_key = self.month_mapping.get(previous_month_str, '')

        results = []
        for row in data['data']['rows']:
            for community in department_id_mapping:
                if row['departmentId'] == community['departmentId']:
                    area = community['area']
                    community_name = community['community']
                    break
            else:
                continue

            month_money = row.get(month_key, 0)

            results.append({
                "area": area,
                "community": community_name,
                "date": previous_month_str,
                month_key: month_money
            })

        return results
