
frappe.ui.form.on("Sales Invoice", {
    refresh: function (frm) {
        const showQrButton = () => {
            frm.add_custom_button(__("Create QR Code"), function () {
                frm.call({
                    method: "zatca.zatca.sign_invoice.create_qr_code_for_invoice",
                    args: {
                        invoice_number: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __("Creating QR Code..."),
                    callback: function (response) {
                        if (response.message && response.message.message) {
                            frappe.msgprint(response.message.message);
                        }
                        frm.reload_doc();
                    }
                });
            }, __("Zatca Phase-2"));
        };

        const checkFileExists = (fileUrl) => {
            if (!fileUrl) {
                return Promise.resolve(false);
            }

            const url = fileUrl.startsWith("http") ? fileUrl : `${window.location.origin}${fileUrl}`;

            return fetch(url, {
                method: "HEAD",
                credentials: "same-origin"
            }).then((res) => {
                if (res.ok || res.status === 403) {
                    return true;
                }

                return false;
            }).catch(() => false);
        };

        if (frm.doc.docstatus === 1 && !["CLEARED", "REPORTED"].includes(frm.doc.custom_zatca_status)) {
            frm.add_custom_button(__("Send invoice to Zatca"), function () {
                frm.call({
                    method: "zatca.zatca.sign_invoice.zatca_Background",
                    args: {
                        "invoice_number": frm.doc.name

                    },
                    callback: function (response) {
                        if (response.message) {
                            frappe.msgprint(response.message);
                            frm.reload_doc();

                        }
                        frm.reload_doc();
                    }


                });
                frm.reload_doc();
            }, __("Zatca Phase-2"));
        }

        if (frm.doc.docstatus === 1) {
            frappe.db.get_list("File", {
                fields: ["name", "file_url"],
                filters: {
                    attached_to_doctype: "Sales Invoice",
                    attached_to_name: frm.doc.name,
                    file_name: ["like", `QR_image_${frm.doc.name}%`]
                },
                limit: 1
            }).then((files) => {
                if (!files || files.length === 0) {
                    showQrButton();
                    return;
                }

                checkFileExists(files[0].file_url).then((exists) => {
                    if (!exists) {
                        showQrButton();
                    }
                });
            });
        }

        // frm.add_custom_button(__("Check invoice Validity"), function() {
        //     frm.call({
        //         method:"zatca2024.zatca2024.validation_inside_invoice.zatca_Call_compliance_inside",
        //         args: {
        //             "invoice_number": frm.doc.name
        //         },
        //         callback: function(response) {
        //             if (response.message) {  
        //                 frappe.msgprint(response.message);
        //                 frm.reload_doc();

        //             }
        //             frm.reload_doc();
        //         }


        //     });
        //     frm.reload_doc();
        // }, __("Zatca Phase-2"));
    }
});
