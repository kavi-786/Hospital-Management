import os
from flask import Flask, render_template, session, g
import pymysql
import pymysql.cursors
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Secret key
app.secret_key = app.config.get("SECRET_KEY")


# =========================
# DATABASE CONNECTION
# =========================
def get_db_connection():
    try:
        return pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            db=app.config['MYSQL_DB'],
            port=app.config.get('MYSQL_PORT', 3306),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    except Exception as e:
        print("❌ DB CONNECTION FAILED:", e)
        return None


# =========================
# BEFORE REQUEST
# =========================
@app.before_request
def before_request():
    g.db = get_db_connection()


# =========================
# TEARDOWN
# =========================
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db:
        db.close()


# =========================
# CONTEXT PROCESSOR
# =========================
@app.context_processor
def inject_user():
    return dict(
        session_role=session.get('role'),
        session_username=session.get('username'),
        session_user_id=session.get('user_id')
    )


# =========================
# BLUEPRINTS
# =========================
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.doctor_routes import doctor_bp
from routes.patient_routes import patient_bp
from routes.staff_routes import staff_bp
from routes.main_routes import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(doctor_bp, url_prefix='/doctor')
app.register_blueprint(patient_bp, url_prefix='/patient')
app.register_blueprint(staff_bp, url_prefix='/staff')
app.register_blueprint(main_bp)


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# =========================
# RENDER ENTRY POINT
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
