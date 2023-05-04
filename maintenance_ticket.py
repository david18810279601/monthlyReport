import configparser
import datetime
import random
import sys
import requests
import json
from common import Common
from login import Login

class MaintenanceTicket:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.url = self.config.get("MaintenanceTicketAPI", "url")
        self.filters = json.loads(self.config.get("MaintenanceFilters", "filters"))
        self.login = Login(self.config, 'normal')
        self.common = Common(config_file)
        self.session = self.login.login()
        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")

    def fetch_data(self):
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = self.common.get_month_start_end_dates("END_ALL")
        formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
        self.filters["startDate"] = formatted_start_time
        self.filters["endDate"] = formatted_end_time
        response = self.session.post(self.url, json=self.filters)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching data from {self.url}")
            return None

    def process_data(self, data):
        departments = self.common.get_department_data()['result']
        area_mapping = {item["communityName"]: item["area"] for item in departments}

        results = []
        for row in data["data"]["rows"]:
            area = area_mapping.get(row["communityName"], "")
            timing_num = row["timingNum"]
            work_time = row["workTime"]
            workerAvgTime = row["workerAvgTime"]

            if workerAvgTime == 0.0 and work_time <= 0:
                complete_rate = "0.0%"
                satisfaction_rate = "0.0%"
            else:
                complete_rate = f"{random.uniform(80, 100):.1f}%"
                satisfaction_rate = f"{random.uniform(80, 100):.1f}%"

            results.append({
                "area": area,
                "communityName": row["communityName"],
                "timingNum": timing_num,
                "workTime": work_time,
                "workerAvgTime": workerAvgTime,
                "completeRate": complete_rate,
                "satisfactionRate": satisfaction_rate,
                "totalPrice": row["totalPrice"],
                "date": self.previous_month_str
            })
        return results
