import os
from flask import render_template_string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from app import app

def send_appointment_confirmation(appointment):
    """
    Send appointment confirmation emails to both customer and admin.
    Returns True if both emails are sent successfully, False otherwise.
    """
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        
        # Verified sender email from SendGrid
        from_email = Email("noreply@stylishcuts.com")  # Update this with your verified sender
        
        # Email templates
        customer_template = '''
        Dear {{ appointment.client_name }},

        Thank you for booking an appointment with Stylish Cuts Barbershop!

        Appointment Details:
        Service: {{ appointment.service }}
        Date: {{ appointment.date.strftime('%B %d, %Y') }}
        Time: {{ appointment.date.strftime('%I:%M %p') }} PST

        Location: 123 Main Street, City, State 12345

        If you need to reschedule or cancel your appointment, please contact us at:
        Phone: (555) 123-4567
        Email: info@stylishcuts.com

        We look forward to seeing you!

        Best regards,
        Stylish Cuts Team
        '''
        
        admin_template = '''
        New Appointment Booking:

        Client: {{ appointment.client_name }}
        Email: {{ appointment.client_email }}
        Service: {{ appointment.service }}
        Date: {{ appointment.date.strftime('%B %d, %Y') }}
        Time: {{ appointment.date.strftime('%I:%M %p') }} PST
        '''

        # Send confirmation to customer
        try:
            customer_message = Mail(
                from_email=from_email,
                to_emails=appointment.client_email,
                subject='Appointment Confirmation - Stylish Cuts',
                html_content=render_template_string(customer_template, appointment=appointment)
            )
            response = sg.send(customer_message)
            app.logger.info(f"Customer confirmation email sent successfully. Status code: {response.status_code}")
        except Exception as e:
            app.logger.error(f"Failed to send customer confirmation email: {str(e)}")
            raise
        
        # Send notification to admin
        try:
            admin_message = Mail(
                from_email=from_email,
                to_emails='admin@stylishcuts.com',
                subject='New Appointment Booking',
                html_content=render_template_string(admin_template, appointment=appointment)
            )
            response = sg.send(admin_message)
            app.logger.info(f"Admin notification email sent successfully. Status code: {response.status_code}")
        except Exception as e:
            app.logger.error(f"Failed to send admin notification email: {str(e)}")
            raise
        
        return True

    except Exception as e:
        app.logger.error(f"Email sending failed: {str(e)}")
        return False
