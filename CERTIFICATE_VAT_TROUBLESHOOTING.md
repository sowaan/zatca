# ZATCA Certificate VAT Mismatch - Troubleshooting Guide

## Problem
You're getting this error:
```
certificate-permissions: User only allowed to use the vat number that exists in the authentication certificate
```

This means the VAT/Tax ID in your **Company master** doesn't match the VAT number embedded in your **ZATCA certificate**.

---

## Quick Fix - Check Certificate VAT

### Step 1: Run the diagnostic script

Open your Frappe bench terminal and run:

```bash
bench --site [your-site-name] console
```

Then in the Python console:

```python
from zatca.zatca.check_certificate_vat import print_certificate_vat

# Replace 'Your Company Name' with your actual company name
print_certificate_vat('Your Company Name')
```

This will show you:
- The VAT number in your Company master
- The VAT number in your ZATCA certificate
- Whether they match

---

## Step 2: Fix the Mismatch

### Option A: Update Company Tax ID (Recommended)

1. Go to: **Company List** → Open your company
2. Find the field: **Tax ID** (or **VAT Number**)
3. Update it to match the VAT from the certificate (shown in diagnostic output)
4. Save the company
5. Try submitting to ZATCA again

### Option B: Use Correct Certificate

If you have the wrong certificate:
1. Go to your company settings
2. Find the **ZATCA Certificate** field (usually `custom_certificate`)
3. Upload the correct certificate that matches your company's VAT number

---

## Common Scenarios

### Sandbox vs Production

**Important**: If you selected **Sandbox** in ZATCA settings:
- You must use a **SANDBOX certificate** (not production)
- The VAT number must match the sandbox certificate
- Sandbox certificates often have test VAT numbers like `300000000000003`

**If using Sandbox:**
- Set your Company Tax ID to match your sandbox certificate VAT
- OR use production mode with your real certificate

### Certificate Format Issues

The certificate VAT might be in formats like:
- `VATSA-300000000000003` → Extract `300000000000003`
- `300000000000003` → Use as-is

The script handles this automatically.

---

## Manual Check (Alternative Method)

If you can't run the script, manually check your certificate:

### 1. Get your certificate text
From Company → ZATCA Certificate field (custom_certificate)

### 2. Decode it online
Go to: https://www.sslshopper.com/certificate-decoder.html
Paste your certificate

### 3. Look for VAT in these fields:
- Subject → UID
- Subject → organizationIdentifier  
- Subject → serialNumber

### 4. Compare with Company Tax ID
The VAT numbers must match exactly (no spaces, same format)

---

## API Command Alternative

You can also check via Frappe API:

```bash
# From bench directory
bench --site [your-site-name] execute zatca.zatca.check_certificate_vat.check_certificate_vat --args "['Your Company Name']"
```

---

## Still Getting Errors?

If VAT numbers match but you still get the error:

1. **Check Production CSID**: 
   - Company → `custom_basic_auth_from_production` field must be set
   - This is your authentication token from ZATCA

2. **Regenerate Production Certificate**:
   - Your production certificate may be expired or invalid
   - Go through ZATCA onboarding process again

3. **Sandbox Mode Issues**:
   - Ensure sandbox certificate is properly configured
   - Sandbox has different API endpoints

---

## Quick Validation Checklist

Before submitting to ZATCA:

- [ ] Company Tax ID is set
- [ ] Company Tax ID matches certificate VAT exactly
- [ ] Certificate is uploaded in Company
- [ ] Production CSID is set (for production mode)
- [ ] Postal codes are 5 digits
- [ ] Company Registration Number (CRN) is set

---

## Contact Support

If you've verified everything matches but still get errors:
1. Check ZATCA portal for certificate status
2. Verify your company is registered with ZATCA
3. Contact ZATCA support for certificate validation

## Files Modified

The diagnostic script is located at:
`zatca/zatca/check_certificate_vat.py`
