import frappe

def execute():
    try:
        if frappe.db.has_column("Address", "address_line1") and frappe.db.has_column("Address", "custom_zatca_address_line_1"):
            frappe.db.sql("""
                UPDATE `tabAddress` SET custom_zatca_address_line_1 = address_line1 
                WHERE address_line1 IS NOT NULL
            """)
        if frappe.db.has_column("Address", "address_line2") and frappe.db.has_column("Address", "custom_zatca_address_line_2"):
            frappe.db.sql("""
                UPDATE `tabAddress` SET custom_zatca_address_line_2 = address_line2 
                WHERE address_line2 IS NOT NULL
            """)
        if frappe.db.has_column("Address", "city") and frappe.db.has_column("Address", "custom_zatca_city"):
            frappe.db.sql("""
                UPDATE `tabAddress` SET custom_zatca_city = city 
                WHERE city IS NOT NULL
            """)
        if frappe.db.has_column("Address", "pincode") and frappe.db.has_column("Address", "custom_zatca_pincode"):
            frappe.db.sql("""
                UPDATE `tabAddress` SET custom_zatca_pincode = pincode 
                WHERE pincode IS NOT NULL
            """)
        if frappe.db.has_column("Address", "state") and frappe.db.has_column("Address", "custom_zatca_state"):
            frappe.db.sql("""
                UPDATE `tabAddress` SET custom_zatca_state = state 
                WHERE state IS NOT NULL
            """)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "ZATCA Address Patch Error")
