from flask import Flask, render_template, request, flash, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)

# Database Config
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "James"
app.config['MYSQL_DB'] = 'shadowrobot'
app.config['MYSQL_SSL'] = {'ssl': {'verify_ssl': False}}  # Disable SSL verification
app.config['SECRET_KEY'] = 'Jamiecoo202'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# File Upload Config
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Mail Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pleasurex.customer.care@gmail.com'
app.config['MAIL_PASSWORD'] = 'hkyh tjnl gdib atzf'
app.config['MAIL_DEFAULT_SENDER'] = 'pleasurex.customer.care@gmail.com'

# Initialize extensions
bcrypt = Bcrypt(app)
mysql = MySQL(app)
mail = Mail(app)





@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')  # Fixed typo
        attachment = request.files.get('attachment')
        name_selection = request.form.get('name_selection')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        age = request.form.get('age')
        password = request.form.get('password')

        # Handle File Upload
        attachment_filename = None
        if attachment:
            filename = secure_filename(attachment.filename)
            attachment_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment.save(attachment_path)
            attachment_filename = filename  # Store filename in DB

        conn = mysql.connection
        cursor = conn.cursor()

        # Check if phone (card number) is already registered
        cursor.execute("SELECT * FROM user WHERE phone = %s", (phone,))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            flash("Card already registered. Please choose another card.", "error")
            return redirect(url_for('signup'))

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert user data into database
        cursor.execute(
            """INSERT INTO user (email, attachment, name_selection, phone, dob, age, password, created_at) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
            (email, attachment_filename, name_selection, phone, dob, age, hashed_password)
        )

        conn.commit()
        cursor.close()

        flash("Form submitted successfully!After reviewing your file in few days we will update you in via the email you provided. Whishing you all the luck .", "success")
        return redirect(url_for('index'))

    return render_template('index.html')




@app.route('/Application', methods=['GET', 'POST'])
def Application():
    if request.method == 'POST':
        # Handle form submission here
        email = request.form.get('email')
        position = request.form.get('position')
        username = request.form.get('username')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        age = request.form.get('age')
        country = request.form.get('country')
        postalcode = request.form.get('postalcode')
        attachment = request.files.get('attachment')
        password = request.form.get('password')

        if not email or not position or not username or not phone:
            flash("All required fields must be filled.", "error")
            return redirect(url_for('Application'))

        # Save attachment if uploaded
        filename = None
        if attachment and attachment.filename != '':
            filename = attachment.filename
            attachment_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment.save(attachment_path)

        # Check if phone number is already registered
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications WHERE phone = %s", (phone,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            flash("Phone number already registered.", "error")
            return redirect(url_for('Application'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert new application into the database
        try:
            cursor.execute(
                """INSERT INTO applications (email, position, username, phone, dob, age, country, postalcode, attachment, password, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                (email, position, username, phone, dob, age, country, postalcode, filename, hashed_password)
            )
            conn.commit()

            # If insertion is successful, send the email
            send_email(email, username, position)

            flash("Application submitted successfully! Check your email for updates.", "success")
            return redirect(url_for('index'))

        except Exception as e:
            # Rollback if any error occurs
            conn.rollback()
            cursor.close()
            print(f"Error: {e}")
            flash("There was an issue with the submission. Please try again.", "error")
            return redirect(url_for('Application'))

        cursor.close()

    return render_template('index.html')

def send_email(user_email, username, position):
    """Send confirmation email to the user."""
    try:
        msg = Message("Application Received - PleasureX",
                      sender=app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[user_email])
        msg.body = f"""
        Hi {username},

        Thank you for applying for the {position} position at PleasureX.
        Your application has been received successfully. Our team will review your details and get back to you soon.

        Regards,
        PleasureX Recruitment Team
        """

        mail.send(msg)
        print(f"Email sent successfully to {user_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
        flash("Error sending email. Please try again.", "error")
        return redirect(url_for('Application'))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
