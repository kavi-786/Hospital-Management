from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()   

def create_app():
    app = Flask(__name__)

   
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        "mysql+mysqlconnector://if0_41821364:rf5jJst9MjTKjps@sql102.infinityfree.com:3306/if0_41821364_hospital_db"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

   
    db.init_app(app)

    return app
