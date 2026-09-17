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

def item_wise_tax_json(sales_invoice_doc):
    """Return the first tax row's per-item tax breakdown as a JSON string
    ``{item_code: [rate, amount]}`` — the shape ``get_tax_for_item`` expects — in
    a way that works on both ERPNext v15 and v16.

    v15 stores it as a JSON string on each Sales Taxes and Charges row
    (``item_wise_tax_detail``). v16 dropped that field and moved the data to the
    invoice's ``item_wise_tax_details`` child table (keyed by item/tax row name).
    """
    taxes = sales_invoice_doc.get("taxes") or []
    if not taxes:
        return "{}"
    first_tax = taxes[0]

    # v15: JSON string directly on the tax row (missing on v16, so .get() is safe).
    legacy = first_tax.get("item_wise_tax_detail")
    if legacy:
        return legacy

    # v16: rebuild from the Item Wise Tax Detail child table on the invoice.
    detail_rows = sales_invoice_doc.get("item_wise_tax_details") or []
    if not detail_rows:
        return "{}"
    item_code_by_row = {it.name: it.item_code for it in sales_invoice_doc.get("items") or []}
    result = {}
    for row in detail_rows:
        if row.get("tax_row") and row.get("tax_row") != first_tax.name:
            continue
        item_code = item_code_by_row.get(row.get("item_row"))
        if not item_code:
            continue
        rate = row.get("rate") or 0
        amount = row.get("amount") or 0
        if item_code in result:
            result[item_code][1] += amount
        else:
            result[item_code] = [rate, amount]
    return json.dumps(result)


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