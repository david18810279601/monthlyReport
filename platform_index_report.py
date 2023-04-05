import configparser
import datetime
import sys
import requests
import json
from login import Login

class PlatformIndexReport:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.url = self.config.get("PlatformIndexReportAPI", "url")
        self.filters = json.loads(self.config.get("PlatformIndexReportFilters", "filters"))
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()
        self.eshenghuo_url = self.config.get("EshenghuoPlatformIndexReportAPI", "url")
        self.eshenghuo_filters = json.loads(self.config.get("EshenghuoPlatformIndexReportFilters", "filters"))
        self.eshenghuo_login = Login(self.config, 'eshenghuo')
        self.eshenghuo_session = self.eshenghuo_login.login()
        area_data = json.loads(self.config.get("Area", "areaCommunityName"))
        self.area_mapping = {item["communityName"]: item["area"] for item in area_data}
        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")

    def fetch_data(self):
        # 海e
        count_date = self.config.get("PlatformIndexReportAPI", "countDate")
        url = f"{self.url}?countDate={count_date}"
        response = self.session.post(url, json=self.filters)

        if response.status_code != 200:
            print(f"Error fetching data from {url}")
            return None

        data = response.json()
        # rows = data["data"]["rows"]

        # e生活
        # eshenghuo_response = self.eshenghuo_session.post(self.eshenghuo_url, data=self.eshenghuo_filters)
        # if eshenghuo_response.status_code == 200:
        #     eshenghuo_data = eshenghuo_response.json()
        #     rows.extend(eshenghuo_data["data"]["rows"])
        # else:
        #     print(f"Error fetching data from {self.eshenghuo_url}")
        # data["data"]["rows"] = rows
        return data

    def process_data(self, data):
        rows = data["data"]["rows"]
        result = []
        for row in rows:
            community_name = row["departmentName"]
            if community_name in self.area_mapping:
                result.append({
                    "area": self.area_mapping.get(community_name, ''),
                    "communityName": community_name,
                    "operationNum": row["operationNum"],
                    "employeeActivity": row["employeeActivity"],
                    "saturation": row["saturation"],
                    "completion": row["completion"],
                    "certification": row["certification"],
                    "customerActivity": row["customerActivity"],
                    "reportRate": row["reportRate"],
                    "paymentRate": row["paymentRate"],
                    "date": self.previous_month_str
                })
        return result