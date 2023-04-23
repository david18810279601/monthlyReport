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


class CustomerService:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()
        self.common = Common(config_file)


        self.customer_complaint_managementUrl = self.config.get("CustomerServiceReportAPI", "customerComplaintManagementUrl")
        self.customer_complaint_matterReportUrl = self.config.get("CustomerServiceReportAPI", "customerComplaintMatterReportUrl")
        self.customer_praiseUrl = self.config.get("CustomerServiceReportAPI", "customerPraiselUrl")
        self.customer_applyUrl = self.config.get("CustomerServiceReportAPI", "customerApplyUrl")
        self.customer_noticeUrl = self.config.get("CustomerServiceReportAPI", "customerNoticeUrl")
        self.customer_apply_filters = json.loads(self.config.get("CustomerServiceReportAPI", "customerApplyFilters"))
        self.customer_notice_filters = json.loads(self.config.get("CustomerServiceReportAPI", "customerNoticeFilters"))
        self.customer_communicationUrl = self.config.get("CustomerServiceReportAPI", "customerCommunicationUrl")
        self.customer_communication_filters = json.loads(self.config.get("CustomerServiceReportAPI", "customerCommunicationFilters"))
        self.customer_topicUrl = self.config.get("CustomerServiceReportAPI", "customerTopicUrl")
        self.customer_topic_filters = json.loads(self.config.get("CustomerServiceReportAPI", "customerTopicFilters"))
        self.customer_complaint_communities = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "communities"))
        self.eshenghuo_url = self.config.get("EshenghuoPlatformIndexReportAPI", "url")
        self.eshenghuo_filters = json.loads(self.config.get("EshenghuoPlatformIndexReportAPI", "filters"))
        self.eshenghuo_filters_data = json.loads(self.config.get("EshenghuoFilter", "EshenghuoFilterData"))
        self.hie_filters_data = json.loads(self.config.get("HiEFilter", "FilterData"))
        self.eshenghuoComplaintCountUrl = self.config.get("EshenghuoCustomerServiceReportAPI", "eshenghuoComplaintCountUrl")
        self.eshenghuo_login = Login(self.config, 'eshenghuo')
        # self.eshenghuo_session = self.eshenghuo_login.login()
        area_data = json.loads(self.config.get("Area", "areaCommunityName"))
        self.area_mapping = {item["communityName"]: item["area"] for item in area_data}
        self.previous_month_str = (dt.date.today().replace(day=1) - dt.timedelta(days=1)).strftime("%Y%m")

    #投诉管理
    def esh_customer_complaint_management(self):
        #e生活
        esh_data = ESHData(self.config, 'eshenghuo')
        eshenghuo_data = esh_data.eshenghuoComplaintCount(self.eshenghuoComplaintCountUrl)
        data = eshenghuo_data
        # print(eshenghuo_data)
        # sys.exit()
        return data

    #投诉管理-项目数据
    def get_customer_complaint_management(self, community_id):
        url = self.customer_complaint_managementUrl.format(community_id=community_id)
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            rows = data.get("data", [])
            if not rows:
                return {'totalAmount': 0, 'toCommunity': 0, 'finishPercent': 0}
            community_data = {
                'totalAmount': rows[0]['totalAmount'],
                'toCommunity': rows[0]['toCommunity'],
                'finishPercent': f"{rows[0]['finishPercent']}%"
            }
            return community_data
        else:
            print(f"Error fetching data from {url}. Response code: {response.status_code}")
            return None

    #投诉管理-报事项目数据
    def customer_complaint_matterReport(self):
        community_data = []
        for community in self.customer_complaint_communities:
            community_id = community['communityId']
            communityName = community['communityName']
            data = self.customer_complaint_matterReport_fetch_community_data(community_id, communityName)
            if data:
                community_data.append(data)
        return community_data

    def get_customer_complaint_matterReport(self, community_id):
        url = self.customer_complaint_matterReportUrl.format(community_id=community_id)
        response = self.session.post(url)
        if response.status_code == 200:
            data = response.json()

            rows = data["data"]
            if not rows:
                return {'appNum': 0,  'finishRate': 0}
            community_data = {
                'appNum': rows[0]['appNum'],
                'finishRate': f"{rows[0]['finishRate']}%"
            }
            return community_data
        else:
            print(f"Error fetching data from {url}")
            return None

    def process_data(self):
        departments = self.common.get_department_data().get("result", [])
        result = [
            {
                'area': department['area'],
                'communityName': department['communityName'],
                'totalAmount': parent_department.get('totalAmount', 0),
                'toCommunity': parent_department.get('toCommunity', 0),
                'finishPercent': f"{parent_department.get('finishPercent', 0)}%",
                'appNum': parent_matterReport.get('appNum', 0),
                'finishRate': f"{parent_matterReport.get('finishRate', 0)}%",
                "date": self.previous_month_str
            }
            for department in departments
            for parent_department in [self.get_customer_complaint_management(department['communityId'])]
            for parent_matterReport in [self.get_customer_complaint_matterReport(department['communityId'])]
        ]

        return result





    #投诉管理-投诉表扬
    def customer_praise(self):
        community_data = []
        for community in self.customer_complaint_communities:
            community_id = community['communityId']
            communityName = community['communityName']
            data = self.customer_praise_fetch_community_data(community_id, communityName)
            if data:
                community_data.append(data)
        return community_data

    #投诉管理-投诉表扬-项目数据
    def customer_praise_fetch_community_data(self, community_id, communityName):
        url = self.customer_praiseUrl.format(community_id=community_id)
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            rows = data["data"]
            if not rows:
                return {'communityName': communityName, 'totalAmount': '-',  'finishPercent': '-'}
            community_data = {
                'communityName': communityName,
                'totalAmount': rows[0]['totalAmount'],
                'finishRate': f"{rows[0]['finishPercent']}%"
            }
            return community_data
        else:
            print(f"Error fetching data from {url}")
            return None

    def customer_apply(self):
        community_data = []
        for community in self.customer_complaint_communities:
            community_id = community['communityId']
            communityName = community['communityName']
            data = self.customer_apply_fetch_community_data(community_id, communityName)
            if data:
                community_data.append(data)
        return community_data
    def customer_apply_fetch_community_data(self, community_id, communityName):
        # 更新 filters 中的 communityId value
        updated_filters = self.customer_apply_filters.copy()
        updated_filters['filters'][1]['value'] = community_id

        response = self.session.post(self.customer_applyUrl, json=updated_filters)
        if response.status_code == 200:
            data = response.json()
            rows = data["data"]["rows"]

            start_date = datetime.strptime("2023-03-01", "%Y-%m-%d")
            end_date = datetime.strptime("2023-03-31", "%Y-%m-%d")

            count = 0
            for row in rows:
                created_date = datetime.strptime(row['createdDate'][:10], "%Y-%m-%d")
                if start_date <= created_date <= end_date:
                    count += 1

            approveUserNum_data = {'communityName': communityName, 'approveUserNum': count}
            return approveUserNum_data
        else:
            print(f"Error fetching data from {self.customer_applyUrl}")
            return None

    #通知公告数量
    def customer_notice(self):
        community_data = []
        for community in self.customer_complaint_communities:
            community_id = community['communityId']
            communityName = community['communityName']
            data = self.customer_notice_fetch_community_data(community_id, communityName)
            if data:
                community_data.append(data)
        return community_data

    #通知公告数量数据清理
    def customer_notice_fetch_community_data(self, community_id, communityName):
        # 更新 filters 中的 communityId value
        updated_filters = self.customer_notice_filters.copy()
        updated_filters['filters'][0]['value'] = community_id

        response = self.session.post(self.customer_noticeUrl, json=updated_filters)
        if response.status_code == 200:
            data = response.json()
            rows = data["data"]["rows"]

            start_date = datetime.strptime("2023-03-01", "%Y-%m-%d")
            end_date = datetime.strptime("2023-03-31", "%Y-%m-%d")

            count = 0
            for row in rows:
                created_date = datetime.strptime(row['createdDate'][:10], "%Y-%m-%d")
                if start_date <= created_date <= end_date:
                    count += 1

            notice_data = {'communityName': communityName, 'noticeNum': count}
            return notice_data
        else:
            print(f"Error fetching data from {self.customer_noticeUrl}")
            return None

    #投诉管理-社区活动数量
    def customer_communication(self):
        community_data = []
        for community in self.customer_complaint_communities:
            community_id = community['communityId']
            communityName = community['communityName']
            data = self.customer_communication_fetch_community_data(community_id, communityName)
            if data:
                community_data.append(data)
        return community_data

    #投诉管理-社区活动数量数据清理
    def customer_communication_fetch_community_data(self, community_id, communityName):
        # 更新 filters 中的 communityId value
        updated_filters = self.customer_communication_filters.copy()
        updated_filters['communityId'] = community_id

        response = self.session.post(self.customer_communicationUrl, json=updated_filters)
        if response.status_code == 200:
            data = response.json()
            rows = data["data"]["rows"]

            start_date = datetime.strptime("2023-03-01", "%Y-%m-%d")
            end_date = datetime.strptime("2023-03-31", "%Y-%m-%d")

            count = 0
            for row in rows:
                created_date = datetime.strptime(row['deadline'][:10], "%Y-%m-%d")
                if start_date <= created_date <= end_date:
                    count += 1

            communication_data = {'communityName': communityName, 'communicationNum': count}
            return communication_data
        else:
            print(f"Error fetching data from {self.customer_communicationUrl}")
            return None

    #投诉管理-文章发布数量
    def customer_topic(self):
        community_data = []
        for community in self.customer_complaint_communities:
            community_id = community['communityId']
            communityName = community['communityName']
            data = self.customer_topic_fetch_community_data(community_id, communityName)
            if data:
                community_data.append(data)
        return community_data
    #投诉管理-文章发布数量数据处理
    def customer_topic_fetch_community_data(self, community_id, communityName):
        # 更新 filters 中的 communityId value
        updated_filters = self.customer_topic_filters.copy()
        updated_filters['filters'][0]['value'] = community_id

        response = self.session.post(self.customer_topicUrl, json=updated_filters)
        if response.status_code == 200:
            data = response.json()
            rows = data["data"]["rows"]

            start_date = datetime.strptime("2023-03-01", "%Y-%m-%d")
            end_date = datetime.strptime("2023-03-31", "%Y-%m-%d")

            count = 0
            for row in rows:
                created_date = datetime.strptime(row['createdDate'][:10], "%Y-%m-%d")
                if start_date <= created_date <= end_date:
                    count += 1

            topic_data = {'communityName': communityName, 'topicNum': count}
            return topic_data
        else:
            print(f"Error fetching data from {self.customer_topicUrl}")
            return None

    def combine_data(self):
        complaint_management_data = self.customer_complaint_management()
        complaint_matter_report_data = self.customer_complaint_matterReport()
        praise_data = self.customer_praise()
        apply_data = self.customer_apply()
        notice_data = self.customer_notice()
        communication_data = self.customer_communication()
        topic_data = self.customer_topic()

        combined_data = []

        for community in self.customer_complaint_communities:
            community_name = community['communityName']
            area = self.get_area(community_name)  # 使用get_area方法替换原来的代码

            combined_item = {
                'area': area,
                'communityName': community_name,
                "date": self.previous_month_str
            }

            for data in complaint_management_data:
                if data['communityName'] == community_name:
                    combined_item.update(data)
                    break

            for data in complaint_matter_report_data:
                if data['communityName'] == community_name:
                    combined_item.update(data)
                    break

            for data in praise_data:
                if data['communityName'] == community_name:
                    combined_item.update(data)
                    break

            for data in apply_data:
                if data['communityName'] == community_name:
                    combined_item.update(data)
                    break

            for data in notice_data:
                if data['communityName'] == community_name:
                    combined_item.update(data)
                    break

            for data in communication_data:
                if data['communityName'] == community_name:
                    combined_item.update(data)
                    break

            for data in topic_data:
                if data['communityName'] == community_name:
                    combined_item.update(data)
                    break

            combined_data.append(combined_item)

        return combined_data

    def get_area(self, community_name):
        try:
            area = self.area_mapping[community_name]
        except KeyError:
            if community_name == '泛海国际居住区一期管理处':
                area = '北京'
            elif community_name == '泛海国际居住区二期管理处':
                area = '北京'
            elif community_name == '深圳新世纪':
                area = '深圳'
            elif community_name == '深圳太子山庄':
                area = '深圳'
            elif community_name == '深圳城市广场':
                area = '深圳'
            else:
                raise KeyError(f"未找到地区：{community_name}")
        return area

    def insert_or_update_data(self, data):
        db = DB()
        for record in data:
            community_name = record['communityName']
            date = record['date']
            query = "SELECT * FROM customer_service WHERE communityName = %s AND date = %s"
            result = db.select(query, (community_name, date))

            if result:
                record_id = result[0][0]
                update_data = {
                    'totalAmount': record['totalAmount'],
                    'toCommunity': record['toCommunity'],
                    'finishPercent': record['finishPercent'],
                    'appNum': record['appNum'],
                    'finishRate': record['finishRate'],
                    'approveUserNum': record['approveUserNum'],
                    'noticeNum': record['noticeNum'],
                    'communicationNum': record['communicationNum']
                }
                condition = f"id = {record_id} AND communityName = '{community_name}' AND date = '{date}'"
                db.update('customer_service', update_data, condition)
                print(f"{community_name} on {date}: updated {len(result)} rows")
            else:
                insert_data = {
                    'area': record['area'],
                    'communityName': community_name,
                    'totalAmount': record['totalAmount'],
                    'toCommunity': record['toCommunity'],
                    'finishPercent': record['finishPercent'],
                    'appNum': record['appNum'],
                    'finishRate': record['finishRate'],
                    'approveUserNum': record['approveUserNum'],
                    'noticeNum': record['noticeNum'],
                    'communicationNum': record['communicationNum'],
                    'date': date
                }
                db.insert('customer_service', insert_data)
                print(f"{community_name} on {date}: inserted 1 row")
