frappe.pages['zatca-wizard'].on_page_load = function (wrapper) {
	const COMPLIANCE_TESTS = [
		{ key: "simplified_invoice", label: __("Simplified Invoice"), code: "1" },
		{ key: "standard_invoice", label: __("Standard Invoice"), code: "2" },
		{ key: "simplified_credit_note", label: __("Simplified Credit Note"), code: "3" },
		{ key: "standard_credit_note", label: __("Standard Credit Note"), code: "4" },
		{ key: "simplified_debit_note", label: __("Simplified Debit Note"), code: "5" },
		{ key: "standard_debit_note", label: __("Standard Debit Note"), code: "6" },
	];

	function renderComplianceTable(dialog) {
		const wrapper = dialog.fields_dict.compliance_table.$wrapper;

		const rows = COMPLIANCE_TESTS.map(t => `
    <tr id="row-${t.key}">
      <td style="font-weight:500;">${t.label}</td>

      <td class="text-center">
        <button
          class="btn btn-sm btn-light border"
          title="${__("Run Test")}"
          onclick="runComplianceTest('${t.key}')"
          style="padding:4px 10px;border-radius:6px;"
        >
          ▶
        </button>
      </td>

      <td id="${t.key}-reporting" class="text-muted">–</td>
      <td id="${t.key}-clearance" class="text-muted">–</td>

      <td id="${t.key}-status">
        <span class="badge bg-secondary">${__("Pending")}</span>
      </td>
    </tr>
  `).join("");

		wrapper.html(`
    <div style="
      background:#ffffff;
      border-radius:10px;
      box-shadow:0 6px 18px rgba(0,0,0,0.06);
      padding:12px;
    ">
      <table class="table table-sm align-middle mb-0">
        <thead style="background:#f9fafb;">
          <tr>
            <th>${__("Test Case")}</th>
            <th class="text-center">${__("Run")}</th>
            <th>${__("Reporting")}</th>
            <th>${__("Clearance")}</th>
            <th>${__("Status")}</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `);
	}


	window.runComplianceTest = function (key) {
		const test = COMPLIANCE_TESTS.find(t => t.key === key);
		if (!test) return;

		const statusCell = document.getElementById(`${key}-status`);
		if (statusCell) {
			statusCell.innerHTML = `
  <span class="badge bg-info">
    <i class="fa fa-spinner fa-spin"></i> ${__("Running")}
  </span>
`;

		}

		const isOfflinePOS = slideData["select_company_is_offline_pos"];
		const doctype = isOfflinePOS ? "ZATCA Multiple Setting" : "Company";
		const name = isOfflinePOS ? slideData["selected_machine"] : selected_company;

		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Company",
				filters: { name: selected_company },
				fieldname: ["abbr"],
			},
			callback(res) {
				if (!res.message || !res.message.abbr) {
					frappe.msgprint(__("Company abbreviation is missing."));
					return;
				}
				const company_abbr = res.message.abbr;

				frappe.call({
					method: "zatca.zatca.wizardbutton.wizard_button",
					args: {
						company_abbr,
						button: `${key}_button`,
						pos: doctype,
						machine: name
					},
					callback(r) {
						const msg = r.message || {};
						const reporting = msg.reportingStatus || "–";
						const clearance = msg.clearanceStatus || "–";

						const rEl = document.getElementById(`${key}-reporting`);
						const cEl = document.getElementById(`${key}-clearance`);

						if (rEl) rEl.innerText = reporting;
						if (cEl) cEl.innerText = clearance;

						const success =
							reporting === "REPORTED" || clearance === "CLEARED";

						complianceState[key] = success;

						statusCell.innerHTML = success
							? `<span class="badge bg-success">✔ ${__("Passed")}</span>`
							: `<span class="badge bg-danger">✖ ${__("Failed")}</span>`;
						const row = document.getElementById(`row-${key}`);
						row.style.background = success ? "#f0fdf4" : "#fef2f2";
						if (!success && msg.warnings?.length) {
							frappe.msgprint({
								title: __("ZATCA Warnings"),
								message: msg.warnings.map(w => w.message).join("<br><br>"),
								indicator: "orange",
							});
						}
					}
				});
			}
		});
	};

	const complianceState = {}; // runtime status

	const unifiedTooltips = [
		{
			fieldname: "company_name",
			context: "dialog",
			text: "Your registered company name.",
			links: ["https://docs.claudion.com/Field"],
		},
		{
			fieldname: "otp",
			context: "dialog",
			text: "Enter the OTP received for verification.",
			links: ["https://example.com/otp-help"],
		},
		{
			fieldname: "integration_type",
			context: "dialog",
			text: "Provide your basic auth credentials here.",
			links: ["https://example.com/auth-help"],
		},
		{
			fieldname: "company",
			context: "dialog",
			text: "Enter the company information.",
			links: ["https://docs.claudion.com/Field"],
		},
		{
			fieldname: "vat_number",
			context: "dialog",
			text: "Provide the VAT number for your company.",
			links: ["https://docs.claudion.com/Field"],
		},
		{
			fieldname: "building",
			context: "dialog",
			text: "Enter the building number or name.",
			links: ["https://docs.claudion.com/Field"],
		},
		{
			fieldname: "city",
			context: "dialog",
			text: "Enter the city name where the business is located.",
			links: ["https://docs.claudion.com/Field"],
		},
		{
			fieldname: "zip",
			context: "dialog",
			text: "Provide the ZIP or postal code.",
			links: ["https://docs.claudion.com/Field"],
		},
		{
			fieldname: "business_category",
			context: "dialog",
			text: "Select the business category for your company.",
			links: ["https://docs.claudion.com/Field"],
		},
		{
			fieldname: "csr_config_box",
			context: "dialog",
			text: "Configure the CSR details in this box.",
			links: ["https://example.com/csr-config-help"],
		},

		{
			fieldname: "created_csr_config",
			context: "dialog",
			text: "View or manage your created CSR configurations.",
			links: ["https://example.com/created-csr-config-help"],
		},

		{
			fieldname: "basic_auth_from_csid",
			context: "dialog",
			text: "Provide the basic authentication credentials from your CSID.",
			links: ["https://example.com/basic-auth-from-csid-help"],
		},
		{
			fieldname: "invoice_number",
			context: "dialog",
			text: "Enter the invoice number for tracking purposes.",
			links: ["https://example.com/invoice-number-help"],
		},

	];

	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Zatca Setup Wizard',
		single_column: true
	});

	let current_slide_index = 0;
	let selected_company = null;
	// Despite the name (kept from the previous Dialog-based implementation to
	// minimize churn across this file), this now holds a frappe.ui.FieldGroup
	// instance — frappe.ui.Dialog itself extends FieldGroup, so every method
	// used on it here (get_value, set_value, get_values, fields_dict, refresh)
	// behaves identically; only the modal chrome (show/hide/backdrop) is gone.
	let current_dialog = null;
	let slideData = {};

	// Gates advancing past a step whose action button hasn't actually been run
	// yet (e.g. clicking Next on "Create CSR" without ever clicking the
	// Create CSR button) — separate from field validation, this is a
	// workflow-sequencing check.
	let csrGenerated = false;
	let csidGenerated = false;
	let finalCsidGenerated = false;

	const WIZARD_PROGRESS_KEY = `zatca_wizard_progress:${frappe.session.user}`;

	function saveWizardProgress() {
		try {
			localStorage.setItem(
				WIZARD_PROGRESS_KEY,
				JSON.stringify({
					current_slide_index,
					slideData,
					selected_company,
					csrGenerated,
					csidGenerated,
					finalCsidGenerated,
					complianceState,
				})
			);
		} catch (e) {
			// localStorage can throw (private browsing, quota) — losing resume
			// state isn't fatal, so fail silently rather than break the wizard.
		}
	}

	function clearWizardProgress() {
		try {
			localStorage.removeItem(WIZARD_PROGRESS_KEY);
		} catch (e) {
			// ignore
		}
	}

	function loadWizardProgress() {
		try {
			const raw = localStorage.getItem(WIZARD_PROGRESS_KEY);
			return raw ? JSON.parse(raw) : null;
		} catch (e) {
			return null;
		}
	}

	// Inline field errors instead of frappe.msgprint popups. Deliberately not
	// using `reqd: 1` for this — FieldGroup.get_values() unconditionally shows
	// its own "Missing Values Required" msgprint whenever a reqd field is
	// empty (unless called with ignore_errors=true, which we do), so relying
	// on `reqd` either pops up frappe's own dialog or silently does nothing.
	// Validation here is entirely manual and independent of `reqd`.
	function showFieldError(dialog, fieldname, message) {
		const field = dialog.fields_dict[fieldname];
		if (!field) return;
		field.set_description(`<span style="color:#e03131;">${frappe.utils.escape_html(message)}</span>`);
		field.$wrapper.find(".form-control").addClass("zatca-field-invalid");
	}

	function clearFieldError(dialog, fieldname) {
		const field = dialog.fields_dict[fieldname];
		if (!field) return;
		field.set_description("");
		field.$wrapper.find(".form-control").removeClass("zatca-field-invalid");
	}

	function clearFieldErrors(dialog, fieldnames) {
		fieldnames.forEach((fieldname) => clearFieldError(dialog, fieldname));
	}

	const SLIDE_STEP_LABELS = [
		__("Welcome"),
		__("Select Company"),
		__("Integration Type"),
		__("Company Details"),
		__("Create CSR"),
		__("Enter OTP"),
		__("Compliance Check"),
		__("Final CSID"),
		__("Steps to Follow"),
	];

	function updateStepIndicator(index) {
		const steps_html = SLIDE_STEP_LABELS.map((label, i) => {
			const state = i < index ? "done" : i === index ? "active" : "upcoming";
			return `
				<div class="zatca-step-item">
					<span class="zatca-step zatca-step-${state}">${i < index ? "✓" : i + 1}</span>
					<span class="zatca-step-label zatca-step-label-${state}">${frappe.utils.escape_html(label)}</span>
				</div>
			`;
		}).join('<div class="zatca-step-sep"></div>');

		$wizard_steps_row.html(steps_html);
	}

	const slides_settings = [
		{
			name: "welcome",
			title: __("ZATCA Wizard (Sowaan)"),
			fields: [
				{
					fieldtype: "HTML",
					options: `
						<div style="
							display: flex;
							justify-content: center;
							align-items: center;
							min-height: 320px;
						">
							<div style="
								background: #ffffff;
								border-radius: 12px;
								padding: 32px 40px;
								max-width: 520px;
								width: 100%;
								box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
								text-align: center;
							">
								<!-- Logos -->
								<div style="
									display: flex;
									justify-content: center;
									align-items: center;
									gap: 24px;
									margin-bottom: 24px;
								">
									<img
										src="/assets/zatca/images/zatca-logo.png"
										alt="Sowaan"
										style="max-height: 55px;"
									/>
								</div>

								<!-- Title -->
								<h2 style="
									margin: 0 0 12px 0;
									font-size: 22px;
									font-weight: 600;
									color: #1f2937;
								">
									${__("ZATCA Phase 2 Wizard")}
								</h2>

								<!-- Subtitle -->
								<p style="
									margin: 0;
									font-size: 14px;
									color: #6b7280;
									line-height: 1.6;
								">
									${__("This wizard will guide you step by step to complete the <strong>ZATCA Phase 2 Integration</strong> successfully.")}<br>
									${__("Please ensure all information is accurate before proceeding.")}
								</p>
							</div>
						</div>
					`,
				},
			],
			primary_action_label: __("Start"),
		},

		{
			name: "select_company",
			title: __("Select Company"),
			fields: [
				{
					fieldtype: "HTML",
					options: `
		<div style="
			background:#f0f9ff;
			border:1px solid #bae6fd;
			border-radius:8px;
			padding:16px;
			margin-bottom:12px;
			font-size:13px;
		">
			<strong>${__("Company Selection")}</strong><br>
			${__("Choose the company for which you want to configure ZATCA Phase 2.")}
		</div>
	`
				}
				,
				{
					fieldname: "company",
					label: __("Select Company"),
					fieldtype: "Link",
					options: "Company",
					change: function () {
						const company = this.get_value("company");
						if (company) {
							selected_company = company;
							load_company_related_data(company, current_dialog, true);
							// Prevent multiple triggers by checking a global flag
							if (window.confirmationDialogShownFor === company) {
								return; // Dialog already shown for this company
							}

							// Check for existing ZATCA setup in the selected company
							frappe.call({
								method: "frappe.client.get",
								args: {
									doctype: "Company",
									name: selected_company,
								},
								callback: function (res) {
									if (res && res.message) {
										const zatcaSetup = res.message.custom_basic_auth_from_production;
										// console.log(zatcaSetup)
										if (zatcaSetup) {
											// Show confirmation dialog
											frappe.confirm(
												__(
													"ZATCA setup already exists for this company. Do you want to override the existing setup?"
												),
												function () {
													// User selected "Yes"
													// frappe.msgprint(
													// 	__("Proceeding to the next step.")
													// );
												},
												function () {
													// User selected "No" — exit the wizard entirely
													// (there's no dialog to hide any more, this is a
													// full page, so leave the route instead).
													frappe.msgprint(
														__("Setup canceled. Please select another company or exit the wizard.")
													);
													selected_company = null;
													frappe.set_route("");
												}
											);
											// Mark this company as having shown the dialog
											window.confirmationDialogShownFor = company;
										}
									}
								},
							});
						}
					},
				},
				{
					fieldname: "is_offline_pos",
					label: __("Is Offline POS?"),
					fieldtype: "Check",
					hidden: true,
					onchange: function (e) {
						// Ensure fields_dict is accessible and the field exists
						const isOffline = this.get_value(); // Get checkbox value
						slideData["select_company_is_offline_pos"] = isOffline
						const selectMachineField = this.layout.fields_dict.select_machine;

						if (selectMachineField) {
							const isOffline = this.get_value(); // Get checkbox value
							selectMachineField.df.hidden = !isOffline; // Toggle hidden property
							selectMachineField.refresh();// Apply changes
						} else {
							console.error("Field 'select_machine' not found.");
						}
					},
				},
				{
					fieldname: "select_machine",
					label: __("Select Machine"),
					fieldtype: "Link",
					options: "ZATCA Multiple Setting",
					hidden: true, // Initially hidden
					onchange: function () {
						const selectedMachine = this.get_value();
						slideData["selected_machine"] = selectedMachine; // Save globally
						// console.log("Selected Machine:", selectedMachine); // Log the value
					},
				},
			],
			primary_action_label: __("Next"),
		},
		{
			name: "integration_type",
			title: __("ZATCA Integration Type"),
			fields: [
				{
					fieldtype: "HTML",
					options: `
		<ul style="
			font-size:13px;
			color:#374151;
			margin-bottom:10px;
			padding-left:18px;
		">
			<li><strong>${__("Simulation")}</strong> – ${__("For testing without ZATCA APIs")}</li>
			<li><strong>${__("Sandbox")}</strong> – ${__("ZATCA test environment")}</li>
			<li><strong>${__("Production")}</strong> – ${__("Live ZATCA integration")}</li>
		</ul>
	`
				}
				,
				{
					fieldname: "integration_type",
					label: __("Integration Type"),
					fieldtype: "Select",
					options: ["Simulation", "Sandbox", "Production"],
					default: "Sandbox",
					onchange: function () {
						const selectedIntegrationType = this.get_value();
						if (selectedIntegrationType && selected_company) {
							// Update the custom_select field in the selected company
							frappe.call({
								method: "frappe.client.set_value",
								args: {
									doctype: "Company",
									name: selected_company,
									fieldname: "custom_select",
									value: selectedIntegrationType,
								},

							});
						} else if (!selected_company) {
							frappe.msgprint({
								title: __("Error"),
								indicator: "red",
								message: __("Please select a company first."),
							});
						}
					},
				},
			],
			primary_action_label: __("Next"),
		},


		{
			name: "company_details",
			title: __("Company Details"),
			fields: [
				{
					fieldtype: "HTML",
					options: `
		<div style="
			background:#fff7ed;
			border:1px solid #fed7aa;
			border-radius:8px;
			padding:14px;
			margin-bottom:12px;
			font-size:13px;
		">
			<strong>${__("Important:")}</strong>
			${__("Ensure VAT and address details exactly match your ZATCA registration.")}
		</div>
	`
				},
				{
					fieldname: "company_name",
					label: __("Company Name"),
					fieldtype: "Data",
					read_only: 1,
				},
				{
					fieldname: "vat_number",
					label: __("VAT Registration No"),
					fieldtype: "Data",
				},
				{
					fieldname: "building",
					label: __("Building Number"),
					fieldtype: "Data",
					read_only: 0,
				},
				{ fieldname: "city", label: __("City"), fieldtype: "Data" },
				{ fieldname: "zip", label: __("ZIP Code"), fieldtype: "Data" },
				{
					fieldname: "business_category",
					label: __("Select Business Category"),
					fieldtype: "Select",
					options: [
						{ label: "Retail Trade", value: "RETAIL" },
						{ label: "Wholesale Trade", value: "WHOLESALE" },
						{ label: "Manufacturing", value: "MANUFACTURING" },
						{ label: "Professional Services", value: "SERVICES" },
						{ label: "Information Technology", value: "IT" },
						{ label: "Healthcare Services", value: "HEALTHCARE" },
						{ label: "Education Services", value: "EDUCATION" },
						{ label: "Hospitality & Restaurants", value: "HOSPITALITY" },
						{ label: "Transportation & Logistics", value: "LOGISTICS" },
						{ label: "Construction", value: "CONSTRUCTION" },
						{ label: "Real Estate", value: "REAL_ESTATE" },
						{ label: "Financial Services", value: "FINANCIAL" },
						{ label: "Telecommunications", value: "TELECOM" },
						{ label: "Government / Semi-Government", value: "GOVERNMENT" },
						{ label: "Other", value: "OTHER" }
					]
				},
			],
			primary_action_label: __("Next"),
		},


		{
			name: "create_csr",
			title: __("Create CSR"),
			fields: [
				{
					fieldtype: "HTML",
					options: `
						<div style="
							background:#f8fafc;
							border-left:4px solid #6366f1;
							padding:14px;
							margin-bottom:12px;
							font-size:13px;
						">
							${__("This step generates a <strong>Cryptographic CSR</strong> required by ZATCA.")}
							${__("Click the button below and wait for the generated data.")}
						</div>
					`
				}
				,
				{
					fieldname: "csr_config_box",
					label: __("Generated CSR (Read-only)"),
					fieldtype: "Small Text",
					read_only: 1,
				},
				{
					fieldname: "activate_csr",
					label: __("Create CSR"),
					fieldtype: "Button",
					click: function () {
						if (!selected_company) {
							frappe.msgprint(__("Please select a company before creating CSR."));
							return;
						}

						const isOfflinePOS = slideData["select_company_is_offline_pos"];
						console.log("Retrieved Offline POS Value in Create CSR:", isOfflinePOS);
						const selectedMachine = slideData["selected_machine"];
						if (isOfflinePOS == 1) {
							console.log("Selected Machine in Create CSR:", selectedMachine);

							if (!selectedMachine) {
								frappe.msgprint(__("Please select a machine for offline POS."));
								return;
							}
						}

						frappe.call({
							method: "frappe.client.get_value",
							args: {
								doctype: "Company",
								filters: { name: selected_company },
								fieldname: ["abbr"],
							},
							callback: function (res) {
								if (res && res.message) {
									const company_abbr = res.message.abbr;

									const integrationSlide = slides_settings.find(
										(slide) => slide.name === "integration_type"
									);
									const integrationField = integrationSlide?.fields.find(
										(field) => field.fieldname === "integration_type"
									);
									const portal_type = integrationField?.options
										? integrationField.options[0]
										: null;
									if (portal_type && company_abbr) {
										const doctype = isOfflinePOS
											? "ZATCA Multiple Setting"
											: "Company";

										const name = isOfflinePOS
											? selectedMachine
											: selected_company;

										const csr_config_string = current_dialog.get_value("csr_config_box");
										console.log("CSR Config Data:", csr_config_string);
										frappe.call({
											method: "zatca.zatca.sign_invoice_first.create_csr",
											args: {
												zatca_doc: {
													doctype: doctype,
													name: name,
												}, portal_type, company_abbr, csr_config_string
											},
											callback: function (response) {
												if (response && response.message) {
													const encodedString = response.message.trim();
													// console.log(encodedString)
													// frappe.msgprint(encodedString)
													if (current_dialog) {
														current_dialog.fields_dict.created_csr_config.set_value(encodedString);
														// current_dialog.set_value("created_csr_config", encodedString);
														// current_dialog.refresh();
														csrGenerated = true;
														saveWizardProgress();
													} else {
														frappe.msgprint(__("Dialog reference not found."));
													}

												} else {
													frappe.msgprint(__("Failed to create CSR. Please check the logs."));
												}
											},
										});
									} else {
										frappe.msgprint(__("Invalid portal type or company abbreviation."));
									}
								} else {
									frappe.msgprint(__("Failed to fetch company abbreviation."));
								}
							},
						});
					},
				},
				{
					fieldname: "created_csr_config",
					label: __("Generated CSR Data"),
					fieldtype: "Code",
					read_only: 1,
				},



			],
			primary_action_label: __("Next"),
			// Added primary action label
		}
		,
		{
			name: "enter_otp",
			title: __("Enter OTP"),
			fields: [
				{
					fieldtype: "HTML",
					options: `
		<div style="
			background:#fef2f2;
			border:1px solid #fecaca;
			border-radius:8px;
			padding:14px;
			margin-bottom:12px;
			font-size:13px;
		">
			<strong>${__("OTP Required")}</strong><br>
			${__("Enter the OTP received from ZATCA portal. This OTP can be used only once.")}
		</div>
	`
				}
				,
				{
					fieldname: "otp",
					label: __("OTP"),
					fieldtype: "Data",
				},

				{
					fieldname: "activate_csid",
					label: __("Activate Compliance CSID"),
					fieldtype: "Button",
					click: function () {
						const otpValue = current_dialog.get_value("otp"); // Get the OTP value from the dialog
						if (!otpValue || otpValue.trim() === "") {
							showFieldError(current_dialog, "otp", __("Please enter the OTP before proceeding."));
							return;
						}
						clearFieldError(current_dialog, "otp");

						if (!selected_company) {
							frappe.msgprint(__("Please select a company before activating CSID."));
							return;
						}
						const isOfflinePOS = slideData["select_company_is_offline_pos"];
						console.log("Retrieved Offline POS Value in Create CSR:", isOfflinePOS);
						const selectedMachine = slideData["selected_machine"];
						if (isOfflinePOS == 1) {
							console.log("Selected Machine in Create CSR:", selectedMachine);

							if (!selectedMachine) {
								frappe.msgprint(__("Please select a machine for offline POS."));
								return;
							}
						}
						// Step 1: Save the OTP in the company document
						const doctype = isOfflinePOS ? "ZATCA Multiple Setting" : "Company";
						const name = isOfflinePOS ? selectedMachine : selected_company;
						frappe.call({
							method: "frappe.client.set_value",
							args: {
								doctype: doctype,
								name: name,
								fieldname: "custom_otp",
								value: otpValue.trim(),
							},
							callback: function (response) {
								if (response && response.message) {

									frappe.call({
										method: "frappe.client.get_value",
										args: {
											doctype: "Company",
											filters: { name: selected_company },
											fieldname: ["abbr"],
										},
										callback: function (res) {
											if (res && res.message) {
												const company_abbr = res.message.abbr;

												// Safely fetch portal_type
												const integrationSlide = slides_settings.find(
													(slide) => slide.name === "integration_type"
												);
												const integrationField = integrationSlide?.fields.find(
													(field) => field.fieldname === "integration_type"
												);
												const portal_type = integrationField?.options
													? integrationField.options[0]
													: null;

												if (portal_type && company_abbr) {
													const doctype = isOfflinePOS
														? "ZATCA Multiple Setting"
														: "Company";
													const name = isOfflinePOS
														? selectedMachine
														: selected_company;
													// Step 3: Generate CSID
													frappe.call({
														method: "zatca.zatca.sign_invoice_first.create_csid",
														args: {
															zatca_doc: {
																doctype: doctype,
																name: name,
															}, portal_type, company_abbr
														},
														callback: function (response) {
															if (response && response.message) {

																const encodedString = response.message.trim();

																if (current_dialog) {
																	current_dialog.set_value("basic_auth_from_csid", encodedString);
																	current_dialog.refresh();
																	csidGenerated = true;
																	saveWizardProgress();

																	frappe.show_alert(
																		{
																			message: __("CSID generated successfully"),
																			indicator: "green",
																		},
																		5 // seconds
																	);
																} else {
																	frappe.msgprint(
																		__("Dialog reference not found.")
																	);
																}
															} else {
																frappe.msgprint(
																	__("Failed to generate CSID. Please check the logs.")
																);
															}
														},
													});
												} else {
													frappe.msgprint(__("Invalid portal type or company abbreviation."));
												}
											} else {
												frappe.msgprint(__("Failed to fetch company abbreviation."));
											}
										},
									});
								} else {
									frappe.msgprint(__("Failed to save OTP. Please try again."));
								}
							},
						});
					},
				},

				{
					fieldname: "basic_auth_from_csid",
					label: __("Basic Auth from CSID"),
					fieldtype: "Long Text",
				},
			],
			primary_action_label: __("Next"),
		},
		{
			name: "zatca_compliance_check",
			title: __("ZATCA Compliance Check"),
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "compliance_table",
					options: `<div id="zatca-compliance-table"></div>`
				}
			],
			primary_action_label: __("Next")
		}
		,
		{
			name: "final_csid_generation",
			title: __("Final CSID Generation"),
			fields: [
				{
					fieldtype: "HTML",
					options: `
		<div style="
			background:#eef2ff;
			border:1px solid #c7d2fe;
			border-radius:8px;
			padding:16px;
			margin-bottom:12px;
			font-size:13px;
		">
			<strong>${__("Final Step:")}</strong>
			${__("This will generate your <strong>Production CSID</strong>.")}
			${__("Once generated, invoices will be sent to ZATCA live.")}
		</div>
	`
				}
				,
				{
					fieldname: "final_csid",
					label: __("Generate Final CSIDs"),
					fieldtype: "Button",
					click: function () {
						if (!selected_company) {
							frappe.msgprint(__("Please select a company before creating CSR."));
							return;
						}
						const isOfflinePOS = slideData["select_company_is_offline_pos"];
						console.log("Retrieved Offline POS Value in Create CSR:", isOfflinePOS);
						const selectedMachine = slideData["selected_machine"];
						if (isOfflinePOS == 1) {
							console.log("Selected Machine in Create CSR:", selectedMachine);

							if (!selectedMachine) {
								frappe.msgprint(__("Please select a machine for offline POS."));
								return;
							}
						}

						frappe.call({
							method: "frappe.client.get_value",
							args: {
								doctype: "Company",
								filters: { name: selected_company },
								fieldname: ["abbr"],
							},
							callback: function (res) {
								if (res && res.message) {
									const company_abbr = res.message.abbr;



									if (company_abbr) {
										const doctype = isOfflinePOS
											? "ZATCA Multiple Setting"
											: "Company";
										const name = isOfflinePOS
											? selectedMachine
											: selected_company;

										frappe.call({
											method: "zatca.zatca.sign_invoice_first.production_csid",
											args: {
												zatca_doc: {
													doctype: doctype,
													name: name,
												}, company_abbr
											},
											callback: function (response) {
												if (response && response.message) {
													const csid = response.message.trim();

													// Store CSID in textarea (this is fine)
													current_dialog.set_value("final_auth_csid", csid);
													current_dialog.refresh();
													finalCsidGenerated = true;
													saveWizardProgress();

													// ✅ Show success message ONLY now
													const successBox = document.getElementById("final-csid-success");
													if (successBox) {
														successBox.style.display = "block";
													}

													// Copy handler (safe)
													document
														.getElementById("copy-final-csid")
														?.addEventListener("click", () => {
															navigator.clipboard.writeText(csid);
															frappe.show_alert({
																message: __("CSID copied to clipboard"),
																indicator: "green",
															});
														});

													frappe.show_alert({
														message: __("Production CSID generated successfully"),
														indicator: "green",
													});

													const btn = current_dialog.fields_dict.final_csid?.$wrapper.find("button");
													btn?.prop("disabled", true).text("CSID Generated");
												}
												else {
													frappe.msgprint(__("Failed to create CSR. Please check the logs."));
												}
											},
										});
									} else {
										frappe.msgprint(__("Invalid portal type or company abbreviation."));
									}
								} else {
									frappe.msgprint(__("Failed to fetch company abbreviation."));
								}
							},
						});
					},
				},

				{
					fieldname: "final_auth_csid",
					label: __("Final Auth CSID"),
					fieldtype: "Long Text",
				},
				{
					fieldtype: "HTML",
					fieldname: "final_csid_message",
					options: `
    <div
      id="final-csid-success"
      style="
        display:none;
        background:#ecfdf5;
        border:1px solid #a7f3d0;
        border-radius:8px;
        padding:14px;
        font-size:13px;
      "
    >
      <strong>✅ ${__("Production CSID Generated")}</strong><br>
      ${__("Your system is now live with ZATCA.")}<br><br>

      <button class="btn btn-sm btn-primary" id="copy-final-csid">
        ${__("Copy CSID")}
      </button>
    </div>
  `
				}


			],
			primary_action_label: __("Next"),
		},
		{
			name: "steps_to_follow",
			title: __("Steps to Follow Next"),
			fields: [
				{
					fieldname: "success_message",
					fieldtype: "HTML",
					options: `
						<div style="
							display:flex;
							justify-content:center;
						">
							<div style="
								background:#ffffff;
								border-radius:12px;
								padding:32px;
								max-width:520px;
								width:100%;
								box-shadow:0 8px 24px rgba(0,0,0,0.08);
								text-align:center;
							">
								<h2 style="color:#16a34a; margin-bottom:10px;">✅ ${__("Success")}</h2>
								<p style="font-size:14px; color:#374151;">
									${__("ZATCA Phase-2 onboarding is now complete.")}
								</p>
								<hr style="margin:16px 0;">
								<p style="font-size:13px; color:#6b7280;">
									• ${__("Invoices will be sent automatically upon submission")}<br>
									• ${__("You can update settings from <strong>Company → ZATCA Settings</strong>")}
								</p>
							</div>
						</div>
					`,
				},
			],
			primary_action_label: __("Submit"),
		},
	];

	// --- Persistent full-page wizard shell ------------------------------
	// Rendered once. Only the fields inside `.zatca-wizard-fields` get
	// swapped per step, so navigating feels like updating one screen rather
	// than closing and reopening separate popups.
	const $shell = $(`
		<div class="zatca-wizard-shell">
			<style>
				.zatca-wizard-shell { max-width: 900px; margin: 0 auto; }
				.zatca-wizard-topbar { display:flex; align-items:center; gap:10px; padding:16px 0 12px 0; }
				.zatca-wizard-topbar img { height:28px; }
				.zatca-wizard-topbar span { font-size:16px; font-weight:600; color:var(--text-color, #1f2937); }
				.zatca-steps-row { display:flex; align-items:flex-start; padding:14px 16px; background:#f9fafb; border:1px solid #e2e2e2; border-radius:8px; margin-bottom:20px; }
				.zatca-step-item { display:flex; flex-direction:column; align-items:center; gap:4px; flex-shrink:0; }
				.zatca-step { width:22px;height:22px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;flex-shrink:0; }
				.zatca-step-done { background:#2e844a;color:#fff; }
				.zatca-step-active { background:#2490ef;color:#fff;box-shadow:0 0 0 3px rgba(36,144,239,.25); }
				.zatca-step-upcoming { background:#e2e2e2;color:#8d99a6; }
				.zatca-step-label { font-size:10px; text-align:center; max-width:76px; line-height:1.2; }
				.zatca-step-label-done, .zatca-step-label-active { color:#1f2937; font-weight:500; }
				.zatca-step-label-upcoming { color:#8d99a6; }
				.zatca-step-sep { flex:1; height:2px; background:#e2e2e2; margin-top:11px; }
				.zatca-field-invalid { border-color:#e03131 !important; box-shadow:0 0 0 1px rgba(224,49,49,.15) !important; }
				.zatca-wizard-fields { min-height: 240px; padding-bottom: 16px; }
				.zatca-wizard-footer { display:flex; justify-content:space-between; align-items:center; padding:16px 0 32px 0; border-top:1px solid #e2e2e2; margin-top:8px; position:sticky; bottom:0; background:var(--fg-color, #fff); }
			</style>
			<div class="zatca-wizard-topbar">
				<img src="/assets/zatca/images/zatca-logo.png" alt="Sowaan" />
				<span>${__("ZATCA Phase 2 Setup")}</span>
			</div>
			<div class="zatca-steps-row"></div>
			<div class="zatca-wizard-fields"></div>
			<div class="zatca-wizard-footer">
				<button class="btn btn-default zatca-prev-btn">${__("Previous")}</button>
				<button class="btn btn-primary zatca-next-btn">${__("Next")}</button>
			</div>
		</div>
	`).appendTo(page.body);

	const $wizard_steps_row = $shell.find(".zatca-steps-row");
	const $wizard_fields = $shell.find(".zatca-wizard-fields");
	const $prev_btn = $shell.find(".zatca-prev-btn");
	const $next_btn = $shell.find(".zatca-next-btn");

	function render_slide(slide) {
		$wizard_fields.empty();

		const field_group = new frappe.ui.FieldGroup({
			fields: slide.fields,
			parent: $wizard_fields[0],
		});
		field_group.make();
		current_dialog = field_group;

		if (slide.name === "company_details") {
			// Pre-fill data when arriving at company_details slide
			if (selected_company) {
				load_company_related_data(selected_company, field_group);
			}
		}

		if (slideData[slide.name]) {
			field_group.set_values(slideData[slide.name]);
		}

		updateStepIndicator(current_slide_index);
		if (slide.name === "zatca_compliance_check") {
			renderComplianceTable(field_group);
		}
		applyTooltips({ dialog: field_group }, unifiedTooltips);

		field_group.wrapper
			.find('button[data-fieldname="activate_csr"]')
			.addClass("btn-primary btn-lg");

		field_group.wrapper
			.find('button[data-fieldname="activate_csid"]')
			.addClass("btn-warning btn-lg");

		field_group.wrapper
			.find('button[data-fieldname="final_csid"]')
			.addClass("btn-danger btn-lg");

		if (slide.name === "create_csr") {
			field_group.set_value("csr_config_box", csr_config.replace(/^\s+|\s+$/gm, ""));
		}

		$prev_btn.toggle(current_slide_index > 0);
		$next_btn.text(slide.primary_action_label || __("Next"));

		$shell[0].scrollIntoView({ block: "start", behavior: "instant" });
	}

	function go_to_next_step() {
		const slide = slides_settings[current_slide_index];
		const values = current_dialog.get_values(true); // ignore_errors: validated manually below

		slideData[slide.name] = values;
		if (slide.name === "final_csid_generation") {

			// Set 'custom_zatca_invoice_enabled' to 1 in Company
			frappe.call({
				method: "frappe.client.set_value",
				args: {
					doctype: "Company",
					name: selected_company,  // Ensure 'selected_company' has the current company name
					fieldname: "custom_zatca_invoice_enabled",
					value: 1,
				},
				callback: function (response) {
					if (response && response.message) {
						console.log(__("✅ 'ZATCA Invoice Enabled' has been activated for the company."));
					} else {
						frappe.msgprint(__("⚠️ Failed to enable 'ZATCA Invoice'. Please check logs."));
					}
				}
			});
			current_dialog.fields_dict.final_csid_message.$wrapper.hide();
		}

		if (slide.name === "zatca_compliance_check") {
			const hasRunAny = Object.keys(complianceState).length > 0;

			if (!hasRunAny) {
				frappe.msgprint(__("Please run the compliance checks first."));
				return;
			}

			const allPassed = COMPLIANCE_TESTS.every(
				t => complianceState[t.key] === true
			);

			if (!allPassed) {
				frappe.msgprint(
					__("⚠️ All compliance checks must pass before continuing.")
				);
				return;
			}
		}

		if (slide.name === "create_csr" && !csrGenerated) {
			frappe.msgprint(__("Please click \"Create CSR\" before continuing."));
			return;
		}

		if (slide.name === "enter_otp" && !csidGenerated) {
			frappe.msgprint(__("Please click \"Activate Compliance CSID\" before continuing."));
			return;
		}

		if (slide.name === "final_csid_generation" && !finalCsidGenerated) {
			frappe.msgprint(__("Please click \"Generate Final CSIDs\" before continuing."));
			return;
		}

		if (slide.name === "integration_type") {
			if (!values.integration_type) {
				showFieldError(current_dialog, "integration_type", __("Please select an integration type."));
				return;
			}
			clearFieldError(current_dialog, "integration_type");
		}
		if (slide.name === "select_company") {
			if (!values.company) {
				showFieldError(current_dialog, "company", __("Please select a company to proceed."));
				return;
			}
			clearFieldError(current_dialog, "company");
			fetch_company_details(values.company);
		}

		if (slide.name === "company_details") {
			const savedData = slideData[slide.name];
			if (savedData) {
				current_dialog.set_values(savedData);
			}
			clearFieldErrors(current_dialog, ["vat_number", "city", "business_category"]);
			if (!values.vat_number || !values.city || !values.business_category) {
				if (!values.vat_number) {
					showFieldError(current_dialog, "vat_number", __("VAT Registration No is required."));
				}
				if (!values.city) {
					showFieldError(current_dialog, "city", __("City is required."));
				}
				if (!values.business_category) {
					showFieldError(current_dialog, "business_category", __("Please select a business category."));
				}
				return;
			}
			frappe.call({
				method: "frappe.client.set_value",
				args: {
					doctype: "Company",
					name: selected_company,  // Ensure 'selected_company' has the current company
					fieldname: {
						"custom_zatca__location_for_csr_configuratoin": values.city,  // Save city
						"custom_zatca__company_category_for_csr_configuration": values.business_category  // Save business category
					},
				},
				callback: function (response) {
					if (response && response.message) {
						console.log(__("✅ Company details have been updated successfully."));
					} else {
						frappe.msgprint(__("⚠️ Failed to update Company details. Please try again."));
					}
				}
			});


			generate_csr_config(current_dialog.get_values(true));
		}


		if (current_slide_index < slides_settings.length - 1) {
			current_slide_index++;
			saveWizardProgress();
			render_slide(slides_settings[current_slide_index]);
		} else {
			submit_wizard(values);
			clearWizardProgress();
		}
	}

	function go_to_previous_step() {
		if (current_slide_index > 0) {
			slideData[slides_settings[current_slide_index].name] = current_dialog.get_values(true);
			current_slide_index--;
			saveWizardProgress();
			render_slide(slides_settings[current_slide_index]);
		}
	}

	$next_btn.on("click", go_to_next_step);
	$prev_btn.on("click", go_to_previous_step);


	function fetch_company_details(company) {
		if (!company) return;
		selected_company = company;
	}

	function generate_csr_config(values) {
		const vat_number = values.vat_number || "";
		const city = values.city ? values.city.toUpperCase() : "N/A";
		const business_category = values.business_category || "N/A";

		const hexSegment = () => Math.random().toString(16).substr(2, 8);

		csr_config = `
		  csr.common.name=TST-886431145-${vat_number}
		  csr.serial.number=1-TST|2-TST|3-${hexSegment()}-${hexSegment().substr(0, 4)}-${hexSegment().substr(0, 4)}-${hexSegment().substr(0, 4)}-${hexSegment().substr(0, 12)}
		  csr.organization.identifier=${vat_number}
		  csr.organization.unit.name=${vat_number}
		  csr.organization.name=${values.company_name || "Your Company name"}
		  csr.country.name=SA
		  csr.invoice.type=1100
		  csr.location.address=${city}
		  csr.industry.business.category=${business_category}
		`.trim();
	}

	function submit_wizard(values) {
		// frappe.call({
		// 	method: "frappe.client.set_value",
		// 	args: {
		// 		doctype: "System Settings",
		// 		name: "System Settings",
		// 		fieldname: "custom_zatca_wizard_completed",
		// 		value: 1,
		// 	},
		// 	callback() {
		// 		frappe.msgprint(__("ZATCA Phase 2 onboarding completed successfully."));
		// 		frappe.set_route("desk");
		// 	},
		// });
		frappe.msgprint(__("Thank You! Successfully completed ZATCA Phase 2 integration."));
	}

	function prefill_default_company() {
		const default_company = frappe.defaults.get_user_default("Company");
		if (default_company && current_dialog && !selected_company) {
			current_dialog.set_value("company", default_company);
			selected_company = default_company;

			load_company_related_data(default_company, current_dialog);
		}
	}

	const saved_progress = loadWizardProgress();
	if (saved_progress && saved_progress.current_slide_index > 0) {
		frappe.confirm(
			__("You have an in-progress ZATCA setup. Resume where you left off?"),
			() => {
				current_slide_index = saved_progress.current_slide_index;
				slideData = saved_progress.slideData || {};
				selected_company = saved_progress.selected_company || null;
				csrGenerated = !!saved_progress.csrGenerated;
				csidGenerated = !!saved_progress.csidGenerated;
				finalCsidGenerated = !!saved_progress.finalCsidGenerated;
				Object.assign(complianceState, saved_progress.complianceState || {});
				render_slide(slides_settings[current_slide_index]);
				prefill_default_company();
			},
			() => {
				clearWizardProgress();
				render_slide(slides_settings[current_slide_index]);
				prefill_default_company();
			}
		);
	} else {
		render_slide(slides_settings[current_slide_index]);
		prefill_default_company();
	}
};

