from wisdom_ticket import WisdomTicket
from customer_service import CustomerService
from maintenance_ticket import MaintenanceTicket
from facility_equipment import FacilityEquipment
from procurement_inventory import ProcurementInventory
from platform_index_report import PlatformIndexReport
from payment_manager import PaymentManager
from contract_management import ContractManagement
from perform_inspection import PerformInspection
from health_club_data import HealthClubData
from EcommerceOperation import EcommerceOperation
from calculate_revenue import CalculateRevenue
from check_permission import checkPermission


#1、平台运营指标
def platform_index_report(config_file):
    platform_index_report = PlatformIndexReport(config_file)
    raw_data = platform_index_report.fetch_data()
    processed_data = platform_index_report.process_data(raw_data)
    data = platform_index_report.insert_or_update_data(processed_data)
    return data

#2、客服工单
def customer_service(config_file):
    customer_service = CustomerService(config_file)
    raw_data = customer_service.process_data()
    # raw_data = customer_service.combine_data()
    data = customer_service.insert_or_update_data(raw_data)
    return data

#3、物业费收缴情况
def payment_manager(config_file):
    payment_manager = PaymentManager(config_file)
    # raw_data = payment_manager.eshenghuo_data()
    processed_data = payment_manager.process_data()
    data = payment_manager.insert_or_update_data(processed_data)
    return data
#4、维修工单
def maintenance_ticket(config_file):
    maintenance_ticket = MaintenanceTicket(config_file)
    raw_data = maintenance_ticket.sum_process_data()
    processed_data = maintenance_ticket.insert_or_update_data(raw_data)
    return processed_data

#5、智慧工单
def wisdom_ticket(config_file):
    wisdom_ticket = WisdomTicket(config_file)
    raw_data = wisdom_ticket.combine_data()
    processed_data = wisdom_ticket.insert_or_update_data(raw_data)
    return processed_data

# 7.设备设施
def facility_equipment(config_file):
    facility_equipment = FacilityEquipment(config_file)
    raw_data = facility_equipment.process_data()
    processed_data = facility_equipment.insert_or_update_data(raw_data)
    return processed_data

# 6.采购库存
def procurement_inventory(config_file):
    procurement_inventory = ProcurementInventory(config_file)
    raw_data = procurement_inventory.combine_data()
    processed_data = procurement_inventory.insert_or_update_data(raw_data)
    return processed_data

# 8.合同管理
def contract_management(config_file):
    contract_management = ContractManagement(config_file)
    raw_data = contract_management.get_contractManagement_data()
    processed_data = contract_management.insert_or_update_data(raw_data)
    return processed_data

# 9.资产管理
def calculate_revenue(config_file):
    calculate_revenue = CalculateRevenue(config_file)
    raw_data = calculate_revenue.get_calculate_revenue_data()
    processed_data = calculate_revenue.insert_or_update_data(raw_data)
    return processed_data

# 巡航巡检
def perform_inspection(config_file):
    perform_inspection = PerformInspection(config_file)
    raw_data = perform_inspection.process_data()
    processed_data = perform_inspection.insert_or_update_data(raw_data)
    return processed_data

def health_club_data(config_file):
    health_club_data = HealthClubData(config_file)
    raw_data = health_club_data.esh_health_club_data()
    processed_data = health_club_data.insert_or_update_data(raw_data)
    return processed_data

# 电商运营
def ecommerce_operation(config_file):
    ecommerce_operation = EcommerceOperation(config_file)
    raw_data = ecommerce_operation.esh_ecommerce_operation_data()
    processed_data = ecommerce_operation.insert_or_update_data(raw_data)
    return processed_data

# 权限检查
def check_permission(config_file):
    check_permission = checkPermission(config_file)
    # raw_data = check_permission.get_roleManager_id_and_name()
    raw_data = check_permission.get_roleManager_id_and_name()
    processed_data = check_permission.transform_data(raw_data)
    return processed_data


if __name__ == "__main__":
    config_file = "config.ini"

    # 01.平台运营指标
    # platform_index_report_result = platform_index_report(config_file)
    # print("Platform Index Report Result:")
    # print(platform_index_report_result)

    # 02.客服工单
    # customer_service_result = customer_service(config_file)
    # print("Customer Service Result:")
    # print(customer_service_result)

    # 03.物业费收缴情况
    # payment_manager_result = payment_manager(config_file)
    # print("Payment Manager Result:")
    # print(payment_manager_result)

    # 04.智慧工单
    # wisdom_ticket_result = wisdom_ticket(config_file)
    # print("Wisdom Ticket Result:")
    # print(wisdom_ticket_result)

    # 5.维修工单
    # maintenance_ticket_result = maintenance_ticket(config_file)
    # print("\nMaintenance Ticket Result:")
    # print(maintenance_ticket_result)

    # 6.采购库存
    # procurement_inventory_result = procurement_inventory(config_file)
    # print("\nFacility Equipment Result:")
    # print(procurement_inventory_result)

    # 7.设备设施
    # facility_equipment_result = facility_equipment(config_file)
    # print("\nFacility Equipment Result:")
    # print(facility_equipment_result)

    # 8.合同管理
    # contract_management = contract_management(config_file)
    # print("\nContract Management Result:")
    # print(contract_management)

    # 9.巡航检查
    # perform_inspection = perform_inspection(config_file)
    # print("\nPerform Inspection Result:")
    # print(perform_inspection)

    # 10.健身房数据
    # health_club_data = health_club_data(config_file)
    # print("\nHealth Club Data Result:")
    # print(health_club_data)

    # 11.电商运营
    # ecommerce_operation = ecommerce_operation(config_file)
    # print("\nEcommerce Operation Result:")
    # print(ecommerce_operation)

    # 12.计算收益
    # calculate_revenue = calculate_revenue(config_file)
    # print("\nCalculate Revenue Result:")
    # print(calculate_revenue)

    # 13.权限检查
    check_permission = check_permission(config_file)
    print("\nCheck Permission Result:")
    print(check_permission)



