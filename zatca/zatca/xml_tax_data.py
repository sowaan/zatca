"""
This module contains utilities for ZATCA 2024 e-invoicing.
Includes functions for XML parsing, API interactions, and custom handling.
"""

import json
from frappe import _
import frappe

TAX_CALCULATION_ERROR = "Tax Calculation Error"
CAC_TAX_TOTAL = "cac:TaxTotal"


def get_exemption_reason_map():
    """Mapping of the exception reason code accoding to the reason code"""
    return {
        "VATEX-SA-29": (
            "Financial services mentioned in Article 29 of the VAT Regulations."
        ),
        "VATEX-SA-29-7": (
            "Life insurance services mentioned in Article 29 of the VAT Regulations."
        ),
        "VATEX-SA-30": (
            "Real estate transactions mentioned in Article 30 of the VAT Regulations."
        ),
        "VATEX-SA-32": "Export of goods.",
        "VATEX-SA-33": "Export of services.",
        "VATEX-SA-34-1": "The international transport of Goods.",
        "VATEX-SA-34-2": "International transport of passengers.",
        "VATEX-SA-34-3": (
            "Services directly connected and incidental to a Supply of "
            "international passenger transport."
        ),
        "VATEX-SA-34-4": "Supply of a qualifying means of transport.",
        "VATEX-SA-34-5": (
            "Any services relating to Goods or passenger transportation, as defined "
            "in article twenty five of these Regulations."
        ),
        "VATEX-SA-35": "Medicines and medical equipment.",
        "VATEX-SA-36": "Qualifying metals.",
        "VATEX-SA-EDU": "Private education to citizen.",
        "VATEX-SA-HEA": "Private healthcare to citizen.",
        "VATEX-SA-MLTRY": "Supply of qualified military goods",
        "VATEX-SA-OOS": (
            "The reason is a free text, has to be provided by the taxpayer on a "
            "case-by-case basis."
        ),
    }

def get_tax_for_item(full_string, item):
    """
    Extracts the tax amount and tax percentage for a specific item from a JSON-encoded string.
    """
    try:  # getting tax percentage and tax amount
        data = json.loads(full_string)
        tax_percentage = data.get(item, [0, 0])[0]
        tax_amount = data.get(item, [0, 0])[1]
        return tax_amount, tax_percentage
    except json.JSONDecodeError as e:
        frappe.throw(_("JSON decoding error occurred in tax for item: " + str(e)))
        return None
    except KeyError as e:
        frappe.throw(_(f"Key error occurred while accessing item '{item}': " + str(e)))
        return None
    except TypeError as e:
        frappe.throw(_("Type error occurred in tax for item: " + str(e)))
        return None
