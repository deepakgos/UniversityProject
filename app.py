from flask import Flask, request, render_template, send_from_directory
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

# Route to handle the report page
@app.route('/analysis')
def analysis_page():
    return render_template('analysis.html')

# Route to handle the contact page
@app.route('/contact')
def contact_page():
    return render_template('contact.html')

# Route to handle the admin_login page
@app.route('/admin_login')
def admin_login_page():
    return render_template('admin_login.html')

# Route to handle the static pages
@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'static'), filename)


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



# Route to handle the form submission
# @app.route('/submit', methods=['POST'])
# def submit_form():
#     name = request.form.get('name')
#     email = request.form.get('email')
#     phone = request.form.get('phone')
#     message = request.form.get('message')


#     try:
#         # Create a database connection
#         conn = create_connection()

#         # Get the current timestamp
#         timestamp = datetime.now()

#         # Insert form data into the database
#         cursor = conn.cursor()
#         cursor.execute(
#             "EXEC EnterContactDetails @name=?, @email=?, @phone=?, @message=?, @timestamp=?",
#             name, email, phone, message, timestamp
#         )
#         conn.commit()
#         cursor.close()
#         conn.close()

#         # Clear form fields and render the contact form again
#         return render_template('contact.html', message="Form submitted successfully.")

#     except Exception as e:
#         # Handle any errors that occur during database operations
#         print("An error occurred while submitting the form:", str(e))
#         return "An error occurred while submitting the form."



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
                return render_template('contact.html', message="Form submitted successfully.")

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
        return render_template('contact.html', message="Form submitted successfully.")

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

# Run the Flask app
if __name__ == '__main__':
    app.run()
