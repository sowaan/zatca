"""
Script to extract and display VAT number from ZATCA certificate
Run this to check what VAT number is in your certificate
"""

import frappe
from cryptography import x509
from cryptography.hazmat.backends import default_backend

@frappe.whitelist()
def check_certificate_vat(company_name):
    """
    Extract VAT number from ZATCA certificate for a company
    This helps diagnose certificate-permissions errors
    """
    try:
        company_doc = frappe.get_doc('Company', company_name)
        
        # Get certificate
        certificate_data_str = company_doc.get("custom_certificate")
        if not certificate_data_str:
            return {
                "success": False,
                "message": f"No certificate found for company {company_name}. Please upload ZATCA certificate first."
            }
        
        # Format certificate to PEM
        certificate_content = certificate_data_str.strip()
        formatted_certificate = "-----BEGIN CERTIFICATE-----\n"
        formatted_certificate += "\n".join(certificate_content[i:i+64] for i in range(0, len(certificate_content), 64))
        formatted_certificate += "\n-----END CERTIFICATE-----\n"
        
        # Load certificate
        certificate_bytes = formatted_certificate.encode('utf-8')
        cert = x509.load_pem_x509_certificate(certificate_bytes, default_backend())
        
        # Extract all relevant fields
        result = {
            "success": True,
            "company_name": company_name,
            "company_tax_id": company_doc.tax_id if hasattr(company_doc, 'tax_id') else "NOT SET",
            "certificate_info": {}
        }
        
        # Get subject details
        subject_details = {}
        for attribute in cert.subject:
            oid_name = attribute.oid._name if hasattr(attribute.oid, '_name') else attribute.oid.dotted_string
            subject_details[oid_name] = attribute.value
        
        result["certificate_info"]["subject"] = subject_details
        
        # Try to extract VAT from common OIDs
        vat_candidates = []
        
        # Check UID (0.9.2342.19200300.100.1.1)
        for attribute in cert.subject:
            if attribute.oid.dotted_string == '0.9.2342.19200300.100.1.1':
                vat_candidates.append(("UID", attribute.value))
        
        # Check organizationIdentifier (2.5.4.97)
        for attribute in cert.subject:
            if attribute.oid.dotted_string == '2.5.4.97':
                vat_candidates.append(("organizationIdentifier", attribute.value))
        
        # Check serialNumber
        try:
            serial_attrs = cert.subject.get_attributes_for_oid(x509.oid.NameOID.SERIAL_NUMBER)
            for attr in serial_attrs:
                vat_candidates.append(("serialNumber", attr.value))
        except:
            pass
        
        result["certificate_info"]["vat_candidates"] = vat_candidates
        
        # Determine most likely VAT
        if vat_candidates:
            # Clean and extract VAT
            for field_name, value in vat_candidates:
                if '-' in value:
                    # Format like "VATSA-300000000000003"
                    clean_vat = value.split('-')[-1]
                else:
                    clean_vat = value
                result["certificate_info"]["extracted_vat"] = clean_vat
                result["certificate_info"]["extracted_from"] = field_name
                break
        
        # Compare with company tax ID
        company_vat = str(company_doc.tax_id).strip() if hasattr(company_doc, 'tax_id') and company_doc.tax_id else ""
        cert_vat = result["certificate_info"].get("extracted_vat", "")
        
        if company_vat and cert_vat:
            if company_vat == cert_vat:
                result["match"] = True
                result["message"] = "✅ VAT numbers MATCH - Certificate is valid!"
            else:
                result["match"] = False
                result["message"] = f"❌ VAT MISMATCH!\n\nCompany Tax ID: {company_vat}\nCertificate VAT: {cert_vat}\n\nPlease update Company Tax ID to match certificate."
        else:
            result["match"] = False
            result["message"] = "⚠️ Could not compare - missing data"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error checking certificate: {str(e)}",
            "error": str(e)
        }


@frappe.whitelist()
def check_all_companies():
    """Check VAT for all companies with ZATCA certificates"""
    companies = frappe.get_all("Company", 
                               filters={"custom_certificate": ["!=", ""]},
                               fields=["name"])
    
    results = []
    for company in companies:
        result = check_certificate_vat(company.name)
        results.append(result)
    
    return results


def print_certificate_vat(company_name):
    """Console function to print certificate VAT info"""
    result = check_certificate_vat(company_name)
    
    if result.get("success"):
        print("\n" + "="*80)
        print(f"ZATCA CERTIFICATE VAT CHECK - {company_name}")
        print("="*80)
        print(f"\nCompany Tax ID: {result.get('company_tax_id')}")
        
        if "extracted_vat" in result.get("certificate_info", {}):
            print(f"Certificate VAT: {result['certificate_info']['extracted_vat']}")
            print(f"Extracted from: {result['certificate_info']['extracted_from']}")
        
        print(f"\n{result.get('message')}")
        
        if result.get("certificate_info", {}).get("vat_candidates"):
            print("\nAll VAT candidates found in certificate:")
            for field, value in result["certificate_info"]["vat_candidates"]:
                print(f"  - {field}: {value}")
        
        print("\nCertificate Subject Details:")
        for key, value in result.get("certificate_info", {}).get("subject", {}).items():
            print(f"  - {key}: {value}")
        
        print("="*80 + "\n")
    else:
        print(f"\n❌ Error: {result.get('message')}\n")
    
    return result
