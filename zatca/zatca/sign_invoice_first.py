
from frappe import _
import frappe

SUPPORTED_INVOICES = ["Sales Invoice", "POS Invoice"]


def structuring_signedxml():
    """structuring the signed xml"""
    try:
        with open(
            frappe.local.site + "/private/files/final_xml_after_sign.xml",
            "r",
            encoding="utf-8",
        ) as file:
            xml_content = file.readlines()
        indentations = {
            29: [
                '<xades:QualifyingProperties xmlns:xades="http://uri.etsi.org/01903/v1.3.2#" Target="signature">',
                "</xades:QualifyingProperties>",
            ],
            33: [
                '<xades:SignedProperties Id="xadesSignedProperties">',
                "</xades:SignedProperties>",
            ],
            37: [
                "<xades:SignedSignatureProperties>",
                "</xades:SignedSignatureProperties>",
            ],
            41: [
                "<xades:SigningTime>",
                "<xades:SigningCertificate>",
                "</xades:SigningCertificate>",
            ],
            45: ["<xades:Cert>", "</xades:Cert>"],
            49: [
                "<xades:CertDigest>",
                "<xades:IssuerSerial>",
                "</xades:CertDigest>",
                "</xades:IssuerSerial>",
            ],
            53: [
                '<ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>',
                "<ds:DigestValue>",
                "<ds:X509IssuerName>",
                "<ds:X509SerialNumber>",
            ],
        }

        def adjust_indentation(line):
            for col, tags in indentations.items():
                for tag in tags:
                    if line.strip().startswith(tag):
                        return " " * (col - 1) + line.lstrip()
            return line

        adjusted_xml_content = [adjust_indentation(line) for line in xml_content]
        with open(
            frappe.local.site + "/private/files/final_xml_after_indent.xml",
            "w",
            encoding="utf-8",
        ) as file:
            file.writelines(adjusted_xml_content)
        signed_xmlfile_name = (
            frappe.local.site + "/private/files/final_xml_after_indent.xml"
        )
        return signed_xmlfile_name
    except (ValueError, KeyError, TypeError, frappe.ValidationError) as e:
        frappe.throw(_(" error in structuring signed xml: " + str(e)))
        return None