from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
from google.oauth2.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Neon DB config
DATABASE_URL = os.getenv("NEON_DB_URL", "postgresql://neondb_owner:npg_vrnafFqP6i9B@ep-tiny-dust-a4m85eqk-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require")

# Google OAuth2 configuration
GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "project_id": "medicycle-461417",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": ["http://127.0.0.1:5000/google-callback"],
        "javascript_origins": ["http://127.0.0.1:5000"]
    }
}

# Create OAuth2 flow
def create_flow():
    return Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
        redirect_uri="http://127.0.0.1:5000/google-callback"
    )

# DB connection function
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# Session protecting decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login_signup'))
        return f(*args, **kwargs)
    return decorated_function

# Role-based access control
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                flash('Please login first.', 'warning')
                return redirect(url_for('login_signup'))
            if session.get('role') != role:
                flash('Access denied: Insufficient privileges.', 'danger')
                if session.get('role') == 'volunteer':
                    return redirect(url_for('index'))
                return redirect(url_for('my_activities'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Function to setup database tables
def setup_database():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Check if users table exists
    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
    table_exists = cur.fetchone()[0]
    
    if not table_exists:
        # Create users table if it doesn't exist
        print("Creating users table...")
        cur.execute('''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            fullname VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL,
            city VARCHAR(50),
            address VARCHAR(200),
            pincode VARCHAR(10),
            is_blocked BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            index_number SERIAL
        )
        ''')
    else:
        # Check if index_number column exists
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'index_number')")
        index_exists = cur.fetchone()[0]
        
        if not index_exists:
            print("Adding index_number column to users table...")
            try:
                cur.execute("ALTER TABLE users ADD COLUMN index_number SERIAL")
            except Exception as e:
                print(f"Error adding index_number column: {str(e)}")
                conn.rollback()
    
    # Check if medicines table exists
    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'medicines')")
    medicines_table_exists = cur.fetchone()[0]
    
    if not medicines_table_exists:
        print("Creating medicines table...")
        cur.execute('''
        CREATE TABLE medicines (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            quantity DECIMAL(10,2) NOT NULL,
            quantity_unit VARCHAR(20) NOT NULL,
            expiry_date DATE NOT NULL,
            description TEXT,
            donation_type VARCHAR(20) NOT NULL,
            price DECIMAL(10,2),
            city VARCHAR(50) NOT NULL,
            area VARCHAR(100) NOT NULL,
            pincode VARCHAR(10) NOT NULL,
            user_id INTEGER REFERENCES users(id),
            image_path VARCHAR(255),
            status VARCHAR(20) DEFAULT 'Available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            index_number SERIAL
        )
        ''')
    else:
        # Check if status column exists
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'medicines' AND column_name = 'status')")
        status_exists = cur.fetchone()[0]
        
        if not status_exists:
            print("Adding status column to medicines table...")
            try:
                cur.execute("ALTER TABLE medicines ADD COLUMN status VARCHAR(20) DEFAULT 'Available'")
            except Exception as e:
                print(f"Error adding status column: {str(e)}")
                conn.rollback()
        
        # Check if index_number column exists
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'medicines' AND column_name = 'index_number')")
        index_exists = cur.fetchone()[0]
        
        if not index_exists:
            print("Adding index_number column to medicines table...")
            try:
                cur.execute("ALTER TABLE medicines ADD COLUMN index_number SERIAL")
            except Exception as e:
                print(f"Error adding index_number column: {str(e)}")
                conn.rollback()
    
    # Check if findmedicine table exists
    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'findmedicine')")
    findmedicine_exists = cur.fetchone()[0]
    
    if not findmedicine_exists:
        print("Creating findmedicine table...")
        cur.execute('''
        CREATE TABLE findmedicine (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) NOT NULL,
            medicine_name VARCHAR(100) NOT NULL,
            quantity INTEGER NOT NULL,
            purpose VARCHAR(50) NOT NULL,
            message TEXT,
            address TEXT NOT NULL,
            contact VARCHAR(15) NOT NULL,
            status VARCHAR(20) DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            index_number SERIAL
        )
        ''')
    else:
        # Check if index_number column exists
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'findmedicine' AND column_name = 'index_number')")
        index_exists = cur.fetchone()[0]
        
        if not index_exists:
            print("Adding index_number column to findmedicine table...")
            try:
                cur.execute("ALTER TABLE findmedicine ADD COLUMN index_number SERIAL")
            except Exception as e:
                print(f"Error adding index_number column: {str(e)}")
                conn.rollback()
    
    # Close connection
    cur.close()
    conn.close()

