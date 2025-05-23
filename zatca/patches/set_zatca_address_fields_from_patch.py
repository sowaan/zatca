import frappe

def execute():
    try:
        fields = {
            "address_line1": "custom_zatca_address_line_1",
            "address_line2": "custom_zatca_address_line_2",
            "city": "custom_zatca_city",
            "pincode": "custom_zatca_pincode",
            "state": "custom_zatca_state"
        }

        for source, target in fields.items():
            if frappe.db.has_column("Address", source) and frappe.db.has_column("Address", target):
                frappe.db.sql(f"""
                    UPDATE `tabAddress`
                    SET `{target}` = `{source}`
                    WHERE `{source}` IS NOT NULL
                """)

    except Exception:
        frappe.log_error(frappe.get_traceback(), "ZATCA Address Patch Error")