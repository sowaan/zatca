import frappe


@frappe.whitelist()
def get_pending_zatca_companies():
	"""Companies that haven't completed ZATCA setup, for the eligible-user onboarding banner."""
	if frappe.session.user != "Administrator" and "System Manager" not in frappe.get_roles():
		return []

	return frappe.get_all(
		"Company",
		filters={"custom_zatca_invoice_enabled": ["!=", 1]},
		pluck="name",
	)
