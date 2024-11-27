#Author : Visahl Samson (visahlsamson@gmail.com)
#Version : V1.0
#Date : 27 Nov 2024

from flask import Flask, request, redirect, url_for, flash, render_template, session
from flask_pymongo import PyMongo
import bcrypt
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['MAIL_SERVER'] = os.getenv('SMTP_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('SMTP_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('SMTP_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('SMTP_PASSWORD')
app.config['SENDER_EMAIL'] = os.getenv('EMAIL_FROM')

# Initialize MongoDB connection
mongo = PyMongo(app)

# Function to send OTP email
def send_otp_email(email, otp):
    sender_email = app.config['SENDER_EMAIL']
    sender_password = app.config['MAIL_PASSWORD']
    smtp_server = app.config['MAIL_SERVER']
    smtp_port = app.config['MAIL_PORT']

    subject = "Your OTP Code"
    body = f"Your OTP code is {otp}. It is valid for 5 minutes."

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
            print(f"OTP email sent to {email}")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')

        # Validation
        if not username or len(username) < 3 or len(username) > 15 or ' ' in username or not username.isalnum() or username.isdigit():
            flash('Invalid username.', 'danger')
            return redirect(url_for('signup'))

        if not email or '@' not in email or '.' not in email.split('@')[-1]:
            flash('Invalid email address.', 'danger')
            return redirect(url_for('signup'))

        if not mobile or not mobile.isdigit() or len(mobile) < 6 or len(mobile) > 15:
            flash('Invalid mobile number.', 'danger')
            return redirect(url_for('signup'))

        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password):
            flash('Invalid password.', 'danger')
            return redirect(url_for('signup'))

        # Check if user already exists
        if mongo.db.user.find_one({'email': email}):
            flash('Email is already registered.', 'danger')
            return redirect(url_for('signup'))
        if mongo.db.user.find_one({'username': username}):
            flash('Username is not available.', 'danger')
            return redirect(url_for('signup'))
        if mongo.db.user.find_one({'mobile': mobile}):
            flash('Mobile is already registered.', 'danger')
            return redirect(url_for('signup'))

        # Generate and store OTP
        otp = str(random.randint(100000, 999999))
        expiration_time = datetime.utcnow() + timedelta(minutes=5)
        mongo.db.otps.insert_one({'email': email, 'otp': otp, 'expires_at': expiration_time})

        send_otp_email(email, otp)
        session['email'] = email
        session['mobile'] = mobile
        session['username'] = username
        session['password'] = password

        return render_template('verify_otp.html')

    return render_template('signup.html')

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    email = session.get('email')
    mobile = session.get('mobile')
    user_otp = request.form.get('otp')
    username = session.get('username')
    password = session.get('password')

    otp_record = mongo.db.otps.find_one({'email': email, 'otp': user_otp})
    if otp_record and otp_record['expires_at'] > datetime.utcnow():
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        mongo.db.user.insert_one({'username': username, 'email': email, 'mobile': mobile, 'password': hashed_password.decode('utf-8')})
        mongo.db.otps.delete_one({'_id': otp_record['_id']})
        session.clear()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    else:
        flash('Invalid or expired OTP', 'danger')
        return redirect(url_for('signup'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password').encode('utf-8')

        user = mongo.db.user.find_one({'username': username})
        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            flash(f"Welcome back, {username}!", 'success')
            return redirect(url_for('home'))
        else:
            flash('Incorrect username or password.', 'danger')

    return render_template('login.html')

if __name__ == '__main__':
    run_simple('0.0.0.0', 5000, app, use_reloader=False)
