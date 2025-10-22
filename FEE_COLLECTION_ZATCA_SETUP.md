# ZATCA Integration for Fee Collections - Setup Guide

## Overview
This document explains how to set up and use ZATCA (Saudi E-Invoicing Phase-2) integration for Fee Collections in ERPNext Education module.

## Architecture

### Data Flow
```
Fee Collections
    └── student_fee_details (Child Table)
            ├── student_id → Student
            └── fees → Fees Document
                    ├── components (Fee Component)
                    ├── taxes (Sales Taxes and Charges)
                    ├── grand_total_before_tax
                    └── total_taxes_and_charges
```

### Key Difference from Sales Invoice
- **Fee Collections** does NOT have direct tax templates
- Tax information comes from **linked Fees documents**
- Each Fees document has:
  - `components` table (fee categories and amounts) - NO tax templates here
  - `taxes` table (Sales Taxes and Charges) - tax amounts and rates
  
## Custom Fields (Already in Fixtures)

The following custom fields are already defined in `zatca/fixtures/custom_field.json`:

### Fee Collections
1. **custom_zatca_status** (Select)
   - Options: "Not Submitted\nREPORTED\nCLEARED"
   - Insert after: "student"
   
2. **custom_uuid** (Data)
   - Label: "ZATCA UUID"
   - Insert after: "posting_time"
   - Read only

## Installation Steps

### 1. Install/Update Custom Fields

Run this command to install the custom fields:

```bash
cd /path/to/frappe-bench
bench --site [your-site-name] migrate
```

This will create the custom fields defined in the fixtures.

### 2. Clear Cache and Restart

```bash
bench clear-cache
bench restart
```

### 3. Reload Fee Collections Doctype

```bash
bench --site [your-site-name] reload-doctype "Fee Collections"
```

## Configuration

### ⚠️ CRITICAL: Company ZATCA Certificate Setup (MUST DO FIRST!)

**Before using any ZATCA integration, you MUST configure ZATCA certificates in your Company master. Skipping this will cause "No private key data found" error.**

#### Step 1: Obtain ZATCA Certificate

