import frappe
import base64
import hashlib
import pyqrcode
import requests
import uuid
import re
from lxml import etree
from datetime import datetime
import xml.etree.ElementTree as ET
from zatca.zatca.createxml import (
    xml_tags, invoice_Typecode_Simplified, invoice_Typecode_Standard,
    additional_Reference, company_Data, xml_structuring,
    invoice_Typecode_Compliance
)
from frappe.utils.data import get_time

from zatca.zatca.sign_invoice import (
    removeTags, canonicalize_xml, getInvoiceHash, digital_signature,
    extract_certificate_details, certificate_hash, signxml_modify,
    generate_Signed_Properties_Hash, populate_The_UBL_Extensions_Output,
    generate_tlv_xml, get_tlv_for_value, update_Qr_toXml, structuring_signedxml,
    xml_base64_Decode, get_API_url, attach_QR_Image, success_Log, error_Log
)

def get_Issue_Time(fee_collection_doc):
    """Get posting time in required format"""
    time = get_time(fee_collection_doc.posting_time) if hasattr(fee_collection_doc, 'posting_time') else datetime.now().time()
    issue_time = time.strftime("%H:%M:%S")
    return issue_time


def fee_collection_data(invoice, fee_collection_number):
    """Extract fee collection data and populate invoice structure"""
    try:
        fee_collection_doc = frappe.get_doc("Fee Collections", fee_collection_number)
        
        cbc_ProfileID = ET.SubElement(invoice, "cbc:ProfileID")
        cbc_ProfileID.text = "reporting:1.0"
        
        cbc_ID = ET.SubElement(invoice, "cbc:ID")
        cbc_ID.text = str(fee_collection_doc.name)
        
        cbc_UUID = ET.SubElement(invoice, "cbc:UUID")
        cbc_UUID.text = str(uuid.uuid1())
        uuid1 = cbc_UUID.text
        
        cbc_IssueDate = ET.SubElement(invoice, "cbc:IssueDate")
        # Use posting_date from first fee detail if available
        if hasattr(fee_collection_doc, 'student_fee_details') and fee_collection_doc.student_fee_details:
            posting_date = fee_collection_doc.student_fee_details[0].posting_date
        else:
            posting_date = fee_collection_doc.posting_date
        cbc_IssueDate.text = str(posting_date)
        
        cbc_IssueTime = ET.SubElement(invoice, "cbc:IssueTime")
        cbc_IssueTime.text = get_Issue_Time(fee_collection_doc)
        
        return invoice, uuid1, fee_collection_doc
    except Exception as e:
        frappe.throw(f"Error in extracting fee collection data: {str(e)}")


def fee_doc_Reference(invoice, fee_collection_doc, fee_collection_number):
    """Create document reference for fee collection"""
    try:
        # Document Currency Code
        cbc_DocumentCurrencyCode = ET.SubElement(invoice, "cbc:DocumentCurrencyCode")
        cbc_DocumentCurrencyCode.text = "SAR"  # Fee Collections always in SAR
        
        # Tax Currency Code (ZATCA requires SAR)
        cbc_TaxCurrencyCode = ET.SubElement(invoice, "cbc:TaxCurrencyCode")
        cbc_TaxCurrencyCode.text = "SAR"
        
        # Billing Reference for Credit/Debit Notes (Return cases)
        if fee_collection_doc.is_return == 1 and hasattr(fee_collection_doc, 'refund_against') and fee_collection_doc.refund_against:
            cac_BillingReference = ET.SubElement(invoice, "cac:BillingReference")
            cac_InvoiceDocumentReference = ET.SubElement(cac_BillingReference, "cac:InvoiceDocumentReference")
            cbc_ID_billing = ET.SubElement(cac_InvoiceDocumentReference, "cbc:ID")
            cbc_ID_billing.text = fee_collection_doc.refund_against
        
        # ICV (Invoice Counter Value) Reference
        cac_AdditionalDocumentReference = ET.SubElement(invoice, "cac:AdditionalDocumentReference")
        cbc_ID_1 = ET.SubElement(cac_AdditionalDocumentReference, "cbc:ID")
        cbc_ID_1.text = "ICV"
        cbc_UUID_1 = ET.SubElement(cac_AdditionalDocumentReference, "cbc:UUID")
        # Extract numeric part from fee collection name for ICV
        icv_code = re.sub(r'\D', '', fee_collection_number)
        cbc_UUID_1.text = str(icv_code) if icv_code else "1"
        
        return invoice
    except Exception as e:
        frappe.throw(f"Error in fee document reference: {str(e)}")