function load_company_related_data(company, dialog, overwrite = false) {
	if (!company || !dialog) return;

	// 1️⃣ Load Company master data
	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "Company",
			name: company,
		},
		callback(res) {
			if (!res.message) return;

			const c = res.message;

			// Only set if empty OR overwrite explicitly
			if (overwrite || !dialog.get_value("company_name")) {
				dialog.set_value("company_name", c.company_name);
			}

			if (overwrite || !dialog.get_value("vat_number")) {
				dialog.set_value("vat_number", c.tax_id || "");
			}
		},
	});

	// 2️⃣ Load linked Address (Company → Address via Dynamic Link)
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Address",
			filters: [
				["Dynamic Link", "link_doctype", "=", "Company"],
				["Dynamic Link", "link_name", "=", company],
			],
			fields: [
				"custom_building_number",
				"city",
				"pincode",
			],
			limit_page_length: 1,
		},
		callback(res) {
			if (!res.message || !res.message.length) return;

			const addr = res.message[0];

			if (overwrite || !dialog.get_value("building")) {
				dialog.set_value("building", addr.custom_building_number || "");
			}
			if (overwrite || !dialog.get_value("city")) {
				dialog.set_value("city", addr.city || "");
			}
			if (overwrite || !dialog.get_value("zip")) {
				dialog.set_value("zip", addr.pincode || "");
			}
		},
	});
}

