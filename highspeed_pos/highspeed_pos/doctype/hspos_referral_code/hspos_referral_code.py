# Copyright (c) 2021, HIGH SPEED IT and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import strip


class HSPOSReferralCode(Document):
    def autoname(self):
        if not self.referral_name:
            self.referral_name = (
                strip(self.customer) + "-" + frappe.generate_hash()[:5].upper()
            )
            self.name = self.referral_name
        else:
            self.referral_name = strip(self.referral_name)
            self.name = self.referral_name

        if not self.hspos_referral_code:
            self.hspos_referral_code = frappe.generate_hash()[:10].upper()

    def validate(self):
        pass


def create_hspos_referral_code(
    company, customer, customer_offer, primary_offer=None, campaign=None
):
    doc = frappe.new_doc("HSPOS Referral Code")
    doc.company = company
    doc.customer = customer
    doc.customer_offer = customer_offer
    doc.primary_offer = primary_offer
    doc.campaign = campaign
    doc.save(ignore_permissions=True)
    return doc
