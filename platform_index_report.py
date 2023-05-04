import configparser
import datetime
import sys
import requests
import json
from login import Login
from ESHData import ESHData
from common import Common
from DB import DB

class PlatformIndexReport:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.common = Common(config_file)
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
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        count_date = start_time.strftime("%Y-%m-%d")
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
        self.eshenghuo_filters["filters[0][value]"] = start_time.strftime("%Y-%m")
        self.eshenghuo_filters["filters[0][sourceValue]"] = start_time.strftime("%Y-%m")

        eshenghuo_data = esh_data.platform_index_report(self.eshenghuo_url, self.eshenghuo_filters)
        data = eshenghuo_data['rows']

        esh_filtered_data = [item for item in data if item['departmentName'] in self.eshenghuo_filters_data['communities']]
        esh_cleaned_data = self.clean_data(esh_filtered_data)
        return hie_filtered_data + esh_filtered_data

    def clean_data(self, data):
        for item in data:
            for key in ['employeeActivity', 'saturation', 'completion', 'certification', 'customerActivity',
                        'reportRate', 'paymentRate']:
                value = item.get(key)
                if value is None:
                    item[key] = '-'
                elif value not in [0.0, '-']:
                    item[key] = str(round(value * 100, 2)) + '%'
        return data

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

    def insert_or_update_data(self, data):
        db = DB()
        for record in data:
            community_name = record['communityName']
            date = record['date']
            query = "SELECT * FROM operation WHERE communityName = %s AND date = %s"
            result = db.select(query, (community_name, date))

            if result:
                record_id = result[0][0]
                update_data = {
                    'operationNum': record['operationNum'],
                    'employeeActivity': record['employeeActivity'],
                    'saturation': record['saturation'],
                    'completion': record['completion'],
                    'certification': record['certification'],
                    'customerActivity': record['customerActivity'],
                    'reportRate': record['reportRate'],
                    "paymentRate": record["paymentRate"]
                }
                condition = f"id = {record_id} AND communityName = '{community_name}' AND date = '{date}'"
                db.update('operation', update_data, condition)
                print(f"{community_name} on {date}: updated {len(result)} rows")
            else:
                insert_data = {
                    'area': record['area'],
                    'communityName': community_name,
                    'operationNum': record['operationNum'],
                    'employeeActivity': record['employeeActivity'],
                    'saturation': record['saturation'],
                    'completion': record['completion'],
                    'certification': record['certification'],
                    'customerActivity': record['customerActivity'],
                    'reportRate': record['reportRate'],
                    "paymentRate": record["paymentRate"],
                    'date': date
                }
                db.insert('operation', insert_data)
                print(f"{community_name} on {date}: inserted 1 row")