# Routes
@app.route('/')
def index():
    if 'user' in session:
        # Check user's role and redirect accordingly
        if session.get('role') in ['ngo', 'medical_org']:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('my_activities'))
    return render_template('index.html')

@app.route('/login-signup', methods=['GET', 'POST'])
def login_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        role = request.form.get('role')
        city = request.form.get('city')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        if 'login' in request.form:
            # Login logic
            cur.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cur.fetchone()
            
            if user and check_password_hash(user['password'], password):
                if user['is_blocked']:
                    flash('Your account has been blocked. Please contact support.', 'danger')
                    return redirect(url_for('login_signup'))
                
                session['user'] = {
                    'id': user['id'],
                    'email': user['email'],
                    'fullname': user['fullname'],
                    'role': user['role']
                }
                session['role'] = user['role']
                
                if user['role'] in ['ngo', 'medical_org']:
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('my_activities'))
            else:
                flash('Invalid email or password', 'danger')
        
        elif 'signup' in request.form:
            # Signup logic
            cur.execute('SELECT * FROM users WHERE email = %s', (email,))
            if cur.fetchone():
                flash('Email already exists', 'danger')
            else:
                hashed_password = generate_password_hash(password)
                cur.execute(
                    'INSERT INTO users (fullname, email, password, role, city, address, pincode) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (fullname, email, hashed_password, role, city, address, pincode)
                )
                conn.commit()
                flash('Registration successful! Please login.', 'success')
        
        cur.close()
        conn.close()
    
    return render_template('login_signup.html')

@app.route('/my-activities')
@login_required
def my_activities():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get user's medicines
    cur.execute('''
        SELECT * FROM medicines 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    ''', (session['user']['id'],))
    medicines = cur.fetchall()
    
    # Get user's medicine requests
    cur.execute('''
        SELECT * FROM findmedicine 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    ''', (session['user']['id'],))
    requests = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('my_activities.html', medicines=medicines, requests=requests)

@app.route('/find-medicine', methods=['GET', 'POST'])
@login_required
def find_medicine():
    if request.method == 'POST':
        medicine_name = request.form.get('medicine_name')
        quantity = request.form.get('quantity')
        purpose = request.form.get('purpose')
        message = request.form.get('message')
        address = request.form.get('address')
        contact = request.form.get('contact')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO findmedicine (user_id, medicine_name, quantity, purpose, message, address, contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (session['user']['id'], medicine_name, quantity, purpose, message, address, contact))
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Medicine request posted successfully!', 'success')
        return redirect(url_for('my_activities'))
    
    return render_template('find_medicine.html')

@app.route('/list-medicine', methods=['GET', 'POST'])
@login_required
def list_medicine():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        quantity_unit = request.form.get('quantity_unit')
        expiry_date = request.form.get('expiry_date')
        description = request.form.get('description')
        donation_type = request.form.get('donation_type')
        price = request.form.get('price')
        city = request.form.get('city')
        area = request.form.get('area')
        pincode = request.form.get('pincode')
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Save image to static/uploads directory
                image_path = f"uploads/{image.filename}"
                image.save(os.path.join('static', image_path))
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO medicines (name, quantity, quantity_unit, expiry_date, description, 
                                 donation_type, price, city, area, pincode, user_id, image_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (name, quantity, quantity_unit, expiry_date, description, 
              donation_type, price, city, area, pincode, session['user']['id'], image_path))
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Medicine listed successfully!', 'success')
        return redirect(url_for('my_activities'))
    
    return render_template('list_medicine.html')

