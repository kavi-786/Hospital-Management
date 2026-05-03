from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['name'] = user['name']
            
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user['role'] == 'Admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'Doctor':
                return redirect(url_for('doctor.dashboard'))
            elif user['role'] == 'Patient':
                return redirect(url_for('patient.dashboard'))
            else:
                return redirect(url_for('staff.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        role = 'Patient' # Default role for public registration
        
        # Check if username exists
        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash('Username already exists!', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_password = generate_password_hash(password)
        
        try:
            # Insert User
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, name, email, phone) 
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (username, hashed_password, role, name, email, phone))
            user_id = cursor.lastrowid
            
            # Insert Patient record
            cursor.execute("INSERT INTO patients (user_id) VALUES (%s)", (user_id,))
            g.db.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            g.db.rollback()
            flash('An error occurred. Please try again.', 'danger')
            print(e)
            
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
