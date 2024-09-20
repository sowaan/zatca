import os
import frappe
from datetime import datetime
from fatoora import Fatoora

@frappe.whitelist(allow_guest=True)
def get_fatoora_qr(seller_name,tax_number,date,total,tax_amount):
    fatoora_obj = Fatoora(
        seller_name=seller_name,
        tax_number=tax_number, # or "1234567891"
        invoice_date=datetime.strptime(date, '%Y-%m-%d %H:%M'), # timestamp or datetime object, or string ISO 8601 Zulu format
        total_amount=total, # or 100.0, 100.00, "100.0", "100.00"
        tax_amount=tax_amount, # or 15.0, 15.00, "15.0", "15.00",
    )

    fatoora_obj.qrcode("qr_code.png")
    
    # file = frappe.get_doc("File", "5fd4cf4571")
    with open("qr_code.png", mode="rb") as f:
        frappe.response.filecontent = f.read()
        frappe.response.filename = "qr_code.png"
        frappe.response.type = "download"
        frappe.response.display_content_as = "attachment"

        # now remove the generated QR Code file from server
        os.remove("qr_code.png")
        