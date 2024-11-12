from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Appointment, Deal, Service
from forms import LoginForm, AppointmentForm, DealForm, ServiceForm
from datetime import datetime, timedelta
from utils.email_utils import send_appointment_confirmation
import pytz

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    deals = Deal.query.filter_by(active=True).all()
    services = Service.query.all()
    return render_template('index.html', deals=deals, services=services)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('admin' if user.is_admin else 'index'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/available-slots', methods=['GET'])
def get_available_slots():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Start and end dates are required'}), 400
    
    # Convert to PST timezone
    pst = pytz.timezone('America/Los_Angeles')
    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00')).astimezone(pst)
    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00')).astimezone(pst)
    
    # Get all appointments within the date range
    appointments = Appointment.query.filter(
        Appointment.date >= start_dt,
        Appointment.date <= end_dt
    ).all()
    
    # Convert appointments to events
    booked_slots = [{
        'title': 'Booked',
        'start': appt.date.isoformat(),
        'end': (appt.date + timedelta(hours=1)).isoformat(),
        'display': 'background',
        'color': '#ff0000'
    } for appt in appointments]
    
    return jsonify(booked_slots)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    form = AppointmentForm()
    form.service.choices = [(s.id, s.name) for s in Service.query.all()]
    
    if form.validate_on_submit():
        try:
            # Convert appointment time to PST
            pst = pytz.timezone('America/Los_Angeles')
            appointment_time = datetime.fromisoformat(form.date.data.replace('Z', '+00:00'))
            appointment_time_pst = appointment_time.astimezone(pst)
            
            # Validate business hours (8 AM to 5 PM PST)
            if appointment_time_pst.hour < 8 or appointment_time_pst.hour >= 17:
                flash('Please select a time between 8 AM and 5 PM PST')
                return render_template('booking.html', form=form)
            
            # Check for existing appointments
            existing_appointment = Appointment.query.filter_by(
                date=appointment_time_pst
            ).first()
            
            if existing_appointment:
                flash('This time slot is already booked. Please select another time.')
                return render_template('booking.html', form=form)
            
            # Create new appointment
            service = Service.query.get(form.service.data)
            if not service:
                flash('Invalid service selected')
                return render_template('booking.html', form=form)
                
            appointment = Appointment(
                client_name=form.client_name.data,
                client_email=form.client_email.data,
                date=appointment_time_pst,
                service=service.name
            )
            db.session.add(appointment)
            db.session.commit()
            
            # Send email notifications
            try:
                send_appointment_confirmation(appointment)
                flash('Appointment booked successfully! A confirmation email has been sent.')
            except Exception as e:
                app.logger.error(f"Failed to send email notification: {str(e)}")
                flash('Appointment booked successfully! However, there was an issue sending the confirmation email.')
            
            return redirect(url_for('index'))
            
        except (ValueError, TypeError) as e:
            app.logger.error(f"Invalid date format: {str(e)}")
            flash('Invalid date format. Please select a valid time slot.')
            return render_template('booking.html', form=form)
    
    return render_template('booking.html', form=form)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    appointments = Appointment.query.order_by(Appointment.date.desc()).all()
    deals = Deal.query.all()
    return render_template('admin.html', appointments=appointments, deals=deals)

@app.route('/admin/deals', methods=['GET', 'POST'])
@login_required
def manage_deals():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    form = DealForm()
    if form.validate_on_submit():
        deal = Deal(
            title=form.title.data,
            description=form.description.data,
            valid_until=form.valid_until.data
        )
        db.session.add(deal)
        db.session.commit()
        flash('Deal added successfully!')
        return redirect(url_for('admin'))
    
    return render_template('deals.html', form=form)
