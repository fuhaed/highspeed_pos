import frappe

meta = frappe.get_meta('POS Profile')
for f in meta.fields:
    if not f.fieldname.startswith('hspos_') and not f.fieldname.startswith('custom_') and f.fieldname != 'highspeed_pos_payments' and f.fieldname != 'use_customer_credit' and f.fieldname != 'use_cashback' and f.fieldname != 'pose_use_limit_search':
        print(f"{f.fieldname} ({f.fieldtype})")
