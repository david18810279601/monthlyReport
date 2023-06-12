import configparser
import datetime
import sys
import requests
import json
from login import Login
from DB import DB
from common import Common

class WisdomTicket:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.url = self.config.get("WisdomTicketAPI", "url")
        self.sDate = self.config.get("WisdomTicketAPI", "sDate")
        self.eDate = self.config.get("WisdomTicketAPI", "eDate")
        self.login = Login(self.config, 'normal')
        self.common = Common(config_file)
        self.session = self.login.login()

        self.getCompanyIDurl = self.config.get("HieGet", "getCompanyIDUrl")
        self.getDictionaryIDUrl = self.config.get("HieGet", "getDictionaryIDUrl")
        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")

        self.ESHCommunityNames = json.loads(self.config.get("ESHContractManagementAPI", "eshenghuoCommunities"))

        # self.communities = []
        # raw_communities = json.loads(self.config.get("WisdomTicketCommunities", "community_list"))
        # for community in raw_communities:
        #     self.communities.append({
        #         "area": community["area"],
        #         "communityName": community["communityName"],
        #         "departmentId": community["departmentId"],
        #         "departments": community["departments"]
        #     })

    def getCompanyID(self):
        response = self.session.get(self.getCompanyIDurl)
        if response.status_code == 200:
            data = response.json()
            return data["data"]
        else:
            print(f"Error fetching data from {self.getCompanyIDurl}")
            return None
    def getDictionaryID(self):
        response = self.session.get(self.getDictionaryIDUrl)
        if response.status_code == 200:
            data = response.json()
            return data["data"]
        else:
            print(f"Error fetching data from {self.getDictionaryIDUrl}")
            return None

    def fetch_data(self):
        departments = self.common.get_department_data()['result']
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        formatted_start_time = start_time.strftime("%Y-%m-%d")
        end_time = self.common.get_month_start_end_dates("END_ALL")
        formatted_end_time = end_time.strftime("%Y-%m-%d")
        results = []
        for community in departments:
            area = community["area"]
            community_name = community["communityName"]
            departmentId = community["departmentId"]
            for department in community["departments"]:
                id = department["id"]
                departmentName = department["name"]
                url_with_params = f"{self.url}/{departmentId}?departmentId={id}&sDate={formatted_start_time}&eDate={formatted_end_time}"
                response = self.session.post(url_with_params)
                if response.status_code == 200:
                    data = response.json()
                    data["area"] = area
                    data["communityName"] = community_name
                    data["departmentName"] = departmentName
                    results.append(data)
                else:
                    print(f"Error fetching data for department ID {id} in community {departmentId}")
        return results

    def process_data(self, data):
        result = []
        for community in data:
            department_name = community["departmentName"]
            for item in community["data"]:
                if item["departmentName"] == "合计":
                    result.append({
                        "area": community["area"],
                        "communityName": community["communityName"],
                        "departmentName": department_name,
                        "sumCompleteTimeQuota": item["sumCompleteTimeQuota"],
                        "sumTimeActual": item["sumTimeActual"],
                        "sumTimeFixedWorkOrder": item["sumTimeFixedWorkOrder"],
                        "averageCompleteTimeQuota": item["averageCompleteTimeQuota"],
                        "completeRate": item["completeRate"],
                        "standardRate": item["standardRate"],
                        "inspectRate": item["inspectRate"],
                        "date": self.previous_month_str
                    })
        return result

    def ESH_WisdomTicket(self):
        departments = self.ESHCommunityNames
        results = []
        department_names = ['单位领导', '安全管理部', '客户服务部', '工程管理部', '资产财务部', '行政人事部']
        for department in departments:
            for department_name in department_names:
                results.append({
                    'area': department['area'],
                    'communityName': department['communityName'],
                    'departmentName': department_name,
                    'sumCompleteTimeQuota': 0.0,
                    'sumTimeActual': 0.0,
                    'sumTimeFixedWorkOrder': 0.0,
                    'averageCompleteTimeQuota': 0.0,
                    'completeRate': 0.0,
                    'standardRate': 0.0,
                    'inspectRate': 0.0,
                    'date': self.previous_month_str
                })
        return results

    def combine_data(self):
        data = self.fetch_data()
        processed_data = self.process_data(data)
        ESH_data = self.ESH_WisdomTicket()
        combined_data = processed_data + ESH_data
        return combined_data

    def insert_or_update_data(self, data):
        db = DB()
        for record in data:
            communityName = record['communityName']
            date = record['date']
            department_name = record['departmentName']
            query = "SELECT * FROM wisdom_ticket WHERE communityName = %s AND date = %s AND departmentName = %s"
            result = db.select(query, (communityName, date, department_name))

            if result:
                record_id = result[0][0]
                update_data = {
                    'area': record['area'],
                    'sumCompleteTimeQuota': record['sumCompleteTimeQuota'],
                    'sumTimeActual': record['sumTimeActual'],
                    'sumTimeFixedWorkOrder': record['sumTimeFixedWorkOrder'],
                    'averageCompleteTimeQuota': record['averageCompleteTimeQuota'],
                    'completeRate': record['completeRate'],
                    'standardRate': record['standardRate'],
                    'inspectRate': record['inspectRate'],
                }
                condition = f"id = {record_id} AND communityName = '{communityName}' AND date = '{date}' AND departmentName = '{department_name}'"
                db.update('wisdom_ticket', update_data, condition)
                print(f"{communityName} on {date} for department {department_name}: updated {len(result)} rows")
            else:
                insert_data = {
                    'area': record['area'],
                    'communityName': communityName,
                    'departmentName': department_name,
                    'sumCompleteTimeQuota': record['sumCompleteTimeQuota'],
                    'sumTimeActual': record['sumTimeActual'],
                    'sumTimeFixedWorkOrder': record['sumTimeFixedWorkOrder'],
                    'averageCompleteTimeQuota': record['averageCompleteTimeQuota'],
                    'completeRate': record['completeRate'],
                    'standardRate': record['standardRate'],
                    'inspectRate': record['inspectRate'],
                    'date': date
                }
                db.insert('wisdom_ticket', insert_data)
                print(f"{communityName} on {date} for department {department_name}: inserted 1 row")
