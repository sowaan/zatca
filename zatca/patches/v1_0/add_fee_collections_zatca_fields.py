import frappe # type: ignore

def execute():
    # Skip completely if DocType does not exist
    if not frappe.db.exists("DocType", "Fee Collections"):
        return

    fields = [
        {
            "fieldname": "custom_uuid",
            "label": "ZATCA UUID",
            "fieldtype": "Data",
            "insert_after": "posting_time",
            "no_copy": 1,
            "translatable": 1,
            "module": "Zatca",
        },
        {
            "fieldname": "custom_zatca_status",
            "label": "ZATCA Status",
            "fieldtype": "Select",
            "options": "Not Submitted\nREPORTED\nCLEARED",
            "insert_after": "student",
            "no_copy": 1,
            "translatable": 1,
            "module": "Zatca",
        },
    ]

    for field in fields:
        if not frappe.db.exists(
            "Custom Field",
            f"Fee Collections-{field['fieldname']}"
        ):
            frappe.create_custom_field(
                "Fee Collections",
                field,
                ignore_validate=True
            )
