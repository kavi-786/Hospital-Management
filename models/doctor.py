from . import db

class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    availability_status = db.Column(db.Boolean, default=True)
    image = db.Column(db.String(255), nullable=True)

    # ✅ Relationships
    user = db.relationship('User', backref='doctor_profile', lazy=True)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)