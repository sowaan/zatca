from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():

    ADDRESS_CUSTOM_FIELDS = {
        "Address": [
            {
                "fieldname": "custom_zatca",
                "fieldtype": "Section Break",
                "label": "ZATCA",
                "insert_after": "links",
            },
            {
                "fieldname": "custom_zatca_address_line_1",
                "fieldtype": "Data",
                "label": "Zatca Address Line 1",
                "insert_after": "custom_zatca",
            },
            {
                "fieldname": "custom_zatca_address_line_2",
                "fieldtype": "Data",
                "label": "Zatca Address Line 2",
                "insert_after": "custom_zatca_address_line_1",
            },
            {
                "fieldname": "custom_zatca_city",
                "fieldtype": "Data",
                "label": "Zatca City",
                "insert_after": "custom_zatca_address_line_2",
            },
            {
                "fieldname": "custom_zatca_pincode",
                "fieldtype": "Data",
                "label": "Zatca Pincode",
                "insert_after": "custom_zatca_city",
            },
            {
                "fieldname": "custom_zatca_state",
                "fieldtype": "Data",
                "label": "Zatca State",
                "insert_after": "custom_zatca_pincode",
            },
        ],
    }

    create_custom_fields(ADDRESS_CUSTOM_FIELDS, ignore_validate=True)