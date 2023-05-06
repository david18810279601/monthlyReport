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


class EcommerceOperation:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()
        self.common = Common(config_file)

        self.previous_month_str = (dt.date.today().replace(day=1) - dt.timedelta(days=1)).strftime("%Y%m")

    #电商运营
    def esh_ecommerce_operation_data(self):
        #e生活
        esh_data = ESHData(self.config, 'eshenghuo')
        eshenghuo_data = esh_data.ESH_e_commerce_operation_data()
        # print(eshenghuo_data)
        # sys.exit()
        return eshenghuo_data

    def insert_or_update_data(self, data):
        db = DB()
        for record in data:
            community_name = record['communityName']
            date = record['date']
            query = "SELECT * FROM ecommerce_operation WHERE communityName = %s AND date = %s"
            result = db.select(query, (community_name, date))

            if result:
                record_id = result[0][0]
                update_data = {
                    'orderAmount': record['orderAmount'],
                    'orderTotal': record['orderTotal'],
                    'refundAmount': record['refundAmount']
                }
                condition = f"id = {record_id} AND communityName = '{community_name}' AND date = '{date}'"
                db.update('ecommerce_operation', update_data, condition)
                print(f"{community_name} on {date}: updated {len(result)} rows")
            else:
                insert_data = {
                    'communityName': community_name,
                    'orderAmount': record['orderAmount'],
                    'orderTotal': record['orderTotal'],
                    'refundAmount': record['refundAmount'],
                    'date': date
                }
                db.insert('ecommerce_operation', insert_data)
                print(f"{community_name} on {date}: inserted 1 row")