def fee_customer_Data(invoice, fee_collection_doc):
    """Extract customer/student data from fee collection - using first guardian"""
    try:
        # Fee Collection has student_fee_details child table with student and fees link
        if hasattr(fee_collection_doc, 'student_fee_details') and fee_collection_doc.student_fee_details:
            first_fee_detail = fee_collection_doc.student_fee_details[0]
            if first_fee_detail.student_id:
                student_doc = frappe.get_doc("Student", first_fee_detail.student_id)
                
                # Get first guardian from guardians child table
                guardian_data = None
                customer_name = student_doc.student_name or student_doc.name
                
                if hasattr(student_doc, 'guardians') and student_doc.guardians:
                    first_guardian = student_doc.guardians[0]
                    if first_guardian.guardian:
                        # Get Guardian document
                        guardian_doc = frappe.get_doc("Guardian", first_guardian.guardian)
                        guardian_data = guardian_doc
                        customer_name = guardian_doc.guardian_name or guardian_doc.name
                
                # Use guardian data if available, otherwise fall back to student
                data_source = guardian_data if guardian_data else student_doc
                
                cac_AccountingCustomerParty = ET.SubElement(invoice, "cac:AccountingCustomerParty")
                cac_Party_2 = ET.SubElement(cac_AccountingCustomerParty, "cac:Party")
                cac_PartyIdentification_1 = ET.SubElement(cac_Party_2, "cac:PartyIdentification")
                cbc_ID_4 = ET.SubElement(cac_PartyIdentification_1, "cbc:ID")
                cbc_ID_4.set("schemeID", "CRN")
                cbc_ID_4.text = data_source.iqama_no or data_source.ksa_vat_no
                
                cac_PostalAddress_1 = ET.SubElement(cac_Party_2, "cac:PostalAddress")
                cbc_StreetName_1 = ET.SubElement(cac_PostalAddress_1, "cbc:StreetName")
                cbc_StreetName_1.text = data_source.ksa_address if hasattr(data_source, 'ksa_address') and data_source.ksa_address else "Street"
                
                cbc_BuildingNumber_1 = ET.SubElement(cac_PostalAddress_1, "cbc:BuildingNumber")
                cbc_BuildingNumber_1.text = data_source.pakistan_address if hasattr(data_source, 'pakistan_address') and data_source.pakistan_address else "1234"
                
                cbc_PlotIdentification_1 = ET.SubElement(cac_PostalAddress_1, "cbc:PlotIdentification")
                cbc_PlotIdentification_1.text = data_source.ksa_address if hasattr(data_source, 'ksa_address') and data_source.ksa_address else "Plot"
                
                cbc_CitySubdivisionName_1 = ET.SubElement(cac_PostalAddress_1, "cbc:CitySubdivisionName")
                district_1 = data_source.pakistan_address if hasattr(data_source, 'pakistan_address') and data_source.pakistan_address else "District"
                cbc_CitySubdivisionName_1.text = district_1
                
                cbc_CityName_1 = ET.SubElement(cac_PostalAddress_1, "cbc:CityName")
                cbc_CityName_1.text = data_source.city if hasattr(data_source, 'city') and data_source.city else "Riyadh"
                
                cbc_PostalZone_1 = ET.SubElement(cac_PostalAddress_1, "cbc:PostalZone")
                # Validate buyer pincode is 5 digits
                buyer_pincode = str(data_source.pincode) if hasattr(data_source, 'pincode') and data_source.pincode else "12345"
                if not buyer_pincode.isdigit():
                    buyer_pincode = "12345"
                elif len(buyer_pincode) != 5:
                    buyer_pincode = buyer_pincode.zfill(5)[:5]  # Pad or trim to 5 digits
                cbc_PostalZone_1.text = buyer_pincode
                
                cbc_CountrySubentity_1 = ET.SubElement(cac_PostalAddress_1, "cbc:CountrySubentity")
                cbc_CountrySubentity_1.text = "SA"
                
                cac_Country_1 = ET.SubElement(cac_PostalAddress_1, "cac:Country")
                cbc_IdentificationCode_1 = ET.SubElement(cac_Country_1, "cbc:IdentificationCode")
                cbc_IdentificationCode_1.text = "SA"
                
                cac_PartyTaxScheme_1 = ET.SubElement(cac_Party_2, "cac:PartyTaxScheme")
                cac_TaxScheme_1 = ET.SubElement(cac_PartyTaxScheme_1, "cac:TaxScheme")
                cbc_ID_5 = ET.SubElement(cac_TaxScheme_1, "cbc:ID")
                cbc_ID_5.text = "VAT"
                
                cac_PartyLegalEntity_1 = ET.SubElement(cac_Party_2, "cac:PartyLegalEntity")
                cbc_RegistrationName_1 = ET.SubElement(cac_PartyLegalEntity_1, "cbc:RegistrationName")
                cbc_RegistrationName_1.text = customer_name
        
        return invoice
    except Exception as e:
        frappe.throw(f"Error in fee customer data: {str(e)}")


