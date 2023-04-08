import configparser
import datetime
import sys
import requests
import json
from login import Login
from ESHData import ESHData
from DB import DB

class CustomerService:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.customer_complaint_managementUrl = self.config.get("CustomerServiceReportAPI", "customerComplaintManagementUrl")
        self.customer_complaint_matterReportUrl = self.config.get("CustomerServiceReportAPI", "customerComplaintMatterReportUrl")
        self.customer_praiseUrl = self.config.get("CustomerServiceReportAPI", "customerPraiseUrl")
        self.customer_complaint_communities = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "communities"))
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

    #投诉管理
    def customer_complaint_management(self):
        community_data = []
        for community in self.customer_complaint_communities:
            community_id = community['communityId']
            data = self.customer_complaint_fetch_community_data(community_id)
            if data:
                community_data.append(data)
        return community_data
    #投诉管理-项目数据
    def customer_complaint_fetch_community_data(self, community_id):
        url = self.customer_complaint_managementUrl.format(community_id=community_id)
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            rows = data["data"]
            if not rows:
                return {'totalAmount': '-', 'toCommunity': '-', 'finishPercent': '-'}
            community_data = {
                'totalAmount': rows[0]['totalAmount'],
                'toCommunity': rows[0]['toCommunity'],
                'finishPercent': f"{rows[0]['finishPercent']}%"
            }
            return community_data
        else:
            print(f"Error fetching data from {url}")
            return None
    #投诉管理-报事项目数据
    def customer_complaint_matterReport(self):
        community_data = []
        for community in self.customer_complaint_communities:
            community_id = community['communityId']
            data = self.customer_complaint_matterReport_fetch_community_data(community_id)
            if data:
                community_data.append(data)
        return community_data

    def customer_complaint_matterReport_fetch_community_data(self, community_id):
        url = self.customer_complaint_matterReportUrl.format(community_id=community_id)
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            rows = data["data"]
            if not rows:
                return {'appNum': '-',  'finishRate': '-'}
            community_data = {
                'appNum': rows[0]['appNum'],
                'finishRate': f"{rows[0]['finishRate']}%"
            }
            return community_data
        else:
            print(f"Error fetching data from {url}")
            return None
    #投诉管理-投诉表扬
    def customer_praise(self):
        community_data = []
        for community in self.customer_complaint_communities:
            community_id = community['communityId']
            data = self.customer_praise_fetch_community_data(community_id)
            if data:
                community_data.append(data)
        return community_data

    #投诉管理-投诉表扬-项目数据
    def customer_praise_fetch_community_data(self, community_id):
        url = self.customer_praiseUrl.format(community_id=community_id)
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            rows = data["data"]
            if not rows:
                return {'totalAmount': '-',  'finishPercent': '-'}
            community_data = {
                'totalAmount': rows[0]['totalAmount'],
                'finishRate': f"{rows[0]['finishPercent']}%"
            }
            return community_data
        else:
            print(f"Error fetching data from {url}")
            return None