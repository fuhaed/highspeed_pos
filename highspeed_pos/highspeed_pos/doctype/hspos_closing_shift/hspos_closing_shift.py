# -*- coding: utf-8 -*-
# Copyright (c) 2020, HIGH SPEED IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class HSPOSClosingShift(Document):
    def validate(self):
        user = frappe.get_all(
            "HSPOS Closing Shift",
            filters={
                "user": self.user,
                "docstatus": 1,
                "hspos_opening_shift": self.hspos_opening_shift,
                "name": ["!=", self.name],
            },
        )

        if user:
            frappe.throw(
                _(
                    "HSPOS Closing Shift {} against {} between selected period".format(
                        frappe.bold("already exists"), frappe.bold(self.user)
                    )
                ),
                title=_("Invalid Period"),
            )

        if (
            frappe.db.get_value("HSPOS Opening Shift", self.hspos_opening_shift, "status")
            != "Open"
        ):
            frappe.throw(
                _("Selected HSPOS Opening Shift should be open."),
                title=_("Invalid Opening Entry"),
            )
        self.update_payment_reconciliation()

    def update_payment_reconciliation(self):
        # update the difference values in Payment Reconciliation child table
        # get default precision for site
        precision = (
            frappe.get_cached_value("System Settings", None, "currency_precision") or 3
        )
        for d in self.payment_reconciliation:
            d.difference = +flt(d.closing_amount, precision) - flt(
                d.expected_amount, precision
            )

    def on_submit(self):
        opening_entry = frappe.get_doc("HSPOS Opening Shift", self.hspos_opening_shift)
        opening_entry.hspos_closing_shift = self.name
        opening_entry.set_status()
        self.delete_draft_invoices()
        opening_entry.save()

    def delete_draft_invoices(self):
        if frappe.get_value("POS Profile", self.pos_profile, "hspos_allow_delete"):
            data = frappe.db.sql(
                """
                select
                    name
                from
                    `tabSales Invoice`
                where
                    docstatus = 0 and hspos_is_printed = 0 and hspos_hspos_opening_shift = %s
                """,
                (self.hspos_opening_shift),
                as_dict=1,
            )

            for invoice in data:
                frappe.delete_doc("Sales Invoice", invoice.name, force=1)

    @frappe.whitelist()
    def get_payment_reconciliation_details(self):
        currency = frappe.get_cached_value("Company", self.company, "default_currency")
        return frappe.render_template(
            "highspeed_pos/highspeed_pos/doctype/hspos_closing_shift/closing_shift_details.html",
            {"data": self, "currency": currency},
        )

    def get_print_stats(self):
        opening_shift_doc = frappe.get_doc("HSPOS Opening Shift", self.hspos_opening_shift)
        temp_cs = make_closing_shift_from_opening(opening_shift_doc, submit_invoices=False)
        return {
            "product_sales": temp_cs.get("product_sales"),
            "addon_sales": temp_cs.get("addon_sales"),
            "average_ticket": temp_cs.get("average_ticket"),
            "hspos_zatca_stats": temp_cs.get("hspos_zatca_stats")
        }


@frappe.whitelist()
def get_cashiers(doctype, txt, searchfield, start, page_len, filters):
    cashiers_list = frappe.get_all("POS Profile User", filters=filters, fields=["user"])
    result = []
    for cashier in cashiers_list:
        user_email = frappe.get_value("User", cashier.user, "email")
        if user_email:
            # Return list of tuples in format (value, label) where value is user ID and label shows both ID and email
            result.append([cashier.user, f"{cashier.user} ({user_email})"])
    return result


@frappe.whitelist()
def get_pos_invoices(hspos_opening_shift, submit_invoices=True):
    if frappe.parse_json(submit_invoices):
        submit_printed_invoices(hspos_opening_shift)
    data = frappe.db.sql(
        """
	select
		name
	from
		`tabSales Invoice`
	where
		docstatus = 1 and hspos_hspos_opening_shift = %s
	""",
        (hspos_opening_shift),
        as_dict=1,
    )

    data = [frappe.get_doc("Sales Invoice", d.name).as_dict() for d in data]

    return data


@frappe.whitelist()
def get_payments_entries(hspos_opening_shift):
    return frappe.get_all(
        "Payment Entry",
        filters={
            "docstatus": 1,
            "reference_no": hspos_opening_shift,
            "payment_type": "Receive",
        },
        fields=[
            "name",
            "mode_of_payment",
            "paid_amount",
            "reference_no",
            "posting_date",
            "party",
        ],
    )


