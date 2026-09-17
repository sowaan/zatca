"""KSA print formats bundled inside the ZATCA app.

This mirrors the standalone `ksa_print_formats` app so a site that installs ONLY
zatca still gets the bilingual (EN/AR) KSA print formats and the Arabic
amount-in-words field — without needing `ksa_print_formats` installed separately.

Coexistence with `ksa_print_formats` (both apps installed) is deliberate and
conflict-free:

* `ksa_print_formats` ships these formats as **standard** module files, so on
  migrate Frappe syncs them into the DB owned by its "Ksa Print Formats" module.
* zatca ships the same definitions as plain **data** files (this package is NOT a
  Frappe module folder, so Frappe never auto-syncs them) and creates them
  programmatically as **non-standard** records — but only when a same-named
  format does not already exist as a standard record. So when both apps are
  present, zatca defers to `ksa_print_formats` and never fights over ownership.
"""

import json
import os

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.utils import flt

FORMATS_DIR = os.path.join(os.path.dirname(__file__), "formats")

# Module the programmatically-created (non-standard) formats are filed under, so
# they are cleaned up if zatca is uninstalled on a zatca-only site.
OWNER_MODULE = "Zatca"

# DocType -> the KSA print format that should be its default.
DEFAULT_PRINT_FORMATS = {
    "Sales Invoice": "KSA Tax Invoice",
    "Sales Order": "KSA Sales Order",
    "Quotation": "KSA Quotation",
    "Delivery Note": "KSA Delivery Note",
    "Payment Entry": "KSA Payment Entry",
    "Purchase Invoice": "KSA Purchase Invoice",
    "Purchase Order": "KSA Purchase Order",
    "Purchase Receipt": "KSA Purchase Receipt",
}

# ---------------------------------------------------------------------------
# Arabic amount-in-words (identical behaviour to the ksa_print_formats app)
# ---------------------------------------------------------------------------

CURRENCY_AR = {
    "SAR": ("ريال سعودي", "هللة"),
    "AED": ("درهم إماراتي", "فلس"),
    "QAR": ("ريال قطري", "درهم"),
    "KWD": ("دينار كويتي", "فلس"),
    "BHD": ("دينار بحريني", "فلس"),
    "OMR": ("ريال عماني", "بيسة"),
    "USD": ("دولار أمريكي", "سنت"),
    "EUR": ("يورو", "سنت"),
    "GBP": ("جنيه إسترليني", "بنس"),
    "PKR": ("روبية باكستانية", "بيسة"),
    "INR": ("روبية هندية", "بيسة"),
    "EGP": ("جنيه مصري", "قرش"),
}

IN_WORDS_DOCTYPES = [
    "Sales Invoice",
    "POS Invoice",
    "Purchase Invoice",
    "Sales Order",
    "Purchase Order",
    "Quotation",
    "Supplier Quotation",
    "Delivery Note",
    "Purchase Receipt",
    "Subcontracting Receipt",
    "Payment Entry",
]

_AMOUNT_FIELDS = ("rounded_total", "grand_total", "paid_amount", "total_amount", "base_grand_total")


def money_in_words_arabic(amount, currency=None):
    """Return the amount spelled out in Arabic, e.g. 'تسعمائة و عشرون ريال سعودي فقط لا غير'."""
    from num2words import num2words

    amount = flt(amount)
    main = int(amount)
    fraction = int(round((amount - main) * 100))
    # Known currency -> (unit, sub-unit). Unknown -> use the code itself so we
    # never mislabel e.g. PKR as SAR.
    main_name, fraction_name = CURRENCY_AR.get(currency or "SAR", (currency or "SAR", None))

    words = f"{num2words(main, lang='ar')} {main_name}"
    if fraction and fraction_name:
        words += f" و {num2words(fraction, lang='ar')} {fraction_name}"
    return f"{words} فقط لا غير"


def _amount_for_in_words(doc):
    for fieldname in _AMOUNT_FIELDS:
        value = doc.get(fieldname)
        if value:
            return flt(value)
    return 0


def set_in_words_arabic(doc, method=None):
    """doc_events validate hook: fill in_words_arabic from the document's total.

    Guarded with a doc flag so that if BOTH this app and `ksa_print_formats`
    register the same validate hook, only the first one does the work.
    """
    if doc.flags.get("ksa_in_words_arabic_done"):
        return
    if not doc.meta.get_field("in_words_arabic"):
        return
    currency = doc.get("currency") or (
        frappe.get_cached_value("Company", doc.get("company"), "default_currency")
        if doc.get("company")
        else None
    )
    doc.in_words_arabic = money_in_words_arabic(_amount_for_in_words(doc), currency)
    doc.flags.ksa_in_words_arabic_done = True


