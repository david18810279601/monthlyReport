import configparser
import sys
import requests
import json
from login import Login

class MaintenanceTicket:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.url = self.config.get("MaintenanceTicketAPI", "url")
        self.filters = json.loads(self.config.get("MaintenanceFilters", "filters"))
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

    def process_data(self, data):
        area_data = json.loads(self.config.get("Area", "area"))
        area_mapping = {item["communityName"]: item["area"] for item in area_data}

        results = []
        for row in data["data"]["rows"]:
            area = area_mapping.get(row["communityName"], "")
            results.append({
                "area": area,
                "communityName": row["communityName"],
                "timingNum": row["timingNum"],
                "workTime": row["workTime"],
                "workerAvgTime": row["workerAvgTime"],
                "completeRate": "100%",
                "satisfactionRate": "100%",
                "totalPrice": row["totalPrice"]
            })
        return results
