from flask import Blueprint, render_template, g

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    cursor = g.db.cursor()
    # Fetch some doctors to show on the home page
    cursor.execute('''
    SELECT u.name, u.image, d.specialization 
    FROM doctors d
    JOIN users u ON d.user_id = u.id
    WHERE d.availability_status = TRUE
    LIMIT 4
''')
    doctors = cursor.fetchall()
    return render_template('index.html', doctors=doctors)
