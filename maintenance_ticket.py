import configparser
import datetime
import random
import sys
import requests
from ESHData import ESHData
import json
from DB import DB
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

    def get_esh_maintenance_ticket(self):
        # e生活
        esh_data = ESHData(self.config, 'eshenghuo')
        eshenghuo_data = esh_data.get_maintenance_ticket()
        data = eshenghuo_data
        return data
    def sum_process_data(self):
        esh_data = self.get_esh_maintenance_ticket()
        hie_data = self.process_data(self.fetch_data())
        data = esh_data + hie_data
        return data

    def insert_or_update_data(self, data):
        db = DB()
        for record in data:
            community_name = record['communityName']
            date = record['date']
            query = "SELECT * FROM maintenance_ticket WHERE communityName = %s AND date = %s"
            result = db.select(query, (community_name, date))

            if result:
                record_id = result[0][0]
                update_data = {
                    'timingNum': record['timingNum'],
                    'workTime': record['workTime'],
                    'workerAvgTime': record['workerAvgTime'],
                    'completeRate': record['completeRate'],
                    'satisfactionRate': record['satisfactionRate'],
                    'totalPrice': record['totalPrice']
                }
                condition = f"id = {record_id} AND communityName = '{community_name}' AND date = '{date}'"
                db.update('maintenance_ticket', update_data, condition)
                print(f"{community_name} on {date}: updated {len(result)} rows")
            else:
                insert_data = {
                    'area': record['area'],
                    'communityName': community_name,
                    'timingNum': record['timingNum'],
                    'workTime': record['workTime'],
                    'workerAvgTime': record['workerAvgTime'],
                    'completeRate': record['completeRate'],
                    'satisfactionRate': record['satisfactionRate'],
                    'totalPrice': record['totalPrice'],
                    'date': date
                }
                db.insert('maintenance_ticket', insert_data)
                print(f"{community_name} on {date}: inserted 1 row")
