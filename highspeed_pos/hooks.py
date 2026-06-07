# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "highspeed_pos"
app_title = "HIGHSPEED POS"
app_publisher = "HIGH SPEED IT"
app_description = "HIGHSPEED POS"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@highspeed.com"
app_license = "GPLv3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/highspeed_pos/css/highspeed_pos.css"
# app_include_js = "/assets/highspeed_pos/js/highspeed_pos.js"
app_include_js = [
    "highspeed_pos.bundle.js",
]
app_include_css = [
    "highspeed_pos.bundle.css",
]

# include js, css files in header of web template
# web_include_css = "/assets/highspeed_pos/css/highspeed_pos.css"
# web_include_js = "/assets/highspeed_pos/js/highspeed_pos.js"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "POS Profile": "highspeed_pos/api/pos_profile.js",
    "Sales Invoice": "highspeed_pos/api/invoice.js",
    "Company": "highspeed_pos/api/company.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "highspeed_pos.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "highspeed_pos.install.before_install"
# after_install = "highspeed_pos.install.after_install"
# before_uninstall = "highspeed_pos.uninstall.before_uninstall"
after_uninstall = "highspeed_pos.uninstall.after_uninstall"
before_migrate = "highspeed_pos.highspeed_pos.api.hsposapp.before_migrate"
after_migrate = "highspeed_pos.highspeed_pos.api.hsposapp.after_migrate"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "highspeed_pos.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Invoice": {
        "validate": "highspeed_pos.highspeed_pos.api.invoice.validate",
        "before_submit": "highspeed_pos.highspeed_pos.api.invoice.before_submit",
        "before_cancel": "highspeed_pos.highspeed_pos.api.invoice.before_cancel",
    },
    "Customer": {
        "validate": "highspeed_pos.highspeed_pos.api.customer.validate",
        "after_insert": "highspeed_pos.highspeed_pos.api.customer.after_insert",
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "highspeed_pos.highspeed_pos.api.hsposapp.reset_daily_order_numbers"
    ]
}

# Testing
# -------

# before_tests = "highspeed_pos.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "highspeed_pos.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "highspeed_pos.task.get_dashboard_data"
# }

# override_doctype_class = {
# "doctype": "method",
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                (
                    "Sales Invoice-hspos_hspos_opening_shift",
                    "Item Barcode-hspos_uom",
                    "Batch-hspos_batch_price",
                    "Sales Invoice-hspos_is_printed",
                    "Customer-hspos_discount",
                    "Sales Invoice-hspos_offers",
                    "Sales Invoice-hspos_coupons",
                    "Sales Invoice Item-hspos_offers",
                    "Sales Invoice Item-hspos_row_id",
                    "Sales Invoice Item-hspos_offer_applied",
                    "Sales Invoice Item-hspos_is_offer",
                    "Sales Invoice Item-hspos_is_replace",
                    "Sales Invoice-hspos_additional_notes_section",
                    "Sales Invoice-hspos_notes",
                    "Sales Invoice-hspos_column_break_111",
                    "Sales Invoice-hspos_delivery_date",
                    "Sales Invoice Item-hspos_notes",
                    "Sales Invoice Item-hspos_delivery_date",
                    "Sales Order-hspos_additional_notes_section",
                    "Sales Order-hspos_notes",
                    "Sales Order Item-hspos_notes",
                    "Customer-hspos_hspos_referral_code",
                    "Company-hspos_referral_section",
                    "Company-hspos_auto_referral",
                    "Company-hspos_column_break_22",
                    "Company-hspos_customer_offer",
                    "Company-hspos_primary_offer",
                    "Company-hspos_referral_campaign",
                    "Customer-hspos_referral_company",
                    "Customer-hspos_referral_section",
                    "Customer-hspos_birthday",
                    "Sales Order-hspos_offers",
                    "Sales Order-hspos_coupons",
                    "Sales Order Item-hspos_row_id",
                    "Sales Invoice-hspos_order_type",
                    "Address-hspos_hspos_delivery_charges",
                    "Sales Invoice-hspos_hspos_delivery_charges",
                    "Sales Invoice-hspos_hspos_delivery_charges_rate",
                    "Sales Invoice-hspos_order_no",
                    "Item-hspos_add_ons_section",
                    "Item-hspos_add_ons",
                    "Sales Invoice Item-hspos_is_addon",
                    "Sales Invoice Item-hspos_parent_item_row",
                    "Sales Invoice Item-hspos_addon_name",
                    "Sales Invoice Item-hspos_addons_desc",
                    "Sales Invoice-hspos_kitchen_status",
                ),
            ]
        ],
    },
    {
        "doctype": "Custom Field",
        "filters": [
            ["dt", "=", "POS Profile"]
        ]
    },
    {
        "doctype": "Print Format",
        "filters": [
            ["name", "in", ("POS ZATCA PRINT", "HSPOS Closing Shift Print")]
        ]
    },
    {
        "doctype": "Property Setter",
        "filters": [["name", "in", ("Sales Invoice-hspos_hspos_opening_shift-no_copy", "HSPOS Closing Shift-main-default_print_format")]],
    },
    {
        "doctype": "Number Card",
        "filters": [["module", "=", "highspeed_pos"]]
    },
    {
        "doctype": "Dashboard Chart",
        "filters": [["module", "=", "highspeed_pos"]]
    },
    {
        "doctype": "Workspace",
        "filters": [["name", "=", "HIGHSPEED POS"]]
    }
]
