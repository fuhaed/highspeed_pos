# -*- coding: utf-8 -*-
# Copyright (c) 2020, HIGH SPEED IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from frappe.model.document import Document
from highspeed_pos.highspeed_pos.api.status_updater import StatusUpdater


class HSPOSOpeningShift(StatusUpdater):
	def validate(self):
		self.validate_pos_profile_and_cashier()
		self.set_status()

	def validate_pos_profile_and_cashier(self):
		if self.company != frappe.db.get_value("POS Profile", self.pos_profile, "company"):
			frappe.throw(_("POS Profile {} does not belongs to company {}".format(self.pos_profile, self.company)))

		if not cint(frappe.db.get_value("User", self.user, "enabled")):
			frappe.throw(_("User {} has been disabled. Please select valid user/cashier".format(self.user)))

	def on_submit(self):
		self.set_status(update=True)
		self.reset_order_number_if_required()

	def reset_order_number_if_required(self):
		pos_profile = frappe.get_doc("POS Profile", self.pos_profile)
		if pos_profile.hspos_enable_order_number and pos_profile.hspos_order_number_reset_cycle == "With Every Shift":
			frappe.db.set_value("POS Profile", self.pos_profile, "hspos_next_order_number", 1, update_modified=False)
			frappe.db.commit()
