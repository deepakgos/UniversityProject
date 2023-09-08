from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from datetime import datetime  # Import the datetime module
from flask_mail import Mail
from flask import send_from_directory
from werkzeug.utils import secure_filename  # Import secure_filename function
import pyodbc
import os

app = Flask(__name__)

# Database connection configuration
server = 'BOJO\SQLEXPRESS'
database = 'university'
driver = '{ODBC Driver 17 for SQL Server}'

# Function to establish a database connection
def create_connection():
    return pyodbc.connect(
        f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    )

@app.route('/')
def home():
    return render_template('index.html')


# Route to handle the about page
@app.route('/about')
def about_page():
    return render_template('about.html')


# Route to handle the service page
@app.route('/service')
def service_page():
    return render_template('service.html')

# Route to handle the services page
@app.route('/servicereports')
def servicedem_page():
    return render_template('services.html')

# Route to handle the report page
@app.route('/analysis')
def analysis_page():
    return render_template('analysis.html')

# Route to handle the upload page
@app.route('/upload data')
def upload_page():
    return render_template('upload.html')

# Route to handle the admin_login page
@app.route('/admin_login')
def admin_login_page():
    return render_template('admin_login.html')

# Route to handle the static pages
@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'static'), filename)

# Route to handle the customer_registration page
@app.route('/customer_registration')
def customer_registration_page():
    return render_template('customer_registration.html')

#Route to handle admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if admin credentials are valid
        # if email == 'admin@example.com' and password == 'admin_password':
        # Fetch the list of people who have contacted
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT email, password FROM AdminCredentials WHERE email = ? AND password = ?", email, password)
            admin = cursor.fetchone()
            if admin:
                cursor.execute("SELECT name, email, phone, message, timestamp FROM tblContactForm ORDER BY timestamp DESC")
                contact_list = cursor.fetchall()
                conn.close()

                return render_template('admin_dashboard.html', contact_list=contact_list)

        except Exception as e:
            print("An error occurred:", str(e))
            return "An error occurred while fetching data."

    return render_template('admin_login.html')

# #email handling

# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'datamind.org@gmail.com'
# app.config['MAIL_PASSWORD'] = 'your-email-password'

# mail = Mail(app)

# @app.route('/submit', methods=['POST'])
# def submit_form():
#     name = request.form.get('name')
#     email = request.form.get('email')
#     phone = request.form.get('phone')
#     message = request.form.get('message')

#     # Check if a file was uploaded
#     if 'zip_file' in request.files:
#         zip_file = request.files['zip_file']

#         # Handle the uploaded zip file (e.g., save it to the 'uploads' folder)
#         if zip_file and zip_file.filename.endswith('.zip'):
#             # Generate a unique filename (you can use a timestamp)
#             timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#             filename = f"{timestamp}_{secure_filename(zip_file.filename)}"
#             zip_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

#             try:
#                 # Create a database connection
#                 conn = create_connection()

#                 # Get the current timestamp
#                 timestamp = datetime.now()

#                 # Insert form data into the database, including the filename
#                 cursor = conn.cursor()
#                 cursor.execute(
#                     "EXEC EnterContactDetails @name=?, @email=?, @phone=?, @message=?, @timestamp=?, @zip_filename=?",
#                     name, email, phone, message, timestamp, filename
#                 )
#                 conn.commit()
#                 cursor.close()
#                 conn.close()

#                 # Clear form fields and render the contact form again
#                 return render_template('upload.html', message="Form submitted successfully.")

#             except Exception as e:
#                 # Handle any errors that occur during database operations
#                 print("An error occurred while submitting the form:", str(e))
#                 return "An error occurred while submitting the form."

#     # If no file was uploaded or the uploaded file is not a .zip file, proceed without saving and just insert the form data
#     try:
#         # Create a database connection
#         conn = create_connection()

#         # Get the current timestamp
#         timestamp = datetime.now()

#         # Insert form data into the database without a filename
#         cursor = conn.cursor()
#         cursor.execute(
#             "EXEC EnterContactDetails @name=?, @email=?, @phone=?, @message=?, @timestamp=?, @zip_filename=NULL",
#             name, email, phone, message, timestamp
#         )
#         conn.commit()
#         cursor.close()
#         conn.close()

#         # Clear form fields and render the contact form again
#         return render_template('upload.html', message="Form submitted successfully.")

#     except Exception as e:
#         # Handle any errors that occur during database operations
#         print("An error occurred while submitting the form:", str(e))
#         return "An error occurred while submitting the form."

