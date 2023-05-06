import configparser
import datetime as dt
import sys
import requests
from datetime import datetime
import json
from login import Login
from ESHData import ESHData
from DB import DB
from common import Common


class HealthClubData:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()
        self.common = Common(config_file)

        self.previous_month_str = (dt.date.today().replace(day=1) - dt.timedelta(days=1)).strftime("%Y%m")

    #投诉管理
    def esh_health_club_data(self):
        #e生活
        esh_data = ESHData(self.config, 'eshenghuo')
        eshenghuo_data = esh_data.get_health_club_data()
        # print(eshenghuo_data)
        # sys.exit()
        return eshenghuo_data

    def insert_or_update_data(self, data):
        db = DB()
        for record in data:
            community_name = record['communityName']
            date = record['date']
            query = "SELECT * FROM health_club WHERE communityName = %s AND date = %s"
            result = db.select(query, (community_name, date))

            if result:
                record_id = result[0][0]
                update_data = {
                    'memberNum': record['memberNum'],
                    'privateCoachNum': record['privateCoachNum'],
                    'private_training_amount': record['private_training_amount'],
                    'cardUsedNum': record['cardUsedNum'],
                    'unpassNum': record['unpassNum'],
                    'dining_reservation_quantity': record['dining_reservation_quantity'],
                    'foodRevenue': record['foodRevenue']
                }
                condition = f"id = {record_id} AND communityName = '{community_name}' AND date = '{date}'"
                db.update('health_club', update_data, condition)
                print(f"{community_name} on {date}: updated {len(result)} rows")
            else:
                insert_data = {
                    'area': record['area'],
                    'communityName': community_name,
                    'memberNum': record['memberNum'],
                    'privateCoachNum': record['privateCoachNum'],
                    'private_training_amount': record['private_training_amount'],
                    'cardUsedNum': record['cardUsedNum'],
                    'unpassNum': record['unpassNum'],
                    'dining_reservation_quantity': record['dining_reservation_quantity'],
                    'foodRevenue': record['foodRevenue'],
                    'date': date
                }
                db.insert('health_club', insert_data)
                print(f"{community_name} on {date}: inserted 1 row")