@frappe.whitelist()
def make_closing_shift_from_opening(opening_shift, submit_invoices=True):
    opening_shift = json.loads(opening_shift) if isinstance(opening_shift, str) else opening_shift
    should_submit = frappe.parse_json(submit_invoices)
    if should_submit:
        submit_printed_invoices(opening_shift.get("name"))
    closing_shift = frappe.new_doc("HSPOS Closing Shift")
    closing_shift.hspos_opening_shift = opening_shift.get("name")
    closing_shift.period_start_date = opening_shift.get("period_start_date")
    closing_shift.period_end_date = frappe.utils.get_datetime()
    closing_shift.pos_profile = opening_shift.get("pos_profile")
    closing_shift.user = opening_shift.get("user")
    closing_shift.company = opening_shift.get("company")
    closing_shift.grand_total = 0
    closing_shift.net_total = 0
    closing_shift.total_quantity = 0

    invoices = get_pos_invoices(opening_shift.get("name"), submit_invoices=should_submit)

    pos_transactions = []
    taxes = []
    payments = []
    pos_payments_table = []
    for detail in opening_shift.get("balance_details"):
        payments.append(
            frappe._dict(
                {
                    "mode_of_payment": detail.get("mode_of_payment"),
                    "opening_amount": detail.get("amount") or 0,
                    "expected_amount": detail.get("amount") or 0,
                }
            )
        )

    for d in invoices:
        pos_transactions.append(
            frappe._dict(
                {
                    "sales_invoice": d.name,
                    "posting_date": d.posting_date,
                    "grand_total": d.grand_total,
                    "customer": d.customer,
                }
            )
        )
        closing_shift.grand_total += flt(d.grand_total)
        closing_shift.net_total += flt(d.net_total)
        closing_shift.total_quantity += flt(d.total_qty)

        for t in d.taxes:
            existing_tax = [
                tx
                for tx in taxes
                if tx.account_head == t.account_head and tx.rate == t.rate
            ]
            if existing_tax:
                existing_tax[0].amount += flt(t.tax_amount)
            else:
                taxes.append(
                    frappe._dict(
                        {
                            "account_head": t.account_head,
                            "rate": t.rate,
                            "amount": t.tax_amount,
                        }
                    )
                )

        for p in d.payments:
            existing_pay = [
                pay for pay in payments if pay.mode_of_payment == p.mode_of_payment
            ]
            if existing_pay:
                cash_mode_of_payment = frappe.get_value(
                    "POS Profile",
                    opening_shift.get("pos_profile"),
                    "hspos_cash_mode_of_payment",
                )
                if not cash_mode_of_payment:
                    cash_mode_of_payment = "Cash"
                if existing_pay[0].mode_of_payment == cash_mode_of_payment:
                    amount = flt(p.amount) - flt(d.get("change_amount") or 0)
                else:
                    amount = flt(p.amount)
                existing_pay[0].expected_amount += flt(amount)
            else:
                payments.append(
                    frappe._dict(
                        {
                            "mode_of_payment": p.mode_of_payment,
                            "opening_amount": 0,
                            "expected_amount": flt(p.amount),
                        }
                    )
                )

    pos_payments = get_payments_entries(opening_shift.get("name"))

    for py in pos_payments:
        pos_payments_table.append(
            frappe._dict(
                {
                    "payment_entry": py.name,
                    "mode_of_payment": py.mode_of_payment,
                    "paid_amount": py.paid_amount,
                    "posting_date": py.posting_date,
                    "customer": py.party,
                }
            )
        )
        existing_pay = [
            pay for pay in payments if pay.mode_of_payment == py.mode_of_payment
        ]
        if existing_pay:
            existing_pay[0].expected_amount += flt(py.paid_amount)
        else:
            payments.append(
                frappe._dict(
                    {
                        "mode_of_payment": py.mode_of_payment,
                        "opening_amount": 0,
                        "expected_amount": py.paid_amount,
                    }
                )
            )

    closing_shift.set("pos_transactions", pos_transactions)
    closing_shift.set("payment_reconciliation", payments)
    closing_shift.set("taxes", taxes)
    closing_shift.set("pos_payments", pos_payments_table)

    # Product Sales & Add-ons aggregation
    product_sales = {}
    addon_sales = {}

    for d in invoices:
        for item in d.get("items") or []:
            qty = flt(item.get("qty") or 0)
            amount = flt(item.get("amount") or 0)
            
            is_addon = bool(item.get("hspos_is_addon") or 0)
            addon_name = item.get("hspos_addon_name") or item.get("item_name")
            
            if is_addon:
                if addon_name not in addon_sales:
                    addon_sales[addon_name] = {"qty": 0.0, "amount": 0.0, "item_code": item.get("item_code")}
                addon_sales[addon_name]["qty"] += qty
                addon_sales[addon_name]["amount"] += amount
            else:
                item_code = item.get("item_code")
                item_name = item.get("item_name") or item_code
                if item_code not in product_sales:
                    product_sales[item_code] = {"item_name": item_name, "qty": 0.0, "amount": 0.0}
                product_sales[item_code]["qty"] += qty
                product_sales[item_code]["amount"] += amount

    closing_shift.set("product_sales", [
        {"item_code": k, "item_name": v["item_name"], "qty": v["qty"], "amount": v["amount"]}
        for k, v in product_sales.items()
    ])
    closing_shift.set("addon_sales", [
        {"addon_name": k, "qty": v["qty"], "amount": v["amount"], "item_code": v["item_code"]}
        for k, v in addon_sales.items()
    ])

    total_invoices = len(pos_transactions)
    avg_ticket = closing_shift.grand_total / total_invoices if total_invoices > 0 else 0
    closing_shift.set("average_ticket", avg_ticket)

    # Fetch ZATCA stats
    zatca_stats = {"reported": 0, "cleared": 0, "rejected": 0, "not_sent": 0}
    try:
        if frappe.db.has_column("Sales Invoice", "custom_zhs_zatca_status"):
            counts = frappe.db.sql("""
                select custom_zhs_zatca_status, count(*) as cnt
                from `tabSales Invoice`
                where hspos_hspos_opening_shift = %s and docstatus = 1
                group by custom_zhs_zatca_status
            """, (opening_shift.get("name"),), as_dict=1)
            for row in counts:
                status = (row.get("custom_zhs_zatca_status") or "").lower()
                cnt = row.get("cnt") or 0
                if "reported" in status:
                    zatca_stats["reported"] += cnt
                elif "cleared" in status:
                    zatca_stats["cleared"] += cnt
                elif "reject" in status:
                    zatca_stats["rejected"] += cnt
                else:
                    zatca_stats["not_sent"] += cnt
    except Exception as e:
        frappe.log_error(f"Error getting ZATCA shift stats: {str(e)}", "POS ZATCA Status Query")
    closing_shift.set("hspos_zatca_stats", zatca_stats)

    return closing_shift