#file upload with checking
@app.route('/submit', methods=['POST'])
def submit_form():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')

    upload_success = False
    user_not_registered = False
    # Check if the user is registered
    if is_user_registered(email):  # Implement is_user_registered function
        # Handle file uploads for registered users
        # ...
        # Check if a file was uploaded
        if 'zip_file' in request.files:
            zip_file = request.files['zip_file']

            # Handle the uploaded zip file (e.g., save it to the 'uploads' folder)
            if zip_file and zip_file.filename.endswith('.zip'):
                # Generate a unique filename (you can use a timestamp)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{timestamp}_{secure_filename(zip_file.filename)}"
                zip_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                try:
                    # Create a database connection
                    conn = create_connection()

                    # Get the current timestamp
                    timestamp = datetime.now()

                    # Insert form data into the database, including the filename
                    cursor = conn.cursor()
                    cursor.execute(
                        "EXEC EnterContactDetails @name=?, @email=?, @phone=?, @message=?, @timestamp=?, @zip_filename=?",
                        name, email, phone, message, timestamp, filename
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()

                    # Clear form fields and render the contact form again
                    # return render_template('upload.html', upload_success=True)
                    upload_success = True
                except Exception as e:
                    # Handle any errors that occur during database operations
                    print("An error occurred while submitting the form:", str(e))
                    # return "An error occurred while submitting the form."
        # return render_template('upload.html', upload_success=False)
    else:
        user_not_registered = True
        # return render_template('upload.html', user_not_registered=user_not_registered)
    return render_template('upload.html', upload_success=upload_success, user_not_registered=user_not_registered)
# Function to check if a user is registered based on their email
def is_user_registered(email):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tblCustomerRegistration WHERE Email = ?", email)
        count = cursor.fetchone()[0]
        conn.close()

        return count > 0  # Return True if the count is greater than 0 (user is registered)
    except Exception as e:
        print("An error occurred while checking user registration:", str(e))
        return False  # Assume the user is not registered on error


# Route to render the admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    # Fetch the list of people who have contacted (you can move this code to a function)
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, email, phone, message, timestamp, zip_filename FROM tblContactForm ORDER BY timestamp DESC")
        contact_list = cursor.fetchall()
        conn.close()

        return render_template('admin_dashboard.html', contact_list=contact_list)

    except Exception as e:
        print("An error occurred:", str(e))
        return "An error occurred while fetching data."

#Route to handle downloads
@app.route('/download_zip/<filename>')
def download_zip(filename):
    zip_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f"Attempting to download file: {zip_file_path}")

    # Check if the file exists before attempting to send it
    if os.path.exists(zip_file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        return "File not found."
    

#Route to handle customer registrations
@app.route('/register', methods=['POST'])
def submit():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        postalcode = request.form['postalcode']
        country = request.form['country']

        # Insert data into the database
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("Exec sp_EnterRegistrationDetails @FirstName=?, @LastName=?, @Email=?, @Password=?, @Phone=?, @Address=?, @City=?, @State=?, @PostalCode=?, @Country=?",
                       firstname, lastname, email, password, phone, address, city, state, postalcode, country)
        conn.commit()
        cursor.close()

        # return 'Registration Successful! Thank you for registering.'
    return render_template('customer_registration.html',message='Registration Successful! Thank you for registering.')



@app.route('/customer/<int:customer_id>')
def customer_profile(customer_id):
    # Your code to retrieve customer information goes here
    # You can use the customer_id parameter to look up the customer's data
    return f"Customer Profile Page for ID {customer_id}"




@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tblCustomerRegistration WHERE Email = ? AND Password = ?', (email, password))
            customer = cursor.fetchone()
            conn.close()

            # error = False
            if customer:
                # Instead of accessing elements by string indices, use integer indices
                customer_id = customer[0]  # Replace 0 with the correct index of CustomerID
                # Check for an embedded link in tblReportMaster
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT EmbeddedLink FROM tblReportMaster WHERE CustomerID = ?', (customer_id,))
                report = cursor.fetchone()
                conn.close()

                if report and report[0]:  # Replace 0 with the correct index of EmbeddedLink
                    # Pass 'report' to the template
                    embedded_link = report[0]
                    print(f"Embedded Link: {embedded_link}")
                    return render_template('user_reports.html', embedded_link=embedded_link)
                else:
                    # There is no embedded link, show the "please upload data" message
                    return render_template('upload.html', message='Please upload data to access your reports.')

            else:
                error = True
                print("error is:",error)
                return render_template('customer_login.html', error=error)

        return render_template('customer_login.html')

    except Exception as e:
        # Handle any exceptions that occur
        print("An error occurred:", str(e))
        return "An error occurred while processing your request."

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
