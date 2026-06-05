import frappe

meta = frappe.get_meta('POS Profile')
in_tab = False
for f in meta.fields:
    if f.fieldname == 'hspos_highspeed_pos_settings':
        in_tab = True
    if in_tab:
        print(f"{f.fieldname} ({f.fieldtype}) -> hidden: {f.hidden}, read_only: {f.read_only}, label: {f.label}")
