# highspeed_pos/highspeed_pos/api/zatca.py
# Full Path: highspeed_pos/highspeed_pos/api/zatca.py

import frappe
import base64
import qrcode
from io import BytesIO
from frappe import _

@frappe.whitelist()
def get_invoice_qr_code(invoice_name):
    """
    Get ZATCA QR Code for Sales Invoice (with image generation)
    
    Args:
        invoice_name: Sales Invoice name
        
    Returns:
        dict: {'qr_code': base64_string, 'source': string}
    """
    
    try:
        # Check if invoice exists
        if not frappe.db.exists("Sales Invoice", invoice_name):
            return {
                'success': False,
                'message': _('Invoice not found')
            }
        
        # Get QR text from Additional Fields
        qr_text = frappe.db.get_value(
            "Sales Invoice Additional Fields",
            {"parent": invoice_name},
            "qr_code"
        )
        
        if not qr_text:
            return {
                'success': False,
                'message': _('No QR code found')
            }
        
        # Check if already base64 image
        if qr_text.startswith('iVBOR') or 'base64,' in qr_text:
            if 'base64,' in qr_text:
                qr_text = qr_text.split('base64,')[-1]
            
            return {
                'success': True,
                'qr_code': qr_text,
                'source': 'pre_generated_image',
                'size': len(qr_text)
            }
        
        # Generate QR image from text
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                'success': True,
                'qr_code': img_base64,
                'source': 'generated_from_text',
                'size': len(img_base64),
                'qr_text_length': len(qr_text)
            }
            
        except Exception as e:
            frappe.log_error(f"QR generation failed: {str(e)}")
            
            return {
                'success': False,
                'message': f'QR generation failed: {str(e)}'
            }
        
    except Exception as e:
        frappe.log_error(
            title=f"QR Code Error: {invoice_name}",
            message=str(e)
        )
        
        return {
            'success': False,
            'message': str(e)
        }


@frappe.whitelist()
def get_invoice_zatca_qr(invoice_name):
    """
    Get ZATCA QR Code text only (for Flutter generation)
    
    Args:
        invoice_name: Sales Invoice name
        
    Returns:
        dict: {'qr_code': string}
    """
    
    try:
        # Check if invoice exists
        if not frappe.db.exists("Sales Invoice", invoice_name):
            return {
                'success': False,
                'message': _('Invoice not found')
            }
        
        # Get QR code from Additional Fields
        qr_code = frappe.db.get_value(
            "Sales Invoice Additional Fields",
            {"parent": invoice_name},
            "qr_code"
        )
        
        if qr_code:
            return {
                'success': True,
                'qr_code': qr_code,
                'length': len(qr_code)
            }
        
        return {
            'success': False,
            'message': _('No QR code found for this invoice')
        }
        
    except Exception as e:
        frappe.log_error(
            title=f"Get ZATCA QR Error: {invoice_name}",
            message=str(e)
        )
        
        return {
            'success': False,
            'message': str(e)
        }