import frappe
import json

# Enable developer mode temporarily in frappe.conf to write schema to app files
frappe.conf.developer_mode = 1

# 1. Create or update Child DocType "HSPOS Item Addon"
name = "HSPOS Item Addon"
print(f"Creating/updating child DocType '{name}'...")
if frappe.db.exists("DocType", name):
    doc = frappe.get_doc("DocType", name)
else:
    doc = frappe.new_doc("DocType")
    doc.name = name

doc.module = "highspeed_pos"
doc.custom = 0
doc.istable = 1
doc.editable_grid = 1
doc.quick_entry = 1

doc.set("fields", [])
doc.append("fields", {
    "fieldname": "add_on_name",
    "fieldtype": "Data",
    "label": "Add-on Name",
    "reqd": 1,
    "in_list_view": 1
})
doc.append("fields", {
    "fieldname": "add_on_item",
    "fieldtype": "Link",
    "label": "Add-on Item",
    "options": "Item",
    "in_list_view": 1
})
doc.append("fields", {
    "fieldname": "extra_price",
    "fieldtype": "Currency",
    "label": "Extra Price",
    "default": 0.0,
    "in_list_view": 1
})

doc.save(ignore_permissions=True)
frappe.db.commit()

# 2. Add custom fields:
custom_fields = {
    "Item": [
        {
            "fieldname": "hspos_add_ons_section",
            "fieldtype": "Section Break",
            "label": "HIGHSPEED POS Add-ons",
            "insert_after": "image"
        },
        {
            "fieldname": "hspos_add_ons",
            "fieldtype": "Table",
            "label": "Add-ons Table",
            "options": "HSPOS Item Addon",
            "insert_after": "hspos_add_ons_section"
        }
    ],
    "Sales Invoice Item": [
        {
            "fieldname": "hspos_is_addon",
            "fieldtype": "Check",
            "label": "Is HSPOS Addon",
            "insert_after": "hspos_notes",
            "default": 0
        },
        {
            "fieldname": "hspos_parent_item_row",
            "fieldtype": "Data",
            "label": "HSPOS Parent Item Row ID",
            "insert_after": "hspos_is_addon",
            "read_only": 1
        },
        {
            "fieldname": "hspos_addon_name",
            "fieldtype": "Data",
            "label": "HSPOS Addon Name",
            "insert_after": "hspos_parent_item_row",
            "read_only": 1
        },
        {
            "fieldname": "hspos_addons_desc",
            "fieldtype": "Small Text",
            "label": "HSPOS Addons Description",
            "insert_after": "hspos_addon_name",
            "read_only": 1
        }
    ]
}

print("Configuring custom fields...")
for doctype, fields in custom_fields.items():
    for f in fields:
        fname = f"{doctype}-{f['fieldname']}"
        if frappe.db.exists("Custom Field", fname):
            cf = frappe.get_doc("Custom Field", fname)
        else:
            cf = frappe.new_doc("Custom Field")
            cf.dt = doctype
            cf.fieldname = f["fieldname"]
        
        cf.fieldtype = f["fieldtype"]
        cf.label = f["label"]
        cf.insert_after = f["insert_after"]
        if "options" in f:
            cf.options = f["options"]
        if "default" in f:
            cf.default = f["default"]
        if "read_only" in f:
            cf.read_only = f["read_only"]
            
        cf.save(ignore_permissions=True)

frappe.db.commit()
print("Setup completed successfully!")
