# Copyright (c) 2021, HIGH SPEED IT and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _
from highspeed_pos.highspeed_pos.doctype.hspos_referral_code.hspos_referral_code import (
    create_hspos_referral_code,
)

def after_insert(doc, method):
    create_customer_hspos_referral_code(doc)
    create_gift_coupon(doc)

def validate(doc, method):
    validate_hspos_referral_code(doc)

def create_customer_hspos_referral_code(doc):
    # Check if field exists before using it
    if not hasattr(doc, 'hspos_referral_company'):
        return
    
    if doc.hspos_referral_company:
        company = frappe.get_cached_doc("Company", doc.hspos_referral_company)
        if not company.hspos_auto_referral:
            return
        create_hspos_referral_code(
            doc.hspos_referral_company,
            doc.name,
            company.hspos_customer_offer,
            company.hspos_primary_offer,
            company.hspos_referral_campaign,
        )

def create_gift_coupon(doc):
    # Check if field exists before using it
    if not hasattr(doc, 'hspos_hspos_referral_code'):
        return
    
    if doc.hspos_hspos_referral_code:
        coupon = frappe.new_doc("HSPOS Coupon")
        coupon.customer = doc.name
        coupon.hspos_referral_code = doc.hspos_hspos_referral_code
        coupon.create_coupon_from_referral()

def validate_hspos_referral_code(doc):
    # Check if field exists before using it
    if not hasattr(doc, 'hspos_hspos_referral_code'):
        return
    
    hspos_referral_code = doc.hspos_hspos_referral_code
    exist = None
    if hspos_referral_code:
        exist = frappe.db.exists("HSPOS Referral Code", hspos_referral_code)
        if not exist:
            exist = frappe.db.exists("HSPOS Referral Code", {"hspos_referral_code": hspos_referral_code})
        if not exist:
            frappe.throw(_("This HSPOS Referral Code {0} not exists").format(hspos_referral_code))

@frappe.whitelist()
def get_customer_balance(customer):
    if not customer:
        return {"balance": 0, "customer_name": None}
    try:
        customer_doc = frappe.get_doc("Customer", customer)
        customer_name = customer_doc.customer_name
        # Fetch outstanding balance from GL Entries
        balance = frappe.db.sql("""
            SELECT SUM(debit - credit) AS balance
            FROM `tabGL Entry`
            WHERE party_type = 'Customer' AND party = %s AND docstatus = 1
        """, (customer,), as_dict=True)
        return {
            "balance": flt(balance[0].get("balance", 0)) if balance else 0,
            "customer_name": customer_name
        }
    except Exception as e:
        frappe.log_error(f"Error fetching customer balance: {e}")
        return {"balance": 0, "customer_name": None}