def fee_delivery_And_PaymentMeans(invoice, fee_collection_doc, is_return):
    """Set delivery and payment means for fee collection"""
    try:
        # Use posting_date from first fee detail
        if hasattr(fee_collection_doc, 'student_fee_details') and fee_collection_doc.student_fee_details:
            due_date = fee_collection_doc.student_fee_details[0].due_date
        else:
            due_date = datetime.now().date()
        
        cac_Delivery = ET.SubElement(invoice, "cac:Delivery")
        cbc_ActualDeliveryDate = ET.SubElement(cac_Delivery, "cbc:ActualDeliveryDate")
        cbc_ActualDeliveryDate.text = str(due_date)
        
        cac_PaymentMeans = ET.SubElement(invoice, "cac:PaymentMeans")
        cbc_PaymentMeansCode = ET.SubElement(cac_PaymentMeans, "cbc:PaymentMeansCode")
        
        # Map mode of payment
        if hasattr(fee_collection_doc, 'mode_of_payment') and fee_collection_doc.mode_of_payment:
            mode_map = {"Cash": "10", "Credit": "30", "Bank Transfer": "42", "Card": "48"}
            cbc_PaymentMeansCode.text = mode_map.get(fee_collection_doc.mode_of_payment, "10")
        else:
            cbc_PaymentMeansCode.text = "10"  # Default to Cash
        
        # Add cancellation note for returns
        if is_return == 1:
            cbc_InstructionNote = ET.SubElement(cac_PaymentMeans, "cbc:InstructionNote")
            cbc_InstructionNote.text = "Cancellation"
        
        return invoice
    except Exception as e:
        frappe.throw(f"Error in fee delivery and payment means: {str(e)}")


def fee_tax_Data(invoice, fee_collection_doc):
    """Calculate tax data from fee collection using taxes table from linked Fees documents"""
    try:
        total_tax = 0
        taxable_amount = 0
        tax_rate = 15.0  # Default VAT rate
        
        # Get tax from linked Fees documents in student_fee_details
        if hasattr(fee_collection_doc, 'student_fee_details'):
            for fee_detail in fee_collection_doc.student_fee_details:
                if fee_detail.fees:
                    fees_doc = frappe.get_doc("Fees", fee_detail.fees)
                    
                    # Get tax from taxes table
                    if hasattr(fees_doc, 'taxes') and fees_doc.taxes:
                        for tax_row in fees_doc.taxes:
                            total_tax += tax_row.tax_amount or 0
                            if tax_row.rate:
                                tax_rate = tax_row.rate
                    
                    # Taxable amount is grand_total_before_tax
                    if hasattr(fees_doc, 'grand_total_before_tax'):
                        taxable_amount += fees_doc.grand_total_before_tax or 0
        
        # Add tax total in SAR
        cac_TaxTotal = ET.SubElement(invoice, "cac:TaxTotal")
        cbc_TaxAmount_SAR = ET.SubElement(cac_TaxTotal, "cbc:TaxAmount")
        cbc_TaxAmount_SAR.set("currencyID", "SAR")
        cbc_TaxAmount_SAR.text = f"{abs(round(total_tax, 2)):.2f}"
        
        # Add main tax total
        cac_TaxTotal_2 = ET.SubElement(invoice, "cac:TaxTotal")
        cbc_TaxAmount = ET.SubElement(cac_TaxTotal_2, "cbc:TaxAmount")
        cbc_TaxAmount.set("currencyID", "SAR")
        cbc_TaxAmount.text = f"{abs(round(total_tax, 2)):.2f}"
        
        cac_TaxSubtotal = ET.SubElement(cac_TaxTotal_2, "cac:TaxSubtotal")
        cbc_TaxableAmount = ET.SubElement(cac_TaxSubtotal, "cbc:TaxableAmount")
        cbc_TaxableAmount.set("currencyID", "SAR")
        cbc_TaxableAmount.text = f"{abs(round(taxable_amount, 2)):.2f}"
        
        cbc_TaxAmount_2 = ET.SubElement(cac_TaxSubtotal, "cbc:TaxAmount")
        cbc_TaxAmount_2.set("currencyID", "SAR")
        cbc_TaxAmount_2.text = f"{abs(round(total_tax, 2)):.2f}"
        
        cac_TaxCategory_1 = ET.SubElement(cac_TaxSubtotal, "cac:TaxCategory")
        cbc_ID_8 = ET.SubElement(cac_TaxCategory_1, "cbc:ID")
        cbc_ID_8.text = "S"  # Standard
        
        cbc_Percent_1 = ET.SubElement(cac_TaxCategory_1, "cbc:Percent")
        cbc_Percent_1.text = f"{float(tax_rate):.2f}"
        
        cac_TaxScheme_3 = ET.SubElement(cac_TaxCategory_1, "cac:TaxScheme")
        cbc_ID_9 = ET.SubElement(cac_TaxScheme_3, "cbc:ID")
        cbc_ID_9.text = "VAT"
        
        # Legal Monetary Total
        cac_LegalMonetaryTotal = ET.SubElement(invoice, "cac:LegalMonetaryTotal")
        cbc_LineExtensionAmount = ET.SubElement(cac_LegalMonetaryTotal, "cbc:LineExtensionAmount")
        cbc_LineExtensionAmount.set("currencyID", "SAR")
        cbc_LineExtensionAmount.text = f"{abs(round(taxable_amount, 2)):.2f}"
        
        cbc_TaxExclusiveAmount = ET.SubElement(cac_LegalMonetaryTotal, "cbc:TaxExclusiveAmount")
        cbc_TaxExclusiveAmount.set("currencyID", "SAR")
        cbc_TaxExclusiveAmount.text = f"{abs(round(taxable_amount, 2)):.2f}"
        
        # BR-CO-15: Invoice total amount with VAT (BT-112) must be correct
        total_with_vat = abs(round(taxable_amount, 2)) + abs(round(total_tax, 2))
        cbc_TaxInclusiveAmount = ET.SubElement(cac_LegalMonetaryTotal, "cbc:TaxInclusiveAmount")
        cbc_TaxInclusiveAmount.set("currencyID", "SAR")
        cbc_TaxInclusiveAmount.text = f"{total_with_vat:.2f}"
        
        cbc_AllowanceTotalAmount = ET.SubElement(cac_LegalMonetaryTotal, "cbc:AllowanceTotalAmount")
        cbc_AllowanceTotalAmount.set("currencyID", "SAR")
        cbc_AllowanceTotalAmount.text = "0.00"
        
        cbc_PayableAmount = ET.SubElement(cac_LegalMonetaryTotal, "cbc:PayableAmount")
        cbc_PayableAmount.set("currencyID", "SAR")
        cbc_PayableAmount.text = f"{total_with_vat:.2f}"
        
        return invoice
    except Exception as e:
        frappe.throw(f"Error in fee tax data: {str(e)}")