# ---------------------------------------------------------------------------
# Install/migrate helpers
# ---------------------------------------------------------------------------

def ensure_in_words_arabic_fields():
    """Add a read-only 'In Words (Arabic)' custom field after `in_words` on every
    DocType that has one. Idempotent — skips DocTypes that already have it."""
    fields = {}
    for doctype in IN_WORDS_DOCTYPES:
        if not frappe.db.exists("DocType", doctype):
            continue
        meta = frappe.get_meta(doctype)
        if not meta.get_field("in_words"):
            continue
        if meta.get_field("in_words_arabic"):
            continue
        fields[doctype] = [
            {
                "fieldname": "in_words_arabic",
                "label": "In Words (Arabic)",
                "fieldtype": "Small Text",
                "insert_after": "in_words",
                "read_only": 1,
                "translatable": 0,
                "no_copy": 1,
            }
        ]
    if fields:
        create_custom_fields(fields, ignore_validate=True)


# Fields copied from the bundled JSON into the created Print Format doc.
_PF_FIELDS = (
    "print_format_type", "custom_format", "html", "css", "format_data",
    "margin_top", "margin_bottom", "margin_left", "margin_right",
    "font_size", "align_labels_right", "line_breaks", "absolute_value",
    "show_section_headings", "default_print_language", "print_format_builder",
    "print_format_builder_beta", "font", "page_number", "raw_printing",
)


def _load_bundled_formats():
    formats = []
    for fname in sorted(os.listdir(FORMATS_DIR)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(FORMATS_DIR, fname)) as fh:
            formats.append(json.load(fh))
    return formats


def ensure_ksa_print_formats():
    """Create the KSA print formats programmatically as non-standard records.

    Deference rule so this never conflicts with the standalone
    `ksa_print_formats` app:
      * missing            -> create (standard='No', module=Zatca)
      * exists, standard=No -> update it (zatca-managed / unmanaged copy: refresh)
      * exists, standard=Yes -> skip (owned by ksa_print_formats; leave it alone)
    """
    for data in _load_bundled_formats():
        name = data.get("name")
        if not name:
            continue

        existing = frappe.db.get_value(
            "Print Format", name, ["name", "standard"], as_dict=True
        )
        if existing and existing.standard == "Yes":
            # ksa_print_formats owns this one via its standard module file — defer.
            continue

        if existing:
            doc = frappe.get_doc("Print Format", name)
        else:
            doc = frappe.new_doc("Print Format")
            doc.name = name
            doc.doc_type = data.get("doc_type")

        doc.standard = "No"
        doc.module = OWNER_MODULE
        doc.disabled = 0
        for field in _PF_FIELDS:
            if field in data:
                doc.set(field, data.get(field))

        doc.flags.ignore_permissions = True
        doc.flags.ignore_version = True
        if existing:
            doc.save()
        else:
            doc.insert(ignore_permissions=True)


def set_default_print_formats():
    """Make each KSA format the default for its DocType (durable Property Setter)."""
    changed = False
    for doctype, print_format in DEFAULT_PRINT_FORMATS.items():
        if not frappe.db.exists("DocType", doctype):
            continue
        if not frappe.db.exists("Print Format", print_format):
            continue

        existing = frappe.db.get_value(
            "Property Setter",
            {"doc_type": doctype, "doctype_or_field": "DocType", "property": "default_print_format"},
            ["name", "value"],
            as_dict=True,
        )
        if existing and existing.value == print_format:
            continue

        if existing:
            frappe.db.set_value("Property Setter", existing.name, "value", print_format)
        else:
            make_property_setter(
                doctype, "", "default_print_format", print_format, "Data",
                for_doctype=True, validate_fields_for_doctype=False,
            )
        changed = True

    if changed:
        frappe.clear_cache()


def setup_ksa_print_formats():
    ensure_in_words_arabic_fields()
    ensure_ksa_print_formats()
    set_default_print_formats()
    frappe.db.commit()


def after_install():
    setup_ksa_print_formats()


def after_migrate():
    setup_ksa_print_formats()
