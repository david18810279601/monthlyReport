import configparser
import datetime
import sys
import requests
import json
from login import Login
from DB import DB
from common import Common

class checkPermission:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.login = Login(self.config, 'normal')
        self.common = Common(config_file)
        self.session = self.login.login()

        #角色管理
        self.get_RoleManager_Url = self.config.get("roleUrlApi", "RoleManager_Url")
        self.get_RoleManager_Filters = json.loads(self.config.get("roleUrlApi", "RoleManager_Filters"))

    def get_roleManager_id_and_name(self):
        response = self.session.post(self.get_RoleManager_Url, json=self.get_RoleManager_Filters)
        if response.status_code == 200:
            data = response.json()
            rows = data['data']['rows']
            role_manager_data = []
            for row in rows:
                role_manager_id = row['id']
                role_manager_name = row['name']
                role_manager_data.append({'id': role_manager_id, 'name': role_manager_name})
            return role_manager_data
        else:
            print(f"Error get_roleManager_id_and_name data from {self.get_RoleManager_Url}")
            return None

    def get_roleManager_menu(self, role_manager_id):
        get_RoleManager_Menu_Url = self.config.get("roleUrlApi", "RoleManager_Menu_Url")
        get_RoleManager_Menu_Filters = json.loads(self.config.get("roleUrlApi", "RoleManager_Menu_Filters"))
        get_RoleManager_Menu_Filters['roleId'] = role_manager_id
        response = self.session.post(get_RoleManager_Menu_Url, json=get_RoleManager_Menu_Filters)
        if response.status_code == 200:
            data = response.json()
            rows = data['data']['rows']
            role_manager_menu = []
            for row in rows:
                role_manager_menu.append({'id': row['id'], 'name': row['name'], 'isParent': row['isParent'], 'chosen': row['chosen']})
            return role_manager_menu
        else:
            print(f"Error get_roleManager_menu data from {get_RoleManager_Menu_Url}")
            return None

    def traverse_menu_data(self, data):
        result = []
        stack = []
        stack.append((data, None))

        while stack:
            node, parent = stack.pop()
            if node["isParent"]:
                stack.extend((child, node) for child in reversed(node["children"]))
            elif node["chosen"]:
                menu_item = {
                    "id": node["id"],
                    "name": node["name"]
                }
                if parent:
                    if "children" not in parent:
                        parent["children"] = []
                    parent["children"].append(menu_item)
                else:
                    result.append(menu_item)

        return result