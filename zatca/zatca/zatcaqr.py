import os
import frappe
import pyqrcode
import base64 
from zatca.zatca.sign_invoice import generate_tlv_xml, get_tlv_for_value

@frappe.whitelist(allow_guest=True)
def get_fatoora_qr(company):
    company_abbr = frappe.db.get_value("Company", {"name": company}, "abbr")
    tlv_data = generate_tlv_xml(company_abbr)

    tagsBufsArray = []
    for tag_num, tag_value in tlv_data.items():
        tagsBufsArray.append(get_tlv_for_value(tag_num, tag_value))

    qrCodeBuf = b"".join(tagsBufsArray)
    qrCodeB64 = base64.b64encode(qrCodeBuf).decode('utf-8')
    qr = pyqrcode.create(qrCodeB64)
    qr.png('qr_code.png', scale=5)
    # file = frappe.get_doc("File", "5fd4cf4571")
    with open("qr_code.png", mode="rb") as f:
        frappe.response.filecontent = f.read()
        frappe.response.filename = "qr_code.png"
        frappe.response.type = "download"
        frappe.response.display_content_as = "attachment"

        # now remove the generated QR Code file from server
        os.remove("qr_code.png")
        