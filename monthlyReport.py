from wisdom_ticket import WisdomTicket
from maintenance_ticket import MaintenanceTicket
from facility_equipment import FacilityEquipment
from procurement_inventory import ProcurementInventory
from platform_index_report import PlatformIndexReport
from payment_manager import PaymentManager

def wisdom_ticket(config_file):
    wisdom_ticket = WisdomTicket(config_file)
    data = wisdom_ticket.fetch_data()

    result = []
    for community in data:
        department_name = community["departmentName"]
        for item in community["data"]:
            if item["departmentName"] == "合计":
                result.append({
                    "area": community["area"],
                    "community": community["community"],
                    "departmentName": department_name,
                    "sumCompleteTimeQuota": item["sumCompleteTimeQuota"],
                    "sumTimeActual": item["sumTimeActual"],
                    "sumTimeFixedWorkOrder": item["sumTimeFixedWorkOrder"],
                    "averageCompleteTimeQuota": item["averageCompleteTimeQuota"],
                    "completeRate": item["completeRate"],
                    "standardRate": item["standardRate"],
                    "inspectRate": item["inspectRate"]
                })

    return result
#1、平台运营指标
def platform_index_report(config_file):
    platform_index_report = PlatformIndexReport(config_file)
    raw_data = platform_index_report.fetch_data()
    processed_data = platform_index_report.process_data(raw_data)
    return processed_data

#2、物业费收缴情况
def payment_manager(config_file):
    payment_manager = PaymentManager(config_file)
    raw_data = payment_manager.get_fee_count_num()
    # processed_data = payment_manager.process_data(raw_data)
    return raw_data

def maintenance_ticket(config_file):
    maintenance_ticket = MaintenanceTicket(config_file)
    raw_data = maintenance_ticket.fetch_data()
    processed_data = maintenance_ticket.process_data(raw_data)
    return processed_data

def facility_equipment(config_file):
    facility_equipment = FacilityEquipment(config_file)
    raw_data = facility_equipment.fetch_data()
    processed_data = facility_equipment.process_facility_equipment_data(raw_data)
    return processed_data

# 7.采购库存
def procurement_inventory(config_file):
    procurement_inventory = ProcurementInventory(config_file)
    raw_data = procurement_inventory.inventory()
    # raw_data = procurement_inventory.fetch_data()
    # processed_data = procurement_inventory.process_data(raw_data)
    return raw_data

if __name__ == "__main__":
    config_file = "config.ini"

    # platform_index_report_result = platform_index_report(config_file)
    # print("Platform Index Report Result:")
    # print(platform_index_report_result)

    # payment_manager_result = payment_manager(config_file)
    # print("Payment Manager Result:")
    # print(payment_manager_result)

    # wisdom_ticket_result = wisdom_ticket(config_file)
    # print("Wisdom Ticket Result:")
    # print(wisdom_ticket_result)
    #
    # maintenance_ticket_result = maintenance_ticket(config_file)
    # print("\nMaintenance Ticket Result:")
    # print(maintenance_ticket_result)
    #
    # facility_equipment_result = facility_equipment(config_file)
    # print("\nFacility Equipment Result:")
    # print(facility_equipment_result)
    #
    procurement_inventory_result = procurement_inventory(config_file)
    print("\nFacility Equipment Result:")
    print(procurement_inventory_result)