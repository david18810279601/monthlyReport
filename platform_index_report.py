import configparser
import datetime
import sys
import requests
import json
from login import Login
from ESHData import ESHData

class PlatformIndexReport:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.url = self.config.get("PlatformIndexReportAPI", "url")
        self.filters = json.loads(self.config.get("PlatformIndexReportFilters", "filters"))
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()
        self.eshenghuo_url = self.config.get("EshenghuoPlatformIndexReportAPI", "url")
        self.eshenghuo_filters = json.loads(self.config.get("EshenghuoPlatformIndexReportAPI", "filters"))
        self.eshenghuo_filters_data = json.loads(self.config.get("EshenghuoFilter", "EshenghuoFilterData"))
        self.hie_filters_data = json.loads(self.config.get("HiEFilter", "FilterData"))
        self.eshenghuo_login = Login(self.config, 'eshenghuo')
        # self.eshenghuo_session = self.eshenghuo_login.login()
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
        rows = data["data"]["rows"]
        hie_filtered_data = [item for item in rows if item['departmentName'] in self.hie_filters_data['centers']]

        #e生活
        esh_data = ESHData(self.config, 'eshenghuo')
        eshenghuo_data = esh_data.platform_index_report(self.eshenghuo_url, self.eshenghuo_filters)
        data = eshenghuo_data['rows']

        esh_filtered_data = [item for item in data if item['departmentName'] in self.eshenghuo_filters_data['communities']]
        return hie_filtered_data + esh_filtered_data

    def process_data(self, data):
        rows = data
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