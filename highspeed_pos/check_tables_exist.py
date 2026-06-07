import frappe

doctypes_to_check = ["Restaurant Table", "POS Table", "Table", "Dining Table", "Restaurant Dining Table"]
for dt in doctypes_to_check:
    exists = frappe.db.exists("DocType", dt)
    print(f"{dt} exists: {exists}")
