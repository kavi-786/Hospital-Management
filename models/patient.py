from . import db

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blood_group = db.Column(db.String(5))
    address = db.Column(db.Text)

    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True)