@frappe.whitelist()
def submit_closing_shift(closing_shift):
    closing_shift = json.loads(closing_shift)
    closing_shift_doc = frappe.get_doc(closing_shift)
    closing_shift_doc.flags.ignore_permissions = True
    closing_shift_doc.save()
    closing_shift_doc.submit()
    
    try:
        from highspeed_pos.highspeed_pos.api.hsposapp import log_cashier_action
        log_cashier_action(
            action="Shift Close",
            details=f"Closed POS shift register from closing shift {closing_shift_doc.name}.",
            pos_profile=closing_shift_doc.pos_profile,
            shift=closing_shift_doc.hspos_opening_shift
        )
    except Exception as e:
        frappe.log_error(f"Failed to log cashier shift close: {str(e)}", "HIGHSPEED POS Logger")
        
    return closing_shift_doc.name


def submit_printed_invoices(hspos_opening_shift):
    invoices_list = frappe.get_all(
        "Sales Invoice",
        filters={
            "hspos_hspos_opening_shift": hspos_opening_shift,
            "docstatus": 0,
            "hspos_is_printed": 1,
        },
    )
def submit_printed_invoices(hspos_opening_shift):
    invoices_list = frappe.get_all(
        "Sales Invoice",
        filters={
            "hspos_hspos_opening_shift": hspos_opening_shift,
            "docstatus": 0,
            "hspos_is_printed": 1,
        },
    )
    for invoice in invoices_list:
        invoice_doc = frappe.get_doc("Sales Invoice", invoice.name)
        invoice_doc.submit()
