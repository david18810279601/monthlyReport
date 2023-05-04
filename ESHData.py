import json
import configparser
import sys
import datetime as dt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from common import Common
config_file = "/Users/davidli/PycharmProjects/pythonProject1/Emonthlyreport/monthlyReport/config.ini"
class ESHData:
    def __init__(self, config, login_type):
        self.login_type = login_type
        if login_type == "eshenghuo":
            self.login_url = config.get("LOGIN", "eshenghuo_url")
            eshenghuo_login_data = json.loads(config.get("EshenghuoLoginInformation", "EshenghuoLoginData"))
            self.payload = {
                "j_username": eshenghuo_login_data["j_username"],
                "j_password": eshenghuo_login_data["j_password"],
            }
        # Set up session with retries
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.previous_month_str = (dt.date.today().replace(day=1) - dt.timedelta(days=1)).strftime("%Y%m")
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.common = Common(config_file)
        # E生活 项目名称&参数
        self.eshenghuoCostDataUrl = self.config.get("EshenghuoPaymentManagerCostDataNumAPI", "eshenghuoCostDataUrl")
        # E生活 项目名称
        self.eshenghuoCommunities = json.loads(self.config.get("ESHContractManagementAPI", "eshenghuoCommunities"))

        # 8、E生活平台合同参数
        self.ExecuteData_Url = self.config.get("ESHContractManagementAPI", "ExecuteData_Url")
        self.ExecuteData_Filters = json.loads(self.config.get("ESHContractManagementAPI", "ExecuteData_Filters"))


    def platform_index_report(self, url, filters):
        session = requests.Session()
        if self.login_type == "eshenghuo":
            eshenghuo_response = session.post(self.login_url, data=self.payload)
            if eshenghuo_response.status_code == 200:
                platform_index_report = session.post(url, filters)
                return platform_index_report.json()
            else:
                raise Exception("Login failed")

    # 2、E生活客服报告
    def eshenghuoComplaintCount(self, url):
        session = requests.Session()
        if self.login_type == "eshenghuo":
            eshenghuo_response = session.post(self.login_url, data=self.payload)
            if eshenghuo_response.status_code == 200:
                payload = {
                    'resourceItem': 'department,A003f7f09862d9384310afe8953935109460',
                    'startDate': '2023-03-01',
                    'endDate': '2023-03-31',
                    'selectType': '2',
                    'filters[0][field]': 'resourceItem',
                    'filters[0][oper]': 'Custom',
                    'filters[0][value]': 'department,A003f7f09862d9384310afe8953935109460',
                    'filters[0][sourceValue]': 'department,A003f7f09862d9384310afe8953935109460',
                }
                EshenghuoComplaintCount = session.post(url, data=payload)
                data = EshenghuoComplaintCount.json()
                return data['list']
            else:
                raise Exception("Login failed")


    # 2、E生活客服报告总览
    # def eshenghuo_complaint_process_data(self):
    #     departments = self.common.get_department_data().get("result", [])
    #     result = [
    #         {
    #             'area': department['area'],
    #             'communityName': department['communityName'],
    #             'totalAmount': parent_department.get('totalAmount', 0),
    #             'toCommunity': parent_department.get('toCommunity', 0),
    #             'finishPercent': f"{parent_department.get('finishPercent', 0)}%",
    #             'appNum': parent_matterReport.get('appNum', 0),
    #             'finishRate': f"{parent_matterReport.get('finishRate', 0)}%",
    #             'totalPraiseAmount': parent_praise.get('totalAmount', 0),
    #             'finishPraiseRate': f"{parent_praise.get('finishPercent', 0)}%",
    #             'approveUserNum': parent_customer_apply,
    #             'noticeNum': parent_notice,
    #             'communicationNum': parent_customer_communication_data,
    #             'topicNum': parent_topic,
    #             "date": self.previous_month_str
    #         }
    #         for department in departments
    #         for parent_department in [self.get_customer_complaint_management(department['communityId'])]
    #         for parent_matterReport in [self.get_customer_complaint_matterReport(department['communityId'])]
    #         for parent_praise in [self.get_customer_praise_fetch_community_data(department['communityId'])]
    #         for parent_customer_apply in [self.get_customer_apply_fetch(department['communityId'])]
    #         for parent_notice in [self.get_customer_notice(department['communityId'])]
    #         for parent_customer_communication_data in [self.get_customer_communication_data(department['communityId'])]
    #         for parent_topic in [self.get_customer_topic_data(department['communityId'])]
    #     ]

    #3、E生活缴费管理报告
    def eshenghuo_cost_data(self, url, formatted_start_time,formatted_end_time):
        session = requests.Session()
        if self.login_type == "eshenghuo":
            eshenghuo_response = session.post(self.login_url, data=self.payload)
            if eshenghuo_response.status_code == 200:
                payload = {
                    'order': 'asc',
                    'offset': 0,
                    'limit': 100,
                    'filters[0][field]': 'startDate',
                    'filters[0][oper]': 'GreaterThenEq',
                    'filters[0][value]': formatted_start_time,
                    'filters[0][sourceValue]': formatted_start_time,
                    'filters[1][field]': 'endDate',
                    'filters[1][oper]': 'LessThenEq',
                    'filters[1][value]': formatted_end_time,
                    'filters[1][type]': 'date',
                    'filters[1][sourceValue]': formatted_end_time,
                    'filters[2][field]': 'resourceItem',
                    'filters[2][oper]': 'Custom',
                    'filters[2][value]': 'department,A003f7f09862d9384310afe8953935109460',
                    'filters[2][sourceValue]': 'department,A003f7f09862d9384310afe8953935109460',
                    'statType': 3
                }
                eshenghuo_cost_data = session.post(url, data=payload)
                return eshenghuo_cost_data.json()
            else:
                raise Exception("Login failed")

    def eshenghuoProperty_CostsData(self, url, communityId, feeItemId, formatted_start_time, formatted_end_time):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            payload = {
                'resourceItem': f'community,{communityId}',
                'feeItemIds': feeItemId,
                'feeMethodIds': '',
                'receivedDateStart': formatted_start_time,
                'receivedDateEnd': formatted_end_time
            }
            try:
                eshenghuoProperty_CostsData = self.session.post(url, data=payload, timeout=10)
                eshenghuoProperty_CostsData.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            response_data = eshenghuoProperty_CostsData.json()
            amount_paid = response_data.get("obj").get("amountPaid")
            return amount_paid

    def eshenghuoParking_FeeData(self, url, communityId, feeItemId, formatted_start_time, formatted_end_time):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            payload = {
                'resourceItem': f'community,{communityId}',
                'feeItemIds': feeItemId,
                'feeMethodIds': '',
                'receivedDateStart': formatted_start_time,
                'receivedDateEnd': formatted_end_time
            }
            try:
                eshenghuoParking_FeeUrl = self.session.post(url, data=payload, timeout=10)
                eshenghuoParking_FeeUrl.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            response_data = eshenghuoParking_FeeUrl.json()
            amount_paid = response_data.get("obj").get("amountPaid")
            return amount_paid

    def eshenghuo_all(self, url, communityId, formatted_start_time, formatted_end_time):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            payload = {
                'resourceItem': f'community,{communityId}',
                'feeItemIds': '',
                'feeMethodIds': '',
                'receivedDateStart': formatted_start_time,
                'receivedDateEnd': formatted_end_time
            }
            try:
                eshenghuoAll = self.session.post(url, data=payload, timeout=10)
                eshenghuoAll.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            response_data = eshenghuoAll.json()
            amount_paid = response_data.get("obj").get("amountPaid")
            return amount_paid

    # 8、E生活合同报告
    def get_esh_process_data(self):
        departments = self.eshenghuoCommunities
        result = [
            {
                'area': department['area'],
                'communityName': department['communityName'],
                'new_contract': parent_new_contract,
                'maturity': parent_maturity,
                'contract_progress': parent_contract_progress,
                'actual_payment': parent_actual_payment,
                'tangible_receipts': parent_actual_payment,
                'payment_plan': parent_payment,
                'collection_plan': parent_payment,
                "date": self.previous_month_str
            }
            for department in departments
            for parent_actual_payment in [self.get_esh_contractManagement(department['departmentId'], 1)]
            for parent_payment in [self.get_esh_contractManagement(department['departmentId'],2)]
            for parent_contract_progress in [self.get_esh_contractManagementAll(department['departmentId'], 1)]
            for parent_new_contract in [self.get_esh_new_contract(department['departmentId'], 1)]
            for parent_maturity in [self.get_esh_new_contract(department['departmentId'], 2)]
        ]

        return result

    def get_esh_contractManagement(self, departmentId, num):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None
            start_time = self.common.get_month_start_end_dates("ST_ALL")
            formatted_start_time = start_time.strftime("%Y-%m-%d")
            payload = {
                'sort': 'createdDate',
                'order': 'desc',
                'offset': 0,
                'limit': 10,
                'filters[0][field]': 'resourceItem',
                'filters[0][oper]': 'Custom',
                'filters[0][value]': f'department,{departmentId}',
                'filters[0][sourceValue]': f'department,{departmentId}',
                'filters[1][field]': 'direction',
                'filters[1][oper]': 'Eq',
                'filters[1][value]': num,
                'filters[1][type]': 'string',
                'filters[1][sourceValue]': num,
                'filters[2][field]': 'status',
                'filters[2][oper]': 'Eq',
                'filters[2][value]': 1,
                'filters[2][type]': 'string',
                'filters[2][sourceValue]': 1,
                'filters[3][field]': 'startTime',
                'filters[3][oper]': 'GreaterThenEq',
                'filters[3][value]': formatted_start_time,
                'filters[3][sourceValue]': formatted_start_time
            }
            try:
                eshenghuoContractManagement = self.session.post(self.ExecuteData_Url, data=payload, timeout=10)
                eshenghuoContractManagement.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            response_data = eshenghuoContractManagement.json()
            Num_Count = response_data["rowCount"]
            return Num_Count

    def get_esh_contractManagementAll(self, departmentId, num):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None
            start_time = self.common.get_month_start_end_dates("ST_ALL")
            formatted_start_time = start_time.strftime("%Y-%m-%d")
            payload = {
                'sort': 'createdDate',
                'order': 'desc',
                'offset': 0,
                'limit': 10,
                'filters[0][field]': 'resourceItem',
                'filters[0][oper]': 'Custom',
                'filters[0][value]': f'department,{departmentId}',
                'filters[0][sourceValue]': f'department,{departmentId}',
                'filters[1][field]': 'status',
                'filters[1][oper]': 'Eq',
                'filters[1][value]': num,
                'filters[1][type]': 'string',
                'filters[1][sourceValue]': num,
                'filters[2][field]': 'startTime',
                'filters[2][oper]': 'GreaterThenEq',
                'filters[2][value]': formatted_start_time,
                'filters[2][sourceValue]': formatted_start_time
            }
            try:
                eshenghuoContractManagement = self.session.post(self.ExecuteData_Url, data=payload, timeout=10)
                eshenghuoContractManagement.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            response_data = eshenghuoContractManagement.json()
            Num_Count = response_data["rowCount"]
            return Num_Count

    def get_esh_new_contract(self, departmentId, num):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None
            start_time = self.common.get_month_start_end_dates("ST_ALL")
            formatted_start_time = start_time.strftime("%Y-%m-%d")
            end_time = self.common.get_month_start_end_dates("END_ALL")
            formatted_end_time = end_time.strftime("%Y-%m-%d")
            if num == 1:
                time_value = formatted_start_time
                time_source_value = formatted_start_time
            elif num == 2:
                time_value = formatted_end_time
                time_source_value = formatted_end_time
            else:
                print("Invalid num value")
                return None
            payload = {
                'sort': 'createdDate',
                'order': 'desc',
                'offset': 0,
                'limit': 10,
                'filters[0][field]': 'resourceItem',
                'filters[0][oper]': 'Custom',
                'filters[0][value]': f'department,{departmentId}',
                'filters[0][sourceValue]': f'department,{departmentId}',
                'filters[1][field]': 'startTime',
                'filters[1][oper]': 'GreaterThenEq',
                'filters[1][value]': time_value,
                'filters[1][sourceValue]': time_source_value
            }
            try:
                eshenghuoContractManagement = self.session.post(self.ExecuteData_Url, data=payload, timeout=10)
                eshenghuoContractManagement.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            response_data = eshenghuoContractManagement.json()
            Num_Count = response_data["rowCount"]
            return Num_Count