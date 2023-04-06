import configparser
import datetime
import sys
import requests
import json
from login import Login

class PaymentManager:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.FeeCountNumUrl = self.config.get("PaymentManagerFeeCountNumAPI", "getFeeAmountUrl")
        self.FeeCountNumFilters = json.loads(self.config.get("PaymentManagerFeeCountNumAPI", "getFeeAmountData"))
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
        return result['data']['total']

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