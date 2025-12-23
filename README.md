# ZATCA E-Invoicing (Fatoora)

A comprehensive Frappe/ERPNext application for Saudi Arabia's ZATCA (Zakat, Tax and Customs Authority) E-Invoicing Phase-2 compliance. This app enables businesses to generate, sign, and submit e-invoices in accordance with Saudi Arabian tax regulations.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Technical Details](#technical-details)
- [Support](#support)
- [Contributing](#contributing)
- [License](#license)

## Overview

The ZATCA E-Invoicing app implements Saudi Arabia's mandatory e-invoicing requirements (also known as "Fatoora"). This solution ensures full compliance with ZATCA Phase-2 regulations, supporting both simplified and standard tax invoices with digital signatures, QR code generation, and direct integration with ZATCA's systems.

### Key Capabilities

- **Simplified Tax Invoices**: B2C transactions with QR code generation
- **Standard Tax Invoices**: B2B transactions with full XML structure
- **Digital Signatures**: Cryptographic signing using ECDSA (SECP256K1)
- **ZATCA Integration**: Direct API integration for invoice submission and validation
- **Compliance Checking**: Built-in compliance validation tools
- **Multi-Company Support**: Handle multiple entities with separate configurations

## Features

### 🔐 Security & Compliance

- **CSR Generation**: Create Certificate Signing Requests with company-specific data
- **Private Key Management**: Secure generation and storage of cryptographic keys
- **Digital Signatures**: XML invoice signing using X.509 certificates
- **Certificate Lifecycle**: Support for both compliance (CCSID) and production (PCSID) certificates

### 📄 Invoice Management

- **XML Generation**: UBL 2.1 compliant XML invoices
- **QR Code Generation**: TLV-encoded QR codes for simplified invoices
- **Invoice Hashing**: SHA-256 hashing for invoice integrity
- **PIH (Previous Invoice Hash)**: Cryptographic chaining of invoices
- **ICV (Invoice Counter Value)**: Sequential invoice numbering

### 🔌 ZATCA API Integration

- **Sandbox Testing**: Test invoices in ZATCA sandbox environment
- **Simulation Mode**: Pre-production validation
- **Production Mode**: Live invoice submission
- **Compliance Checks**: Automated validation against ZATCA rules
- **Success Logging**: Track all successful submissions

### 🎨 User Interface

- **Custom Fields**: Extended Sales Invoice and Company doctypes
- **ZATCA Settings**: Centralized configuration interface
- **Multiple Settings**: Support for different invoice scenarios
- **Status Tracking**: Real-time e-invoice submission status
- **Attachments**: Auto-attach XML and QR codes to invoices

### 📊 Supported Documents

- Sales Invoices
- Credit Notes
- Debit Notes
- Fee Collections (custom implementation)

## Requirements

- **Frappe Framework**: Version 15.0 or higher
- **ERPNext**: Version 15.0 or higher
- **Python**: 3.10 or higher
- **Dependencies**:
  - `asn1` ~= 2.7.0
  - Standard cryptography libraries (included with Frappe)

## Installation

### Using Bench

1. **Navigate to your bench directory**:
   ```bash
   cd frappe-bench
   ```

2. **Get the app from GitHub**:
   ```bash
   bench get-app https://github.com/sowaan/zatca.git
   ```
   
   Or for local development:
   ```bash
   bench get-app /path/to/zatca
   ```

3. **Install the app on your site**:
   ```bash
   bench --site your-site-name install-app zatca
   ```

4. **Run database migrations**:
   ```bash
   bench --site your-site-name migrate
   ```

5. **Restart bench**:
   ```bash
   bench restart
   ```

### Manual Installation

1. Clone the repository into the `apps` directory:
   ```bash
   cd frappe-bench/apps
   git clone https://github.com/sowaan/zatca.git
   ```

2. Install dependencies:
   ```bash
   cd zatca
   pip install -e .
   ```

3. Install on site and migrate:
   ```bash
   bench --site your-site-name install-app zatca
   bench --site your-site-name migrate
   ```

## Configuration

### Initial Setup

1. **Navigate to ZATCA Settings**:
   - Go to: `Setup > ZATCA > ZATCA Setting`

2. **Configure Company Details**:
   - Select your company
   - Enter company abbreviation
   - Enable ZATCA invoice processing

3. **CSR Configuration**:
   Create a CSR configuration in your Company doctype with the following format:
   ```
   csr.common.name=Your Company Name
   csr.serial.number=1-Your|2-VAT123456|3-Invoice
   csr.organization.identifier=VAT-Number-Without-3
   csr.organization.unit.name=Your Unit
   csr.organization.name=Your Organization
   csr.country.name=SA
   csr.invoice.type=1100
   csr.location.address=Your Address
   csr.industry.business.category=Your Industry
   ```

4. **Generate Cryptographic Materials**:
   - Click "Create CSR" to generate CSR and private keys
   - The system will automatically generate and store private/public keys

5. **Obtain Certificates**:
   
   **Compliance Phase (Testing)**:
   - Enter OTP received from ZATCA
   - Generate compliance CSID (Certificate ID)
   - Test with sample invoices
   - Verify all compliance checks pass
   
   **Production Phase**:
   - Generate production CSID
   - Configure production credentials

6. **API Endpoints**:
   - Sandbox URL: For initial development
   - Simulation URL: For pre-production testing
   - Production URL: For live invoices

### Company Configuration

In the Company doctype, configure:
- **VAT Number**: Your 15-digit VAT number
- **CSR Config**: Certificate signing request parameters
- **Address Details**: Complete address information
- **Custom Fields**: Populated automatically by the app

### Settings Options

- **Attach XML with Invoice**: Automatically attach generated XML
- **Attach QR Code**: Include QR code images
- **Send to ZATCA**: Enable automatic submission
- **Background Processing**: Process invoices asynchronously

## Usage

### Creating E-Invoices

#### Standard Invoice (B2B)

1. Create a Sales Invoice as usual in ERPNext
2. Ensure customer has valid VAT number and address
3. Submit the invoice
4. The system will automatically:
   - Generate UBL 2.1 XML
   - Create digital signature
   - Generate invoice hash
   - Submit to ZATCA (if enabled)

#### Simplified Invoice (B2C)

1. Create a Sales Invoice for B2C customer
2. Submit the invoice
3. System generates:
   - Simplified XML structure
   - QR code with TLV encoding
   - Cryptographic hash
   - Auto-submits to ZATCA

### Manual Operations

**Check Compliance**:
```python
# From ZATCA Settings
1. Select validation type
2. Choose sample invoice
3. Click "Check Compliance"
```

**Regenerate Invoice**:
```python
# From Sales Invoice
1. Click "Actions"
2. Select "Regenerate ZATCA Invoice"
```

### API Methods

```python
# Generate QR Code
from zatca.zatca.zatcaqr import get_fatoora_qr

qr_image = get_fatoora_qr(
    company="Company Name",
    tax_number="VAT123456",
    date="2025-12-23T15:30:00",
    total="1150.00",
    tax_amount="150.00"
)

# Sign Invoice
from zatca.zatca.sign_invoice import get_signed_invoice_xml

signed_xml = get_signed_invoice_xml(invoice_number="INV-001")
```

## Technical Details

### Architecture

```
zatca/
├── zatca/                      # Main module
│   ├── sign_invoice.py         # Cryptographic signing
│   ├── createxml.py           # XML generation (UBL 2.1)
│   ├── zatcaqr.py             # QR code generation
│   ├── validations.py         # Business rule validations
│   ├── check_certificate_vat.py # Certificate verification
│   └── doctype/               # Custom doctypes
│       ├── zatca_setting/     # Configuration
│       ├── zatca_multiple_setting/
│       └── zatca_success_log/  # Submission logs
├── public/js/                 # Client-side scripts
│   ├── our_sales_invoice.js   # Sales Invoice customization
│   ├── company.js             # Company enhancements
│   └── address.js             # Address validations
└── fixtures/                  # Custom fields
```

### XML Structure

The app generates UBL 2.1 compliant XML with:
- **Invoice Header**: ICV, PIH, UUID, timestamps
- **Parties**: Supplier and customer details
- **Lines**: Item details with taxes
- **Totals**: Tax breakdown and totals
- **Signature**: UBL signature extension

### Cryptographic Flow

1. **Key Generation**: ECDSA with SECP256K1 curve
2. **CSR Creation**: X.509 certificate request with custom OIDs
3. **Certificate Issuance**: ZATCA provides signed certificate
4. **Invoice Signing**: 
   - Canonicalize XML
   - Hash signed properties
   - Sign hash with private key
   - Embed signature in XML

### QR Code Format

TLV (Tag-Length-Value) encoding with:
- Tag 1: Seller Name
- Tag 2: VAT Number
- Tag 3: Timestamp
- Tag 4: Total with VAT
- Tag 5: VAT Amount

### Database Schema

**Custom Fields Added**:
- Sales Invoice: ZATCA status, XML, hash, counter
- Company: CSR config, private key, certificate
- Address: Country code mapping
- Customer: VAT validation fields

## Troubleshooting

### Common Issues

**Certificate Errors**:
- Ensure CSR config is correct
- Verify OTP is valid (expires in 1 hour)
- Check private key exists

**Validation Failures**:
- Verify customer VAT number format
- Ensure address has all required fields
- Check item tax templates

**Submission Errors**:
- Confirm network connectivity to ZATCA
- Validate credentials (Basic Auth)
- Check invoice counter sequence

### Logs

Check logs for debugging:
```bash
bench --site your-site-name console
```

```python
frappe.get_all("ZATCA Success Log", 
    fields=["*"], 
    filters={"invoice_number": "INV-001"}
)
```

## Support

For issues, questions, or feature requests:

- **Publisher**: Sowaan
- **Email**: support@sowaan.com
- **GitHub Issues**: [Create an issue](https://github.com/sowaan/zatca/issues)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Get the app in development mode
bench get-app /path/to/zatca --skip-assets

# Install on a site
bench --site dev.local install-app zatca

# Enable developer mode
bench --site dev.local set-config developer_mode 1

# Watch for changes
bench watch
```

## Roadmap

- [ ] Support for additional document types
- [ ] Enhanced reporting and analytics
- [ ] Batch invoice submission
- [ ] Integration with POS
- [ ] Multi-language support
- [ ] Advanced error recovery

## Compliance Statement

This application is designed to comply with ZATCA's E-Invoicing requirements as per the official specifications. However, users are responsible for:

- Accurate configuration of company and tax details
- Proper testing in sandbox/simulation environments
- Maintaining security of cryptographic materials
- Regular updates to maintain compliance with regulatory changes

## Changelog

### Version 1.0.0
- Initial release
- Phase-2 compliance support
- Simplified and standard invoice types
- QR code generation
- ZATCA API integration
- Compliance checking tools

## License

This project is licensed under the MIT License - see the [LICENSE](license.txt) file for details.

---

**Developed by [Sowaan](mailto:support@sowaan.com)**

*Making ERPNext ZATCA-compliant, one invoice at a time.* 🇸🇦