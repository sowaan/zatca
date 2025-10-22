# ZATCA Certificate Setup Guide

## ⚠️ CRITICAL: Required Before Any ZATCA Integration

This guide shows how to configure ZATCA certificates in your ERPNext Company master. **This is MANDATORY** for ZATCA integration to work with Sales Invoices, Fee Collections, or any other documents.

## Error You're Seeing

If you see this error:
```
No private key data found for the company.
Error in digital signature: No private key data found for the company.
```

**It means you haven't configured ZATCA certificates yet!**

## Solution: Configure Company ZATCA Settings

### Step 1: Get Your ZATCA Certificate Files

You need two files from ZATCA:

1. **Private Key** (`.key` file) - Generated during ZATCA onboarding
2. **Certificate** (`.pem` or `.crt` file) - Issued by ZATCA after compliance

If you don't have these files:
- Go to ZATCA Portal: https://fatoora.zatca.gov.sa/
- Complete the onboarding process
- Generate CSID (Cryptographic Stamp Identifier)
- Download the certificate files

### Step 2: Open Your Certificate Files

Open both files in a **text editor** (Notepad, TextEdit, VS Code, etc.):

**Private Key** looks like:
```
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIL9jC7xZx8L5tISLs1234567890abcdefghijklmnopqrstuvw
xyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890+/=
... (more lines) ...
-----END EC PRIVATE KEY-----
```

**Certificate** looks like:
```
-----BEGIN CERTIFICATE-----
MIICFzCCAbygAwIBAgIGAYZ1234567890abcdefghijklmnopqrstuvwxyz
ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890+/=
... (more lines) ...
-----END CERTIFICATE-----
```

### Step 3: Configure in ERPNext

1. **Login to ERPNext**

2. **Go to Company Master**:
   - Search: "Company" in the search bar
   - Click on your company name

3. **Scroll to "Keys / Certificate for ZATCA"** section

4. **Fill these fields**:

   a. **Private Key** (Custom Private Key):
      - Copy the ENTIRE content from your `.key` file
      - Including `-----BEGIN EC PRIVATE KEY-----` and `-----END EC PRIVATE KEY-----`
      - Paste into the field

   b. **Certificate** (Custom Certificate):
      - Copy the ENTIRE content from your `.pem` or `.crt` file
      - Including `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`
      - Paste into the field

   c. **Company Registration**:
      - Enter your CR number (Commercial Registration)
      - Example: "1234567890"

   d. **Tax ID**:
      - Enter your 15-digit VAT number
      - Must start with 3 and end with 3
      - Example: "312345678912345"

5. **Scroll to "URLs / API EndPoints"** section:

   Fill these URLs:

   **For Production (Live invoices)**:
   - **Reporting API**: `https://gw-fatoora.zatca.gov.sa/e-invoicing/core/invoices/reporting/single`
   - **Clearance API**: `https://gw-fatoora.zatca.gov.sa/e-invoicing/core/invoices/clearance/single`

   **For Testing**:
   - **Compliance API**: `https://gw-fatoora.zatca.gov.sa/e-invoicing/developer-portal`

6. **Save** the Company document

### Step 4: Verify Company Address

ZATCA requires a valid company address:

1. Go to **Address List**
2. Find your company address
3. Make sure:
   - ✅ "Is Your Company Address" is checked
   - ✅ Address Line 1 is filled
   - ✅ City is filled
   - ✅ Pincode is filled
   - ✅ State is filled

### Step 5: Test the Setup

1. Create a **Sales Invoice** or **Fee Collection**
2. Submit it
3. Click "Send to Zatca"
4. You should **NOT** see "No private key data found" error anymore

## Checklist: What You Need

Before testing ZATCA integration, verify:

- [ ] Private Key field in Company is populated (entire key with BEGIN/END)
- [ ] Certificate field in Company is populated (entire certificate with BEGIN/END)
- [ ] Company Registration (CR) is filled
- [ ] Tax ID (VAT number) is filled
- [ ] Reporting API URL is configured
- [ ] Clearance API URL is configured
- [ ] Company address exists with "Is Your Company Address" checked
- [ ] Address has: Line 1, City, Pincode, State

## Common Mistakes

1. ❌ **Only copying part of the certificate**
   - ✅ Copy the ENTIRE file including BEGIN and END markers

2. ❌ **Missing BEGIN/END markers**
   - ✅ Include `-----BEGIN EC PRIVATE KEY-----` and `-----END EC PRIVATE KEY-----`
   - ✅ Include `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`

3. ❌ **Extra spaces or line breaks**
   - ✅ Paste exactly as it appears in the file

4. ❌ **Wrong field (mixing up private key and certificate)**
   - ✅ Private Key goes in "Private Key" field
   - ✅ Certificate goes in "Certificate" field

5. ❌ **No company address**
   - ✅ Create address with "Is Your Company Address" checked

## Need Help?

If you still get errors after setup:

1. Double-check all fields are filled
2. Verify certificate files are correct and not expired
3. Check ZATCA portal for certificate status
4. Check ERPNext error logs for detailed error messages

## Testing vs Production

- **Testing/Compliance**: Use Compliance API endpoint
- **Production**: Use Reporting API (B2C) and Clearance API (B2B)

Make sure you're using the correct endpoint for your environment!

---

**✅ After completing this setup, you can use ZATCA integration with Sales Invoices, Fee Collections, and other documents.**
