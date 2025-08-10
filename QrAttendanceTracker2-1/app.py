import os
import logging
import qrcode
import io
import base64
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, flash, session
from urllib.parse import urlparse
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from forms import AttendanceForm, SessionForm, LoginForm, RegistrationForm

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
# Default admin password - should be changed in production
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///attendance.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# We're not using Flask-Login anymore, just session-based authentication

with app.app_context():
    # Import models
    from models import Session, Attendance, Admin
    db.create_all()

@app.route('/')
def index():
    """Home page with link to generate QR and view attendance"""
    is_admin = session.get('is_admin', False)
    if is_admin:
        return render_template('generate_qr.html', form=SessionForm())
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Admin login route"""
    if session.get('is_admin'):
        return redirect(url_for('generate_qr'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash('Login successful! You can now generate QR codes.', 'success')
            return redirect(url_for('generate_qr'))
        else:
            flash('Invalid admin password. Please try again.', 'danger')
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    """Admin logout route"""
    session.pop('is_admin', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/generate_qr', methods=['GET', 'POST'])
def generate_qr():
    """Generate a QR code for a specific session"""
    # Check if user is admin
    if not session.get('is_admin'):
        flash('Admin access required to generate QR codes', 'warning')
        return redirect(url_for('admin_login'))
        
    form = SessionForm()
    
    if form.validate_on_submit():
        session_name = form.session_name.data
        duration_minutes = form.duration_minutes.data
        
        # Check if session already exists
        existing_session = Session.query.filter_by(name=session_name).first()
        
        # Set expiration time based on user input
        duration = duration_minutes or 5  # Default to 5 minutes if None
        expiration_time = datetime.now() + timedelta(minutes=duration)
        
        if existing_session:
            # Update the existing session with new expiration time
            existing_session.expires_at = expiration_time
            existing_session.is_active = True
            token = existing_session.token
            db.session.commit()
            logging.debug(f"Updated session: {session_name} with new expiration time: {expiration_time}")
        else:
            # Generate new token and create session
            token = str(uuid.uuid4())
            new_session = Session()
            new_session.name = session_name
            new_session.token = token
            new_session.created_at = datetime.now()
            new_session.expires_at = expiration_time
            new_session.is_active = True
            db.session.add(new_session)
            db.session.commit()
            logging.debug(f"Created new session: {session_name} with token: {token}, expires at: {expiration_time}")
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        url = url_for('scan', token=token, _external=True)
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert image to base64 to embed in HTML
        buffered = io.BytesIO()
        img.save(buffered)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return render_template('generate_qr.html', form=form, img_data=img_str, 
                               session_name=session_name, url=url, duration=duration_minutes)
    
    return render_template('generate_qr.html', form=form)

@app.route('/scan/<token>', methods=['GET', 'POST'])
def scan(token):
    """Form for students to mark attendance"""
    # Find session by token
    session_obj = Session.query.filter_by(token=token).first()
    
    if not session_obj:
        flash('Invalid session token', 'danger')
        return redirect(url_for('index'))
    
    # Check if the session has expired (5 minutes)
    if session_obj.is_expired():
        flash('This QR code has expired. Please ask for a new one.', 'warning')
        return redirect(url_for('index'))
    
    # Check if the session is still active
    if not session_obj.is_active:
        flash('This attendance session is no longer active.', 'warning')
        return redirect(url_for('index'))
    
    form = AttendanceForm()
    
    if form.validate_on_submit():
        student_id = form.student_id.data
        reg_number = form.reg_number.data
        name = form.name.data
        
        # Get the user's IP address
        ip_address = request.remote_addr
        # For proxied requests (e.g., behind a load balancer)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            ip_address = forwarded_for.split(',')[0].strip()
        
        # Check if student has already marked attendance for this session
        existing_attendance = Attendance.query.filter_by(
            session_id=session_obj.id, student_id=student_id
        ).first()
        
        if existing_attendance:
            flash('You have already marked attendance for this session', 'warning')
            return redirect(url_for('scan', token=token))
        
        # Record new attendance with IP address
        attendance = Attendance()
        attendance.session_id = session_obj.id
        attendance.student_id = student_id
        attendance.reg_number = reg_number
        attendance.name = name
        attendance.timestamp = datetime.now()
        attendance.ip_address = ip_address
        db.session.add(attendance)
        db.session.commit()
        logging.debug(f"Recorded attendance for {name} (ID: {student_id}) in session: {session_obj.name} from IP: {ip_address}")
        
        flash('Attendance marked successfully!', 'success')
        return redirect(url_for('success'))
    
    return render_template('scan.html', form=form, session=session_obj)

@app.route('/success')
def success():
    """Success page after marking attendance"""
    return render_template('success.html')

@app.route('/get_attendance', methods=['GET'])
def get_attendance():
    """View all attendance records"""
    # Get all sessions
    sessions = Session.query.all()
    
    # For each session, get attendance records
    attendance_data = {}
    for session_obj in sessions:
        attendance_data[session_obj] = Attendance.query.filter_by(session_id=session_obj.id).all()
    
    return render_template('attendance_list.html', attendance_data=attendance_data)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('base.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('base.html', error="Internal server error"), 500
