frappe.ui.form.on("Fee Collections", {
    refresh: function (frm) {
        // Add "Send to Zatca" button for submitted fee collections
        if (frm.doc.docstatus === 1 && !["CLEARED", "REPORTED"].includes(frm.doc.custom_zatca_status)) {
            frm.add_custom_button(__("Send to Zatca"), function () {
                frm.call({
                    method: "zatca.zatca.sign_fee_collection.zatca_Background_fee_collection",
                    args: {
                        "fee_collection_number": frm.doc.name
                    },
                    callback: function (response) {
                        if (response.message) {
                            frappe.msgprint(response.message);
                        }
                        frm.reload_doc();
                    }
                });
            }, __("Zatca Phase-2"));
        }
    }
});
