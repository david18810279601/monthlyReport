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

        #
        self.get_RoleManager_AddUrl = self.config.get("roleUrlApi", "RoleManager_AddUrl")

    def get_role_manager_data(self, rows):
        return [{'id': row['id'], 'name': row['name']} for row in rows]

    def get_roleManager_id_and_name(self):
        response = self.session.post(self.get_RoleManager_Url, json=self.get_RoleManager_Filters)

        if response.status_code == 200:
            data = response.json()
            rows = data['data']['rows']

            role_manager_data = self.get_role_manager_data(rows)
            new_role_manager = self.get_roleManager_menu(role_manager_data)
            new_role_manager_data = self.check_menu_access(new_role_manager, ["缴费管理-基础设置-收费方式-编辑", "缴费管理-基础设置-收费方式-新增"])


            return new_role_manager_data
        else:
            print(f"Error get_roleManager_id_and_name data from {self.get_RoleManager_Url}")
            return None

    def get_roleManager_menu(self, roleData):
        new_array_rows = []

        for role in roleData:
            url = f"{self.get_RoleManager_AddUrl}?roleId={role['id']}"

            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                rows = data['data']

                new_row = {}  # Initialize new_row as a dictionary
                new_row_key = f"{role['name']}-{role['id']}"  # Create a key by concatenating name and id
                new_row[new_row_key] = rows  # Add data to the dictionary

                new_array_rows.append(new_row)  # Append the dictionary to the list
            else:
                print(f"Error get_roleManager_menu data from {self.get_RoleManager_AddUrl}")
                return None

        return new_array_rows

    def check_menu_access(self, role_menu_data, paths_to_check):
        def _traverse(node, path):
            new_path = path + "-" + node['name']
            results = {}
            if not node['isParent'] and not node['children']:
                for path in paths_to_check:
                    if new_path.endswith(path) and node['chosen'] is True:  # Only return when chosen is True
                        return {new_path: node['chosen']}
            for child in node['children']:
                results.update(_traverse(child, new_path))
            return results

        access_dict = {}
        for role_menu_item in role_menu_data:
            for role, menu_data in role_menu_item.items():
                for data in menu_data:
                    access_dict.update({f"{role}{k}": v for k, v in _traverse(data, "").items()})
        return access_dict




    # def assemble_menu_data(self, menu_list):
    #     result = []
    #
    #     def traverse(menu_list, parent_list):
    #         for item in menu_list:
    #             if item['isParent']:
    #                 new_list = parent_list + [[item['id'], item['name'], item['isParent']]]
    #                 traverse(item['children'], new_list)
    #             elif item['chosen']:
    #                 result.append(parent_list + [[item['id'], item['name'], item['chosen']]])
    #
    #     traverse(menu_list, [])
    #
    #     return result

    # def parse_data(self, data):
    #     new_dict = {}
    #
    #     # 遍历data中的每一个项目
    #     for item in data:
    #         # 如果isParent为true，则进行递归解析子节点
    #         if item.get('isParent', False):
    #             new_dict.update({
    #                 item['id']: {
    #                     'name': item['name'],
    #                     'isParent': item['isParent'],
    #                     'children': self.parse_data(item.get('children', []))
    #                 }
    #             })
    #         # 如果isParent为false，且chosen为true，则记录此节点
    #         elif item.get('chosen', False):
    #             new_dict.update({
    #                 item['id']: {
    #                     'name': item['name'],
    #                     'chosen': item['chosen']
    #                 }
    #             })
    #
    #     return new_dict
    #
    # def transform_data(self, role_data):
    #     new_dict = {}
    #     for role_name, data in role_data.items():
    #         new_dict[role_name] = self.parse_data(data)
    #
    #     return new_dict