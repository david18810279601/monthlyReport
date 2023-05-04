import configparser
import datetime as dt
import sys
import requests
import datetime
import json
from login import Login
from ESHData import ESHData
from DB import DB
from common import Common

class PerformInspection:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.common = Common(config_file)
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()

        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")

    def get_esh_perform_inspection(self):
        #e生活
        esh_data = ESHData(self.config, 'eshenghuo')
        eshenghuo_data = esh_data.get_perform_inspection()
        data = eshenghuo_data
        return data

    def get_hie_perform_inspection(self):
        #hiE
        departments = self.common.get_department_data()['result']
        new_data = []
        for department in departments:
            data_dict = {
                'area': department['area'],
                'communityName': department['community'],
                'cruiseNum': 0,
                'cruiseRate': '0%',
                'cruiseCompletedRate': '0%',
                'workRate': '0%',
                'workNum': 0,
                'workCompletedRate': '0%',
                'date': '202304'
            }
            new_data.append(data_dict)
        return new_data

    def process_data(self):
        esh_data = self.get_esh_perform_inspection()
        hie_data = self.get_hie_perform_inspection()
        data = esh_data + hie_data
        return data

    def insert_or_update_data(self, data):
        db = DB()
        for record in data:
            community_name = record['communityName']
            date = record['date']
            query = "SELECT * FROM perform_inspection WHERE communityName = %s AND date = %s"
            result = db.select(query, (community_name, date))

            if result:
                record_id = result[0][0]
                update_data = {
                    'cruiseNum': record['cruiseNum'],
                    'cruiseRate': record['cruiseRate'],
                    'cruiseCompletedRate': record['cruiseCompletedRate'],
                    'workRate': record['workRate'],
                    'workNum': record['workNum'],
                    'workCompletedRate': record['workCompletedRate']
                }
                condition = f"id = {record_id} AND communityName = '{community_name}' AND date = '{date}'"
                db.update('perform_inspection', update_data, condition)
                print(f"{community_name} on {date}: updated {len(result)} rows")
            else:
                insert_data = {
                    'area': record['area'],
                    'communityName': community_name,
                    'cruiseNum': record['cruiseNum'],
                    'cruiseRate': record['cruiseRate'],
                    'cruiseCompletedRate': record['cruiseCompletedRate'],
                    'workRate': record['workRate'],
                    'workNum': record['workNum'],
                    'workCompletedRate': record['workCompletedRate'],
                    'date': date
                }
                db.insert('perform_inspection', insert_data)
                print(f"{community_name} on {date}: inserted 1 row")
