from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Deal, Service
from forms import LoginForm, DealForm, ServiceForm
from datetime import datetime

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

from utils.email_utils import send_appointment_confirmation

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/webhook/appointment', methods=['POST'])
def appointment_webhook():
    try:
        data = request.json
        # Create appointment record
        appointment = Appointment(
            client_name=data['firstName'] + ' ' + data['lastName'],
            client_email=data['email'],
            date=datetime.fromisoformat(data['datetime'].replace('Z', '+00:00')),
            service=data['type'],
            status='confirmed'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Send email notifications
        success, error_message = send_appointment_confirmation(appointment)
        if not success:
            app.logger.error(f"Failed to send email notifications: {error_message}")
            
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        app.logger.error(f"Error processing appointment webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    deals = Deal.query.all()
    return render_template('admin.html', deals=deals)

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