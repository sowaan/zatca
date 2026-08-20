$(function () {
	// frappe.session.user / frappe.user_roles are only populated later during the
	// desk app's own boot sequence (after frappe.provide("frappe.session") merely
	// creates an empty {}). frappe.boot.user is embedded inline in the page's own
	// boot script and is safe to read immediately, so use that instead.
	const boot_user = (frappe.boot && frappe.boot.user) || {};
	const username = boot_user.name;
	if (!username || username === "Guest") return;

	const is_eligible = username === "Administrator" || (boot_user.roles || []).includes("System Manager");
	if (!is_eligible) return;

	const dismiss_key = `zatca_banner_dismissed_${username}_${frappe.datetime.get_today()}`;
	if (localStorage.getItem(dismiss_key)) return;

	frappe.call({
		method: "zatca.zatca.setup_status.get_pending_zatca_companies",
		callback(r) {
			const pending = r.message || [];
			if (!pending.length) return;
			show_zatca_setup_banner(pending, dismiss_key);
		},
	});
});

function show_zatca_setup_banner(companies, dismiss_key) {
	if (document.getElementById("zatca-setup-banner")) return;

	const label =
		companies.length === 1
			? `company "${frappe.utils.escape_html(companies[0])}"`
			: `${companies.length} companies`;

	// `.main-section` is a plain block scroll container (header, #body, footer
	// stacked in normal flow, not flex/grid) — inserting as a sibling right
	// after <header> stacks us below the desk navbar and pushes #body down
	// naturally, with no fixed/sticky positioning or manual offset needed.
	const $banner = $(`
		<div id="zatca-setup-banner" style="
			background:var(--alert-bg-warning);
			color:var(--alert-text-warning);
			border-bottom:1px solid var(--border-color);
			padding:8px 20px;display:flex;
			align-items:center;justify-content:space-between;
			font-size:13px;gap:12px;flex-wrap:wrap;
		">
			<span>ZATCA e-invoicing isn't set up yet for ${label}. Complete the wizard to enable compliant e-invoicing.</span>
			<span style="white-space:nowrap;">
				<button class="btn btn-sm btn-primary" id="zatca-banner-setup" style="margin-right:8px;">${__("Set up ZATCA")}</button>
				<button class="btn btn-sm btn-secondary" id="zatca-banner-dismiss">${__("Remind me later")}</button>
			</span>
		</div>
	`);

	const $header = $(".main-section > header");
	if ($header.length) {
		$header.after($banner);
	} else {
		$("body").prepend($banner);
	}

	$("#zatca-banner-setup").on("click", () => {
		$banner.remove();
		frappe.set_route("zatca-wizard");
	});
	$("#zatca-banner-dismiss").on("click", () => {
		localStorage.setItem(dismiss_key, "1");
		$banner.remove();
	});
}
