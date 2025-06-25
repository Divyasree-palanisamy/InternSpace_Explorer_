from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask import Flask, request, jsonify
import mysql.connector
import re
from mysql.connector import connect, Error
from datetime import timedelta
from datetime import datetime  


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

def get_db_connection():
    return connect(
        host="localhost",
        user="root",
        password="Divya@2004",
        database="uop"
    )
conn = get_db_connection()
mycursor = conn.cursor(dictionary=True)
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/submit_details', methods=['POST'])
def submit_details():
    # Extract form data
    name = request.form.get('name')
    dob = request.form.get('dob')
    email = request.form.get('email')
    phone = request.form.get('phone')
    role = request.form.get('role')

    # Connect to the database
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Divya@2004',
        database='uop' 
    )
    cursor = connection.cursor()

    # SQL query to insert data
    query = "INSERT INTO student_details (name, dob, email, phone, role) VALUES (%s, %s, %s, %s, %s)"
    values = (name, dob, email, phone, role)

    try:
        # Execute the query
        cursor.execute(query, values)
        connection.commit()  # Commit the transaction to the database
        flash("Details submitted successfully!", "success")
    except Exception as e:
        connection.rollback()  # Rollback in case of error
        flash(f"Error: {str(e)}", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect('/dashboard')  

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    try:
        db = get_db_connection()
        if db is None:
            raise Exception("Database connection failed")

        cursor = db.cursor(dictionary=True)
        
        # Ensure user exists in user_details
        cursor.execute("SELECT * FROM user_details WHERE user_id = %s", (user_id,))
        info_exists = cursor.fetchone() is not None

        cursor.close()
        db.close()

        return render_template(
            'dashboard.html',
            info_exists=info_exists,
            username=session.get('username')
        )
    except Exception as e:
        import traceback
        print("Error in dashboard:", traceback.format_exc())  # Debugging
        return render_template("error.html", error_message="Error loading the dashboard.")  # New error page


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            if user and isinstance(user, dict):
                session['username'] = user['username']
                session['user_id'] = user['id']
                flash("✅ Login successful!", "success")
                return redirect('/dashboard')
            else:
                flash("❌ Invalid credentials", "error")

        except Error as e:
            print(f"Login error: {e}")
        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')


def is_strong_password(password):
    # At least 8 characters, one uppercase, one lowercase, one number, one special char
    return re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password'].strip()
        confirm_password = request.form['confirm_password'].strip()

        if not all([username, email, phone_number, password, confirm_password]):
            flash("All fields are required.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        elif not is_strong_password(password):
            flash("Password must be at least 8 characters long, include an uppercase letter, a lowercase letter, a number, and a special character.", "error")
        else:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                try:
                    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                    if cursor.fetchone():
                        flash(" ❌ Username already taken.", "error")
                    else:
                        cursor.execute("INSERT INTO users (username, email, phone_number, password) VALUES (%s, %s, %s, %s)", 
                                       (username, email, phone_number, password))
                        connection.commit()
                        flash("✅ Account created successfully!", "success")

                        return redirect('/login')
                except Error as err:
                    flash(f"Database error: {err}", "error")
                finally:
                    cursor.close()
                    connection.close()

    return render_template('signup.html')


@app.route('/add_internship', methods=['GET', 'POST'])
def add_internship():
    if request.method == 'POST':
        internship_title = request.form['title']
        department = request.form['department']
        company_name = request.form['company']
        location = request.form['location']
        duration = request.form['duration']
        fee = request.form['fees']
        contact_number = request.form['contact_number']
        contact_email = request.form['contact_email']
        headquarters = request.form['headquarters']
        application_link = request.form['application_link']
        paid = 1 if 'paid' in request.form else 0
        iso_certified = 1 if 'iso_certified' in request.form else 0
        ratings = request.form['ratings']
        print("Form Submitted Successfully!")

        print("Form Data:", internship_title, department, company_name, location, duration, fee,
              contact_number, contact_email, headquarters, application_link, paid, iso_certified, ratings)

        try:
            conn = get_db_connection()  
            cursor = conn.cursor()

            query = """INSERT INTO internships 
                       (internship_title, department, company_name, location, duration, fee,
                        contact_number, contact_email, headquarters, application_link, paid, 
                        iso_certified, ratings)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (internship_title, department, company_name, location, duration, fee,
                      contact_number, contact_email, headquarters, application_link, paid,
                      iso_certified, ratings)
            cursor.execute(query, values)
            conn.commit()

            print("Internship Added Successfully!")

        except Exception as e:
            error_message = f"Error adding internship: {e}"
            print(error_message)
            conn.rollback()

        finally:
            cursor.close()
            conn.close()

        return redirect('/view_internship')

    return render_template('add_internship.html')

@app.route('/tutorial', methods=['GET', 'POST'])
def tutorial():
    return render_template('tutorial.html')

@app.route('/view_internship')
def view_internship():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Fetch data as dictionaries

        query = """SELECT internship_title, department, company_name, headquarters, 
                          location, duration, fee, contact_number, contact_email, 
                          iso_certified, application_link, paid, ratings 
                   FROM internships"""
        cursor.execute(query)
        internships = cursor.fetchall()
        print("Internships Fetched:", internships)


    except Exception as e:
        print("Error fetching internships:", e)
        internships = []

    finally:
        cursor.close()
        conn.close()

    return render_template('view_internship.html', internships=internships)

@app.route('/update_preferences', methods=['POST'])
def update_preferences():
    notifications = request.form.get('notifications')
    theme = request.form.get('theme')
    return render_template('update_preferences.html', notifications=notifications, theme=theme)

@app.route('/manage_linked_accounts', methods=['POST'])
def manage_linked_accounts():
    linkedin = request.form.get('linkedin')
    github = request.form.get('github')
    return render_template('manage_linked_accounts.html', linkedin=linkedin, github=github)


@app.route('/update_avatar', methods=['POST'])
def update_avatar():
    data = request.get_json()
    session['avatar_url'] = data['avatar_url']
    return jsonify({'status': 'avatar updated'})

@app.route('/upload_custom_avatar', methods=['POST'])
def upload_custom_avatar():
    data = request.get_json()
    image_base64 = data.get('image_base64')
    session['avatar_url'] = image_base64  # Store base64 directly in session
    return jsonify({'status': 'custom avatar uploaded'})


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')

@app.route('/help', methods=['GET', 'POST'])
def help():
    return render_template('help.html')

@app.route('/recommended_internships', methods=['GET'])
def recommended_internships():
    # Logic for recommended internships page
    return render_template('recommended_internships.html')

@app.route('/profile', methods=['GET'])
def profile():
    if 'username' not in session:
        flash('You are not logged in. Please log in first.', 'error')
        return redirect('/login')

    username = session['username']

    try:
        # ✅ Step 1: Check database connection
        connection = get_db_connection()
        if not connection:
            flash('Database connection failed.', 'error')
            return redirect('/dashboard')

        cursor = connection.cursor(dictionary=True)

        # ✅ Step 2: Print username before query
        print(f"Fetching profile details for: {username}")

        sql_user = "SELECT email, phone_number, created_at FROM users WHERE username = %s"
        cursor.execute(sql_user, (username,))
        user = cursor.fetchone()

        # ✅ Step 3: Check if user exists
        if not user:
            flash(f'User {username} not found in database.', 'error')
            return redirect('/dashboard')

        # ✅ Step 4: Store data in session
        if isinstance(user, dict):
            session['email'] = user.get('email', 'N/A')
            session['phone_number'] = user.get('phone_number', 'N/A')
            created_at = user.get('created_at')
            session['joined_date'] = created_at.strftime('%d-%m-%Y') if created_at else 'N/A'

    except Error as e:
        print(f"❌ Error fetching user details: {e}")
        flash(f'There was an issue fetching your profile details: {e}', 'error')
        return redirect('/dashboard')

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    return render_template('profile.html', username=username)

@app.route('/filter_internships', methods=['POST'])
def filter_internships():
    filterKeyword = request.form.get('filterKeyword')
    filterDepartment = request.form.get('filterDepartment')
    filterDomain = request.form.get('filterDomain')
    filterCountry = request.form.get('filterCountry')
    filterCity = request.form.get('filterCity')
    filterDuration = request.form.get('filterDuration')
    filterType = request.form.get('filterType')
    filterPrice = request.form.get('filterPrice')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM internships WHERE "
    filters = []
    params = []

    # Adjusted column names based on the database schema
    if filterKeyword:
        filters.append("internship_title LIKE %s")
        params.append(f"%{filterKeyword}%")
    if filterDepartment:
        filters.append("department LIKE %s")
        params.append(f"%{filterDepartment}%")
    if filterDomain:
        filters.append("department LIKE %s")  # If the domain is part of the department
        params.append(f"%{filterDomain}%")
    if filterCountry or filterCity:
        filters.append("location LIKE %s")
        if filterCountry and filterCity:
            params.append(f"%{filterCountry} {filterCity}%")  # Country and city in location
        else:
            params.append(f"%{filterCountry or filterCity}%")
    if filterDuration:
        filters.append("duration LIKE %s")
        params.append(f"%{filterDuration}%")
    if filterType:
        filters.append("paid = %s")
        params.append(1 if filterType.lower() == "paid" else 0)
    if filterPrice:
        try:
            min_price, max_price = map(float, filterPrice.split("-"))
            filters.append("fee BETWEEN %s AND %s")
            params.extend([min_price, max_price])
        except ValueError:
            pass  # Handle invalid price range input

    if filters:
        query += " OR ".join(filters)  # Use 'OR' for partial matching
    else:
        query = "SELECT * FROM internships"  # If no filters are applied, fetch all

    cursor.execute(query, tuple(params))
    internships = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('recommended_internships.html', internships=internships)


@app.route('/logout')
def logout():
    session.clear()  # Clear the entire session
    flash('You have been logged out successfully.')
    return redirect('/login')

@app.route('/logout_confirmation')
def logout_confirmation():
    return render_template('logout_confirmation.html')

@app.route('/delete_internship', methods=['GET'])
def delete_internship():
    title = request.args.get('title')
    company = request.args.get('company')

    if not title or not company:
        return "Error: Missing internship title or company name."

    conn = get_db_connection()
    cursor = conn.cursor()

    # Adjust the query based on your table structure
    cursor.execute("DELETE FROM internships WHERE internship_title = %s AND company_name = %s", (title, company))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/view_internship')


if __name__ == '__main__':
    app.run(debug=True) 