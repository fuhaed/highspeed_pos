import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def create_schema():
    # 1. Create DocType POS Table if it doesn't exist
    if not frappe.db.exists("DocType", "POS Table"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "POS Table",
            "module": "highspeed_pos",
            "custom": 1,
            "autoname": "field:table_name",
            "fields": [
                {
                    "fieldname": "table_name",
                    "label": "Table Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1
                },
                {
                    "fieldname": "pos_profile",
                    "label": "POS Profile",
                    "fieldtype": "Link",
                    "options": "POS Profile",
                    "in_list_view": 1
                },
                {
                    "fieldname": "status",
                    "label": "Status",
                    "fieldtype": "Select",
                    "options": "Available\nOccupied\nReserved",
                    "default": "Available",
                    "in_list_view": 1
                },
                {
                    "fieldname": "capacity",
                    "label": "Capacity",
                    "fieldtype": "Int",
                    "default": 4,
                    "in_list_view": 1
                }
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1
                },
                {
                    "role": "All",
                    "read": 1
                }
            ]
        })
        doc.insert()
        frappe.db.commit()
        print("SUCCESS: Created DocType POS Table")
    else:
        print("INFO: DocType POS Table already exists")
        # Ensure pos_profile field exists
        doc = frappe.get_doc("DocType", "POS Table")
        if not any(f.fieldname == "pos_profile" for f in doc.fields):
            doc.append("fields", {
                "fieldname": "pos_profile",
                "label": "POS Profile",
                "fieldtype": "Link",
                "options": "POS Profile",
                "in_list_view": 1
            })
            doc.save()
            frappe.db.commit()
            print("SUCCESS: Added pos_profile field to existing POS Table DocType")

    # 2. Add custom field hspos_enable_dining_tables to POS Profile if it doesn't exist
    if not frappe.db.exists("Custom Field", "POS Profile-hspos_enable_dining_tables"):
        create_custom_field("POS Profile", dict(
            fieldname="hspos_enable_dining_tables",
            label="Enable Dining Tables",
            fieldtype="Check",
            default="1",
            insert_after="hspos_allow_delivery"
        ))
        frappe.db.commit()
        print("SUCCESS: Added custom field hspos_enable_dining_tables to POS Profile")
    else:
        print("INFO: Custom field hspos_enable_dining_tables on POS Profile already exists")

    # Add custom field hspos_hide_item_search to POS Profile if it doesn't exist
    if not frappe.db.exists("Custom Field", "POS Profile-hspos_hide_item_search"):
        create_custom_field("POS Profile", dict(
            fieldname="hspos_hide_item_search",
            label="Hide Item Search",
            fieldtype="Check",
            default="0",
            insert_after="hspos_enable_dining_tables"
        ))
        frappe.db.commit()
        print("SUCCESS: Added custom field hspos_hide_item_search to POS Profile")
    else:
        print("INFO: Custom field hspos_hide_item_search on POS Profile already exists")

    # 3. Add custom field hspos_table to Sales Invoice if it doesn't exist
    if not frappe.db.exists("Custom Field", "Sales Invoice-hspos_table"):
        create_custom_field("Sales Invoice", dict(
            fieldname="hspos_table",
            label="Table",
            fieldtype="Link",
            options="POS Table",
            insert_after="hspos_order_no"
        ))
        frappe.db.commit()
        print("SUCCESS: Added custom field hspos_table to Sales Invoice")
    else:
        print("INFO: Custom field hspos_table on Sales Invoice already exists")

    # 4. Create sample tables (Table 1 to Table 12) if none exist
    if not frappe.get_all("POS Table", limit=1):
        for i in range(1, 13):
            frappe.get_doc({
                "doctype": "POS Table",
                "table_name": f"Table {i}",
                "status": "Available",
                "capacity": 4
            }).insert()
        frappe.db.commit()
        print("SUCCESS: Inserted sample POS Tables")
    else:
        print("INFO: POS Tables already populated")

    # 5. Associate existing tables with POS Profile 'الافق' if pos_profile is not set
    default_profile = "الافق"
    if not frappe.db.exists("POS Profile", default_profile):
        profiles = frappe.get_all("POS Profile", limit=1)
        if profiles:
            default_profile = profiles[0].name
        else:
            default_profile = None

    if default_profile:
        frappe.db.sql(f"""
            UPDATE `tabPOS Table` 
            SET pos_profile = %s 
            WHERE pos_profile IS NULL OR pos_profile = ''
        """, (default_profile,))
        frappe.db.commit()
        print(f"SUCCESS: Associated unlinked POS Tables with POS Profile '{default_profile}'")

if __name__ == "__main__":
    create_schema()
