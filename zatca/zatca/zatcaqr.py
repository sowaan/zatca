import os
import frappe
import pyqrcode
import base64

@frappe.whitelist(allow_guest=True)
def get_fatoora_qr(company, tax_number, date, total, tax_amount):
    tagsBufsArray = []
    array = [company, tax_number, date, total, tax_amount]
    tagsBufsArray = convert_to_bytes(array)
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
        

def convert_to_bytes(data):
    byte_array = []
    
    for i, item in enumerate(data, start=1):
        # For the first item (string)
        if i == 1:
            byte_array.append(b'\x01,' + item.encode())
        # For the second item (number as a string)
        elif i == 2:
            byte_array.append(b'\x02\x0f' + item.encode())
        # For the third item (date string)
        elif i == 3:
            byte_array.append(b'\x03\x13' + item.encode())
        # For the fourth item (integer converted to float)
        elif i == 4:
            byte_array.append(b'\x04\x05' + f"{float(item)}".encode())
        # For the fifth item (integer converted to float)
        elif i == 5:
            byte_array.append(b'\x05\x04' + f"{float(item)}".encode())
    
    return byte_array

