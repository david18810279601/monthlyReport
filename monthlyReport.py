from wisdom_ticket import WisdomTicket
from customer_service import CustomerService
from maintenance_ticket import MaintenanceTicket
from facility_equipment import FacilityEquipment
from procurement_inventory import ProcurementInventory
from platform_index_report import PlatformIndexReport
from payment_manager import PaymentManager
from contract_management import ContractManagement


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

def maintenance_ticket(config_file):
    maintenance_ticket = MaintenanceTicket(config_file)
    raw_data = maintenance_ticket.fetch_data()
    processed_data = maintenance_ticket.process_data(raw_data)
    return processed_data

#5、智慧工单
def wisdom_ticket(config_file):
    wisdom_ticket = WisdomTicket(config_file)
    raw_data = wisdom_ticket.fetch_data()
    processed_data = wisdom_ticket.process_data(raw_data)
    return processed_data

# 7.设备设施
def facility_equipment(config_file):
    facility_equipment = FacilityEquipment(config_file)
    raw_data = facility_equipment.fetch_data()
    processed_data = facility_equipment.process_facility_equipment_data(raw_data)
    return processed_data

# 6.采购库存
def procurement_inventory(config_file):
    procurement_inventory = ProcurementInventory(config_file)
    raw_data = procurement_inventory.process_data()
    # raw_data = procurement_inventory.fetch_data()
    # processed_data = procurement_inventory.process_data(raw_data)
    return raw_data

# 8.合同管理
def contract_management(config_file):
    contract_management = ContractManagement(config_file)
    raw_data = contract_management.get_contractManagement_data()
    return raw_data


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
