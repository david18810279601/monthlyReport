import configparser
import datetime as dt
import sys
import requests
from datetime import datetime
import json
from login import Login
from ESHData import ESHData
from DB import DB

class ContractManagement:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.login = Login(self.config, 'normal')
        self.session = self.login.login()

        #新增合同
        self.get_contractManagementUrl = self.config.get("ContractManagementAPI", "ContractManagementUrl")
        self.get_ontractManagementFilters = json.loads(self.config.get("ContractManagementAPI", "ContractManagementFilters"))

    def get_contractManagement(self):
        response = self.session.post(self.get_contractManagementUrl, json=self.get_ontractManagementFilters)
        if response.status_code == 200:
            data = response.json()
            return data['data']['total']
        else:
            print(f"Error fetching data from {self.get_contractManagementUrl}")
            return None
