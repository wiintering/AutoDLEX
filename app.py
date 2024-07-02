from flask import Flask, request, render_template, session, redirect, url_for
from blueprints.enforcer.enforcer import enforcer_bp
from blueprints.violators.violators import violator_bp
from blueprints.extracted_data.svm import svm_bp
from blueprints.image_processing.text_extraction import text_extraction_bp
from db_utils import get_db_connection





app = Flask(__name__)


app.register_blueprint(enforcer_bp) #blueprint for the enforcer pages
app.register_blueprint(violator_bp) #blueprint for violators page
app.register_blueprint(svm_bp) #blueprint for the svm alghorithm
app.register_blueprint(text_extraction_bp) #blueprint for text extraction
# Set a secret key for the Flask application
app.secret_key = b'CTMEU/'

#  connection to the MySQL database
db_connection = get_db_connection()
cursor = db_connection.cursor()

# Create a cursor object to execute SQL queries


# Path to Tesseract executable




@app.route('/logout')
def logout():
    session.pop('loggedins',None)
    session.pop('username',None)
    return redirect(url_for('enforcer.enforcer'))


@app.route('/logout_admin')
def logout_admin():
    session.pop('loggedin',None)
    session.pop('username',None)
    return redirect(url_for('admin_signin'))


@app.route('/')
def interface():
    if 'loggedins' in session:
        return redirect(url_for('camera'))
    elif 'loggedin' in session:
        return redirect(url_for('index'))
    
    # Call loggedin() or loggedins() function here if needed
    # Example: loggedins('index')
    # Example: loggedin('camera')

    return render_template('front-interface.html')



@app.route('/camera')
def camera():
    username = request.args.get('username')
    return render_template('camera.html')


