import json
import os

import frappe


def align_custom_field_names():
	"""Rename existing Custom Fields to the names used in this app's fixtures.

	Fixture sync finds each Custom Field by name. When a site already has the same
	dt + fieldname under another name (e.g. an older `custom_custom_` export), the
	lookup misses, the fixture is inserted as new and migrate fails with
	"A field with the name ... already exists in ...".
	"""
	path = frappe.get_app_path("zatca", "fixtures", "custom_field.json")
	if not os.path.exists(path):
		return

	with open(path) as f:
		fixtures = json.load(f)

	for field in fixtures:
		existing = frappe.db.get_value(
			"Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}, "name"
		)
		if not existing or existing == field["name"]:
			continue

		if frappe.db.exists("Custom Field", field["name"]):
			print(f"zatca: skipped renaming Custom Field {existing}, {field['name']} already exists")
			continue

		frappe.rename_doc(
			"Custom Field",
			existing,
			field["name"],
			force=True,
			show_alert=False,
			rebuild_search=False,
		)
		print(f"zatca: renamed Custom Field {existing} -> {field['name']}")

	frappe.db.commit()