@app.route('/delete-medicine/<int:medicine_id>', methods=['POST'])
@login_required
def delete_medicine(medicine_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if medicine belongs to user
    cur.execute('SELECT * FROM medicines WHERE id = %s AND user_id = %s', 
                (medicine_id, session['user']['id']))
    medicine = cur.fetchone()
    
    if medicine:
        # Delete image if exists
        if medicine['image_path']:
            try:
                os.remove(os.path.join('static', medicine['image_path']))
            except:
                pass
        
        # Delete medicine
        cur.execute('DELETE FROM medicines WHERE id = %s', (medicine_id,))
        conn.commit()
        flash('Medicine deleted successfully!', 'success')
    else:
        flash('Medicine not found or unauthorized', 'danger')
    
    cur.close()
    conn.close()
    
    return redirect(url_for('my_activities'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/get-medicine/<int:medicine_id>')
@login_required
def get_medicine(medicine_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT m.*, u.fullname, u.email, u.contact
        FROM medicines m
        JOIN users u ON m.user_id = u.id
        WHERE m.id = %s
    ''', (medicine_id,))
    
    medicine = cur.fetchone()
    cur.close()
    conn.close()
    
    if medicine:
        return jsonify(dict(medicine))
    return jsonify({'error': 'Medicine not found'}), 404

@app.route('/update-medicine/<int:medicine_id>', methods=['POST'])
@login_required
def update_medicine(medicine_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if medicine belongs to user
    cur.execute('SELECT * FROM medicines WHERE id = %s AND user_id = %s', 
                (medicine_id, session['user']['id']))
    medicine = cur.fetchone()
    
    if medicine:
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        quantity_unit = request.form.get('quantity_unit')
        expiry_date = request.form.get('expiry_date')
        description = request.form.get('description')
        donation_type = request.form.get('donation_type')
        price = request.form.get('price')
        city = request.form.get('city')
        area = request.form.get('area')
        pincode = request.form.get('pincode')
        
        # Handle image upload
        image_path = medicine['image_path']
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Delete old image if exists
                if image_path:
                    try:
                        os.remove(os.path.join('static', image_path))
                    except:
                        pass
                
                # Save new image
                image_path = f"uploads/{image.filename}"
                image.save(os.path.join('static', image_path))
        
        cur.execute('''
            UPDATE medicines 
            SET name = %s, quantity = %s, quantity_unit = %s, expiry_date = %s,
                description = %s, donation_type = %s, price = %s, city = %s,
                area = %s, pincode = %s, image_path = %s
            WHERE id = %s
        ''', (name, quantity, quantity_unit, expiry_date, description,
              donation_type, price, city, area, pincode, image_path, medicine_id))
        
        conn.commit()
        flash('Medicine updated successfully!', 'success')
    else:
        flash('Medicine not found or unauthorized', 'danger')
    
    cur.close()
    conn.close()
    
    return redirect(url_for('my_activities'))

@app.route('/submit-medicine-request', methods=['POST'])
@login_required
def submit_medicine_request():
    medicine_id = request.form.get('medicine_id')
    message = request.form.get('message')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get medicine details
    cur.execute('SELECT * FROM medicines WHERE id = %s', (medicine_id,))
    medicine = cur.fetchone()
    
    if medicine:
        # Create request
        cur.execute('''
            INSERT INTO findmedicine (user_id, medicine_name, quantity, purpose, message, address, contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (session['user']['id'], medicine['name'], medicine['quantity'],
              'Request for listed medicine', message, session['user'].get('address', ''),
              session['user'].get('contact', '')))
        
        conn.commit()
        flash('Request submitted successfully!', 'success')
    else:
        flash('Medicine not found', 'danger')
    
    cur.close()
    conn.close()
    
    return redirect(url_for('my_activities'))

@app.route('/delete-medicine-request/<int:request_id>', methods=['POST'])
@login_required
def delete_medicine_request(request_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if request belongs to user
    cur.execute('SELECT * FROM findmedicine WHERE id = %s AND user_id = %s',
                (request_id, session['user']['id']))
    request = cur.fetchone()
    
    if request:
        cur.execute('DELETE FROM findmedicine WHERE id = %s', (request_id,))
        conn.commit()
        flash('Request deleted successfully!', 'success')
    else:
        flash('Request not found or unauthorized', 'danger')
    
    cur.close()
    conn.close()
    
    return redirect(url_for('my_activities'))

@app.route('/dashboard')
@login_required
@role_required('ngo')
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all medicines
    cur.execute('''
        SELECT m.*, u.fullname, u.email
        FROM medicines m
        JOIN users u ON m.user_id = u.id
        ORDER BY m.created_at DESC
    ''')
    medicines = cur.fetchall()
    
    # Get all requests
    cur.execute('''
        SELECT f.*, u.fullname, u.email
        FROM findmedicine f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
    ''')
    requests = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('dashboard.html', medicines=medicines, requests=requests)

@app.route('/google-login')
def google_login():
    flow = create_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/google-callback')
def google_callback():
    flow = create_flow()
    flow.fetch_token(
        authorization_response=request.url,
        state=session['state']
    )
    
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    # Get user info
    userinfo_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {credentials.token}'}
    ).json()
    
    # Check if user exists
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM users WHERE email = %s', (userinfo_response['email'],))
    user = cur.fetchone()
    
    if not user:
        # Create new user
        cur.execute('''
            INSERT INTO users (fullname, email, password, role)
            VALUES (%s, %s, %s, %s)
        ''', (userinfo_response['name'], userinfo_response['email'],
              generate_password_hash('google-oauth'), 'volunteer'))
        conn.commit()
        
        cur.execute('SELECT * FROM users WHERE email = %s', (userinfo_response['email'],))
        user = cur.fetchone()
    
    session['user'] = {
        'id': user['id'],
        'email': user['email'],
        'fullname': user['fullname'],
        'role': user['role']
    }
    session['role'] = user['role']
    
    cur.close()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/block-user/<int:user_id>', methods=['POST'])
@login_required
@role_required('ngo')
def block_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('UPDATE users SET is_blocked = TRUE WHERE id = %s', (user_id,))
    conn.commit()
    
    cur.close()
    conn.close()
    
    flash('User blocked successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/get-all-users', methods=['GET'])
@login_required
@role_required('ngo')
def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify([dict(user) for user in users])

@app.route('/unblock-user/<int:user_id>', methods=['POST'])
@login_required
@role_required('ngo')
def unblock_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('UPDATE users SET is_blocked = FALSE WHERE id = %s', (user_id,))
    conn.commit()
    
    cur.close()
    conn.close()
    
    flash('User unblocked successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/get-all-medicines')
@login_required
def get_all_medicines():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT m.*, u.fullname, u.email
        FROM medicines m
        JOIN users u ON m.user_id = u.id
        ORDER BY m.created_at DESC
    ''')
    medicines = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify([dict(medicine) for medicine in medicines])

@app.route('/get-all-requests')
@login_required
@role_required('ngo')
def get_all_requests():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT f.*, u.fullname, u.email
        FROM findmedicine f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
    ''')
    requests = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify([dict(request) for request in requests])

@app.route('/accept-request/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('UPDATE findmedicine SET status = %s WHERE id = %s',
                ('Accepted', request_id))
    conn.commit()
    
    cur.close()
    conn.close()
    
    flash('Request accepted successfully', 'success')
    return redirect(url_for('my_activities'))

@app.route('/accept-medicine/<int:medicine_id>', methods=['POST'])
@login_required
def accept_medicine(medicine_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('UPDATE medicines SET status = %s WHERE id = %s',
                ('Accepted', medicine_id))
    conn.commit()
    
    cur.close()
    conn.close()
    
    flash('Medicine accepted successfully', 'success')
    return redirect(url_for('my_activities'))

@app.route('/reject-medicine/<int:medicine_id>', methods=['POST'])
@login_required
def reject_medicine(medicine_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('UPDATE medicines SET status = %s WHERE id = %s',
                ('Rejected', medicine_id))
    conn.commit()
    
    cur.close()
    conn.close()
    
    flash('Medicine rejected successfully', 'success')
    return redirect(url_for('my_activities'))

@app.route('/reject-request/<int:request_id>', methods=['POST'])
@login_required
def reject_request(request_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('UPDATE findmedicine SET status = %s WHERE id = %s',
                ('Rejected', request_id))
    conn.commit()
    
    cur.close()
    conn.close()
    
    flash('Request rejected successfully', 'success')
    return redirect(url_for('my_activities'))

@app.route('/test-login/<role>')
def test_login(role):
    if role not in ['volunteer', 'ngo', 'medical_org']:
        return 'Invalid role'
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create test user if not exists
    cur.execute('SELECT * FROM users WHERE email = %s', ('test@example.com',))
    user = cur.fetchone()
    
    if not user:
        cur.execute('''
            INSERT INTO users (fullname, email, password, role)
            VALUES (%s, %s, %s, %s)
        ''', ('Test User', 'test@example.com', generate_password_hash('test123'), role))
        conn.commit()
        
        cur.execute('SELECT * FROM users WHERE email = %s', ('test@example.com',))
        user = cur.fetchone()
    
    session['user'] = {
        'id': user['id'],
        'email': user['email'],
        'fullname': user['fullname'],
        'role': user['role']
    }
    session['role'] = user['role']
    
    cur.close()
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    setup_database()
    app.run(debug=True) 