1. Go to **ZATCA Portal** (https://fatoora.zatca.gov.sa/)
2. Register your company
3. Complete the onboarding/compliance process
4. Generate **CSID** (Cryptographic Stamp Identifier)
5. Download certificate files:
   - **Private Key** (`.key` file)
   - **Certificate** (`.pem` or `.crt` file)

#### Step 2: Configure Company Document

1. Open **Company** in ERPNext (your company name)
2. Scroll to **"Keys / Certificate for ZATCA"** section
3. Fill these fields:

   **Private Key** (Custom Private Key field):
   ```
   -----BEGIN EC PRIVATE KEY-----
   [Your private key content here]
   -----END EC PRIVATE KEY-----
   ```
   
   **Certificate** (Custom Certificate field):
   ```
   -----BEGIN CERTIFICATE-----
   [Your certificate content here]
   -----END CERTIFICATE-----
   ```
   
   **Company Registration**: Your CR number (e.g., "1234567890")
   
   **Tax ID**: Your VAT number (15 digits starting with 3, ending with 3)

4. Scroll to **"URLs / API EndPoints"** section:
   - **Compliance API** (Testing): `https://gw-fatoora.zatca.gov.sa/e-invoicing/developer-portal`
   - **Reporting API** (B2C/Simplified): `https://gw-fatoora.zatca.gov.sa/e-invoicing/core/invoices/reporting/single`
   - **Clearance API** (B2B/Standard): `https://gw-fatoora.zatca.gov.sa/e-invoicing/core/invoices/clearance/single`

5. **Save** the Company document

#### Step 3: Verify Setup

Check that:
- ✅ Private Key field is populated (entire key with BEGIN/END markers)
- ✅ Certificate field is populated (entire certificate with BEGIN/END markers)  
- ✅ Company Registration (CR number) is filled
- ✅ Tax ID is filled
- ✅ API URLs are configured
- ✅ Company address exists with "Is Your Company Address" checked

**Without this setup, you will get: "No private key data found for the company"**

### Company Settings

Ensure the following are set in Company doctype:

1. **ZATCA Invoice Enabled**: Checked
2. **ZATCA Invoices on Submission**: Checked (for auto-submission)
3. **Production CSID**: Set (from ZATCA onboarding)
4. **PIH**: Will be auto-updated
5. **CSR Config**: Set (from initial setup)
6. **Private Key**: Set (from initial setup)

### Fee Collections Setup

1. Create Fee Collections as normal
2. Add students and link to their Fees documents in `student_fee_details` child table
3. Ensure linked Fees documents have:
   - Components with amounts
   - Taxes table with tax rates (if applicable)
   - Proper posting dates and due dates

## Usage

### Manual Submission

1. **Create and Submit Fee Collection**
   - Go to Fee Collections
   - Create new document
   - Add student fee details (linking to Fees documents)
   - Submit the document

2. **Send to ZATCA**
   - After submission, click the "Send to Zatca" button
   - Wait for response
   - Check `custom_zatca_status` field:
     - "REPORTED" = Success (B2C/Simplified)
     - "CLEARED" = Success (B2B/Standard)
     - "Not Submitted" = Failed

### Automatic Submission

If **"ZATCA Invoices on Submission"** is enabled in Company settings:
- Fee Collections will be automatically sent to ZATCA upon submission
- No manual button click needed

## Features

### ✅ Implemented Features

1. **B2C/Simplified Invoices** (Reporting API)
   - Default mode for fee collections
   - Simplified XML structure
   - Faster processing

2. **Return/Refund Handling**
   - Supports `is_return` = 1
   - Links to `refund_against` field
   - Billing reference in XML

3. **QR Code Generation**
   - Auto-generated TLV-encoded QR code
   - Attached to Fee Collections document

4. **Digital Signature**
   - ECDSA with SHA-256
   - Certificate-based signing

5. **Multi-Student Support**
   - Handles multiple students in one collection
   - Creates separate line items per fee component
   - Student name included in item description

6. **Tax Calculation**
   - Reads from Fees document's taxes table
   - Supports custom tax rates
   - Standard 15% VAT default

## XML Structure

### Invoice Line Items

For each Fees document in `student_fee_details`:
- If Fees has **components**: One line item per component
  - Item name: `{Component Description} - {Student Name}`
  - Amount from component.amount
  - Tax calculated based on Fees taxes table
  
- If Fees has **no components**: Single line item
  - Item name: `Fee - {Student Name} ({Fees ID})`
  - Amount from grand_total_before_tax
  - Tax from total_taxes_and_charges

### Tax Information

```xml
<cac:TaxTotal>
    <cbc:TaxAmount currencyID="SAR">150.00</cbc:TaxAmount>
    <cac:TaxSubtotal>
        <cbc:TaxableAmount currencyID="SAR">1000.00</cbc:TaxableAmount>
        <cbc:TaxAmount currencyID="SAR">150.00</cbc:TaxAmount>
        <cac:TaxCategory>
            <cbc:ID>S</cbc:ID>
            <cbc:Percent>15.00</cbc:Percent>
            <cac:TaxScheme>
                <cbc:ID>VAT</cbc:ID>
            </cac:TaxScheme>
        </cac:TaxCategory>
    </cac:TaxSubtotal>
</cac:TaxTotal>
```

## API Endpoints

### For Manual Triggering

```python
# In Frappe console or custom script
frappe.call({
    method: "zatca.zatca.sign_fee_collection.zatca_Background_fee_collection",
    args: {
        fee_collection_number: "CV-S-00001"
    }
})
```

### Hooks (Automatic)

```python
# In hooks.py
doc_events = {
    "Fee Collections": {
        "on_submit": "zatca.zatca.sign_fee_collection.zatca_Background_fee_on_submit"
    }
}
```

## Troubleshooting

### Common Issues

1. **"Please submit the fee collection before sending to Zatca"**
   - Solution: Make sure docstatus = 1 (submitted)

2. **"Already submitted to Zakat and Tax Authority"**
   - Solution: Fee Collection already has ZATCA status = REPORTED or CLEARED
   - Cannot resubmit same document

3. **"Zatca Invoice is not enabled in Company Settings"**
   - Solution: Enable `custom_zatca_invoice_enabled` in Company

4. **"Production CSID not found"**
   - Solution: Complete ZATCA onboarding and generate Production CSID

5. **"No student_fee_details found"**
   - Solution: Add at least one student fee detail linking to a Fees document

6. **Tax calculation errors**
   - Solution: Ensure linked Fees documents have proper taxes table with rates

### Validation

Before sending to ZATCA, the system checks:
- Fee Collection is submitted (docstatus = 1)
- Not already sent (custom_zatca_status not in REPORTED/CLEARED)
- ZATCA enabled in Company
- Has student_fee_details
- Linked Fees documents exist and are accessible

## Technical Details

### File Structure

```
zatca/
├── zatca/
│   └── zatca/
│       ├── sign_fee_collection.py    # Main backend logic
│       ├── sign_invoice.py           # Shared functions
│       └── createxml.py              # XML utilities
├── public/
│   └── js/
│       └── fee_collection.js         # Frontend button
├── hooks.py                          # Event hooks
└── fixtures/
    └── custom_field.json             # Custom fields
```

### Main Functions

**sign_fee_collection.py:**
- `fee_collection_data()` - Extract basic data, generate UUID
- `fee_doc_Reference()` - Document references, ICV, billing ref for returns
- `fee_customer_Data()` - Student information
- `fee_delivery_And_PaymentMeans()` - Payment details
- `fee_tax_Data()` - Tax calculations from Fees taxes table
- `fee_item_data()` - Line items from Fees components
- `zatca_Background_fee_collection()` - Manual trigger (whitelisted)
- `zatca_Background_fee_on_submit()` - Auto-trigger on submit
- `zatca_Call_fee_collection()` - Main processing
- `reporting_API_fee()` - Send to ZATCA Reporting API (B2C)
- `clearance_API_fee()` - Send to ZATCA Clearance API (B2B)

## Limitations

1. **Currency**: Fee Collections always use SAR (hardcoded)
2. **Tax Templates**: Not supported in Fee Components (uses Fees taxes table instead)
3. **Invoice Type**: Always Simplified (B2C) by default
4. **Payment Mode**: Defaults to Cash (code 10) if not specified

## Best Practices

1. **Always test with Compliance API first** before production
2. **Keep Fees documents properly structured** with taxes table
3. **Use consistent tax rates** (15% standard VAT)
4. **Submit Fee Collections in chronological order**
5. **Monitor ZATCA status field** after submission
6. **Check error logs** if submission fails

## Support

For issues related to:
- **ZATCA Integration**: Check `zatca/zatca/sign_fee_collection.py`
- **XML Generation**: Check `zatca/zatca/createxml.py`
- **Frontend Button**: Check `zatca/public/js/fee_collection.js`
- **Hooks**: Check `zatca/hooks.py`

## Version History

- **v1.0** (2025-10-18): Initial implementation
  - Basic fee collection ZATCA integration
  - Support for multiple students
  - Tax from Fees documents taxes table
  - Return/refund handling
  - QR code generation
  - Digital signatures
