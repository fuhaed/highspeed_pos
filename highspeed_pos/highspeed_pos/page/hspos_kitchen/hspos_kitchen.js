frappe.pages['hspos_kitchen'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Kitchen Display System',
		single_column: true
	});

	// Append CSS files if not already in head
	if (!$("link[href*='vuetify.min.css']").length) {
		$("head").append("<link href='/assets/highspeed_pos/node_modules/vuetify/dist/vuetify.min.css' rel='stylesheet'>");
	}
	if (!$("link[href*='materialdesignicons.min.css']").length) {
		$("head").append("<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/@mdi/font@6.x/css/materialdesignicons.min.css'>");
	}
	if (!$("link[href*='Roboto']").length) {
		$("head").append("<link rel='stylesheet' href='https://fonts.googleapis.com/css?family=Roboto:100,300,400,500,700,900' />");
	}

	wrapper.page.$KitchenApp = new frappe.PosApp.kitchen(wrapper.page);
};
