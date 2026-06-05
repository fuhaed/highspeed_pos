import frappe
import json

cfs = frappe.db.get_all('Custom Field', filters={'dt': 'POS Profile'}, fields=['fieldname', 'label', 'fieldtype', 'insert_after'])
# Sort fields by their insert_after or dependency chain to show their exact current layout order
for f in cfs:
    print(f"{f['fieldname']} ({f['fieldtype']}) -> insert_after: {f['insert_after']} (label: {f['label']})")
