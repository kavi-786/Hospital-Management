from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, current_app
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.request
import urllib.parse
import json
import base64
import threading

doctor_bp = Blueprint('doctor', __name__)

def send_notifications_async(app, config, patient, status, nurses, html_content):
    with app.app_context():
        # SEND REAL EMAIL TO PATIENT
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Appointment {status} - HMS"
            msg['From'] = config.get('MAIL_USERNAME', 'hospital@example.com')
            msg['To'] = patient['email']

            part = MIMEText(html_content, 'html')
            msg.attach(part)

            server = smtplib.SMTP(config.get('MAIL_SERVER'), config.get('MAIL_PORT'))
            server.starttls()
            server.login(config.get('MAIL_USERNAME'), config.get('MAIL_PASSWORD'))
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
            server.quit()
            print(f"📧 EMAIL sent to {patient['email']}")
        except Exception as e:
            print(f"❌ Failed to send email to patient: {e}")

        # SEND REAL SMS TO PATIENT
        try:
            account_sid = config.get('TWILIO_ACCOUNT_SID')
            auth_token = config.get('TWILIO_AUTH_TOKEN')
            from_phone = config.get('TWILIO_PHONE_NUMBER')
            to_phone = patient['phone']
            
            if account_sid != 'your_twilio_sid':
                url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
                data = urllib.parse.urlencode({
                    'To': to_phone,
                    'From': from_phone,
                    'Body': f"Hello {patient['patient_name']}, your appointment with Dr. {patient['doctor_name']} is {status}."
                }).encode('utf-8')
                
                auth_str = f"{account_sid}:{auth_token}"
                b64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
                
                req = urllib.request.Request(url, data=data)
                req.add_header("Authorization", f"Basic {b64_auth}")
                urllib.request.urlopen(req)
                print(f"📱 SMS sent to {patient['phone']}")
            else:
                print(f"📱 SMS logic skipped (using placeholder Twilio keys)")
        except Exception as e:
            print(f"❌ Failed to send SMS to patient: {e}")

        # If appointment is accepted, notify nurses
        if status == 'Accepted':
            for nurse in nurses:
                try:
                    msg_nurse = MIMEMultipart('alternative')
                    msg_nurse['Subject'] = f"Action Required: Patient Appointment Accepted"
                    msg_nurse['From'] = config.get('MAIL_USERNAME', 'hospital@example.com')
                    msg_nurse['To'] = nurse['email']
                    
                    nurse_html = f'''
                    <h3>Hello {nurse['name']},</h3>
                    <p>An appointment for patient <strong>{patient['patient_name']}</strong> has been <strong>Accepted</strong> by Dr. {patient['doctor_name']}.</p>
                    <p>Please contact the patient to confirm pre-appointment details.</p>
                    <ul>
                        <li>Patient Phone: {patient['phone']}</li>
                        <li>Patient Email: {patient['email']}</li>
                        <li>Appointment Date: {patient['appointment_date']}</li>
                    </ul>
                    <p>Regards,<br>HMS System</p>
                    '''
                    part_nurse = MIMEText(nurse_html, 'html')
                    msg_nurse.attach(part_nurse)
                    
                    server = smtplib.SMTP(config.get('MAIL_SERVER'), config.get('MAIL_PORT'))
                    server.starttls()
                    server.login(config.get('MAIL_USERNAME'), config.get('MAIL_PASSWORD'))
                    server.sendmail(msg_nurse['From'], [msg_nurse['To']], msg_nurse.as_string())
                    server.quit()
                    print(f"📧 EMAIL sent to Nurse {nurse['name']} at {nurse['email']}")
                except Exception as e:
                    print(f"❌ Failed to send email to nurse: {e}")

# =========================
# AUTH DECORATOR
# =========================
def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'Doctor':
            flash('Access denied. Doctor only.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# =========================
# DOCTOR DASHBOARD
# =========================
@doctor_bp.route('/dashboard')
@doctor_required
def dashboard():
    cursor = g.db.cursor()

    # Get doctor id from logged-in user
    cursor.execute("SELECT id FROM doctors WHERE user_id=%s", (session['user_id'],))
    doctor = cursor.fetchone()

    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('auth.login'))

    doctor_id = doctor['id']

    # Get appointments
    cursor.execute('''
        SELECT a.*, u.name as patient_name, u.phone
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN users u ON p.user_id = u.id
        WHERE a.doctor_id = %s
        ORDER BY a.appointment_date DESC
    ''', (doctor_id,))

    appointments = cursor.fetchall()

    return render_template('doctor_dashboard.html', appointments=appointments)


# =========================
# UPDATE APPOINTMENT (FIX FOR YOUR ERROR)
# =========================
@doctor_bp.route('/appointment/update/<int:id>', methods=['POST'])
@doctor_required
def update_appointment(id):
    cursor = g.db.cursor()

    # get new status from form
    status = request.form.get('status')

    if not status:
        flash("Status is required!", "danger")
        return redirect(url_for('doctor.dashboard'))

    # update appointment
    cursor.execute("""
        UPDATE appointments
        SET status=%s
        WHERE id=%s
    """, (status, id))

    g.db.commit()

    # Fetch patient details for notification
    cursor.execute("""
        SELECT u.email, u.phone, u.name as patient_name, a.appointment_date, du.name as doctor_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN users u ON p.user_id = u.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users du ON d.user_id = du.id
        WHERE a.id = %s
    """, (id,))
    patient = cursor.fetchone()

    if patient:
        nurses = []
        if status == 'Accepted':
            cursor.execute("SELECT name, email FROM users WHERE role = 'Nurse'")
            nurses = cursor.fetchall()
            
        html_content = render_template('email_appointment.html', 
                                       patient_name=patient['patient_name'],
                                       status=status,
                                       doctor_name=patient['doctor_name'],
                                       appointment_date=patient['appointment_date'])
        
        # Start background thread for sending notifications
        app = current_app._get_current_object()
        config = dict(app.config)
        thread = threading.Thread(target=send_notifications_async, args=(app, config, dict(patient), status, list(nurses), html_content))
        thread.start()

        flash(f"Appointment updated! Notifications are being sent in the background.", "success")
    else:
        flash("Appointment updated successfully!", "success")

    return redirect(url_for('doctor.dashboard'))
