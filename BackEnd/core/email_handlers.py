from typing import List, Dict, Any, Optional
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class EmailTemplate:
    """Base class for email templates"""
    
    def __init__(self, template_name: str):
        self.template_name = template_name
    
    def render(self, context: Dict[str, Any]) -> tuple[str, str]:
        """
        Render the email template with the given context
        Returns tuple of (html_content, plain_content)
        """
        try:
            html_content = render_to_string(f'emails/{self.template_name}.html', context)
            plain_content = strip_tags(html_content)
            return html_content, plain_content
        except Exception as e:
            logger.error(f"Error rendering email template: {str(e)}", exc_info=True)
            raise


class BaseEmailHandler:
    """Base class for sending emails"""
    
    def __init__(self):
        self.connection = None
    
    def get_connection(self):
        """Get email connection with proper settings"""
        if not self.connection:
            self.connection = get_connection(
                backend=settings.EMAIL_BACKEND,
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
            )
        return self.connection
    
    def send_email(
        self,
        subject: str,
        to_emails: List[str],
        template: EmailTemplate,
        context: Dict[str, Any],
        from_email: Optional[str] = None,
    ) -> bool:
        """
        Send an email using a template
        Returns True if successful, False otherwise
        """
        if not from_email:
            from_email = settings.DEFAULT_FROM_EMAIL
            
        try:
            html_content, plain_content = template.render(context)
            
            with transaction.atomic():
                email = EmailMessage(
                    subject=subject,
                    body=html_content,
                    from_email=from_email,
                    to=to_emails,
                    connection=self.get_connection()
                )
                email.content_subtype = "html"
                email.send()
                
            logger.info(
                f"Email sent successfully",
                extra={
                    'to': to_emails,
                    'subject': subject,
                    'template': template.template_name
                }
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Failed to send email",
                extra={
                    'to': to_emails,
                    'subject': subject,
                    'template': template.template_name,
                    'error': str(e)
                },
                exc_info=True
            )
            return False


class PurchaseOrderEmailHandler(BaseEmailHandler):
    """Handler for Purchase Order related emails"""
    
    def send_purchase_order_email(self, purchase_order) -> bool:
        """
        Send email notification about a new purchase order to the supplier
        """
        template = EmailTemplate('purchase_order/new_order')
        
        # Get all items from the purchase order
        items = purchase_order.items.select_related('product').all()
        
        # Prepare context for the email template
        context = {
            'supplier_name': purchase_order.supplier.name,
            'order_number': purchase_order.order_number,
            'order_date': purchase_order.order_date,
            'expected_delivery': purchase_order.expected_delivery,
            'items': [
                {
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total': item.calculate_total()
                }
                for item in items
            ],
            'notes': purchase_order.notes,
            'companie_name': purchase_order.companie.name
        }
        
        return self.send_email(
            subject=f"New Purchase Order #{purchase_order.order_number}",
            to_emails=[purchase_order.supplier.email],
            template=template,
            context=context
        )