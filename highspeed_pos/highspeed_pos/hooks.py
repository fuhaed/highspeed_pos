doc_events = {
    "Sales Invoice": {
        "validate": "highspeed_pos.highspeed_pos.api.invoice.validate",
    },
    "Customer": {
        "validate": "highspeed_pos.highspeed_pos.api.hsposapp.set_customer_info",
    },
    "Payment Entry": {
        "on_cancel": "highspeed_pos.highspeed_pos.api.payment_entry.on_payment_entry_cancel"
    }
} 