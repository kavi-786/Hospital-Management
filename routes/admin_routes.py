from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import time

admin_bp = Blueprint('admin', __name__)

# 🔒 Admin protection
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'Admin':
            flash('Access denied. Admin only.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# 📊 Dashboard
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    cursor = g.db.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM doctors")
    doctors_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM patients")
    patients_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM appointments")
    appointments_count = cursor.fetchone()['count']

    return render_template('admin_dashboard.html',
                           d_count=doctors_count,
                           p_count=patients_count,
                           a_count=appointments_count)


# 👨‍⚕️ MANAGE STAFF (FULL FIXED)
@admin_bp.route('/staff', methods=['GET', 'POST'])
@admin_required
def manage_staff():
    cursor = g.db.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        email = request.form.get('email')
        phone = request.form.get('phone')

        hashed_password = generate_password_hash(password)

        # 📸 IMAGE UPLOAD (100% WORKING)
        image_file = request.files.get('image')
        filename = "default.png"

        if image_file and image_file.filename.strip() != "":
            filename = str(int(time.time())) + "_" + secure_filename(image_file.filename)

            upload_folder = os.path.join('static', 'images', 'staff')
            os.makedirs(upload_folder, exist_ok=True)

            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)

            print("✅ SAVED:", image_path)
        else:
            print("❌ NO IMAGE RECEIVED")

        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, name, email, phone, image)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (username, hashed_password, role, name, email, phone, filename))

            user_id = cursor.lastrowid

            # 👨‍⚕️ Doctor insert
            if role == 'Doctor':
                specialization = request.form.get('specialization', 'General')

                cursor.execute("""
                    INSERT INTO doctors (user_id, specialization)
                    VALUES (%s, %s)
                """, (user_id, specialization))

            g.db.commit()
            flash(f'{role} added successfully!', 'success')

        except Exception as e:
            g.db.rollback()
            print("ERROR:", e)
            flash('Error occurred.', 'danger')

        return redirect(url_for('admin.manage_staff'))

    cursor.execute("SELECT * FROM users WHERE role != 'Patient'")
    staff = cursor.fetchall()

    return render_template('admin_staff.html', staff=staff)


# 🧹 DELETE STAFF
@admin_bp.route('/delete_staff/<int:id>')
@admin_required
def delete_staff(id):
    cursor = g.db.cursor()

    # Get image name
    cursor.execute("SELECT image FROM users WHERE id=%s", (id,))
    user = cursor.fetchone()

    if user and user['image'] and user['image'] != "default.png":
        # ✅ Create correct file path
        file_path = os.path.join('static', 'images', 'staff', user['image'])

        # ✅ Delete file if exists
        if os.path.exists(file_path):
            os.remove(file_path)
            print("🗑️ Deleted:", file_path)

    # Delete user from DB
    cursor.execute("DELETE FROM users WHERE id=%s", (id,))
    g.db.commit()

    flash("Deleted successfully!", "danger")
    return redirect(url_for('admin.manage_staff'))