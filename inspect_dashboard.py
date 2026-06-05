import frappe
import json

meta_card = frappe.get_meta('Number Card')
meta_chart = frappe.get_meta('Dashboard Chart')

card_fields = [{'fieldname': df.fieldname, 'label': df.label, 'fieldtype': df.fieldtype} for df in meta_card.fields]
chart_fields = [{'fieldname': df.fieldname, 'label': df.label, 'fieldtype': df.fieldtype} for df in meta_chart.fields]

output = {
    'Number Card Fields': card_fields,
    'Dashboard Chart Fields': chart_fields
}

with open('/home/frappe/frappe-bench/apps/highspeed_pos/fields_output.txt', 'w') as f:
    f.write(json.dumps(output, indent=2))

def run():
    pass
