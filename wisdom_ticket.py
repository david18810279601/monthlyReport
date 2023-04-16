import configparser
import datetime
import sys
import requests
import json
from login import Login
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

        self.communities = []
        raw_communities = json.loads(self.config.get("WisdomTicketCommunities", "community_list"))
        for community in raw_communities:
            self.communities.append({
                "area": community["area"],
                "community": community["community"],
                "departmentId": community["departmentId"],
                "departments": community["departments"]
            })

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
            community_name = community["community"]
            departmentId = community["departmentId"]
            for department in community["departments"]:
                id = department["id"]
                departmentName = department["name"]
                url_with_params = f"{self.url}/{departmentId}?departmentId={id}&sDate={formatted_start_time}&eDate={formatted_end_time}"
                response = self.session.post(url_with_params)
                if response.status_code == 200:
                    data = response.json()
                    data["area"] = area
                    data["community"] = community_name
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
                        "community": community["community"],
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
