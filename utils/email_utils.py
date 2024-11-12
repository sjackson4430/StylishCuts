import os
from flask import render_template_string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from app import app

def send_appointment_confirmation(appointment):
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    
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

    # Sender email (should be verified in SendGrid)
    from_email = Email("appointments@stylishcuts.com")
    
    try:
        # Send confirmation to customer
        customer_message = Mail(
            from_email=from_email,
            to_emails=appointment.client_email,
            subject='Appointment Confirmation - Stylish Cuts',
            html_content=render_template_string(customer_template, appointment=appointment)
        )
        sg.send(customer_message)
        
        # Send notification to admin
        admin_message = Mail(
            from_email=from_email,
            to_emails='admin@stylishcuts.com',
            subject='New Appointment Booking',
            html_content=render_template_string(admin_template, appointment=appointment)
        )
        sg.send(admin_message)
        
        return True
    except Exception as e:
        app.logger.error(f"Failed to send email: {str(e)}")
        return False
