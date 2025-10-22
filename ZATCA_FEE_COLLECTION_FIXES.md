# ZATCA Fee Collection Fixes

## Issues Fixed

This document summarizes the fixes applied to resolve ZATCA validation errors when submitting fee collections.

### 1. **BR-CO-15: Invoice Total Amount with VAT (BT-112)** ✅
**Error**: Invoice total amount with VAT calculation was incorrect.

**Fix**: 
- Ensured consistent decimal formatting (2 decimal places) for all monetary amounts
- Fixed calculation: `TaxInclusiveAmount = LineExtensionAmount + TaxAmount`
- Applied proper rounding before addition to avoid floating-point errors

**Changed in**: `fee_tax_Data()` function

### 2. **certificate-permissions: VAT Number Mismatch** ✅
**Error**: User only allowed to use the VAT number that exists in the authentication certificate.

**Fix**:
- Added validation to ensure Company VAT/Tax ID exists before submission
- Added proper error message if VAT ID is missing
- Ensured the VAT number is correctly populated in `cbc:CompanyID`

**Changed in**: `fee_company_Data()` function

### 3. **BR-KSA-51: Line Amount with VAT Calculation** ✅
**Error**: The line amount with VAT (KSA-12) must be Invoice line net amount (BT-131) + Line VAT amount (KSA-11).

**Fix**:
- Fixed `cbc:RoundingAmount` calculation for each invoice line
- Formula: `LineTotal = LineExtensionAmount + LineTaxAmount`
- Applied consistent decimal formatting (2 places)

**Changed in**: `fee_item_data()` function

### 4. **BR-KSA-66: Seller Postal Code Validation** ✅
**Error**: Seller postal code (BT-38) must be 5 digits.

**Fix**:
- Added validation to ensure postal code is exactly 5 digits
- Added error message if postal code doesn't meet requirements
- Default fallback to "00000" if missing

**Changed in**: `fee_company_Data()` function

### 5. **BR-KSA-F-08 & BR-KSA-F-13: Invalid CRN Values** ✅
**Error**: The value provided in Other Seller ID (BT-29) or Other Buyer ID (BT-46) for the scheme ID 'CRN' appears to be incorrect.

**Fix**:
- Changed buyer/student ID scheme from "CRN" to "NAT" (National ID)
- CRN is for companies, NAT is for individuals/students
- Added validation for company CRN to ensure it exists

**Changed in**: `fee_customer_Data()` function

### 6. **BR-KSA-F-06-C9: District Field Character Limits** ✅
**Error**: Field character limits for the Seller Address - District field (KSA-3) have not been met (min 1, max 127 characters).

**Fix**:
- Added validation to ensure district/subdivision name is between 1-127 characters
- Truncates to 127 characters if exceeded
- Provides default "District" if empty

**Changed in**: `fee_company_Data()` and `fee_customer_Data()` functions

## Additional Improvements

1. **Buyer Postal Code Validation**
   - Ensured buyer postal code is also 5 digits
   - Auto-pads or trims to exactly 5 digits

2. **Null/Empty Value Handling**
   - Added proper default values for all required fields
   - Prevents empty strings or null values in XML

3. **Consistent Decimal Formatting**
   - All monetary amounts now use `.2f` formatting
   - Ensures ZATCA receives properly formatted numbers

## Testing Checklist

Before submitting to ZATCA, ensure:

- [ ] Company has valid Tax ID/VAT Number
- [ ] Company has valid Registration Number (CRN)
- [ ] Company address has 5-digit postal code
- [ ] Company address district is 1-127 characters
- [ ] Student has valid National ID (or use default)
- [ ] Fee collection has linked Fees documents with tax details
- [ ] All amounts calculate correctly (check line totals match)

## API Submission Flow

1. **Validation**: Document is validated against ZATCA schema
2. **Signature**: Digital signature is applied using company certificate
3. **Submission**: Sent to ZATCA reporting API (B2C) or clearance API (B2B)
4. **Response**: Check for success (200) or warnings (202)

## Common Warnings (Non-blocking)

- **BR-KSA-98**: Invoice submitted after 24 hours - informational only
- Other warnings don't prevent submission but should be reviewed

## Critical Errors (Blocking)

If you still encounter errors:

1. **Verify Certificate**: Ensure VAT number in certificate matches Company Tax ID
2. **Check Address**: Postal codes must be exactly 5 digits
3. **Validate Amounts**: All line totals must equal sum of tax-exclusive + tax amounts

## Support

For additional assistance:
- Review ZATCA documentation: https://zatca.gov.sa
- Check certificate details in Company Settings
- Verify all custom fields are properly set up
