import frappe
import json

# Set developer_mode to allow creating standard documents
frappe.conf.developer_mode = 1

# Define Number Cards data
number_cards_data = [
    {
        "doctype": "Number Card",
        "name": "HSPOS Total Sales Today",
        "label": "HSPOS Total Sales Today",
        "type": "Document Type",
        "document_type": "Sales Invoice",
        "function": "Sum",
        "aggregate_function_based_on": "grand_total",
        "is_standard": 1,
        "module": "highspeed_pos",
        "color": "#2ecc71",
        "filters_json": json.dumps([
            ["Sales Invoice", "posting_date", "Timespan", "today", False],
            ["Sales Invoice", "docstatus", "=", "1", False]
        ])
    },
    {
        "doctype": "Number Card",
        "name": "HSPOS Total Invoices Today",
        "label": "HSPOS Total Invoices Today",
        "type": "Document Type",
        "document_type": "Sales Invoice",
        "function": "Count",
        "is_standard": 1,
        "module": "highspeed_pos",
        "color": "#3498db",
        "filters_json": json.dumps([
            ["Sales Invoice", "posting_date", "Timespan", "today", False],
            ["Sales Invoice", "docstatus", "=", "1", False]
        ])
    },
    {
        "doctype": "Number Card",
        "name": "HSPOS Average Ticket Today",
        "label": "HSPOS Average Ticket Today",
        "type": "Document Type",
        "document_type": "Sales Invoice",
        "function": "Average",
        "aggregate_function_based_on": "grand_total",
        "is_standard": 1,
        "module": "highspeed_pos",
        "color": "#9b59b6",
        "filters_json": json.dumps([
            ["Sales Invoice", "posting_date", "Timespan", "today", False],
            ["Sales Invoice", "docstatus", "=", "1", False]
        ])
    },
    {
        "doctype": "Number Card",
        "name": "HSPOS Returned Amount Today",
        "label": "HSPOS Returned Amount Today",
        "type": "Document Type",
        "document_type": "Sales Invoice",
        "function": "Sum",
        "aggregate_function_based_on": "grand_total",
        "is_standard": 1,
        "module": "highspeed_pos",
        "color": "#e74c3c",
        "filters_json": json.dumps([
            ["Sales Invoice", "posting_date", "Timespan", "today", False],
            ["Sales Invoice", "docstatus", "=", "1", False],
            ["Sales Invoice", "is_return", "=", "1", False]
        ])
    },
    {
        "doctype": "Number Card",
        "name": "HSPOS Active Shifts",
        "label": "HSPOS Active Shifts",
        "type": "Document Type",
        "document_type": "HSPOS Opening Shift",
        "function": "Count",
        "is_standard": 1,
        "module": "highspeed_pos",
        "color": "#e67e22",
        "filters_json": json.dumps([
            ["HSPOS Opening Shift", "status", "=", "Open", False]
        ])
    }
]

# Define Dashboard Chart data
dashboard_charts_data = [
    {
        "doctype": "Dashboard Chart",
        "name": "HSPOS Daily Sales Trend",
        "chart_name": "HSPOS Daily Sales Trend",
        "chart_type": "Sum",
        "type": "Line",
        "document_type": "Sales Invoice",
        "based_on": "posting_date",
        "value_based_on": "grand_total",
        "aggregate_function_based_on": "Sum",
        "timespan": "Last Year",
        "time_interval": "Daily",
        "timeseries": 1,
        "is_standard": 1,
        "module": "highspeed_pos",
        "color": "#1abc9c",
        "filters_json": json.dumps([
            ["Sales Invoice", "docstatus", "=", "1", False]
        ])
    }
]

print("Deleting old dashboard docs...")
for card in number_cards_data:
    if frappe.db.exists("Number Card", card["name"]):
        frappe.delete_doc("Number Card", card["name"])
        
for chart in dashboard_charts_data:
    if frappe.db.exists("Dashboard Chart", chart["name"]):
        frappe.delete_doc("Dashboard Chart", chart["name"])

print("Creating new dashboard docs...")
for card in number_cards_data:
    doc = frappe.get_doc(card)
    doc.insert()
    print(f"Created Number Card: {doc.name}")

for chart in dashboard_charts_data:
    doc = frappe.get_doc(chart)
    doc.insert()
    print(f"Created Dashboard Chart: {doc.name}")

# Update Workspace
print("Updating Workspace HIGHSPEED POS...")
if frappe.db.exists("Workspace", "HIGHSPEED POS"):
    workspace = frappe.get_doc("Workspace", "HIGHSPEED POS")
    
    # Reset child tables
    workspace.number_cards = []
    workspace.charts = []
    
    for card in number_cards_data:
        workspace.append("number_cards", {
            "number_card_name": card["name"],
            "label": card["name"]
        })
        
    for chart in dashboard_charts_data:
        workspace.append("charts", {
            "chart_name": chart["name"],
            "label": chart["name"]
        })
        
    # Build Gutenberg content block list
    new_content = [
        {"id": "hspos_stats_header", "type": "header", "data": {"text": '<span class="h4">Statistics & Indicators</span>', "col": 12}},
        {"id": "hspos_sales_today", "type": "number_card", "data": {"number_card_name": "HSPOS Total Sales Today", "col": 4}},
        {"id": "hspos_invoices_today", "type": "number_card", "data": {"number_card_name": "HSPOS Total Invoices Today", "col": 4}},
        {"id": "hspos_average_ticket", "type": "number_card", "data": {"number_card_name": "HSPOS Average Ticket Today", "col": 4}},
        {"id": "hspos_returned_today", "type": "number_card", "data": {"number_card_name": "HSPOS Returned Amount Today", "col": 6}},
        {"id": "hspos_active_shifts", "type": "number_card", "data": {"number_card_name": "HSPOS Active Shifts", "col": 6}},
        {"id": "hspos_daily_sales", "type": "chart", "data": {"chart_name": "HSPOS Daily Sales Trend", "col": 12}},
        {"id": "spacer_after_chart", "type": "spacer", "data": {"col": 12}},
        {"id": "cJigdSD9mh", "type": "header", "data": {"text": '<span class="h4">Point of Sales</span>', "col": 12}},
        {"id": "4D2sc3CbN3", "type": "shortcut", "data": {"shortcut_name": "HIGHSPEED POS App", "col": 3}},
        {"id": "nVBkn7nfDw", "type": "spacer", "data": {"col": 12}},
        {"id": "-B_qEZqEA6", "type": "card", "data": {"card_name": "POS", "col": 4}},
        {"id": "tsAHaUCd5l", "type": "card", "data": {"card_name": "Profile", "col": 4}},
        {"id": "2-3HMkGou3", "type": "card", "data": {"card_name": "Shift", "col": 4}},
        {"id": "GdPtnrazDS", "type": "card", "data": {"card_name": "HSPOS Delivery Charges", "col": 4}},
        {"id": "cABO53xhGv", "type": "card", "data": {"card_name": "Offers &amp; Coupons", "col": 4}}
    ]
    
    workspace.content = json.dumps(new_content)
    workspace.save()
    
    frappe.clear_cache(doctype="Workspace")
    frappe.db.commit()
    print("Workspace updated successfully!")
else:
    print("Workspace HIGHSPEED POS not found!")
