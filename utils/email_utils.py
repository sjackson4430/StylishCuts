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
        # Log attempt to send email
        app.logger.info(f"Attempting to send confirmation emails for appointment {appointment.id}")
        
        # SMTP Configuration
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = int(os.environ.get('SMTP_PORT', 465))  # Default to 465 for SSL
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')

        if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
            error_msg = "SMTP configuration is incomplete"
            app.logger.error(error_msg)
            return False, error_msg

        # Log SMTP connection attempt (without sensitive info)
        app.logger.info(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")
        
        # Create SSL context
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            try:
                # Login to SMTP server
                app.logger.info("Attempting SMTP authentication...")
                server.login(smtp_username, smtp_password)
                app.logger.info("Successfully authenticated with SMTP server")
                
                # Prepare and send customer confirmation
                app.logger.info(f"Preparing customer confirmation email for {appointment.client_email}")
                msg = MIMEMultipart('alternative')
                msg['Subject'] = 'Appointment Confirmation - Stylish Cuts'
                msg['From'] = smtp_username
                msg['To'] = appointment.client_email
                
                html_content = render_template_string(customer_template, appointment=appointment)
                msg.attach(MIMEText(html_content, 'html'))
                
                server.send_message(msg)
                app.logger.info(f"Customer confirmation email sent successfully to {appointment.client_email}")
                
                # Prepare and send admin notification
                app.logger.info("Preparing admin notification email")
                admin_msg = MIMEMultipart('alternative')
                admin_msg['Subject'] = 'New Appointment Booking'
                admin_msg['From'] = smtp_username
                admin_msg['To'] = 'admin@stylishcuts.com'
                
                html_content = render_template_string(admin_template, appointment=appointment)
                admin_msg.attach(MIMEText(html_content, 'html'))
                
                server.send_message(admin_msg)
                app.logger.info("Admin notification email sent successfully")
                
                return True, "Emails sent successfully"
                
            except smtplib.SMTPAuthenticationError as e:
                error_msg = "Failed to authenticate with SMTP server"
                app.logger.error(f"{error_msg}: {str(e)}")
                return False, error_msg
                
            except smtplib.SMTPRecipientsRefused as e:
                error_msg = "Invalid recipient email address"
                app.logger.error(f"{error_msg}: {str(e)}")
                return False, error_msg
                
            except smtplib.SMTPException as e:
                error_msg = "An error occurred while sending the email"
                app.logger.error(f"{error_msg}: {str(e)}")
                return False, error_msg
                
    except Exception as e:
        error_msg = "Failed to establish connection with SMTP server"
        app.logger.error(f"{error_msg}: {str(e)}")
        return False, error_msg
