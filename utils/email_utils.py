from flask_mail import Message
from app import mail, app
from flask import render_template_string

def send_appointment_confirmation(appointment):
    # Email template for customer
    customer_template = '''
    Dear {{ appointment.client_name }},

    Thank you for booking an appointment with Stylish Cuts Barbershop!

    Appointment Details:
    Service: {{ appointment.service }}
    Date: {{ appointment.date.strftime('%B %d, %Y') }}
    Time: {{ appointment.date.strftime('%I:%M %p') }}

    Location: 123 Main Street, City, State 12345

    If you need to reschedule or cancel your appointment, please contact us at:
    Phone: (555) 123-4567
    Email: info@stylishcuts.com

    We look forward to seeing you!

    Best regards,
    Stylish Cuts Team
    '''
    
    # Email template for admin
    admin_template = '''
    New Appointment Booking:

    Client: {{ appointment.client_name }}
    Email: {{ appointment.client_email }}
    Service: {{ appointment.service }}
    Date: {{ appointment.date.strftime('%B %d, %Y') }}
    Time: {{ appointment.date.strftime('%I:%M %p') }}
    '''
    
    with app.app_context():
        # Send confirmation to customer
        customer_msg = Message(
            'Appointment Confirmation - Stylish Cuts',
            recipients=[appointment.client_email]
        )
        customer_msg.body = render_template_string(customer_template, appointment=appointment)
        mail.send(customer_msg)
        
        # Send notification to admin
        admin_msg = Message(
            'New Appointment Booking',
            recipients=['admin@stylishcuts.com']
        )
        admin_msg.body = render_template_string(admin_template, appointment=appointment)
        mail.send(admin_msg)
