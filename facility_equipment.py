import configparser
import datetime
import sys
import requests
import json
from login import Login

class FacilityEquipment:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.url = self.config.get("FacilityEquipmentAPI", "url")
        self.filters = json.loads(self.config.get("FacilityEquipmentFilters", "filters"))
        self.login = Login(self.config)
        self.session = self.login.login()

    def fetch_data(self):
        response = self.session.post(self.url, json=self.filters)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching data from {self.url}")
            return None

    def process_facility_equipment_data(self, data):
        area_data = json.loads(self.config.get("Area", "area"))
        area_mapping = {item["communityName"]: item["area"] for item in area_data}

        # 获取上一个月的日期字符串
        today = datetime.date.today()
        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
        previous_month_str = last_day_of_previous_month.strftime("%Y%m")

        results = []
        for row in data["data"]["rows"]:
            area = area_mapping.get(row["communityName"], "")
            results.append({
                "area": area,
                "communityName": row["communityName"],
                "deviceSum": row["deviceSum"],
                "normalRate": row["normalRate"],
                "date": previous_month_str
            })
        return results