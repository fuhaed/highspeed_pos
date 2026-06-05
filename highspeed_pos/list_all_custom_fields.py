import frappe
import json

fields = frappe.db.get_all('Custom Field', filters={'dt': 'POS Profile'}, fields=['fieldname', 'label', 'fieldtype', 'insert_after', 'hidden'])
for f in fields:
    print(f"{f['fieldname']} ({f['fieldtype']}) -> insert_after: {f['insert_after']}, hidden: {f['hidden']}, label: {f['label']}")
