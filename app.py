from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from datetime import datetime  # Import the datetime module
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


@app.route('/submit', methods=['POST'])
def submit_form():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')

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
                return render_template('upload.html', message="Form submitted successfully.")

            except Exception as e:
                # Handle any errors that occur during database operations
                print("An error occurred while submitting the form:", str(e))
                return "An error occurred while submitting the form."

    # If no file was uploaded or the uploaded file is not a .zip file, proceed without saving and just insert the form data
    try:
        # Create a database connection
        conn = create_connection()

        # Get the current timestamp
        timestamp = datetime.now()

        # Insert form data into the database without a filename
        cursor = conn.cursor()
        cursor.execute(
            "EXEC EnterContactDetails @name=?, @email=?, @phone=?, @message=?, @timestamp=?, @zip_filename=NULL",
            name, email, phone, message, timestamp
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Clear form fields and render the contact form again
        return render_template('upload.html', message="Form submitted successfully.")

    except Exception as e:
        # Handle any errors that occur during database operations
        print("An error occurred while submitting the form:", str(e))
        return "An error occurred while submitting the form."

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

# # Route to handle the customer_login page
# @app.route('/customer_login')
# def customer_login_page():
#     return render_template('customer_login.html')


# @app.route('/customer/login', methods=['GET', 'POST'])
# def customer_login():
#     try:
#         if request.method == 'POST':
#             email = request.form.get('email')
#             password = request.form.get('password')
#             print(f"Received email: {email}, password: {password}")
        
#             conn = create_connection()
#             cursor = conn.cursor()
#             cursor.execute('SELECT * FROM tblCustomerRegistration WHERE Email = ? AND Password = ?', (email, password))
#             customer = cursor.fetchone()
#             conn.close()

#             if customer:
#                 # Debug: Print a message when the login is successful
#                 print("Login successful!")
                
#                 # Redirect to services.html with a success flag and email
#                 return redirect(url_for('services', success=True, email=email))
#             else:
#                 error_message = 'Invalid email or password. Please try again.'
#                 return render_template('customer_login.html', error=error_message)

#         return render_template('customer_login.html')

#     except Exception as e:
#         # Handle any exceptions that occur
#         print("An error occurred:", str(e))
#         return "An error occurred while processing your request."


# @app.route('/services')
# def services():
#     try:
#         success_flag = request.args.get('success', False)
#         email = request.args.get('email')

#         if success_flag and email:
#             # email = request.form['email']
#             email = request.form.get('email')

#             # Check if there is an embedded link for this customer in tblReportMaster
#             conn = create_connection()
#             cursor = conn.cursor()
#             cursor.execute('SELECT * FROM tblCustomerRegistration WHERE Email = ?', (email,))
#             customer = cursor.fetchone()

#             if customer:
#                 cursor.execute('SELECT * FROM tblReportMaster WHERE CustomerID = ?', (customer.CustomerID,))
#                 report = cursor.fetchone()
#                 conn.close()

#                 if report and report.EmbeddedLink:
#                     # There is an embedded link, so redirect to user_reports.html
#                     return redirect(url_for('user_reports', success=True, email=email))
#                 else:
#                     # There is no embedded link, show the "please upload data" message
#                     return render_template('contact.html', message='Please upload data to access your reports.')

#         # If there is no success flag or email, redirect to the login page
#         return redirect(url_for('customer_login'))

#     except Exception as e:
#         # Handle any exceptions that occur during the request
#         print("An error occurred:", str(e))
#         return "An error occurred while processing your request."

#     # If everything goes well, this point should not be reached


# @app.route('/user_reports')
# def user_reports():
#     try:
#         success_flag = request.args.get('success', False)

#         if success_flag:
#             email = request.args.get('email')

#             # Check if there is an embedded link for this customer in tblReportMaster
#             conn = create_connection()
#             cursor = conn.cursor()
#             cursor.execute('SELECT * FROM tblCustomerRegistration WHERE Email = ?', (email,))
#             customer = cursor.fetchone()

#             if customer:
#                 cursor.execute('SELECT * FROM tblReportMaster WHERE CustomerID = ?', (customer.CustomerID,))
#                 report = cursor.fetchone()
#                 conn.close()

#                 if report and report.EmbeddedLink:
#                     # Implement the logic to retrieve and display the reports here
#                     return render_template('user_reports.html')

#         # If there is no success flag, email, or embedded link, redirect to the login page
#         return redirect(url_for('customer_login'))

#     except Exception as e:
#         # Handle any exceptions that occur during the request
#         print("An error occurred:", str(e))
#         return "An error occurred while processing your request."

#     # If everything goes well, this point should not be reached



# Route to handle the customer_login

# @app.route('/customer/login', methods=['GET','POST'])
# def customer_login():
#     try:
#         if request.method == 'POST':
#             email = request.form.get('email')
#             password = request.form.get('password')
            
#             conn = create_connection()
#             cursor = conn.cursor()
#             cursor.execute('SELECT * FROM tblCustomerRegistration WHERE Email = ? AND Password = ?', (email, password))
#             customer = cursor.fetchone()
#             conn.close()

#             if customer:
#                 # Instead of accessing elements by string indices, use integer indices
#                 customer_id = customer[0]  # Replace 0 with the correct index of CustomerID
#                 # Check for an embedded link in tblReportMaster
#                 conn = create_connection()
#                 cursor = conn.cursor()
#                 cursor.execute('SELECT * FROM tblReportMaster WHERE CustomerID = ?', (customer_id,))
#                 report = cursor.fetchone()
#                 conn.close()

#                 # if report and report[1]:  # Replace 1 with the correct index of EmbeddedLink
#                 #     # There is an embedded link, so redirect to user_reports.html
#                 #     return render_template('user_reports.html')
#                 if report and report[1]:  # Replace 1 with the correct index of EmbeddedLink
#                     print(f"Redirecting to: {report[1]}")  # Add this line for debugging
#                     return render_template('user_reports.html')

#                 else:
#                     # There is no embedded link, show the "please upload data" message
#                     return render_template('contact.html', message='Please upload data to access your reports.')

#             else:
#                 error_message = 'Invalid email or password. Please try again.'
#                 return render_template('customer_login.html', error=error_message)

#         return render_template('customer_login.html')

#     except Exception as e:
#         # Handle any exceptions that occur
#         print("An error occurred:", str(e))
#         return "An error occurred while processing your request."


@app.route('/customer/<int:customer_id>')
def customer_profile(customer_id):
    # Your code to retrieve customer information goes here
    # You can use the customer_id parameter to look up the customer's data
    return f"Customer Profile Page for ID {customer_id}"




# @app.route('/customer/login', methods=['GET', 'POST'])
# def customer_login():
#     try:
#         if request.method == 'POST':
#             email = request.form.get('email')
#             password = request.form.get('password')
            
#             conn = create_connection()
#             cursor = conn.cursor()
#             cursor.execute('SELECT * FROM tblCustomerRegistration WHERE Email = ? AND Password = ?', (email, password))
#             customer = cursor.fetchone()
#             conn.close()

#             if customer:
#                 # Instead of accessing elements by string indices, use integer indices
#                 customer_id = customer[0]  # Replace 0 with the correct index of CustomerID
#                 # Check for an embedded link in tblReportMaster
#                 conn = create_connection()
#                 cursor = conn.cursor()
#                 cursor.execute('SELECT * FROM tblReportMaster WHERE CustomerID = ?', (customer_id,))
#                 report = cursor.fetchone()
#                 conn.close()

#                 if report and report[1]:  # Replace 1 with the correct index of EmbeddedLink
#                     # Pass 'report' to the template
#                     print(f"Embedded Link: {report[1]}")
#                     return render_template('user_reports.html', report=report)
#                 else:
#                     # There is no embedded link, show the "please upload data" message
#                     return render_template('contact.html', message='Please upload data to access your reports.')

#             else:
#                 error_message = 'Invalid email or password. Please try again.'
#                 return render_template('customer_login.html', error=error_message)

#         return render_template('customer_login.html')

#     except Exception as e:
#         # Handle any exceptions that occur
#         print("An error occurred:", str(e))
#         return "An error occurred while processing your request."




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
                error_message = 'Invalid email or password. Please try again.'
                return render_template('customer_login.html', error=error_message)

        return render_template('customer_login.html')

    except Exception as e:
        # Handle any exceptions that occur
        print("An error occurred:", str(e))
        return "An error occurred while processing your request."

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