def fee_item_data(invoice, fee_collection_doc):
    """Convert fee collection entries to invoice line items from linked Fees"""
    try:
        line_id = 1
        
        # student_fee_details child table has student and fees columns
        if hasattr(fee_collection_doc, 'student_fee_details'):
            for fee_detail in fee_collection_doc.student_fee_details:
                if fee_detail.fees:
                    # Get the Fees document
                    fees_doc = frappe.get_doc("Fees", fee_detail.fees)
                    
                    # Get student name
                    student_name = fee_detail.student_name if hasattr(fee_detail, 'student_name') else fee_detail.student_id
                    
                    # Get amounts from Fees document
                    grand_total_before_tax = fees_doc.grand_total_before_tax if hasattr(fees_doc, 'grand_total_before_tax') else 0
                    total_tax = fees_doc.total_taxes_and_charges if hasattr(fees_doc, 'total_taxes_and_charges') else 0
                    tax_rate = 15.0  # Default
                    
                    # Get tax rate from taxes table
                    if hasattr(fees_doc, 'taxes') and fees_doc.taxes:
                        for tax_row in fees_doc.taxes:
                            if tax_row.rate:
                                tax_rate = tax_row.rate
                                break
                    
                    # If fees has components, create line items from them
                    if hasattr(fees_doc, 'components') and fees_doc.components:
                        for component in fees_doc.components:
                            cac_InvoiceLine = ET.SubElement(invoice, "cac:InvoiceLine")
                            cbc_ID_10 = ET.SubElement(cac_InvoiceLine, "cbc:ID")
                            cbc_ID_10.text = str(line_id)
                            
                            cbc_InvoicedQuantity = ET.SubElement(cac_InvoiceLine, "cbc:InvoicedQuantity")
                            cbc_InvoicedQuantity.set("unitCode", "PCE")
                            cbc_InvoicedQuantity.text = "1"
                            
                            amount = component.amount or 0
                            item_tax = amount * (tax_rate / 100)
                            
                            cbc_LineExtensionAmount_1 = ET.SubElement(cac_InvoiceLine, "cbc:LineExtensionAmount")
                            cbc_LineExtensionAmount_1.set("currencyID", "SAR")
                            cbc_LineExtensionAmount_1.text = str(abs(round(amount, 2)))
                            
                            cac_TaxTotal_2 = ET.SubElement(cac_InvoiceLine, "cac:TaxTotal")
                            cbc_TaxAmount_3 = ET.SubElement(cac_TaxTotal_2, "cbc:TaxAmount")
                            cbc_TaxAmount_3.set("currencyID", "SAR")
                            cbc_TaxAmount_3.text = str(abs(round(item_tax, 2)))
                            
                            # BR-KSA-51: Line amount with VAT must be LineExtensionAmount + TaxAmount
                            cbc_RoundingAmount = ET.SubElement(cac_TaxTotal_2, "cbc:RoundingAmount")
                            cbc_RoundingAmount.set("currencyID", "SAR")
                            line_total_with_vat = abs(round(amount, 2)) + abs(round(item_tax, 2))
                            cbc_RoundingAmount.text = f"{line_total_with_vat:.2f}"
                            
                            cac_Item = ET.SubElement(cac_InvoiceLine, "cac:Item")
                            cbc_Name = ET.SubElement(cac_Item, "cbc:Name")
                            cbc_Name.text = f"{component.description or component.fees_category} - {student_name}"
                            
                            cac_ClassifiedTaxCategory = ET.SubElement(cac_Item, "cac:ClassifiedTaxCategory")
                            cbc_ID_11 = ET.SubElement(cac_ClassifiedTaxCategory, "cbc:ID")
                            cbc_ID_11.text = "S"  # Standard
                            
                            cbc_Percent_2 = ET.SubElement(cac_ClassifiedTaxCategory, "cbc:Percent")
                            cbc_Percent_2.text = f"{float(tax_rate):.2f}"
                            
                            cac_TaxScheme_4 = ET.SubElement(cac_ClassifiedTaxCategory, "cac:TaxScheme")
                            cbc_ID_12 = ET.SubElement(cac_TaxScheme_4, "cbc:ID")
                            cbc_ID_12.text = "VAT"
                            
                            cac_Price = ET.SubElement(cac_InvoiceLine, "cac:Price")
                            cbc_PriceAmount = ET.SubElement(cac_Price, "cbc:PriceAmount")
                            cbc_PriceAmount.set("currencyID", "SAR")
                            cbc_PriceAmount.text = str(abs(round(amount, 2)))
                            
                            line_id += 1
                    else:
                        # Create single line item for the fee
                        cac_InvoiceLine = ET.SubElement(invoice, "cac:InvoiceLine")
                        cbc_ID_10 = ET.SubElement(cac_InvoiceLine, "cbc:ID")
                        cbc_ID_10.text = str(line_id)
                        
                        cbc_InvoicedQuantity = ET.SubElement(cac_InvoiceLine, "cbc:InvoicedQuantity")
                        cbc_InvoicedQuantity.set("unitCode", "PCE")
                        cbc_InvoicedQuantity.text = "1"
                        
                        cbc_LineExtensionAmount_1 = ET.SubElement(cac_InvoiceLine, "cbc:LineExtensionAmount")
                        cbc_LineExtensionAmount_1.set("currencyID", "SAR")
                        cbc_LineExtensionAmount_1.text = str(abs(round(grand_total_before_tax, 2)))
                        
                        cac_TaxTotal_2 = ET.SubElement(cac_InvoiceLine, "cac:TaxTotal")
                        cbc_TaxAmount_3 = ET.SubElement(cac_TaxTotal_2, "cbc:TaxAmount")
                        cbc_TaxAmount_3.set("currencyID", "SAR")
                        cbc_TaxAmount_3.text = str(abs(round(total_tax, 2)))
                        
                        # BR-KSA-51: Line amount with VAT must be LineExtensionAmount + TaxAmount
                        cbc_RoundingAmount = ET.SubElement(cac_TaxTotal_2, "cbc:RoundingAmount")
                        cbc_RoundingAmount.set("currencyID", "SAR")
                        line_total_with_vat = abs(round(grand_total_before_tax, 2)) + abs(round(total_tax, 2))
                        cbc_RoundingAmount.text = f"{line_total_with_vat:.2f}"
                        
                        cac_Item = ET.SubElement(cac_InvoiceLine, "cac:Item")
                        cbc_Name = ET.SubElement(cac_Item, "cbc:Name")
                        cbc_Name.text = f"Fee - {student_name} ({fees_doc.name})"
                        
                        cac_ClassifiedTaxCategory = ET.SubElement(cac_Item, "cac:ClassifiedTaxCategory")
                        cbc_ID_11 = ET.SubElement(cac_ClassifiedTaxCategory, "cbc:ID")
                        cbc_ID_11.text = "S"
                        
                        cbc_Percent_2 = ET.SubElement(cac_ClassifiedTaxCategory, "cbc:Percent")
                        cbc_Percent_2.text = f"{float(tax_rate):.2f}"
                        
                        cac_TaxScheme_4 = ET.SubElement(cac_ClassifiedTaxCategory, "cac:TaxScheme")
                        cbc_ID_12 = ET.SubElement(cac_TaxScheme_4, "cbc:ID")
                        cbc_ID_12.text = "VAT"
                        
                        cac_Price = ET.SubElement(cac_InvoiceLine, "cac:Price")
                        cbc_PriceAmount = ET.SubElement(cac_Price, "cbc:PriceAmount")
                        cbc_PriceAmount.set("currencyID", "SAR")
                        cbc_PriceAmount.text = str(abs(round(grand_total_before_tax, 2)))
                        
                        line_id += 1
        
        return invoice
    except Exception as e:
        frappe.throw(f"Error in fee item data: {str(e)}")


