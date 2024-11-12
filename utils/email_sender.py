from flask_mail import Message
from app import mail
from flask import render_template

def send_appointment_confirmation(appointment):
    """Send appointment confirmation email to client."""
    msg = Message(
        'Appointment Confirmation - Stylish Cuts',
        sender=('Stylish Cuts', 'noreply@stylishcuts.com'),
        recipients=[appointment.client_email]
    )
    
    msg.html = render_template(
        'emails/appointment_confirmation.html',
        appointment=appointment
    )
    mail.send(msg)

def send_appointment_notification_admin(appointment):
    """Send appointment notification to admin."""
    msg = Message(
        'New Appointment Booking',
        sender=('Stylish Cuts', 'noreply@stylishcuts.com'),
        recipients=['admin@stylishcuts.com']
    )
    
    msg.html = render_template(
        'emails/appointment_notification_admin.html',
        appointment=appointment
    )
    mail.send(msg)
