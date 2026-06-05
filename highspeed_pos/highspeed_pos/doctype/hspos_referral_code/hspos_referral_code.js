// Copyright (c) 2021, HIGH SPEED IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('HSPOS Referral Code', {
	setup: function (frm) {
		frm.set_query("party_type", function () {
			return {
				filters: {
					"name": ["in", ["Customer"]],
				}
			};
		});
		frm.set_query("customer_offer", function () {
			return {
				filters: {
					"company": frm.doc.company,
					"coupon_based": 1,
					"disable": 0,
				}
			};
		});
		frm.set_query("primary_offer", function () {
			return {
				filters: {
					"company": frm.doc.company,
					"coupon_based": 1,
					"disable": 0,
				}
			};
		});
	},
	referral_name: function (frm) {
		if (frm.doc.__islocal === 1) {
			frm.trigger("make_hspos_referral_code");
		}
	},
	make_hspos_referral_code: function (frm) {
		let referral_name = frm.doc.referral_name;
		let hspos_referral_code;
		if (!referral_name) {
			frm.doc.referral_name = frm.doc.party + Math.random().toString(5).substring(2, 5).toUpperCase();
			hspos_referral_code = Math.random().toString(12).substring(2, 12).toUpperCase();
		}
		else {
			referral_name = referral_name.replace(/\s/g, '');
			hspos_referral_code = referral_name.toUpperCase().slice(0, 8);
		}
		frm.doc.hspos_referral_code = hspos_referral_code;
		frm.refresh_field('referral_name');
		frm.refresh_field('hspos_referral_code');
	},

});