@frappe.whitelist(allow_guest=False)
def zatca_Background_fee_collection(fee_collection_number):
    """Manual trigger function to send fee collection to ZATCA"""
    try:
        fee_collection_doc = frappe.get_doc("Fee Collections", fee_collection_number)
        company_name = fee_collection_doc.company
        
        # Get company abbreviation
        company_abbr = frappe.db.get_value("Company", {"name": company_name}, "abbr")
        if not company_abbr:
            frappe.throw(f"Company abbreviation for {company_name} not found.")
        
        # Retrieve company settings
        company_doc = frappe.get_doc('Company', company_name)
        
        # Validate fee collection exists and is submitted
        if not frappe.db.exists("Fee Collections", fee_collection_number):
            frappe.throw("Please save and submit the fee collection before sending to Zatca: " + str(fee_collection_number))
        
        if fee_collection_doc.docstatus in [0, 2]:
            frappe.throw("Please submit the fee collection before sending to Zatca: " + str(fee_collection_number))
        
        # Check if already submitted to ZATCA
        if hasattr(fee_collection_doc, 'custom_zatca_status') and fee_collection_doc.custom_zatca_status in ["REPORTED", "CLEARED"]:
            frappe.throw("Already submitted to Zakat and Tax Authority")
        
        # Check if ZATCA is enabled
        if not hasattr(company_doc, 'custom_zatca_invoice_enabled') or company_doc.custom_zatca_invoice_enabled != 1:
            frappe.throw("Zatca Invoice is not enabled in Company Settings, Please contact your system administrator")
        
        # Call ZATCA for fee collection
        zatca_Call_fee_collection(fee_collection_number, "0", company_abbr)
        
    except Exception as e:
        frappe.throw("Error in fee collection background call: " + str(e))


