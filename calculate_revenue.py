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

class CalculateRevenue:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.common = Common(config_file)
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()

        #资源管理
        self.get_calculate_revenueUrl = self.config.get("CalculateRevenueAPI", "calculate_revenueUrl")

        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")


    def get_calculate_revenue_data(self):
        departments = self.common.get_department_data()['result']
        result = [
            {
                'area': department['area'],
                'communityName': department['community'],
                'sourceProperty': calculate_revenue['sourceProperty'],
                'sourceNum': calculate_revenue['sourceNum'],
                'signedNum': calculate_revenue['signedNum'],
                'sourceVacancyRate': calculate_revenue['sourceVacancyRate'],
                'totalIncome': calculate_revenue['totalIncome'],
                'lastYearIncome': calculate_revenue['lastYearIncome'],
                'riseRate': calculate_revenue['riseRate'],
                'incomeRate': calculate_revenue['incomeRate'],
                'pay': calculate_revenue['pay'],
                'payIntime': calculate_revenue['payIntime'],
                "date": self.previous_month_str
            }
            for department in departments
            for calculate_revenue in [self.get_calculate_revenue(department['communityId'])]
        ]
        return result

    def get_calculate_revenue(self, communityId):
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        start_date = start_time.strftime("%Y-%m-%d")
        end_time = self.common.get_month_start_end_dates("END_ALL")
        end_date = end_time.strftime("%Y-%m-%d")
        url = f"{self.get_calculate_revenueUrl}?startDate={start_date}&endDate={end_date}&communityId={communityId}"
        response = self.session.post(url)
        if response.status_code == 200:
            data = response.json()
            rows = data["data"]
            if not rows:
                return {'sourceProperty': '-', 'sourceNum': '-', 'signedNum': '-', 'sourceVacancyRate': '-', 'totalIncome': '-', 'lastYearIncome': '-', 'riseRate': '-', 'incomeRate': '-', 'pay': '-', 'payIntime': '-'}
            calculate_data = {}
            for row in rows:
                if row['sourceType'] == '总计':
                    calculate_data = {
                        'sourceProperty': row['sourceProperty'],
                        'sourceNum': row['sourceNum'],
                        'signedNum': row['signedNum'],
                        'sourceVacancyRate': f"{row['sourceVacancyRate']}%",
                        'totalIncome': row['totalIncome'],
                        'lastYearIncome': row['lastYearIncome'],
                        'riseRate': f"{row['riseRate']}%",
                        'incomeRate': row['incomeRate'],
                        'pay': f"{row['pay']}%",
                        'payIntime': f"{row['payIntime']}%"
                    }
                    break  # Exit the loop after finding the '总计' row

            return calculate_data
        else:
            print(f"Error fetching data from {url}")
            return None

    def insert_or_update_data(self, data):
        db = DB()
        for record in data:
            community_name = record['communityName']
            date = record['date']
            query = "SELECT * FROM resources WHERE communityName = %s AND date = %s"
            result = db.select(query, (community_name, date))

            if result:
                record_id = result[0][0]
                update_data = {
                    'area': record['area'],
                    'communityName': community_name,
                    'sourceProperty': record['sourceProperty'],
                    'sourceNum': record['sourceNum'],
                    'signedNum': record['signedNum'],
                    'sourceVacancyRate': record['sourceVacancyRate'],
                    'totalIncome': record['totalIncome'],
                    'lastYearIncome': record['lastYearIncome'],
                    'riseRate': record['riseRate'],
                    'incomeRate': record['incomeRate'],
                    'pay': record['pay'],
                    'payIntime': record['payIntime']
                }
                condition = f"id = {record_id} AND communityName = '{community_name}' AND date = '{date}'"
                db.update('resources', update_data, condition)
                print(f"{community_name} on {date}: updated {len(result)} rows")
            else:
                insert_data = {
                    'area': record['area'],
                    'communityName': community_name,
                    'sourceProperty': record['sourceProperty'],
                    'sourceNum': record['sourceNum'],
                    'signedNum': record['signedNum'],
                    'sourceVacancyRate': record['sourceVacancyRate'],
                    'totalIncome': record['totalIncome'],
                    'lastYearIncome': record['lastYearIncome'],
                    'riseRate': record['riseRate'],
                    'incomeRate': record['incomeRate'],
                    'pay': record['pay'],
                    'payIntime': record['payIntime'],
                    'date': date
                }
                db.insert('resources', insert_data)
                print(f"{community_name} on {date}: inserted 1 row")