import json
import sys

import requests

class Login:
    def __init__(self, config, login_type):
        self.login_type = login_type
        if login_type == "eshenghuo":
            self.login_url = config.get("LOGIN", "eshenghuo_url")
            eshenghuo_login_data = json.loads(config.get("EshenghuoLoginInformation", "EshenghuoLoginData"))
            self.payload = {
                "j_username": eshenghuo_login_data["j_username"],
                "j_password": eshenghuo_login_data["j_password"],
            }
        elif login_type == "normal":
            self.login_url = config.get("LOGIN", "login_url")
            self.payload = {
                "username": config.get("LoginInformation", "username"),
                "password": config.get("LoginInformation", "password"),
                "userType": int(config.get("LoginInformation", "userType")),
                "tenantCode": config.get("LoginInformation", "tenantCode"),
            }
        else:
            raise ValueError("Invalid login type provided")

    def login(self):
        session = requests.Session()
        if self.login_type == "eshenghuo":
            eshenghuo_response = session.post(self.login_url, data=self.payload)
            if eshenghuo_response.status_code == 200:
                session.headers.update({"Cookie": eshenghuo_response.headers["Set-Cookie"]})
                return session
            else:
                raise Exception("Login failed")
        else:
            response = session.post(self.login_url, json=self.payload)
            if response.status_code == 200:
                session.headers.update({"Authorization": f"{response.json()['data']['token']}"})
                return session
            else:
                raise Exception("Login failed")