def zatca_Background_fee_on_submit(doc, method=None):
    """Hook function to send fee collection to ZATCA on submission"""
    try:
        fee_collection_doc = doc
        fee_collection_number = fee_collection_doc.name
        
        # Get company abbreviation
        company_abbr = frappe.db.get_value("Company", {"name": fee_collection_doc.company}, "abbr")
        if not company_abbr:
            frappe.throw(f"Company abbreviation for {fee_collection_doc.company} not found.")
        
        # Retrieve company settings
        company_doc = frappe.get_doc('Company', fee_collection_doc.company)
        
        # Check if Zatca Invoice is enabled
        if not hasattr(company_doc, 'custom_zatca_invoice_enabled') or company_doc.custom_zatca_invoice_enabled != 1:
            return  # Silent return if not enabled
        
        # Check if auto-submit on submission is enabled
        if not hasattr(company_doc, 'custom_zatca_invoices_on_submission') or company_doc.custom_zatca_invoices_on_submission != 1:
            return  # Silent return if auto-submit not enabled
        
        if not frappe.db.exists("Fee Collections", fee_collection_number):
            frappe.throw("Please save and submit the fee collection before sending to Zatca: " + str(fee_collection_number))
        
        if fee_collection_doc.docstatus in [0, 2]:
            frappe.throw("Please submit the fee collection before sending to Zatca: " + str(fee_collection_number))
        
        if hasattr(fee_collection_doc, 'custom_zatca_status') and fee_collection_doc.custom_zatca_status in ["REPORTED", "CLEARED"]:
            return  # Already submitted
        
        # Call ZATCA
        zatca_Call_fee_collection(fee_collection_number, "0", company_abbr)
        
    except Exception as e:
        frappe.throw("Error in fee collection background on submit call: " + str(e))


