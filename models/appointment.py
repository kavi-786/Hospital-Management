from . import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)

    status = db.Column(
        db.Enum('Pending', 'Accepted', 'Rejected', 'Completed'),
        default='Pending'
    )

    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)