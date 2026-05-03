from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from functools import wraps

staff_bp = Blueprint('staff', __name__)

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] not in ['Nurse', 'Ambulance', 'Store']:
            flash('Access denied. Staff only.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@staff_bp.route('/dashboard')
@staff_required
def dashboard():
    role = session['role']
    cursor = g.db.cursor()
    
    if role == 'Nurse':
        cursor.execute('''
            SELECT a.*, pu.name as patient_name, pu.email, pu.phone, p.blood_group, p.address, du.name as doctor_name, d.specialization
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN users pu ON p.user_id = pu.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users du ON d.user_id = du.id
            ORDER BY a.appointment_date DESC
        ''')
        appointments = cursor.fetchall()
        
        return render_template('nurse_dashboard.html', appointments=appointments)
        
    elif role == 'Ambulance':
        cursor.execute("SELECT * FROM emergency_requests ORDER BY created_at DESC")
        requests = cursor.fetchall()
        return render_template('ambulance_dashboard.html', requests=requests)
        
    elif role == 'Store':
        cursor.execute("SELECT * FROM medicines")
        medicines = cursor.fetchall()
        return render_template('store_dashboard.html', medicines=medicines)

@staff_bp.route('/ambulance/update/<int:id>', methods=['POST'])
@staff_required
def update_ambulance_status(id):
    if session['role'] != 'Ambulance': return redirect(url_for('main.index'))
    status = request.form['status']
    cursor = g.db.cursor()
    cursor.execute("UPDATE emergency_requests SET status = %s WHERE id = %s", (status, id))
    g.db.commit()
    flash('Emergency request updated.', 'success')
    return redirect(url_for('staff.dashboard'))

@staff_bp.route('/store/medicine/add', methods=['POST'])
@staff_required
def add_medicine():
    if session['role'] != 'Store': return redirect(url_for('main.index'))
    name = request.form['name']
    quantity = request.form['quantity']
    price = request.form['price']
    
    cursor = g.db.cursor()
    cursor.execute('''
        INSERT INTO medicines (name, stock_quantity, price) 
        VALUES (%s, %s, %s)
    ''', (name, quantity, price))
    g.db.commit()
    flash('Medicine added to stock.', 'success')
    return redirect(url_for('staff.dashboard'))

@staff_bp.route('/store/medicine/edit/<int:id>', methods=['POST'])
@staff_required
def edit_medicine(id):
    if session['role'] != 'Store': return redirect(url_for('main.index'))
    name = request.form['name']
    quantity = request.form['quantity']
    price = request.form['price']
    
    cursor = g.db.cursor()
    cursor.execute('''
        UPDATE medicines 
        SET name = %s, stock_quantity = %s, price = %s 
        WHERE id = %s
    ''', (name, quantity, price, id))
    g.db.commit()
    flash('Medicine updated successfully.', 'success')
    return redirect(url_for('staff.dashboard'))
