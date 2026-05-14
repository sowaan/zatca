import frappe
from frappe.utils import today, add_days


def retry_pending_zatca_submissions():
    """
    Daily scheduled task: find Sales Invoices that failed or were skipped for ZATCA
    submission because of a future posting date, and submit them now that their date
    has arrived.

    Controlled per-company via two fields on Company:
      - custom_zatca_auto_retry_enabled  (Check)  – opt-in per company
      - custom_zatca_retry_days          (Int)     – look-back window; 0 = no limit
    """
    companies = frappe.get_all(
        "Company",
        filters={
            "custom_zatca_invoice_enabled": 1,
            "custom_zatca_auto_retry_enabled": 1,
        },
        fields=["name", "abbr", "custom_zatca_retry_days"],
    )

    for company in companies:
        try:
            _process_company(company)
        except Exception:
            frappe.log_error(
                title=f"ZATCA Auto Retry: error processing company {company.name}",
                message=frappe.get_traceback(),
            )


def _process_company(company):
    today_date = today()
    retry_days = cint(company.custom_zatca_retry_days)

    filters = {
        "docstatus": 1,
        "company": company.name,
        "custom_zatca_status": "Not Submitted",
        "posting_date": ["<=", today_date],
    }

    if retry_days > 0:
        from_date = add_days(today_date, -retry_days)
        filters["posting_date"] = ["between", [from_date, today_date]]

    pending = frappe.get_all("Sales Invoice", filters=filters, pluck="name")

    for invoice_name in pending:
        try:
            _submit_to_zatca(invoice_name, company.abbr)
        except Exception:
            frappe.log_error(
                title=f"ZATCA Auto Retry Failed: {invoice_name}",
                message=frappe.get_traceback(),
            )


def _submit_to_zatca(invoice_number, company_abbr):
    from zatca.zatca.sign_invoice import new_zatca_Call

    sales_invoice_doc = frappe.get_doc("Sales Invoice", invoice_number)

    if sales_invoice_doc.custom_zatca_status in ["REPORTED", "CLEARED"]:
        return

    any_item_has_tax_template = any(
        item.item_tax_template for item in sales_invoice_doc.items
    )

    new_zatca_Call(
        invoice_number,
        "0",
        any_item_has_tax_template,
        company_abbr,
        submit_to_zatca=True,
    )


def cint(value):
    try:
        return int(value or 0)
    except (ValueError, TypeError):
        return 0
