// console.log("🔥 after_setup_redirect.js LOADED");

frappe.router.on("change", () => {
	// console.log("🔥 route changed", frappe.boot?.sysdefaults);

	if (!frappe.boot?.setup_complete) return;
	if (frappe.get_route()[0] === "zatca-wizard") return;
	if (frappe.boot.sysdefaults?.custom_zatca_wizard_completed) return;

	// frappe.set_route("zatca-wizard");
});
