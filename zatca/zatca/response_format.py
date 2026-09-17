"""Render a ZATCA API response as a readable HTML summary for the user."""

import json

import frappe
from frappe.utils import escape_html


def _section(title, messages):
    rows = []
    for message in messages or []:
        code = escape_html(str(message.get("code") or ""))
        text = escape_html(str(message.get("message") or ""))
        prefix = f"<b>{code}</b> &ndash; " if code else ""
        rows.append(f"<li>{prefix}{text}</li>")
    if not rows:
        return ""
    return (
        f"<div style='margin-top:8px'><b>{title} ({len(rows)})</b>"
        f"<ul style='margin:4px 0 0;padding-left:18px'>{''.join(rows)}</ul></div>"
    )


def format_zatca_response(response):
    """Return an HTML summary of a ZATCA response (a ``requests`` response or raw
    text): the overall status plus the error/warning/info messages. Falls back to
    the raw/pretty text when it is not the expected JSON."""
    text = getattr(response, "text", response) or ""
    status_code = getattr(response, "status_code", None)

    try:
        data = json.loads(text) if isinstance(text, str) else dict(text)
    except (ValueError, TypeError):
        return escape_html(str(text))

    validation = data.get("validationResults") or {}
    reporting = data.get("reportingStatus")
    clearance = data.get("clearanceStatus")

    # Unexpected shape (no validation block / statuses): show pretty JSON instead.
    if not validation and not reporting and not clearance:
        return f"<pre style='white-space:pre-wrap'>{escape_html(json.dumps(data, indent=2))}</pre>"

    overall = validation.get("status") or reporting or clearance or "—"
    header = (
        f"<div><b>ZATCA status: {escape_html(str(overall))}"
        f"{f' (HTTP {status_code})' if status_code is not None else ''}</b></div>"
    )

    lines = [header]
    if reporting:
        lines.append(f"<div>Reporting status: <b>{escape_html(str(reporting))}</b></div>")
    if clearance:
        lines.append(f"<div>Clearance status: <b>{escape_html(str(clearance))}</b></div>")
    lines.append(_section(frappe._("Errors"), validation.get("errorMessages")))
    lines.append(_section(frappe._("Warnings"), validation.get("warningMessages")))
    lines.append(_section(frappe._("Info"), validation.get("infoMessages")))
    return "".join(line for line in lines if line)
