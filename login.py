import requests


class Login:
    def __init__(self, config):
        self.login_url = config.get("LOGIN", "login_url")
        self.payload = {
            "username": config.get("LoginInformation", "username"),
            "password": config.get("LoginInformation", "password"),
            "userType": int(config.get("LoginInformation", "userType")),
            "tenantCode": config.get("LoginInformation", "tenantCode")
        }

    def login(self):
        response = requests.post(self.login_url, json=self.payload)
        if response.status_code == 200:
            session = requests.Session()
            session.headers.update({"Authorization": f"{response.json()['data']['token']}"})
            return session
        else:
            raise Exception("Login failed")
