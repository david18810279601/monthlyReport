import configparser
import datetime
import sys
import requests
import json
from ESHData import ESHData
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

    def esh_facility_equipment_data(self):
        #e生活
        esh_data = ESHData(self.config, 'eshenghuo')
        # eshenghuo_data = esh_data.ESH_facility_equipment_data()

        eshenghuo_data = [{'area': '武汉地区', 'communityName': '武汉•泛海城市广场一期', 'deviceSum': 32648, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•泛海城市广场二期', 'deviceSum': 2100, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•桂海园', 'deviceSum': 103873, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•松海园', 'deviceSum': 88022, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•竹海园', 'deviceSum': 79654, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•长江证券', 'deviceSum': 0, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•SOHO12', 'deviceSum': 523181, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•SOHO11', 'deviceSum': 787181, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•香兰海园', 'deviceSum': 471832, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•民生金融中心', 'deviceSum': 569964, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•樱海园', 'deviceSum': 72759, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•悦海园', 'deviceSum': 98846, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•碧海园', 'deviceSum': 0, 'normalRate': '0%', 'date': '202304'},
                            {'area': '武汉地区', 'communityName': '武汉•芸海园', 'deviceSum': 63515, 'normalRate': '0%', 'date': '202304'},
                            {'area': '北京地区', 'communityName': '泛海国际居住区一期会所', 'deviceSum': 26878, 'normalRate': '0%', 'date': '202304'},
                            {'area': '北京地区', 'communityName': '泛海国际居住区二期世家会所', 'deviceSum': 294277, 'normalRate': '0%', 'date': '202304'},
                            {'area': '北京地区', 'communityName': '泛海国际居住区二期容郡会所', 'deviceSum': 164358, 'normalRate': '0%', 'date': '202304'}]
        # print(eshenghuo_data)
        # sys.exit()
        return eshenghuo_data

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

    def process_data(self):
        eshenghuo_data = self.esh_facility_equipment_data()
        haie_process_data = self.process_facility_equipment_data(self.fetch_data())
        merged_data = eshenghuo_data + haie_process_data
        return merged_data