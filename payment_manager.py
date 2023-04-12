import configparser
import datetime
import sys
import requests
import json
from ESHData import ESHData
from login import Login

class PaymentManager:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
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
        response = self.session.post(self.FeeAmountUrl, json=self.FeeAmountData)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.FeeAmountUrl}")
            return None
        return result['data']['rows'][0]['amountPaid']

    def get_fee_count_num(self, community_id):
        self.FeeCountNumFilters["communityId"] = community_id
        response = self.session.post(self.FeeCountNumUrl, json=self.FeeCountNumFilters)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.FeeCountNumUrl}")
            return None
        return result['data']['total']

    # 获取app缴费笔数
    def get_app_fee_num(self, community_id):
        updated_params = self.AppFeeNumParams.copy()
        updated_params["communityId"] = community_id
        response = self.session.post(self.AppFeeNumUrl, params=updated_params, json=self.AppFeeData)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.AppFeeNumUrl}")
            return None
        return result['data']['total']

    # 获取app缴费金额
    def get_app_amount(self, community_id):
        updated_params = self.AppAmountParams.copy()
        updated_params["communityId"] = community_id
        response = self.session.post(self.AppAmountUrl, params=updated_params, json=self.AppAmountData)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.AppAmountUrl}")
            return None
        return result['data']['rows'][0]['amount']

    # 获取物业费收入
    def get_property_fee_income(self, community_id, propertyFeeIncomeId):
        updated_data = self.propertyFeeIncomeData.copy()
        updated_data["communityId"] = community_id
        updated_data["feeItemIds"] = [propertyFeeIncomeId]
        response = self.session.post(self.propertyFeeIncomeUrl, json=updated_data)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.propertyFeeIncomeUrl}")
            return None
        return result['data']['rows'][0]['amountPaid']

    # 获取停车费收入
    def get_parking_fee_income(self, community_id, parkingFeeIncomeId):
        updated_data = self.parkingFeeIncomeData.copy()
        updated_data["communityId"] = community_id
        updated_data["feeItemIds"] = [parkingFeeIncomeId]
        response = self.session.post(self.parkingFeeIncomeUrl, json=updated_data)
        result = response.json()
        if response.status_code != 200:
            print(f"Error fetching data from {self.parkingFeeIncomeUrl}")
            return None
        return result['data']['rows'][0]['amountPaid']

    # 获取物业费收缴率
    def get_property_fee_collection_rate(self, community_id, propertyFeeCollectionRateId):
        updated_params = self.propertyFeeCollectionRateParams.copy()
        updated_params["communityId"] = community_id
        updated_params["feeItemId"] = propertyFeeCollectionRateId
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
        percentage = round(amountPaidCount / amountReceivableCount * 100, 2)
        return f'{percentage}%' if percentage else '0%'

    # E生活缴费数据
    def get_eshenghuo_cost_data(self):
        esh_data = ESHData(self.config, 'eshenghuo')
        eshenghuo_data = esh_data.eshenghuo_cost_data(self.eshenghuoCostDataUrl)
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
        eshenghuo_data = esh_data.eshenghuoProperty_CostsData(self.eshenghuoProperty_CostsDataUrl, community_id, propertyFeeIncomeId)
        if eshenghuo_data == None:
            return {'propertyFeeIncome': "0"}
        return {'propertyFeeIncome': eshenghuo_data}

    # E生活停车缴费数据
    def get_eshenghuoParking_FeeData(self, community_id, parkingFeeIncomeId):
        esh_data = ESHData(self.config, 'eshenghuo')
        eshenghuo_data = esh_data.eshenghuoParking_FeeData(self.eshenghuoParking_FeeUrl, community_id, parkingFeeIncomeId)
        if eshenghuo_data == None:
            return {'parkingFeeIncome': "0"}
        return {'parkingFeeIncome': eshenghuo_data}

    def get_community_fee_data(self):
        community_fee_data = []
        for community in self.eshenghuoCommunities:
            property_fee_data = self.get_eshenghuoProperty_CostsData(community["communityId"], community["propertyFeeIncomeId"])
            parking_fee_data = self.get_eshenghuoParking_FeeData(community["communityId"], community["parkingFeeIncomeId"])
            community_fee_data.append({
                "communityName": community["communityName"],
                "propertyFeeIncome": property_fee_data["propertyFeeIncome"],
                "parkingFeeIncome": parking_fee_data["parkingFeeIncome"]
            })
        return community_fee_data

    def process_data(self):
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
            appOrderCountRatio = '{:.2f}%'.format(appFeeCountNum / fee_count_num * 100)
            appOrderAmountRatio = '{:.2f}%'.format(appAmount / fee_amount * 100)

            processed_data.append({
                "companyName": company_name,
                "communityName": community_name,
                "feeAmount": fee_amount,
                "feeCountNum": fee_count_num,
                "appFeeCountNum": appFeeCountNum,
                "appAmount": appAmount,
                "propertyFeeIncome": property_fee_income,
                "parkingFeeIncome": parking_fee_income,
                "appOrderCountRatio": appOrderCountRatio,
                "appOrderAmountRatio": appOrderAmountRatio,
                "propertyFeeCollectionRate": property_fee_collection_rate
            })

        return processed_data