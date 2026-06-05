import frappe

fieldname = "hspos_scale_barcode_type"
name = f"POS Profile-{fieldname}"

print("Creating Scale Barcode Type custom field...")
if frappe.db.exists("Custom Field", name):
    doc = frappe.get_doc("Custom Field", name)
else:
    doc = frappe.new_doc("Custom Field")
    doc.dt = "POS Profile"
    doc.fieldname = fieldname

doc.label = "Scale Barcode Type"
doc.fieldtype = "Select"
doc.options = "Weight-Based\nPrice-Based"
doc.default = "Weight-Based"
doc.insert_after = "hspos_scale_barcode_start"
doc.save()

# Update following field sequence to keep strictly linear layout
if frappe.db.exists("Custom Field", "POS Profile-hspos_search_limit"):
    print("Updating hspos_search_limit sequence...")
    limit_field = frappe.get_doc("Custom Field", "POS Profile-hspos_search_limit")
    limit_field.insert_after = "hspos_scale_barcode_type"
    limit_field.save()

frappe.db.commit()
print("Custom fields successfully configured!")
