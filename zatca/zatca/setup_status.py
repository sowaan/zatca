import frappe


@frappe.whitelist()
def get_pending_zatca_companies():
	"""Companies that haven't completed ZATCA setup, for the eligible-user onboarding banner.

	Deliberately checks `custom_basic_auth_from_production` (the real production
	CSID/certificate), not `custom_zatca_invoice_enabled` — that flag gets set to 1
	prematurely inside create_csr() (wizard step 5 of 9, well before OTP, compliance
	testing, or the actual production certificate exist), so a company can read as
	"enabled" while still having no working ZATCA credentials at all. The production
	CSID is only ever written once the real final step (production_csid()) succeeds,
	so its presence is a true signal that setup is actually complete.
	"""
	if frappe.session.user != "Administrator" and "System Manager" not in frappe.get_roles():
		return []

	return frappe.get_all(
		"Company",
		filters={"custom_basic_auth_from_production": ["is", "not set"]},
		pluck="name",
	)