def zatca_Call_fee_collection(fee_collection_number, compliance_type="0", company_abbr=None):
    """Main function to process and send fee collection to ZATCA"""
    try:
        if not frappe.db.exists("Fee Collections", fee_collection_number):
            frappe.throw("Fee Collection Number is NOT Valid: " + str(fee_collection_number))
        
        invoice = xml_tags()
        invoice, uuid1, fee_collection_doc = fee_collection_data(invoice, fee_collection_number)
        
        # Get the company abbreviation
        if not company_abbr:
            company_abbr = frappe.db.get_value("Company", {"name": fee_collection_doc.company}, "abbr")
        
        # Fee collections are always B2C (simplified)
        is_b2c = True
        
        if compliance_type == "0":
            if is_b2c:
                invoice = invoice_Typecode_Simplified(invoice, fee_collection_doc)
            else:
                invoice = invoice_Typecode_Standard(invoice, fee_collection_doc)
        else:
            invoice = invoice_Typecode_Compliance(invoice, compliance_type)
        
        invoice = fee_doc_Reference(invoice, fee_collection_doc, fee_collection_number)
        invoice = additional_Reference(invoice, company_abbr)
        invoice = company_Data(invoice, fee_collection_doc)
        invoice = fee_customer_Data(invoice, fee_collection_doc)
        invoice = fee_delivery_And_PaymentMeans(invoice, fee_collection_doc, fee_collection_doc.is_return)
        invoice = fee_tax_Data(invoice, fee_collection_doc)
        invoice = fee_item_data(invoice, fee_collection_doc)
        
        pretty_xml_string = xml_structuring(invoice, fee_collection_doc)
        
        try:
            with open(frappe.local.site + "/private/files/finalzatcaxml.xml", 'r') as file:
                file_content = file.read()
        except FileNotFoundError:
            frappe.throw("XML file not found")
        
        tag_removed_xml = removeTags(file_content)
        canonicalized_xml = canonicalize_xml(tag_removed_xml)
        hash1, encoded_hash = getInvoiceHash(canonicalized_xml)
        encoded_signature = digital_signature(hash1, company_abbr)
        issuer_name, serial_number = extract_certificate_details(company_abbr)
        encoded_certificate_hash = certificate_hash(company_abbr)
        namespaces, signing_time = signxml_modify(company_abbr)
        signed_properties_base64 = generate_Signed_Properties_Hash(signing_time, issuer_name, serial_number, encoded_certificate_hash)
        populate_The_UBL_Extensions_Output(encoded_signature, namespaces, signed_properties_base64, encoded_hash, company_abbr)
        tlv_data = generate_tlv_xml(company_abbr)
        
        tagsBufsArray = []
        for tag_num, tag_value in tlv_data.items():
            tagsBufsArray.append(get_tlv_for_value(tag_num, tag_value))
        
        qrCodeBuf = b"".join(tagsBufsArray)
        qrCodeB64 = base64.b64encode(qrCodeBuf).decode('utf-8')
        update_Qr_toXml(qrCodeB64, company_abbr)
        signed_xmlfile_name = structuring_signedxml()
        
        if compliance_type == "0":
            if is_b2c:
                reporting_API_fee(uuid1, encoded_hash, signed_xmlfile_name, fee_collection_number, fee_collection_doc)
                attach_QR_Image(qrCodeB64, fee_collection_doc)
            else:
                clearance_API_fee(uuid1, encoded_hash, signed_xmlfile_name, fee_collection_number, fee_collection_doc)
                attach_QR_Image(qrCodeB64, fee_collection_doc)
        else:
            from zatca.zatca.sign_invoice import compliance_api_call
            compliance_api_call(uuid1, encoded_hash, signed_xmlfile_name, company_abbr)
            attach_QR_Image(qrCodeB64, fee_collection_doc)
        
    except Exception as e:
        frappe.log_error(title='Zatca fee collection call failed', message=frappe.get_traceback())
        frappe.throw("Error in Zatca fee collection call: " + str(e))


def reporting_API_fee(uuid1, encoded_hash, signed_xmlfile_name, fee_collection_number, fee_collection_doc):
    """Send fee collection to ZATCA reporting API (B2C/simplified)"""
    try:
        company_abbr = frappe.db.get_value("Company", {"name": fee_collection_doc.company}, "abbr")
        
        if not company_abbr:
            frappe.throw(f"Company with abbreviation {fee_collection_doc.company} not found.")
        
        company_doc = frappe.get_doc('Company', {"abbr": company_abbr})
        
        payload = {
            "invoiceHash": encoded_hash,
            "uuid": uuid1,
            "invoice": xml_base64_Decode(signed_xmlfile_name),
        }

        print(
            "***********\nPayload checking \n\n\n\n\n",
            signed_xmlfile_name,
            "\n\n\n\n\n ************\n\n\n\n\n"
        )
        
        production_csid = company_doc.custom_basic_auth_from_production
        
        if production_csid:
            headers = {
                'accept': 'application/json',
                'accept-language': 'en',
                'Clearance-Status': '0',
                'Accept-Version': 'V2',
                'Authorization': 'Basic ' + production_csid,
                'Content-Type': 'application/json',
                'Cookie': 'TS0106293e=0132a679c0639d13d069bcba831384623a2ca6da47fac8d91bef610c47c7119dcdd3b817f963ec301682dae864351c67ee3a402866'
            }
        else:
            frappe.throw(f"Production CSID for company {company_abbr} not found.")
        
        try:
            response = requests.post(
                url=get_API_url(company_abbr, base_url="invoices/reporting/single"),
                headers=headers,
                json=payload
            )
            
            if response.status_code in (400, 405, 406, 409):
                fee_collection_doc.db_set('custom_uuid', 'Not Submitted', commit=True, update_modified=True)
                fee_collection_doc.db_set('custom_zatca_status', 'Not Submitted', commit=True, update_modified=True)
                frappe.throw(f"Error: The request you are sending to Zatca is in incorrect format. Status code: {response.status_code}<br><br> {response.text}")
            
            if response.status_code in (401, 403, 407, 451):
                fee_collection_doc.db_set('custom_uuid', 'Not Submitted', commit=True, update_modified=True)
                fee_collection_doc.db_set('custom_zatca_status', 'Not Submitted', commit=True, update_modified=True)
                frappe.throw(f"Error: Zatca Authentication failed. Status code: {response.status_code}<br><br> {response.text}")
            
            if response.status_code not in (200, 202):
                fee_collection_doc.db_set('custom_uuid', 'Not Submitted', commit=True, update_modified=True)
                fee_collection_doc.db_set('custom_zatca_status', 'Not Submitted', commit=True, update_modified=True)
                frappe.throw(f"Error: Zatca server busy or not responding. Status code: {response.status_code}<br><br> {response.text}")
            
            if response.status_code in (200, 202):
                msg = "SUCCESS: <br><br>" if response.status_code == 200 else "REPORTED WITH WARNINGS: <br><br>"
                msg += f"Status Code: {response.status_code}<br><br> Zatca Response: {response.text}<br><br>"
                frappe.msgprint(msg)
                
                company_doc.custom_pih = encoded_hash
                company_doc.save(ignore_permissions=True)
                
                fee_collection_doc.db_set('custom_uuid', uuid1, commit=True, update_modified=True)
                fee_collection_doc.db_set('custom_zatca_status', 'REPORTED', commit=True, update_modified=True)
                
                success_Log(response.text, uuid1, fee_collection_number)
            else:
                error_Log()
        except Exception as e:
            frappe.throw(f"Error in reporting API fee: {str(e)}")
    
    except Exception as e:
        frappe.throw(f"Error in reporting API fee-1: {str(e)}")