function applyTooltips(context, fieldsWithTooltips) {
	fieldsWithTooltips.forEach((field) => {
		let fieldContainer;
		if (context.fields_dict && context.fields_dict[field.fieldname]) {
			fieldContainer = context.fields_dict[field.fieldname];
		}
		else if (context.dialog && context.dialog.fields_dict && context.dialog.fields_dict[field.fieldname]) {
			fieldContainer = context.dialog.fields_dict[field.fieldname];
		}
		else if (context.page) {
			fieldContainer = $(context.page).find(`[data-fieldname="${field.fieldname}"]`).closest('.frappe-control');
		}
		if (!fieldContainer) {
			// console.error(`Field '${field.fieldname}' not found in the provided context.`);
			return;
		}
		const fieldWrapper = fieldContainer.$wrapper || $(fieldContainer); // Handle both Doctype/Dialog and Page contexts
		if (!fieldWrapper || fieldWrapper.length === 0) {
			// console.error(`Field wrapper for '${field.fieldname}' not found.`);
			return;
		}
		let labelElement;
		if (fieldWrapper.find('label').length > 0) {
			labelElement = fieldWrapper.find('label').first();
		} else if (fieldWrapper.find('.control-label').length > 0) {
			labelElement = fieldWrapper.find('.control-label').first();
		}
		if (!labelElement && (context.dialog || context.page)) {
			labelElement = fieldWrapper.find('.form-control').first();
		}

		if (!labelElement || labelElement.length === 0) {
			// console.error(`Label for field '${field.fieldname}' not found.`);
			return;
		}
		// Prevent duplicate tooltips
		if (!$(labelElement).data("bs.tooltip")) {
			let tooltipText = field.text || "";

			// Optional: append links
			if (field.links && field.links.length) {
				tooltipText += "<br><br>" + field.links
					.map(link => `<a href="${link}" target="_blank">Learn more</a>`)
					.join("<br>");
			}

			$(labelElement)
				.attr("data-bs-toggle", "tooltip")
				.attr("data-bs-html", "true")
				.attr("title", tooltipText)
				.tooltip({
					container: "body",
					placement: "right",
					html: true,
					sanitize: false,
					template: `
		<div class="tooltip" role="tooltip">
			<div class="tooltip-arrow"></div>
			<div class="tooltip-inner text-start"></div>
		</div>
	`
				});
		}

	});
};
