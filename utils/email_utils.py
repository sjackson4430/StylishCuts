import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template_string
from app import app

def send_appointment_confirmation(appointment):
    """
    Send appointment confirmation emails to both customer and admin using SMTP.
    Returns True if both emails are sent successfully, False otherwise.
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
        # SMTP Configuration
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = int(os.environ.get('SMTP_PORT'))
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        # Create SSL context
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            try:
                # Login to SMTP server
                server.login(smtp_username, smtp_password)
                app.logger.info("Successfully connected to SMTP server")
                
                # Send customer confirmation
                msg = MIMEMultipart('alternative')
                msg['Subject'] = 'Appointment Confirmation - Stylish Cuts'
                msg['From'] = smtp_username
                msg['To'] = appointment.client_email
                
                html_content = render_template_string(customer_template, appointment=appointment)
                msg.attach(MIMEText(html_content, 'html'))
                
                server.send_message(msg)
                app.logger.info(f"Customer confirmation email sent successfully to {appointment.client_email}")
                
                # Send admin notification
                admin_msg = MIMEMultipart('alternative')
                admin_msg['Subject'] = 'New Appointment Booking'
                admin_msg['From'] = smtp_username
                admin_msg['To'] = 'admin@stylishcuts.com'
                
                html_content = render_template_string(admin_template, appointment=appointment)
                admin_msg.attach(MIMEText(html_content, 'html'))
                
                server.send_message(admin_msg)
                app.logger.info("Admin notification email sent successfully")
                
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                app.logger.error(f"SMTP Authentication failed: {str(e)}")
                return False
            except smtplib.SMTPException as e:
                app.logger.error(f"SMTP error occurred: {str(e)}")
                return False
                
    except Exception as e:
        app.logger.error(f"Failed to send emails: {str(e)}")
        return False
