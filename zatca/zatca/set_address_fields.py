import frappe

def set_zatca_address_fields(doc, method):
    if hasattr(doc, "fetch_from_above"):
        if doc.fetch_from_above:
            if hasattr(doc, "custom_zatca_address_line_1"):
                doc.set('custom_zatca_address_line_1', doc.address_line1)
            if hasattr(doc, "custom_zatca_address_line_2"):
                doc.set('custom_zatca_address_line_2', doc.address_line2)
            if hasattr(doc, "custom_zatca_city"):
                doc.set('custom_zatca_city', doc.city)
            if hasattr(doc, "custom_zatca_pincode"):
                doc.set('custom_zatca_pincode', doc.pincode)
            if hasattr(doc, "custom_zatca_state"):
                doc.set('custom_zatca_state', doc.state)
