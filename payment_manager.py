import configparser
import datetime
import sys
import requests
import json
from login import Login

class PaymentManager:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.FeeCountNumUrl = self.config.get("PaymentManagerFeeCountNumAPI", "url")
        self.FeeCountNumFilters = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "data"))
        self.month_mapping = self.config.get("MonthMapping", "mapping")
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()

        area_data = json.loads(self.config.get("Area", "areaCommunityName"))
        self.area_mapping = {item["communityName"]: item["area"] for item in area_data}
        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")

    def get_fee_count_num(self):
        print(self.FeeCountNumUrl, self.FeeCountNumFilters)

        response = self.session.post(self.FeeCountNumUrl, json=self.FeeCountNumFilters)
        print(response.text)
        sys.exit()
        if response.status_code != 200:
            print(f"Error fetching data from {self.FeeCountNumUrl}")
            return None
        return response.json()