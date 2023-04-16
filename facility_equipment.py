import configparser
import datetime
import sys
import requests
import json
from login import Login
from common import Common

class FacilityEquipment:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.common = Common(config_file)
        self.url = self.config.get("FacilityEquipmentAPI", "url")
        self.filters = json.loads(self.config.get("FacilityEquipmentFilters", "filters"))
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()

        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")

    def fetch_data(self):
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        formatted_start_time = start_time.strftime("%Y-%m-%d")
        end_time = self.common.get_month_start_end_dates("END_ALL")
        formatted_end_time = end_time.strftime("%Y-%m-%d")
        self.filters["startDate"] = formatted_start_time
        self.filters["endDate"] = formatted_end_time
        response = self.session.post(self.url, json=self.filters)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching data from {self.url}")
            return None

    def process_facility_equipment_data(self, data):
        departments = self.common.get_department_data()['result']
        area_mapping = {item["communityName"]: item["area"] for item in departments}

        results = []
        for row in data["data"]["rows"]:
            area = area_mapping.get(row["communityName"], "")
            results.append({
                "area": area,
                "communityName": row["communityName"],
                "deviceSum": row["deviceSum"],
                "normalRate": row["normalRate"],
                "date": self.previous_month_str
            })
        return results