# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = "15.3.0"


def console(*data):
    frappe.publish_realtime("toconsole", data, user=frappe.session.user)
