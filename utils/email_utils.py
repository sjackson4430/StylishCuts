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
        # Log the attempt
        app.logger.info(f"Starting email send process for appointment {appointment.id}")
        
        if not os.environ.get('SENDGRID_API_KEY'):
            error_msg = "SendGrid API key is not configured"
            app.logger.error(error_msg)
            return False, error_msg

        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        
        # Prepare customer email
        app.logger.info(f"Preparing customer confirmation email for {appointment.client_email}")
        message = Mail(
            from_email='info@stylishcuts.com',  # SendGrid verified sender
            to_emails=appointment.client_email,
            subject='Appointment Confirmation - Stylish Cuts',
            html_content=render_template_string(customer_template, appointment=appointment)
        )
        
        # Send customer email
        try:
            app.logger.info(f"Sending customer confirmation to {appointment.client_email}")
            response = sg.send(message)
            app.logger.info(f"SendGrid API Response - Status: {response.status_code}, Body: {response.body}, Headers: {response.headers}")
            
            if response.status_code not in [200, 201, 202]:
                raise Exception(f"SendGrid API returned status code {response.status_code}")
                
        except Exception as e:
            app.logger.error(f"Failed to send customer email: {str(e)}")
            return False, f"Failed to send customer email: {str(e)}"

        # Prepare admin email
        app.logger.info("Preparing admin notification email")
        admin_message = Mail(
            from_email='info@stylishcuts.com',
            to_emails='admin@stylishcuts.com',
            subject='New Appointment Booking',
            html_content=render_template_string(admin_template, appointment=appointment)
        )
        
        # Send admin email
        try:
            app.logger.info("Sending admin notification")
            response = sg.send(admin_message)
            app.logger.info(f"Admin email SendGrid Response - Status: {response.status_code}")
            
            if response.status_code not in [200, 201, 202]:
                raise Exception(f"SendGrid API returned status code {response.status_code}")
                
        except Exception as e:
            app.logger.error(f"Failed to send admin email: {str(e)}")
            return False, f"Failed to send admin email: {str(e)}"

        app.logger.info("All emails sent successfully")
        return True, "Emails sent successfully"
        
    except Exception as e:
        error_msg = f"SendGrid error: {str(e)}"
        app.logger.error(error_msg)
        return False, error_msg
