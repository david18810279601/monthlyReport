import configparser
import datetime
import sys
import requests
import json
from ESHData import ESHData
from login import Login
from DB import DB
from common import Common

class PaymentManager:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.common = Common(config_file)
        self.FeeCountNumUrl = self.config.get("PaymentManagerFeeCountNumAPI", "getFeeCountNumUrl")
        self.FeeCountNumFilters = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "getFeeCountNumData"))
        self.communities = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "communities"))

        self.FeeAmountUrl = self.config.get("PaymentManagerFeeCountNumAPI", "getFeeAmountUrl")
        self.FeeAmountData = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "getFeeAmountData"))

        self.AppFeeNumUrl = self.config.get("PaymentManagerFeeCountNumAPI", "getAppFeeNumUrl")
        self.AppFeeNumParams = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "getAppFeeNumParams"))
        self.AppFeeData = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "getAppFeeData"))

        self.AppAmountUrl= self.config.get("PaymentManagerFeeCountNumAPI", "getAppAmountUrl")
        self.AppAmountParams = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "getAppAmountParams"))
        self.AppAmountData = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "getAppAmountData"))

        self.propertyFeeIncomeUrl= self.config.get("PaymentManagerFeeCountNumAPI", "propertyFeeIncomeUrl")
        self.propertyFeeIncomeData = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "propertyFeeIncomeData"))

        self.parkingFeeIncomeUrl= self.config.get("PaymentManagerFeeCountNumAPI", "parkingFeeIncomeUrl")
        self.parkingFeeIncomeData = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "parkingFeeIncomeData"))

        self.propertyFeeCollectionRateUrl= self.config.get("PaymentManagerFeeCountNumAPI", "propertyFeeCollectionRateUrl")
        self.propertyFeeCollectionRateParams = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "propertyFeeCollectionRateParams"))
        self.propertyFeeCollectionRateData = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "propertyFeeCollectionRateData"))

        #E生活缴费数据
        self.eshenghuoCostDataUrl = self.config.get("EshenghuoPaymentManagerCostDataNumAPI", "eshenghuoCostDataUrl")
        self.communityNames = self.config.get("EshenghuoPaymentManagerCostDataNumAPI", "community_names")
        self.mergeRules = json.loads(self.config.get("EshenghuoPaymentManagerCostDataNumAPI", "merge_rules"))
        self.eshenghuoProperty_CostsDataUrl = self.config.get("EshenghuoPaymentManagerCostDataNumAPI", "eshenghuoProperty_CostsDataUrl")
        self.eshenghuoParking_FeeUrl = self.config.get("EshenghuoPaymentManagerCostDataNumAPI", "eshenghuoParking_FeeUrl")
        self.eshenghuoCommunities = json.loads(self.config.get("EshenghuoPaymentManagerCostDataNumAPI", "eshenghuoCommunities"))

        self.month_mapping = self.config.get("MonthMapping", "mapping")
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()

        area_data = json.loads(self.config.get("Area", "areaCommunityName"))
        self.area_mapping = {item["communityName"]: item["area"] for item in area_data}
        self.previous_month_str = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")

    # 获取物业费收入
    def get_fee_amount(self, community_id):
        self.FeeAmountData["communityId"] = community_id
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        self.FeeAmountData["receivedDateStart"] = start_time.strftime("%Y-%m-%d")
        end_time = self.common.get_month_start_end_dates("END_ALL")
        self.FeeAmountData["receivedDateEnd"] = end_time.strftime("%Y-%m-%d")
        response = self.session.post(self.FeeAmountUrl, json=self.FeeAmountData)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.FeeAmountUrl}")
            return None
        try:
            return result['data']['rows'][0]['amountPaid']
        except IndexError:
            return 0

    def get_fee_count_num(self, community_id):
        self.FeeCountNumFilters["communityId"] = community_id
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        self.FeeCountNumFilters["receivedDateStart"] = start_time.strftime("%Y-%m-%d")
        end_time = self.common.get_month_start_end_dates("END_ALL")
        self.FeeCountNumFilters["receivedDateEnd"] = end_time.strftime("%Y-%m-%d")
        response = self.session.post(self.FeeCountNumUrl, json=self.FeeCountNumFilters)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.FeeCountNumUrl}")
            return None
        try:
            return result['data']['total']
        except IndexError:
            return 0

    # 获取app缴费笔数
    def get_app_fee_num(self, community_id):
        updated_params = self.AppFeeNumParams
        updated_params["communityId"] = community_id
        updated_params["receivedDateStart"] = self.common.get_month_start_end_dates("ST_ALL").strftime("%Y-%m-%d")
        updated_params["receivedDateEnd"] = self.common.get_month_start_end_dates("END_ALL").strftime("%Y-%m-%d")
        response = self.session.post(self.AppFeeNumUrl, params=updated_params, json=self.AppFeeData)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.AppFeeNumUrl}")
            return None
        try:
            return result['data']['total']
        except IndexError:
            return 0

    # 获取app缴费金额
    def get_app_amount(self, community_id):
        updated_params = self.AppAmountParams
        updated_params["receivedDateStart"] = self.common.get_month_start_end_dates("ST_ALL").strftime("%Y-%m-%d")
        updated_params["receivedDateEnd"] = self.common.get_month_start_end_dates("END_ALL").strftime("%Y-%m-%d")
        updated_params["communityId"] = community_id
        response = self.session.post(self.AppAmountUrl, params=updated_params, json=self.AppAmountData)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.AppAmountUrl}")
            return None
        try:
            return result['data']['rows'][0]['amount']
        except IndexError:
            return 0

    # 获取物业费收入
    def get_property_fee_income(self, community_id, propertyFeeIncomeId):
        updated_data = self.propertyFeeIncomeData
        updated_data["communityId"] = community_id
        updated_data["feeItemIds"] = [propertyFeeIncomeId]
        updated_data["receivedDateStart"] = self.common.get_month_start_end_dates("ST_ALL").strftime("%Y-%m-%d")
        updated_data["accountingDateStart"] = self.common.get_month_start_end_dates("ST_ALL").strftime("%Y-%m-%d")
        updated_data["receivedDateEnd"] = self.common.get_month_start_end_dates("END_ALL").strftime("%Y-%m-%d")
        updated_data["accountingDateEnd"] = self.common.get_month_start_end_dates("END_ALL").strftime("%Y-%m-%d")
        response = self.session.post(self.propertyFeeIncomeUrl, json=updated_data)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.propertyFeeIncomeUrl}")
            return None
        try:
            return result['data']['rows'][0]['amountPaid']
        except IndexError:
            return 0

    # 获取停车费收入
    def get_parking_fee_income(self, community_id, parkingFeeIncomeId):
        updated_data = self.parkingFeeIncomeData
        updated_data["communityId"] = community_id
        updated_data["feeItemIds"] = [parkingFeeIncomeId]
        updated_data["receivedDateStart"] = self.common.get_month_start_end_dates("ST_ALL").strftime("%Y-%m-%d")
        updated_data["accountingDateStart"] = self.common.get_month_start_end_dates("ST_ALL").strftime("%Y-%m-%d")
        updated_data["receivedDateEnd"] = self.common.get_month_start_end_dates("END_ALL").strftime("%Y-%m-%d")
        updated_data["accountingDateEnd"] = self.common.get_month_start_end_dates("END_ALL").strftime("%Y-%m-%d")
        response = self.session.post(self.parkingFeeIncomeUrl, json=updated_data)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.parkingFeeIncomeUrl}")
            return None
        try:
            return result['data']['rows'][0]['amountPaid']
        except IndexError:
            return 0

    # 获取物业费收缴率
    def get_property_fee_collection_rate(self, community_id, propertyFeeCollectionRateId):
        updated_params = self.propertyFeeCollectionRateParams.copy()
        updated_params["communityId"] = community_id
        updated_params["feeItemId"] = propertyFeeCollectionRateId
        updated_params["receivedDateStart"] = self.common.get_month_start_end_dates("ST_ALL").strftime("%Y-%m-%d")
        updated_params["accountingDateStart"] = self.common.get_month_start_end_dates("ST_ALL").strftime("%Y-%m-%d")
        updated_params["receivedDateEnd"] = self.common.get_month_start_end_dates("END_ALL").strftime("%Y-%m-%d")
        updated_params["accountingDateEnd"] = self.common.get_month_start_end_dates("END_ALL").strftime("%Y-%m-%d")
        response = self.session.post(self.propertyFeeCollectionRateUrl, params=updated_params, json=self.propertyFeeCollectionRateData)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.propertyFeeCollectionRateUrl}")
            return None
        amountReceivableCount = 0
        amountPaidCount = 0
        for row in result['data']['rows']:
            amountReceivableCount += row['amountReceivable']
            amountPaidCount += row['amountPaid']
        if amountReceivableCount != 0:
            percentage = round(amountPaidCount / amountReceivableCount * 100, 2)
        else:
            percentage = 0
        return f'{percentage}%' if percentage else '0%'

    # E生活缴费数据
    def get_eshenghuo_cost_data(self):
        esh_data = ESHData(self.config, 'eshenghuo')
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        formatted_start_time = start_time.strftime("%Y-%m-%d")
        end_time = self.common.get_month_start_end_dates("END_ALL")
        formatted_end_time = end_time.strftime("%Y-%m-%d")
        eshenghuo_data = esh_data.eshenghuo_cost_data(self.eshenghuoCostDataUrl,formatted_start_time,formatted_end_time)
        eshengh_beijing_data = self.get_eshenghuo_filter_community_data(eshenghuo_data['rows'], self.communityNames)
        eshengh_wuhan_data = self.get_eshenghuo_merge_community_data(eshenghuo_data['rows'], self.mergeRules)
        return eshengh_wuhan_data + eshengh_beijing_data

    def get_eshenghuo_filter_community_data(self, data, community_names):
        result = []

        for item in data:
            if item['communityName'] in community_names:
                app_order_count_ratio = '{:.2f}%'.format(item['appFeeCountNum'] / item['feeCountNum'] * 100)
                app_order_amount_ratio = '{:.2f}%'.format(item['appFeeAmount'] / item['feeAmount'] * 100)

                result_item = {
                    'companyName': item['companyName'],
                    'communityName': item['communityName'],
                    'feeCountNum': item['feeCountNum'],
                    'feeAmount': item['feeAmount'],
                    'appFeeCountNum': item['appFeeCountNum'],
                    'appFeeAmount': item['appFeeAmount'],
                    'appOrderCountRatio': app_order_count_ratio,
                    'appOrderAmountRatio': app_order_amount_ratio
                }

                result.append(result_item)

        return result

    def get_eshenghuo_merge_community_data(self, data, merge_rules):
        result = []
        for new_name, old_names in merge_rules.items():
            merged_item = {
                "companyName": "",
                "communityName": new_name,
                "feeCountNum": 0,
                "feeAmount": 0.0,
                "appFeeCountNum": 0,
                "appFeeAmount": 0.0,
                "appOrderAmountRatio": "-",
                "appOrderCountRatio": "-"
            }
            found = False

            for old_name in old_names:
                for item in data:
                    if item["communityName"] == old_name:
                        found = True
                        merged_item["companyName"] = "武汉地区"  # 修改为 "武汉地区"
                        if merged_item["feeCountNum"] != "-":
                            merged_item["feeCountNum"] += item["feeCountNum"]
                        if merged_item["feeAmount"] != "-":
                            merged_item["feeAmount"] += item["feeAmount"]
                        if merged_item["appFeeCountNum"] != "-":
                            merged_item["appFeeCountNum"] += item["appFeeCountNum"]
                        if merged_item["appFeeAmount"] != "-":
                            merged_item["appFeeAmount"] += item["appFeeAmount"]

            if not found:
                merged_item["companyName"] = "武汉地区"
                merged_item["feeCountNum"] = "-"
                merged_item["feeAmount"] = "-"
                merged_item["appFeeCountNum"] = "-"
                merged_item["appFeeAmount"] = "-"
                merged_item["appOrderAmountRatio"] = "-"
                merged_item["appOrderCountRatio"] = "-"
            else:
                app_order_amount_ratio = '{:.2f}%'.format(merged_item['appFeeAmount'] / merged_item['feeAmount'] * 100)
                app_order_count_ratio = '{:.2f}%'.format(merged_item['appFeeCountNum'] / merged_item['feeCountNum'] * 100)
                merged_item["appOrderAmountRatio"] = app_order_amount_ratio
                merged_item["appOrderCountRatio"] = app_order_count_ratio

            result.append(merged_item)
        return result

    # E生活物业缴费数据
    def get_eshenghuoProperty_CostsData(self, community_id, propertyFeeIncomeId):
        esh_data = ESHData(self.config, 'eshenghuo')
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        formatted_start_time = start_time.strftime("%Y-%m-%d")
        end_time = self.common.get_month_start_end_dates("END_ALL")
        formatted_end_time = end_time.strftime("%Y-%m-%d")
        eshenghuo_data = esh_data.eshenghuoProperty_CostsData(self.eshenghuoProperty_CostsDataUrl, community_id, propertyFeeIncomeId, formatted_start_time,formatted_end_time)
        if eshenghuo_data == None:
            return {'propertyFeeIncome': "0"}
        return {'propertyFeeIncome': eshenghuo_data}

    # E生活停车缴费数据
    def get_eshenghuoParking_FeeData(self, community_id, parkingFeeIncomeId):
        esh_data = ESHData(self.config, 'eshenghuo')
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        formatted_start_time = start_time.strftime("%Y-%m-%d")
        end_time = self.common.get_month_start_end_dates("END_ALL")
        formatted_end_time = end_time.strftime("%Y-%m-%d")
        eshenghuo_data = esh_data.eshenghuoParking_FeeData(self.eshenghuoParking_FeeUrl, community_id, parkingFeeIncomeId,formatted_start_time,formatted_end_time)
        if eshenghuo_data == None:
            return {'parkingFeeIncome': "0"}
        return {'parkingFeeIncome': eshenghuo_data}

    def get_eshenghuo_AllData(self, community_id):
        esh_data = ESHData(self.config, 'eshenghuo')
        start_time = self.common.get_month_start_end_dates("ST_ALL")
        formatted_start_time = start_time.strftime("%Y-%m-%d")
        end_time = self.common.get_month_start_end_dates("END_ALL")
        formatted_end_time = end_time.strftime("%Y-%m-%d")
        eshenghuo_All_Data = esh_data.eshenghuo_all(self.eshenghuoParking_FeeUrl, community_id, formatted_start_time, formatted_end_time)
        if eshenghuo_All_Data == None:
            return {'allData': "0"}
        return {'allData': eshenghuo_All_Data}

    def get_community_fee_data(self):
        community_fee_data = []
        communitys = self.eshenghuoCommunities
        for community in communitys:
            property_fee_data = self.get_eshenghuoProperty_CostsData(community["communityId"], community["propertyFeeIncomeId"])
            parking_fee_data = self.get_eshenghuoParking_FeeData(community["communityId"], community["parkingFeeIncomeId"])
            all_data = self.get_eshenghuo_AllData(community["communityId"])
            property_fee_collection_rate = float(property_fee_data["propertyFeeIncome"]) / float(all_data["allData"])
            community_fee_data.append({
                "communityName": community["communityName"],
                "propertyFeeIncome": property_fee_data["propertyFeeIncome"],
                "parkingFeeIncome": parking_fee_data["parkingFeeIncome"],
                "propertyFeeCollectionRate": property_fee_collection_rate
            })
        return self.merge_community_data(community_fee_data, self.mergeRules)

    def merge_community_data(self, data, merge_rules):
        merged_data = []
        # 创建一个新的列表，用于保存已合并的 communityName
        for key, value in merge_rules.items():
            merged_item = {
                'communityName': key,
                'propertyFeeIncome': 0,
                'parkingFeeIncome': 0,
                'propertyFeeCollectionRate': 0
            }

            for item in data:
                if item['communityName'] in value or item['communityName'] == key:
                    merged_item['propertyFeeIncome'] += float(item['propertyFeeIncome'])
                    merged_item['parkingFeeIncome'] += float(item['parkingFeeIncome'])
                    merged_item['propertyFeeCollectionRate'] += float(item['propertyFeeCollectionRate'])

            merged_data.append(merged_item)
        community_names = [{"communityName": "泛海国际居住区二期容郡会所"},
                           {"communityName": "泛海国际居住区二期世家会所"},
                           {"communityName": "泛海国际居住区一期会所"}]

        # 处理 community_names 中的数据，并将匹配的数据添加到 merged_data 中
        for community in community_names:
            community_name = community["communityName"]

            for item in data:
                if "communityName" in item and item["communityName"] == community_name:
                    merged_data.append(item)
        return merged_data

    def merge_data_by_community(self, cost_data, community_data):
        merged_data = []

        for cost_item in cost_data:
            for community_item in community_data:
                if cost_item['communityName'] == community_item['communityName']:
                    merged_item = cost_item.copy()

                    # 转换为百分比
                    community_item['propertyFeeCollectionRate'] = '{:.2f}%'.format(community_item['propertyFeeCollectionRate'] * 100)
                    community_item['date'] = self.previous_month_str

                    merged_item.update(community_item)
                    merged_data.append(merged_item)
                    break

        return merged_data

    def eshenghuo_data(self):
        cost_data = self.get_eshenghuo_cost_data()
        community_data = self.get_community_fee_data()
        merged_data = self.merge_data_by_community(cost_data, community_data)
        return merged_data

    def haie_process_data(self):
        processed_data = []
        for community in self.communities:
            community_id = community["communityId"]
            company_name = community["companyName"]
            community_name = community["communityName"]
            propertyFeeIncomeId = community["propertyFeeIncomeId"]
            parkingFeeIncomeId = community["parkingFeeIncomeId"]
            propertyFeeCollectionRateId = community["propertyFeeCollectionRateId"]

            fee_amount = self.get_fee_amount(community_id)
            fee_count_num = self.get_fee_count_num(community_id)
            appFeeCountNum = self.get_app_fee_num(community_id)
            appAmount = self.get_app_amount(community_id)
            property_fee_income = self.get_property_fee_income(community_id, propertyFeeIncomeId)
            parking_fee_income = self.get_parking_fee_income(community_id, parkingFeeIncomeId)
            property_fee_collection_rate = self.get_property_fee_collection_rate(community_id, propertyFeeCollectionRateId)
            #appOrderCountRatio = '{:.2f}%'.format(appFeeCountNum / fee_count_num * 100)
            #appOrderAmountRatio = '{:.2f}%'.format(appAmount / fee_amount * 100)
            appOrderAmountRatio = 0
            if appAmount is not None and fee_amount is not None and fee_amount != 0:
                appOrderAmountRatio = '{:.2f}%'.format(appAmount / fee_amount * 100)
            appOrderCountRatio = 0
            if appFeeCountNum is not None and fee_count_num is not None and fee_count_num != 0:
                appOrderCountRatio = '{:.2f}%'.format(appFeeCountNum / fee_count_num * 100)

            processed_data.append({
                "companyName": company_name,
                "communityName": community_name,
                "feeAmount": fee_amount or 0,
                "feeCountNum": fee_count_num or 0,
                "appFeeCountNum": appFeeCountNum or 0,
                "appFeeAmount": appAmount or 0,
                "propertyFeeIncome": property_fee_income or 0,
                "parkingFeeIncome": parking_fee_income or 0,
                "appOrderCountRatio": appOrderCountRatio,
                "appOrderAmountRatio": appOrderAmountRatio,
                "propertyFeeCollectionRate": property_fee_collection_rate,
                "date": self.previous_month_str
            })

        return processed_data

    def process_data(self):
        eshenghuo_data = self.eshenghuo_data()
        haie_process_data = self.haie_process_data()
        merged_data = eshenghuo_data + haie_process_data
        return merged_data

    def insert_or_update_data(self, data):
        db = DB()
        for record in data:
            community_name = record['communityName']
            date = record['date']
            query = "SELECT * FROM payment_manager WHERE communityName = %s AND date = %s"
            result = db.select(query, (community_name, date))

            if result:
                record_id = result[0][0]
                update_data = {
                    'feeCountNum': record['feeCountNum'],
                    'feeAmount': record['feeAmount'],
                    'appFeeCountNum': record['appFeeCountNum'],
                    'appFeeAmount': record['appFeeAmount'],
                    'propertyFeeIncome': record['propertyFeeIncome'],
                    'parkingFeeIncome': record['parkingFeeIncome'],
                    'appOrderAmountRatio': record['appOrderAmountRatio'],
                    'appOrderCountRatio': record['appOrderCountRatio'],
                    'propertyFeeCollectionRate': record['propertyFeeCollectionRate']
                }
                condition = f"id = {record_id} AND communityName = '{community_name}' AND date = '{date}'"
                db.update('payment_manager', update_data, condition)
                print(f"{community_name} on {date}: updated {len(result)} rows")
            else:
                insert_data = {
                    'companyName': record['companyName'],
                    'communityName': community_name,
                    'feeCountNum': record['feeCountNum'],
                    'feeAmount': record['feeAmount'],
                    'appFeeCountNum': record['appFeeCountNum'],
                    'appFeeAmount': record['appFeeAmount'],
                    'propertyFeeIncome': record['propertyFeeIncome'],
                    'parkingFeeIncome': record['parkingFeeIncome'],
                    'appOrderAmountRatio': record['appOrderAmountRatio'],
                    'appOrderCountRatio': record['appOrderCountRatio'],
                    'propertyFeeCollectionRate': record['propertyFeeCollectionRate'],
                    'date': date
                }
                db.insert('payment_manager', insert_data)
                print(f"{community_name} on {date}: inserted 1 row")
