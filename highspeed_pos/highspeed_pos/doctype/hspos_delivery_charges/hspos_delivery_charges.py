# Copyright (c) 2022, HIGH SPEED IT and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from frappe.model.document import Document


class HSPOSDeliveryCharges(Document):
    def validate(self):
        if not self.default_rate or self.default_rate <= 0:
            frappe.throw(_("Default Rate is required"))
        self.validate_profiles()

    def validate_profiles(self):
        profiles = []
        for row in self.profiles:
            if row.pos_profile not in profiles:
                profiles.append(row.pos_profile)
            else:
                frappe.throw("Duplicate POS Profile in HSPOS Delivery Charges")
        self.set_profiles_list(profiles)

    def set_profiles_list(self, profiles_list):
        if len(profiles_list) > 0:
            self.profiles_list = json.dumps(profiles_list)
        else:
            self.profiles_list = None


def get_applicable_hspos_delivery_charges(
    company,
    pos_profile=None,
    customer=None,
    address=None,
    hspos_delivery_charges=None,
    restrict=False,
):
    charges = []
    address_list = []
    hspos_delivery_charges_list = []
    if address:
        address_list.append(address)
    if customer:
        address_list.extend(
            frappe.get_all(
                "Dynamic Link",
                filters={
                    "link_doctype": "Customer",
                    "link_name": customer,
                    "parentfield": "links",
                    "parenttype": "Address",
                },
                pluck="parent",
            )
        )
    for address in address_list:
        address_charges = frappe.get_cached_value(
            "Address", address, "hspos_hspos_delivery_charges"
        )
        if address_charges:
            hspos_delivery_charges_list.append(address_charges)

    hspos_delivery_charges_filters = {"disabled": 0, "company": company}
    if hspos_delivery_charges:
        hspos_delivery_charges_list.append(hspos_delivery_charges)

    if len(hspos_delivery_charges_list) > 0:
        hspos_delivery_charges_filters["name"] = ["in", hspos_delivery_charges_list]
    if restrict:
        hspos_delivery_charges_filters["profiles_list"] = ["not in", ["", None]]

    hspos_delivery_charges_items = frappe.get_all(
        "HSPOS Delivery Charges",
        filters=hspos_delivery_charges_filters,
        fields=["*"],
    )
    hspos_delivery_charges_list = [i.name for i in hspos_delivery_charges_items]

    delivery_profiels_filters = {"parent": ("in", hspos_delivery_charges_list)}
    if pos_profile:
        delivery_profiels_filters["pos_profile"] = pos_profile
    delivery_profiels = frappe.get_all(
        "HSPOS Delivery Charges POS Profile",
        filters=delivery_profiels_filters,
        fields=["*"],
    )
    for charge in hspos_delivery_charges_items:
        profile = next((i for i in delivery_profiels if i.parent == charge.name), None)
        if profile:
            charge.rate = profile.rate
            charges.append(charge)
        else:
            if not restrict:
                if not charge.profiles_list:
                    charge.rate = charge.default_rate
                    charges.append(charge)

    return charges
