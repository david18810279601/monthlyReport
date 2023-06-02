import json
import configparser
import sys
import datetime as dt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from common import Common
# config_file = "/Users/davidli/PycharmProjects/pythonProject1/Emonthlyreport/monthlyReport/config.ini"
config_file = "/Users/davidlee/PycharmProjects/pythonProject1/monthlyReport/config.ini"
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
        self.ESHCommunityNames = json.loads(self.config.get("EshenghuoPaymentManagerCostDataNumAPI", "eshenghuoCommunities"))
        self.eshenghuoCommunities = json.loads(self.config.get("ESHContractManagementAPI", "eshenghuoCommunities"))

        # 8、E生活平台合同参数
        self.ExecuteData_Url = self.config.get("ESHContractManagementAPI", "ExecuteData_Url")
        self.ExecuteData_Filters = json.loads(self.config.get("ESHContractManagementAPI", "ExecuteData_Filters"))

        # 9、E生活巡航巡检
        self.eshenghuoPatrolInspectionUrl = self.config.get("ESHContractManagementAPI", "patrolInspection_Url")

        # 10、维修管理
        self.generate_maintenance_Url = self.config.get("ESHContractManagementAPI", "generate_maintenance_Url")

        # 11、库存
        self.inventory_Url = self.config.get("ESHContractManagementAPI", "inventory_Url")
        self.extraList_Url = self.config.get("ESHContractManagementAPI", "extraList_Url")
        self.purchasemanage_Url = self.config.get("ESHContractManagementAPI", "purchasemanage_Url")
        self.month_mapping = json.loads(self.config.get("MonthMapping", "mapping"))

        # 12、健康会所
        self.health_club_data_url = self.config.get("ESHContractManagementAPI", "healthClub_Url")
        self.healthClub_Communities = json.loads(self.config.get("ESHContractManagementAPI", "healthClub_Communities"))

        # 13、E生活设备设施
        self.equipmentFacilities_Url = self.config.get("ESHContractManagementAPI", "equipmentFacilities_Url")

        # 14、E生活电商运营
        self.eCommerce_Url = self.config.get("ESHContractManagementAPI", "eCommerce_Url")


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

    # 9.巡航巡检
    def get_perform_inspection(self):
        departments = self.ESHCommunityNames
        result = [
            {
                'area': department['area'],
                'communityName': department['communityName'],
                'cruiseNum': parent_cruise['cruiseNum'],
                'cruiseRate': parent_cruise['cruiseRate'],
                'cruiseCompletedRate': parent_rate['cruiseCompletedRate'],
                'workRate': work['workRate'],
                'workNum': work['workNum'],
                'workCompletedRate': workCompletedRate['workCompletedRate'],
                "date": self.previous_month_str
            }
            for department in departments
            for parent_cruise in [self.get_esh_new_cruise(department['communityId'], 5)]
            for parent_rate in [self.get_esh_new_cruise(department['communityId'], 6)]
            for work in [self.get_esh_new_cruise(department['communityId'], 7)]
            for workCompletedRate in [self.get_esh_new_cruise(department['communityId'], 8)]
        ]

        return result

    # 巡航工单数
    def get_esh_new_cruise(self, communityId, num):
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

            payload = {
                'order': 'asc',
                'offset': '0',
                'limit': '100',
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
                'filters[2][value]': f'community,{communityId}',
                'filters[2][sourceValue]': f'community,{communityId}',
                'statType': num
            }
            url = f"{self.eshenghuoPatrolInspectionUrl}?resourceItem=community,{communityId}"
            try:
                eshenghuoContractManagement = self.session.post(url, data=payload, timeout=10)
                eshenghuoContractManagement.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None
            if num == 5:
                response_data = eshenghuoContractManagement.json()
                if not response_data["rows"]:
                    return {'cruiseNum': 0, 'cruiseRate': '0%'}
                cruise_rate_decimal = response_data["rows"][0]["completedRate"]
                cruise_rate_percentage = f'{cruise_rate_decimal * 100:.2f}%'
                data = {'cruiseNum': response_data["rows"][0]["totalAmount"], 'cruiseRate': cruise_rate_percentage}
            elif num == 6:
                response_data = eshenghuoContractManagement.json()
                if not response_data["rows"]:
                    return {'cruiseCompletedRate': '0%'}
                cruise_rate_decimal = response_data["rows"][0]["completedRate"]
                cruise_rate_percentage = f'{cruise_rate_decimal * 100:.2f}%'
                data = {'cruiseCompletedRate': cruise_rate_percentage}
            elif num == 7:
                response_data = eshenghuoContractManagement.json()
                if not response_data["rows"]:
                    return {'workNum': 0, 'workRate': '0%'}
                work_rate_decimal = response_data["rows"][0]["completedRate"]
                work_rate_percentage = f'{work_rate_decimal * 100:.2f}%'
                data = {'workNum': response_data["rows"][0]["totalAmount"], 'workRate': work_rate_percentage}
            elif num == 8:
                response_data = eshenghuoContractManagement.json()
                if not response_data["rows"]:
                    return {'workCompletedRate': '0%'}
                cruise_rate_decimal = response_data["rows"][0]["completedRate"]
                cruise_rate_percentage = f'{cruise_rate_decimal * 100:.2f}%'
                data = {'workCompletedRate': cruise_rate_percentage}
            return data


    # 9.巡航巡检
    def get_maintenance_ticket(self):
        departments = self.eshenghuoCommunities
        result = [
            {
                'area': department['area'],
                'communityName': department['communityName'],
                "timingNum": parent_generate['receiveNum'],
                "workTime": parent_generate['workTime'],
                "workerAvgTime": parent_generate['workerAvgForm'],
                "completeRate": parent_generate['finishRate'],
                "satisfactionRate": parent_generate['finishRate'],
                "totalPrice": parent_generate['totalPrice'],
                "date": self.previous_month_str
            }
            for department in departments
            for parent_generate in [self.generate_maintenance_summary(department['departmentId'])]
        ]

        return result

    def generate_maintenance_summary(self, departmentId):
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
            payload = {
                'order': 'asc',
                'offset': 0,
                'limit': 10,
                'filters[0][field]': 'startDate',
                'filters[0][oper]': 'GreaterThenEq',
                'filters[0][value]': formatted_start_time,
                'filters[0][sourceValue]': formatted_start_time,
                'filters[1][field]': 'endDate',
                'filters[1][oper]': 'LessThenEq',
                'filters[1][value]': formatted_end_time,
                'filters[1][type]': 'date',
                'filters[1][sourceValue]': formatted_end_time
            }

            url = f"{self.generate_maintenance_Url}?resourceItem=department,{departmentId}"
            try:
                eshenghuoContractManagement = self.session.post(url, data=payload, timeout=10)
                eshenghuoContractManagement.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

            response_data = eshenghuoContractManagement.json()
            if not response_data["rows"]:
                return {'receiveNum': 0, 'workTime': 0, 'workerAvgForm': 0, 'totalPrice': 0, 'finishRate': '0%'}
            finishRate_decimal = response_data["rows"][0]["finishRate"]
            finishRate_percentage = f'{finishRate_decimal * 100:.2f}%'
            data = {'receiveNum': response_data["rows"][0]["receiveNum"], 'workTime': response_data["rows"][0]["workTime"], 'workerAvgForm': response_data["rows"][0]["workerAvgForm"], 'totalPrice': response_data["rows"][0]["totalPrice"], 'finishRate': finishRate_percentage}
            return data

    def ESHprocurement_inventory(self):
        departments = self.eshenghuoCommunities
        result = [
            {
                'area': department['area'],
                'communityName': department['communityName'],
                "budget": parent_budget,
                'extraList': parent_extraList["extraList"],
                'property_stock': parent_property_stock["property_stock"],
                "date": self.previous_month_str
            }
            for department in departments
            for parent_budget in [self.get_budget(department['departmentId'])]
            for parent_property_stock in [self.get_budget_process_List(department['departmentId'])]
            for parent_extraList in [self.get_purchasemanage_data(department['departmentId'])]
        ]

        return result

    def get_budget(self, departmentId):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None
            # start_time = self.common.get_month_start_end_dates("ST_ALL")
            # formatted_start_time = start_time.strftime("%Y-%m-%d")
            # end_time = self.common.get_month_start_end_dates("END_ALL")
            # formatted_end_time = end_time.strftime("%Y-%m-%d")
            payload = {
                'order': 'asc',
                'offset': 0,
                'limit': 10,
                'filters[0][field]': 'year',
                'filters[0][oper]': 'Eq',
                'filters[0][value]': 2023,
                'filters[0][type]': 'int',
                'filters[0][sourceValue]': 2023
            }

            url = f"{self.inventory_Url}?departmentId={departmentId}"
            try:
                eshenghuoContractManagement = self.session.post(url, data=payload, timeout=10)
                if eshenghuoContractManagement.status_code == 200:
                    data = eshenghuoContractManagement.json()
                    return self.get_budget_process_data(data)
                else:
                    print(f"Error fetching data from {departmentId}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

    def get_budget_process_data(self, data):
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        previous_month_str = start_time.strftime("%m")
        month_key = self.month_mapping.get(previous_month_str, '')

        if data and month_key:
            rows = data.get('rows', [])
            if rows:
                result = rows[0].get(month_key, 0)
            else:
                result = 0
        else:
            result = 0
        return result

    def get_budget_process_List(self, departmentId):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while logging in: {e}")
                return None

            payload = {
                'sort': 'materiel.code',
                'order': 'asc',
                'offset': 0,
                'limit': 999,
                'filters[0][field]': 'resourceItem',
                'filters[0][oper]': 'Custom',
                'filters[0][value]': f'department,{departmentId}',
                'filters[0][sourceValue]': f'department,{departmentId}',
                'filters[1][field]': 'showStock',
                'filters[1][oper]': 'Contains',
                'filters[1][value]': 'true',
                'filters[1][type]': 'string',
                'filters[1][sourceValue]': 'true'
            }

            url = f"{self.extraList_Url}?resourceItem=department,{departmentId}"
            try:
                eshenghuoContractManagement = self.session.post(url, data=payload, timeout=10)
                if eshenghuoContractManagement.status_code == 200:
                    data = eshenghuoContractManagement.json()
                    return self.get_budget_process_data_All(data)
                else:
                    print(f"Error fetching data from {departmentId}: {eshenghuoContractManagement.text}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while fetching data from {departmentId}: {e}")
                return None

    def get_budget_process_data_All(self, data):
        if not data or not data.get("rows"):
            return {'property_stock': 0}
        else:
            total_money = sum([row.get("totalMoney") for row in data.get("rows")])
            return {'property_stock': total_money}

    def get_purchasemanage_data(self, departmentId):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while logging in: {e}")
                return None
            start_time = self.common.get_month_start_end_dates("ST_ALL")
            formatted_start_time = start_time.strftime("%Y-%m")
            payload = {
                'sort': 'orderNO',
                'order': 'desc',
                'offset': 0,
                'limit': 999,
                'filters[0][field]': 'yearMonth',
                'filters[0][oper]': 'Eq',
                'filters[0][value]': formatted_start_time,
                'filters[0][type]': 'String',
                'filters[0][sourceValue]': formatted_start_time
            }

            url = f"{self.purchasemanage_Url}?departmentId={departmentId}"
            try:
                eshenghuoContractManagement = self.session.post(url, data=payload, timeout=10)
                if eshenghuoContractManagement.status_code == 200:
                    data = eshenghuoContractManagement.json()
                    return self.get_purchasemanage_data_All(data)
                else:
                    print(f"Error fetching data from {departmentId}: {eshenghuoContractManagement.text}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while fetching data from {departmentId}: {e}")
                return None
    def get_purchasemanage_data_All(self, data):
        if not data or not data.get("rows"):
            return {'extraList': 0}
        else:
            total_money = sum([row.get("money") for row in data.get("rows")])
            return {'extraList': total_money}


    def get_health_club_data(self):
        departments = self.healthClub_Communities
        result = [
            {
                'area': department['area'],
                'communityName': department['communityName'],
                "memberNum": parent_health_club_data["memberNum"],
                'privateCoachNum': parent_health_club_data["privateCoachNum"],
                'private_training_amount': '0',
                'cardUsedNum': parent_health_club_data["cardUsedNum"],
                'unpassNum': parent_health_club_data["unpassNum"], #预约场地
                'dining_reservation_quantity': '0',
                'foodRevenue': '0',
                "date": self.previous_month_str
            }
            for department in departments
            for parent_health_club_data in [self.get_health_club_data_all(department['communityId'])]
        ]
        return result

    def get_health_club_data_all(self, communityId):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while logging in: {e}")
                return None
            start_time = self.common.get_month_start_end_dates("ST_ALL")
            formatted_start_time = start_time.strftime("%Y-%m-%d")
            end_time = self.common.get_month_start_end_dates("END_ALL")
            formatted_end_time = end_time.strftime("%Y-%m-%d")

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
                'filters[2][value]': f'community,{communityId}',
                'filters[2][sourceValue]': f'community,{communityId}',
                'statType': 4
            }

            url = f"{self.health_club_data_url}?resourceItem=community,{communityId}"
            try:
                eshenghuoContractManagement = self.session.post(url, data=payload, timeout=10)
                if eshenghuoContractManagement.status_code == 200:
                    data = eshenghuoContractManagement.json()
                    return self.get_health_club_data_All(data)
                else:
                    print(f"Error fetching data from {communityId}: {eshenghuoContractManagement.text}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while fetching data from {communityId}: {e}")
                return None

    def get_health_club_data_All(self, data):
        if not data or not data.get("rows"):
            return {"memberNum": 0, "privateCoachNum": 0, "cardUsedNum": 0, "unpassNum": 0}
        else:
            return {'memberNum': data['rows'][0]['memberNum'], 'privateCoachNum': data['rows'][0]['privateCoachNum'], "cardUsedNum": data['rows'][0]['cardUsedNum'], "unpassNum": data['rows'][0]['unpassNum']}

    def ESH_facility_equipment_data(self):
        departments = self.ESHCommunityNames
        result = [
            {
                'area': department['area'],
                'communityName': department['communityName'],
                "deviceSum": parent_facility_equipment["deviceSum"],
                "normalRate": parent_facility_equipment["normalRate"],
                "date": self.previous_month_str
            }
            for department in departments
            for parent_facility_equipment in [self.get_facility_equipment_data(department['communityId'])]
        ]

        return result

    def get_facility_equipment_data(self, communityId):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while logging in: {e}")
                return None
            start_time = self.common.get_month_start_end_dates("ST_ALL")
            formatted_start_time = start_time.strftime("%Y-%m-%d")
            end_time = self.common.get_month_start_end_dates("END_ALL")
            formatted_end_time = end_time.strftime("%Y-%m-%d")

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
                'filters[1][sourceValue]': formatted_end_time
            }

            url = f"{self.equipmentFacilities_Url}?resourceItem=community,{communityId}&categoryId="
            try:
                eshenghuoContractManagement = self.session.post(url, data=payload, timeout=20)
                if eshenghuoContractManagement.status_code == 200:
                    data = eshenghuoContractManagement.json()
                    return self.get_facility_equipment_data_All(data)
                else:
                    print(f"Error fetching data from {communityId}: {eshenghuoContractManagement.text}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while fetching data from {communityId}: {e}")
                return None


    def get_facility_equipment_data_All(self, data):
        if not data or not data.get("rows"):
            return {'deviceSum': 0, 'normalRate': "0%"}
        else:
            total_okStatus = sum([row.get("okStatus") for row in data.get("rows")])
            return {'deviceSum': total_okStatus, 'normalRate': "100%"}


    # 电商运营
    def ESH_e_commerce_operation_data(self):
        result = [
            {
                'communityName': "电商运营",
                "orderAmount": parent_e_commerce_operation["goodsAmount"],
                "orderTotal": parent_e_commerce_operation["total"],
                "refundAmount": parent_e_commerce_operation["refundAmount"],
                "date": self.previous_month_str
            }
            for parent_e_commerce_operation in [self.get_e_commerce_operation_data()]
        ]

        return result

    def get_e_commerce_operation_data(self):
        if self.login_type == "eshenghuo":
            try:
                eshenghuo_response = self.session.post(self.login_url, data=self.payload, timeout=10)
                eshenghuo_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while logging in: {e}")
                return None
            start_time = self.common.get_month_start_end_dates("ST_ALL")
            formatted_start_time = start_time.strftime("%Y-%m-%d")
            end_time = self.common.get_month_start_end_dates("END_ALL")
            formatted_end_time = end_time.strftime("%Y-%m-%d")

            payload = {
                'sort': 'createdDate',
                'order': 'desc',
                'offset': 0,
                'limit': 10,
                'filters[0][field]': 'paymentStatus',
                'filters[0][oper]': 'Eq',
                'filters[0][value]': 1,
                'filters[0][type]': 'string',
                'filters[0][sourceValue]': 1,
                'filters[1][field]': 'shippingStatus',
                'filters[1][oper]': 'Eq',
                'filters[1][value]': 2,
                'filters[1][type]': 'string',
                'filters[1][sourceValue]': 2,
                'filters[2][field]': 'status',
                'filters[2][oper]': 'Eq',
                'filters[2][value]': 1,
                'filters[2][type]': 'string',
                'filters[2][sourceValue]': 1,
                'filters[3][field]': 'createdDate',
                'filters[3][oper]': 'GreaterThenEq',
                'filters[3][value]': formatted_start_time,
                'filters[3][sourceValue]': formatted_start_time,
                'filters[4][field]': 'createdDate',
                'filters[4][oper]': 'LessThenEq',
                'filters[4][value]': formatted_end_time,
                'filters[4][type]': 'date',
                'filters[4][sourceValue]': formatted_end_time
            }

            try:
                eshenghuoContractManagement = self.session.post(self.eCommerce_Url, data=payload, timeout=20)
                if eshenghuoContractManagement.status_code == 200:
                    data = eshenghuoContractManagement.json()
                    return self.ESH_e_commerce_operation_data_all(data)
                else:
                    print(f"Error fetching data from get_e_commerce_operation_data : {eshenghuoContractManagement.text}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while fetching data from get_e_commerce_operation_data : {e}")
                return None

    # 电商运营
    def ESH_e_commerce_operation_data_all(self,data):
        if not data or not data.get("rows"):
            return {'goodsAmount': 0, 'total': 0, 'refundAmount': 0}
        else:
            total_goodsAmount = sum([row.get("goodsAmount") for row in data.get("rows")])
            return {'goodsAmount': total_goodsAmount, 'total': data['total'], "refundAmount": 0}


