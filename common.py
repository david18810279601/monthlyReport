import configparser
import sys
import time
import requests
from RedisClient import RedisClient
from datetime import datetime
import json
from login import Login
from DB import DB
import datetime
import calendar

class Common:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()

        self.get_departmentUrl = self.config.get("common","get_departmentUrl")
        self.get_departmentCode = self.config.get("common","get_departmentCode")
        self.get_departmentFilterData = json.loads(self.config.get("common","get_departmentFilterData"))
        self.get_communityNameUrl = self.config.get("common","get_communityNameUrl")
        self.get_communityFilterData = json.loads(self.config.get("common","get_communityFilterData"))
        self.get_departmentlistUrl = self.config.get("common","get_departmentlistUrl")
        self.get_communityIdUrl = self.config.get("common","get_communityIdUrl")
        self.get_communityIdFilterData = json.loads(self.config.get("common","get_communityIdFilterData"))
        self.diff = json.loads(self.config.get("common","diff"))

    # 函数返回一个包含月初和月末日期的字典，其中year键包含提供的年份或当前年份，start键包含月初日期，end键包含月末日期。

     # Example output: 2023-03-01 00:00:00
     # Example output: 2023-03-30 00:00:00
     # Example output: {"year": 2023, "start": datetime.date(2023, 3, 1), "end": datetime.date(2023, 3, 30)}
    # def get_month_start_end_dates(self, option=None, year=None):
    #     now = datetime.datetime.now()
    #     now = now - datetime.timedelta(days=now.day)
    #     if year and isinstance(year, int):
    #         now = datetime.datetime(year=year, month=now.month, day=1)
    #     start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    #     _, num_days = calendar.monthrange(now.year, now.month)
    #     end_of_month = start_of_month.replace(day=num_days)
    #
    #     if option == "ST_ALL":
    #         return start_of_month
    #     elif option == "END_ALL":
    #         return end_of_month
    #     else:
    #         return {"year": now.year, "start": start_of_month.date(), "end": end_of_month.date()}

    def get_month_start_end_dates(self, option=None, year=None, sDate=None, eDate=None):
        now = datetime.datetime.now()
        if sDate or eDate:
            if sDate:
                start_of_month = datetime.datetime.strptime(sDate, '%Y-%m-%d').date()
            else:
                start_of_month = datetime.datetime.strptime(eDate, '%Y-%m-%d').date().replace(day=1)
            _, num_days = calendar.monthrange(start_of_month.year, start_of_month.month)
            end_of_month = start_of_month.replace(day=num_days)
        else:
            now = now - datetime.timedelta(days=now.day)
            if year and isinstance(year, int):
                now = datetime.datetime(year=year, month=now.month, day=1)
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            _, num_days = calendar.monthrange(now.year, now.month)
            end_of_month = start_of_month.replace(day=num_days)

        if option == "ST_ALL":
            return start_of_month
        elif option == "END_ALL":
            return end_of_month
        else:
            return {"year": now.year, "start": start_of_month.date(), "end": end_of_month.date()}

    def get_department(self):
        response = self.session.post(self.get_departmentUrl, json=self.get_departmentFilterData)
        if response.status_code == 200:
            data = response.json()['data']['rows']
            return data
        else:
            print(f"Error fetching data from {self.get_departmentUrl}")
            return None

    def clean_department_data(self, department_data):
        result = []
        for department in department_data:
            name = department['name']
            company_id = department['companyId']
            city_id = department['cityId']

            result.append({'area': name, 'cityId': city_id, 'companyId': company_id})
        return result

    # 获取项目名称
    def get_communityName(self, departmentId):
        self.get_communityFilterData['filters'][0]['value'] = departmentId
        response = self.session.post(self.get_communityNameUrl, json=self.get_communityFilterData)
        if response.status_code == 200:
            data = response.json()['data']['rows']
            return data
        else:
            print(f"Error fetching data from {self.get_communityNameUrl}")
            return None

    def get_departmentList(self, departmentId):
        url = f"{self.get_departmentlistUrl}?departmentId={departmentId}&name=&codeName="
        response = self.session.post(url, json=self.get_departmentFilterData)
        if response.status_code == 200:
            data = response.json()['data']['rows']
            return data
        else:
            print(f"Error fetching data from {self.get_departmentlistUrl}")
            return None

    def get_communityId(self, departmentId):
        self.get_communityIdFilterData['filters'][0]['value'] = departmentId
        response = self.session.post(self.get_communityIdUrl, json=self.get_communityIdFilterData)
        if response.status_code == 200:
            data = response.json()['data']['rows']
            return data
        else:
            print(f"Error fetching data from {self.get_communityIdUrl}")
            return None

    def remove_duplicates(self,result):
        unique_departments = set()
        unique_result = []
        for data in result['result']:
            if data['departmentId'] not in unique_departments:
                unique_departments.add(data['departmentId'])
                unique_result.append(data)
        return {'timestamp': result['timestamp'], 'result': unique_result}

    def get_departments_with_parent(self, company_data, diff=None):
        redis = RedisClient()
        redis_key = "departments_data"
        unique_result = redis.get_key(redis_key)
        result = self.remove_duplicates(unique_result)

        if not result or self.is_result_expired(result):
            result = [
                {
                    "area": parent_department['parent'],
                    "community": parent_department['name'],
                    "communityName": parent_communityName['name'],
                    "departmentId": parent_department['id'],
                    "communityId": parent_communityId['id'],
                    "departments": [
                        {
                            "name": child_department['name'],
                            "id": child_department['id']
                        }
                        for child_department in self.get_departmentList(parent_department['id'])
                        if child_department['parentId'] == parent_department['id']
                    ]
                }
                for company in company_data
                for parent_department in self.get_departmentList(company['companyId'])
                for parent_communityId in self.get_communityId(parent_department['id'])
                for parent_communityName in self.get_communityName(parent_department['id'])
                if self.get_departmentList(parent_department['id'])
            ]
            # Save result to Redis with a timestamp
            current_time = int(time.time())
            data_with_timestamp = {"timestamp": current_time, "result": result}
            redis.set_key(redis_key, data_with_timestamp)

        if diff and result:
            result = self.remove_data(result, diff)
            redis.update_key(redis_key, result)
        return result

    def is_result_expired(self, data_with_timestamp):
        current_time = int(time.time())
        one_month_seconds = 30 * 24 * 60 * 60

        if "timestamp" not in data_with_timestamp:
            return True

        time_diff = current_time - data_with_timestamp["timestamp"]
        if time_diff > one_month_seconds:
            return True

        return False

    def remove_data(self, result, diff=None):
        department_ids = diff.get("departmentId", "").split(",")
        result["result"] = [item for item in result["result"] if str(item.get("departmentId")) not in department_ids]
        return result

    def get_department_data(self,diff=None):
        department_data = self.get_department()
        department_data = self.clean_department_data(department_data)
        get_departments_with_parent = self.get_departments_with_parent(department_data, self.diff)
        return get_departments_with_parent

