
frappe.ui.form.on("Address", {
    refresh(frm) {
        toggle_zatca_fields_read_only(frm);
        refresh_values(frm);
    },

    fetch_from_above(frm) {
        toggle_zatca_fields_read_only(frm);
        refresh_values(frm);
    }
});

function toggle_zatca_fields_read_only(frm) {
    const fields = [
        "custom_zatca_address_line_1",
        "custom_zatca_address_line_2",
        "custom_zatca_city",
        "custom_zatca_pincode",
        "custom_zatca_state"
    ];

    const readOnly = !!frm.doc.fetch_from_above;

    fields.forEach(field => {
        if (frm.fields_dict[field]) {
            frm.set_df_property(field, "read_only", readOnly ? 1 : 0);
        }
    });
}

function refresh_values(frm) {
    if (frm.doc.fetch_from_above) {
        if (frm.fields_dict.custom_zatca_address_line_1)
            frm.fields_dict.custom_zatca_address_line_1.set_value(frm.doc.address_line1);
        if (frm.fields_dict.custom_zatca_address_line_2)
            frm.fields_dict.custom_zatca_address_line_2.set_value(frm.doc.address_line2);
        if (frm.fields_dict.custom_zatca_city)
            frm.fields_dict.custom_zatca_city.set_value(frm.doc.city);
        if (frm.fields_dict.custom_zatca_pincode)
            frm.fields_dict.custom_zatca_pincode.set_value(frm.doc.pincode);
        if (frm.fields_dict.custom_zatca_state)
            frm.fields_dict.custom_zatca_state.set_value(frm.doc.state);
    }
}
