from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from functools import wraps

patient_bp = Blueprint('patient', __name__)

def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'Patient':
            flash('Please login as Patient.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@patient_bp.route('/dashboard')
@patient_required
def dashboard():
    cursor = g.db.cursor()
    
    # Get patient ID
    cursor.execute("SELECT id FROM patients WHERE user_id = %s", (session['user_id'],))
    patient = cursor.fetchone()
    patient_id = patient['id']
    
    # Get appointments
    cursor.execute('''
        SELECT a.*, u.name as doctor_name, d.specialization
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date DESC
    ''', (patient_id,))
    appointments = cursor.fetchall()
    # Get user profile details
    cursor.execute("SELECT name, email, phone FROM users WHERE id = %s", (session['user_id'],))
    user_info = cursor.fetchone()
    
    return render_template('patient_dashboard.html', appointments=appointments, user_info=user_info)

@patient_bp.route('/profile/update', methods=['POST'])
@patient_required
def update_profile():
    cursor = g.db.cursor()
    email = request.form.get('email')
    phone = request.form.get('phone')
    
    cursor.execute("UPDATE users SET email = %s, phone = %s WHERE id = %s", (email, phone, session['user_id']))
    g.db.commit()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/book', methods=['GET', 'POST'])
@patient_required
def book_appointment():
    cursor = g.db.cursor()
    
    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        date_str = request.form['date']
        reason = request.form['reason']
        blood_group = request.form.get('blood_group')
        address = request.form.get('address')
        
        from datetime import datetime, timedelta
        try:
            appointment_time = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            if appointment_time < datetime.now() + timedelta(hours=6):
                flash('Appointment must be booked at least 6 hours in advance.', 'danger')
                return redirect(url_for('patient.book_appointment'))
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('patient.book_appointment'))
        
        cursor.execute("SELECT id FROM patients WHERE user_id = %s", (session['user_id'],))
        patient_id = cursor.fetchone()['id']
        
        # Update patient details if provided
        if blood_group or address:
            cursor.execute('''
                UPDATE patients 
                SET blood_group = COALESCE(%s, blood_group), 
                    address = COALESCE(%s, address)
                WHERE id = %s
            ''', (blood_group, address, patient_id))
        
        cursor.execute('''
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason)
            VALUES (%s, %s, %s, %s)
        ''', (patient_id, doctor_id, date_str, reason))
        g.db.commit()
        
        flash('Appointment requested successfully!', 'success')
        return redirect(url_for('patient.dashboard'))
        
    # GET method
    cursor.execute('''
        SELECT d.id, u.name, d.specialization 
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE d.availability_status = TRUE
    ''')
    doctors = cursor.fetchall()
    
    cursor.execute("SELECT blood_group, address FROM patients WHERE user_id = %s", (session['user_id'],))
    patient_info = cursor.fetchone()
    
    return render_template('patient_book.html', doctors=doctors, patient_info=patient_info)