def clearance_API_fee(uuid1, encoded_hash, signed_xmlfile_name, fee_collection_number, fee_collection_doc):
    """Send fee collection to ZATCA clearance API (B2B/standard)"""
    try:
        company_abbr = frappe.db.get_value("Company", {"name": fee_collection_doc.company}, "abbr")
        if not company_abbr:
            frappe.throw(f"Company with abbreviation {fee_collection_doc.company} not found.")
        
        company_doc = frappe.get_doc('Company', {"abbr": company_abbr})
        production_csid = company_doc.custom_basic_auth_from_production or ""
        
        payload = {
            "invoiceHash": encoded_hash,
            "uuid": uuid1,
            "invoice": xml_base64_Decode(signed_xmlfile_name),
        }
        
        if production_csid:
            headers = {
                'accept': 'application/json',
                'accept-language': 'en',
                'Clearance-Status': '1',
                'Accept-Version': 'V2',
                'Authorization': 'Basic ' + production_csid,
                'Content-Type': 'application/json',
                'Cookie': 'TS0106293e=0132a679c03c628e6c49de86c0f6bb76390abb4416868d6368d6d7c05da619c8326266f5bc262b7c0c65a6863cd3b19081d64eee99'
            }
        else:
            frappe.throw(f"Production CSID for company {company_abbr} not found.")
        
        response = requests.post(
            url=get_API_url(company_abbr, base_url="invoices/clearance/single"),
            headers=headers,
            json=payload
        )
        
        if response.status_code in (400, 405, 406, 409):
            fee_collection_doc.db_set('custom_uuid', "Not Submitted", commit=True, update_modified=True)
            fee_collection_doc.db_set('custom_zatca_status', "Not Submitted", commit=True, update_modified=True)
            frappe.throw(f"Error: Incorrect format. Status code: {response.status_code}<br><br>{response.text}")
        
        if response.status_code in (401, 403, 407, 451):
            fee_collection_doc.db_set('custom_uuid', "Not Submitted", commit=True, update_modified=True)
            fee_collection_doc.db_set('custom_zatca_status', "Not Submitted", commit=True, update_modified=True)
            frappe.throw(f"Error: Authentication failed. Status code: {response.status_code}<br><br>{response.text}")
        
        if response.status_code not in (200, 202):
            fee_collection_doc.db_set('custom_uuid', "Not Submitted", commit=True, update_modified=True)
            fee_collection_doc.db_set('custom_zatca_status', "Not Submitted", commit=True, update_modified=True)
            frappe.throw(f"Error: Zatca server error. Status code: {response.status_code}")
        
        if response.status_code in (200, 202):
            msg = "CLEARED WITH WARNINGS: <br><br>" if response.status_code == 202 else "SUCCESS: <br><br>"
            msg += f"Status Code: {response.status_code}<br><br>Zatca Response: {response.text}<br><br>"
            frappe.msgprint(msg)
            
            company_doc.custom_pih = encoded_hash
            company_doc.save(ignore_permissions=True)
            
            fee_collection_doc.db_set('custom_uuid', uuid1, commit=True, update_modified=True)
            fee_collection_doc.db_set('custom_zatca_status', "CLEARED", commit=True, update_modified=True)
            
            data = response.json()
            base64_xml = data.get("clearedInvoice")
            xml_cleared = base64.b64decode(base64_xml).decode('utf-8')
            
            file = frappe.get_doc({
                "doctype": "File",
                "file_name": "Cleared xml file " + fee_collection_doc.name,
                "attached_to_doctype": fee_collection_doc.doctype,
                "attached_to_name": fee_collection_doc.name,
                "content": xml_cleared
            })
            file.save(ignore_permissions=True)
            
            success_Log(response.text, uuid1, fee_collection_number)
            return xml_cleared
        else:
            error_Log()
    
    except Exception as e:
        frappe.throw("Error in clearance API fee: " + str(e))
