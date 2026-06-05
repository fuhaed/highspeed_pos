import frappe

cfs = frappe.db.get_all('Custom Field', filters={'dt': 'POS Profile'}, fields=['fieldname', 'insert_after'])
cf_map = {f['fieldname']: f['insert_after'] for f in cfs}

current = "hspos_highspeed_pos_settings"
for i in range(70):
    # Find the field that inserts after current
    next_fields = []
    for fieldname, insert_after in cf_map.items():
        if insert_after == current:
            next_fields.append(fieldname)
    if not next_fields:
        print(f"--- CHAIN BROKEN after {current} ---")
        break
    for nf in next_fields:
        print(f"{current} -> {nf}")
    current = next_fields[0]
