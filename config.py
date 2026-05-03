import os

class Config:
    SECRET_KEY = "a9f3K!x2@Pq8Zz91Lm"

    
    MYSQL_HOST = mysql.railway.internal
    MYSQL_USER = root
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') 
    MYSQL_DB = railway

    
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your_email@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your_app_password'

    
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID') or 'your_twilio_sid'
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN') or 'your_twilio_auth_token'
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER') or '+1234567890'
