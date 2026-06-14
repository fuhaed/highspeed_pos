import frappe
import json

def run():
    variants = frappe.db.get_all("Item",
        filters=[["variant_of", "=", "15504454-50000005430-"]],
        fields=["name", "item_code", "item_name"]
    )
    print("VARIANTS FOR 15504454-50000005430-:")
    for v in variants:
        v_attrs = frappe.db.get_all("Item Variant Attribute",
            filters=[["parent", "=", v.name]],
            fields=["attribute", "attribute_value"]
        )
        attrs_dict = {a.attribute: a.attribute_value for a in v_attrs}
        print(f"Code: {v.item_code}, Name: {v.item_name}, Attrs: {attrs_dict}")