@app.route('/violators_form', methods=['GET', 'POST'])
def violators_form():
    msg = ''  # Initialize msg here
    if request.method == 'POST':
        tct_number = request.form['tct_number']
        time = request.form['time']
        date = request.form['date']
        violation_list = request.form.getlist('violation[]')
        violation = ', '.join(violation_list)
        barangay = request.form['barangay']
        plateNumber = request.form['plateNumber']
        vehicle = request.form['vehicle']
        status = request.form['status']
        
        # Check if there is an unsettled violation for the given plate number
        cursor.execute("SELECT * FROM violators_data WHERE plateNumber = %s AND status = 'Uknsettled'", (plateNumber,))
        existing_violation = cursor.fetchone()
        
        if existing_violation:
             cursor.execute("INSERT INTO violators_data (tct_number, time, date, violation, barangay, plateNumber, vehicle, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (tct_number, time, date, violation, barangay, plateNumber, vehicle, status))
             db_connection.commit()
        
        # Update reports table
             cursor.execute("UPDATE reports SET violations=%s, place_of_apprehension=%s, plate_number=%s, vehicle=%s WHERE tct_number = %s",
                       (violation, barangay, plateNumber, vehicle, tct_number))
             db_connection.commit()
             
             session['msg'] = 'There is an unsettled violation for this data.'
             return redirect(url_for('violators_form'))
        
        # Insert new violator data
        cursor.execute("INSERT INTO violators_data (tct_number, time, date, violation, barangay, plateNumber, vehicle, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (tct_number, time, date, violation, barangay, plateNumber, vehicle, status))
        db_connection.commit()
        
        # Update reports table
        cursor.execute("UPDATE reports SET violations=%s, place_of_apprehension=%s, plate_number=%s, vehicle=%s WHERE tct_number = %s",
                       (violation, barangay, plateNumber, vehicle, tct_number))
        db_connection.commit()
        
        session['msg'] = 'Report Submitted Successfully!'
        return redirect(url_for('violators_form'))
    
    if 'msg' in session:
        msg = session.pop('msg')
    
    return render_template('mode-selection.html', msg=msg)

@app.route('/manual_input_data', methods=['GET', 'POST'])
def manual_input_data():
    session['submitted'] = True
    msg = ''
    tct_number = ''  # Initialize tct_number

    if request.method == 'POST':
        tct_number = request.form['tct_number']
        name = request.form['name']
        license_number = request.form['license_number']
        expiration_date = request.form['expiration_date']
        date_of_birth = request.form['date_of_birth']
        sex = request.form['sex']
        
        cursor.execute(
            "INSERT INTO extracted_data (tct_number, name, license_number, expiration_date, date_of_birth, sex) VALUES (%s, %s, %s, %s, %s, %s)",
            (tct_number, name, license_number, expiration_date, date_of_birth, sex)
        )            
        
        db_connection.commit()
        cursor.execute("INSERT INTO reports (tct_number, name,license_number) VALUES (%s, %s,%s)", (tct_number,name,license_number))
      
        
        return redirect(url_for('manual_input_data',tct_number = tct_number))
    tct_number = request.args.get('tct_number') 
    return render_template('violators-form.html', tct_number=tct_number)

@app.route('/index')
def index():
    try:
        # Fetch counts
        cursor.execute("SELECT COUNT(*) FROM enforcer_accounts")
        enforcers_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM violators_data")
        violators_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM violators_data WHERE status = 'unsettled'")
        unsettled_reports_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM violators_data WHERE status = 'settled'")
        settled_reports_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT * FROM violators_data")
        violators = cursor.fetchall()
        
        # Pass counts and data to template
        return render_template('index.html', enforcers_count=enforcers_count, violators_count=violators_count,
                               unsettled_reports_count=unsettled_reports_count, settled_reports_count=settled_reports_count,
                               violators=violators)
    except Exception as e:
        # Handle any exceptions gracefully
        return render_template('error.html', error=str(e))


@app.route('/mode_selection')
def mode_selection():
    return render_template('mode-selection.html')


@app.route('/settled_reports')
def settled_reports():
    cursor.execute("SELECT * FROM violators_data WHERE status = 'settled'")
    data =  cursor.fetchall()
    return render_template('settled-reports.html',reports = data)



#routes for admin
@app.route('/admin_signin', methods=['GET','POST'])
def admin_signin():
    if 'loggedin' in session:
        return redirect(url_for('index'))
    msg = ''
    if request.method == 'POST':  
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM admin_accounts WHERE email = %s AND password = %s", (email, password))  # Corrected the SQL query
        record = cursor.fetchone()
        if record:
            session['loggedin'] = True
            session['email'] = record[1]
            return redirect(url_for('index'))  
        else:
            msg = "Incorrect email address or password!"
    return render_template('admin-login.html', msg=msg)



@app.route('/add_enforcer', methods=['POST', 'GET'])
def add_enforcer():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        
        if password != confirm_password:
            # Passwords don't match, return a message
            return render_template('new-enforcer.html', msg="Passwords do not match!")
        else:
            # Insert data into the database
            sql = "INSERT INTO enforcer_accounts (username, password) VALUES (%s, %s)"
            val = (username, password)
            cursor.execute(sql, val)
            db_connection.commit()  # Commit changes to the database

            # Redirect to a success page or another route
            return redirect(url_for('enforcer_data'))
    
    # If it's a GET request or if password matches, render the template without a message
    return render_template('new-enforcer.html')


@app.route('/selection_mode')
def selection_mode():
    session['loggedins'] = True
    return render_template('mode-selection.html')



@app.route('/manual_input')
def manual_input():
    session['manual_input'] = True
    cursor = db_connection.cursor()
    cursor.execute("SELECT MAX(id) FROM reports")
    largest_id = cursor.fetchone()[0]  # Get the latest extracted_id

    if largest_id is None:
                new_id = 1
    else:
        cursor.execute("SELECT tct_number FROM reports WHERE id = %s", (largest_id,))
        existing_tct_number = cursor.fetchone()[0]
        new_id = int(existing_tct_number.split('-')[1]) + 1

    generated_id = 'TCT-' + str(new_id).zfill(5)
    
    tct_number = generated_id   
    
    return render_template('manual-input.html', tct_number=tct_number)




@app.route('/no_license')
def no_license():
    session['manual_input'] = True

    cursor.execute("SELECT MAX(id) FROM reports")
    largest_id = cursor.fetchone()[0]  # Get the latest extracted_id

    if largest_id is None:
                new_id = 1
    else:
        cursor.execute("SELECT tct_number FROM reports WHERE id = %s", (largest_id,))
        existing_tct_number = cursor.fetchone()[0]
        new_id = int(existing_tct_number.split('-')[1]) + 1

    generated_id = 'TCT-' + str(new_id).zfill(5)
    
    tct_number = generated_id   
    return render_template('no_license.html' ,tct_number=tct_number)


@app.route('/no_license_data', methods=['GET', 'POST'])
def no_license_data():
    session['submitted'] = True
    msg = ''
    tct_number = ''  # Initialize tct_number

    if request.method == 'POST':
        tct_number = request.form['tct_number']
        name = request.form['name']
        date_of_birth = request.form['date_of_birth']
        address = request.form['address']
        sex = request.form['sex']
      
        cursor.execute("INSERT INTO no_license (tct_number, name, date_of_birth, address, sex) VALUES (%s, %s, %s, %s, %s)",
               (tct_number, name, date_of_birth, address, sex))
        
        db_connection.commit()
        cursor.execute("INSERT INTO reports (tct_number, name) VALUES (%s, %s)", (tct_number,name))
      
        
        return redirect(url_for('no_license_data',tct_number = tct_number))
    tct_number = request.args.get('tct_number') 
    return render_template('violators-form.html', tct_number=tct_number)

if __name__ == '__main__':
    app.run(debug=True)