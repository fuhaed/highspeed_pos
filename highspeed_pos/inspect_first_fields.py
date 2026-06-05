import frappe

meta = frappe.get_meta('POS Profile')
in_tab = False
count = 0
for f in meta.fields:
    if f.fieldname == 'hspos_highspeed_pos_settings':
        in_tab = True
    if in_tab and count < 30:
        print(f"{f.fieldname} ({f.fieldtype}) -> hidden: {f.hidden}, label: {f.label}")
        count += 1
