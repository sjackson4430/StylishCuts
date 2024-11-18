import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask import render_template_string
from app import app

def send_appointment_confirmation(appointment):
    """
    Send appointment confirmation emails to both customer and admin using SendGrid.
    Returns (success: bool, error_message: str)
    """
    # Email templates with HTML formatting
    customer_template = '''
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2>Appointment Confirmation - Stylish Cuts</h2>
        <p>Dear {{ appointment.client_name }},</p>
        
        <p>Thank you for booking an appointment with Stylish Cuts Barbershop!</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Appointment Details:</h3>
            <ul style="list-style: none; padding-left: 0;">
                <li><strong>Service:</strong> {{ appointment.service }}</li>
                <li><strong>Date:</strong> {{ appointment.date.strftime('%B %d, %Y') }}</li>
                <li><strong>Time:</strong> {{ appointment.date.strftime('%I:%M %p') }} PST</li>
                <li><strong>Location:</strong> 123 Main Street, City, State 12345</li>
            </ul>
        </div>
        
        <p>If you need to reschedule or cancel your appointment, please contact us at:</p>
        <ul>
            <li>Phone: (555) 123-4567</li>
            <li>Email: info@stylishcuts.com</li>
        </ul>
        
        <p>We look forward to seeing you!</p>
        
        <p>Best regards,<br>
        Stylish Cuts Team</p>
    </body>
    </html>
    '''
    
    admin_template = '''
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2>New Appointment Booking</h2>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <ul style="list-style: none; padding-left: 0;">
                <li><strong>Client:</strong> {{ appointment.client_name }}</li>
                <li><strong>Email:</strong> {{ appointment.client_email }}</li>
                <li><strong>Service:</strong> {{ appointment.service }}</li>
                <li><strong>Date:</strong> {{ appointment.date.strftime('%B %d, %Y') }}</li>
                <li><strong>Time:</strong> {{ appointment.date.strftime('%I:%M %p') }} PST</li>
            </ul>
        </div>
    </body>
    </html>
    '''

    try:
        app.logger.info(f"Attempting to send confirmation emails for appointment {appointment.id}")
        
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        
        # Customer email
        message = Mail(
            from_email='sjackson@jacksonwebdev.com',  # SendGrid verified sender
            to_emails=appointment.client_email,
            subject='Appointment Confirmation - Stylish Cuts',
            html_content=render_template_string(customer_template, appointment=appointment)
        )
        
        # Send customer email
        response = sg.send(message)
        app.logger.info(f"Customer confirmation email sent. Status code: {response.status_code}")
        
        # Admin notification
        admin_message = Mail(
            from_email='sjackson@jacksonwebdev.com',
            to_emails='sjackson@jacksonwebdev.com',
            subject='New Appointment Booking',
            html_content=render_template_string(admin_template, appointment=appointment)
        )
        
        # Send admin email
        response = sg.send(admin_message)
        app.logger.info(f"Admin notification email sent. Status code: {response.status_code}")
        
        return True, "Emails sent successfully"
        
    except Exception as e:
        error_msg = f"SendGrid error: {str(e)}"
        app.logger.error(error_msg)
        return False, error_msg