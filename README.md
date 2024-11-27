# Signup-Verify-Login-App

A Flask-based web application to handle user signup, OTP verification, and login functionality. This app uses MongoDB for data storage and includes robust validation, OTP email integration, and user authentication.

## Features
- **Signup**: User registration with validations.
- **OTP Verification**: Email-based OTP verification for secure signup.
- **Login**: User authentication with hashed passwords.
- **MongoDB Integration**: Stores user and OTP data.
- **Email Integration**: Sends OTP emails using SMTP.

## Installation

### Prerequisites
1. Python 3.8+
2. MongoDB instance
3. SMTP server for email delivery

### Steps
1. Clone the repository:
   git clone https://github.com/Samson-DVS/signup-verify-login-app.git

2. Install dependencies
   pip install -r requirements.txt
   
3. Configure environment variables: Create a .env file in the root directory and include the following
  SECRET_KEY=your_secret_key
  MONGO_URI=your_mongo_connection_string
  SMTP_SERVER=smtp.your-email-provider.com
  SMTP_PORT=587
  SMTP_USERNAME=your_email_username
  SMTP_PASSWORD=your_email_password
  EMAIL_FROM=your_email_address

4. Run the application:
  python3 app.py

5. Access the app at http://127.0.0.1:5001/signup
