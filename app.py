from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import requests

# Allow OAuth2 over HTTP for development
# (Google OAuth related code removed)

app = Flask(__name__)
app.secret_key = 'my_super_secret_key_123'

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Neon DB config
DATABASE_URL = os.getenv("NEON_DB_URL", "postgresql://neondb_owner:npg_vrnafFqP6i9B@ep-tiny-dust-a4m85eqk-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require")

# (Google OAuth config and functions removed)

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        if session.get('role') in ['ngo', 'medical_org']:
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html')
    return redirect(url_for('login_signup'))

@app.route('/login-signup', methods=['GET', 'POST'])
def login_signup():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db_connection()
        cur = conn.cursor()

        if form_type == 'login':
            # Login logic
            cur.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cur.fetchone()
            if user and check_password_hash(user['password'], password):
                if user['is_blocked']:
                    flash('Your account has been blocked. Please contact support.', 'danger')
                    return redirect(url_for('login_signup'))
                
                # Store user data in session
                session['user'] = {
                    'id': user['id'],
                    'email': user['email'],
                    'fullname': user['fullname']
                }
                session['role'] = user['role']
                
                print("DEBUG: User logged in:", session['user'])
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'user': session['user'],
                        'role': user['role']
                    })
                
                if user['role'] in ['ngo', 'medical_org']:
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('index'))
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'Invalid email or password'
                    })
                flash('Invalid email or password', 'danger')

        elif form_type == 'signup':
            fullname = request.form.get('fullname')
            role = request.form.get('role')
            org_code = request.form.get('org_code')
            cur.execute('SELECT * FROM users WHERE email = %s', (email,))
            if cur.fetchone():
                flash('Email already exists', 'danger')
            else:
                if role == 'ngo' and not org_code:
                    flash('Organization code is required for NGO registration', 'danger')
                    return redirect(url_for('login_signup'))
                hashed_password = generate_password_hash(password)
                cur.execute(
                    'INSERT INTO users (fullname, email, password, role) VALUES (%s, %s, %s, %s) RETURNING id',
                    (fullname, email, hashed_password, role)
                )
                user_id = cur.fetchone()['id']
                conn.commit()
                
                # Store user data in session after signup
                session['user'] = {
                    'id': user_id,
                    'email': email,
                    'fullname': fullname
                }
                session['role'] = role
                
                print("DEBUG: User signed up:", session['user'])
                
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('index'))

        cur.close()
        conn.close()
    return render_template('Login_SignUp.html')

@app.route('/my-activities')
@login_required
def my_activities():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get user ID from session
        if 'user' not in session or 'id' not in session['user']:
            flash('Please login again', 'warning')
            return redirect(url_for('login_signup'))
            
        user_id = session['user']['id']
        
        # Get user's medicines
        cur.execute('''
            SELECT * FROM medicines 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        ''', (user_id,))
        listed_medicines = cur.fetchall()
        
        # Get user's medicine requests
        cur.execute('''
            SELECT * FROM findmedicine 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        ''', (user_id,))
        medicine_requests = cur.fetchall()
        
        # Calculate stats
        stats = {
            'total_listed': len(listed_medicines),
            'total_requests': len(medicine_requests),
            'active_listings': len([m for m in listed_medicines if m['status'] == 'Available']),
            'pending_requests': len([r for r in medicine_requests if r['status'] == 'Pending']),
            'total_donated': len([m for m in listed_medicines if m['status'].lower() == 'donated']),
            'total_sold': len([r for r in medicine_requests if r['status'].lower() in ['fulfilled', 'completed', 'accepted']])
        }
        
        cur.close()
        conn.close()
        
        return render_template('MyActivities.html', 
                             listed_medicines=listed_medicines, 
                             medicine_requests=medicine_requests, 
                             stats=stats)
    except Exception as e:
        print("DEBUG: Error in my_activities:", str(e))
        flash('Error loading activities. Please try again.', 'danger')
        return redirect(url_for('index'))

@app.route('/find-medicine', methods=['GET', 'POST'])
@login_required
def find_medicine():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Handle POST request (form submission)
        if request.method == 'POST':
            try:
                # Check if user is logged in and has ID
                if 'user' not in session or 'id' not in session['user']:
                    print("DEBUG: User not logged in or missing ID in session")
                    return jsonify({'success': False, 'message': 'Please login first'})
                
                # Get form data
                medicine_name = request.form.get('medicine_name')
                quantity = request.form.get('quantity')
                purpose = request.form.get('reason')
                message = request.form.get('message')
                address = request.form.get('address')
                contact = request.form.get('contact')
                
                print("DEBUG: Form data received:", {
                    'medicine_name': medicine_name,
                    'quantity': quantity,
                    'purpose': purpose,
                    'message': message,
                    'address': address,
                    'contact': contact,
                    'user_id': session['user']['id']
                })
                
                # Basic validation
                if not all([medicine_name, quantity, purpose, address, contact]):
                    return jsonify({'success': False, 'message': 'Please fill all required fields'})
                
                # Insert into database
                cur.execute('''
                    INSERT INTO findmedicine (user_id, medicine_name, quantity, purpose, message, address, contact, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
                    RETURNING id
                ''', (session['user']['id'], medicine_name, quantity, purpose, message, address, contact))
                
                inserted_id = cur.fetchone()['id']
                conn.commit()
                print("DEBUG: Request inserted successfully with ID:", inserted_id)
                
                return jsonify({
                    'success': True, 
                    'message': 'Medicine request posted successfully!'
                })
                
            except Exception as e:
                print("DEBUG: Error in POST:", str(e))
                conn.rollback()
                return jsonify({'success': False, 'message': 'Error submitting request. Please try again.'})
        
        # Handle GET request (display medicines)
        search_query = request.args.get('search', '')
        location = request.args.get('location', '')
        
        # Base query
        query = '''
            SELECT 
                m.medicine_name,
                m.category,
                m.location,
                m.expiry_date,
                m.available_qty,
                m.type_price
            FROM availablemedicine m
        '''
        params = []
        
        # Add filters
        if search_query:
            query += " WHERE (m.medicine_name ILIKE %s OR m.category ILIKE %s)"
            params.extend([f'%{search_query}%', f'%{search_query}%'])
        
        if location:
            if search_query:
                query += " AND m.location = %s"
            else:
                query += " WHERE m.location = %s"
            params.append(location)
        
        # Execute query
        cur.execute(query, params)
        medicines = cur.fetchall()
        
        # Return response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'medicines': [dict(m) for m in medicines]
            })
        
        return render_template('FindMedicine.html', medicines=medicines)
        
    except Exception as e:
        print("DEBUG: Main Error:", str(e))
        return jsonify({'success': False, 'message': str(e)})
        
    finally:
        cur.close()
        conn.close()

@app.route('/list-medicine', methods=['GET', 'POST'])
@login_required
def list_medicine():
    if request.method == 'POST':
        try:
            name = request.form.get('medicine-name')
            quantity = request.form.get('quantity')
            quantity_unit = request.form.get('quantity-unit')
            expiry_date = request.form.get('expiry-date')
            description = request.form.get('description')
            donation_type = request.form.get('donation-type')
            price = request.form.get('price')
            if price == '' or price is None:
                price = None
            else:
                try:
                    price = float(price)
                except ValueError:
                    error_msg = 'Invalid price value.'
                    print(f"[ERROR] {error_msg}")
                    return jsonify({'success': False, 'message': error_msg})
            city = request.form.get('city')
            area = request.form.get('area')
            pincode = request.form.get('pincode')
            
            print("name:", name)
            print("quantity:", quantity)
            print("quantity_unit:", quantity_unit)
            print("expiry_date:", expiry_date)
            print("description:", description)
            print("donation_type:", donation_type)
            print("price:", price)
            print("city:", city)
            print("area:", area)
            print("pincode:", pincode)
            
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
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Medicine listed successfully!'})
            else:
                flash('Medicine listed successfully!', 'success')
                return redirect(url_for('my_activities'))
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': str(e)}), 500
            else:
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('list_medicine'))
    return render_template('ListMedicine.html')
  

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
        msg = 'Medicine deleted successfully!'
        success = True
    else:
        msg = 'Medicine not found or unauthorized'
        success = False
    
    cur.close()
    conn.close()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success, 'message': msg})
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
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
        SELECT m.*, u.fullname, u.email
        FROM medicines m
        JOIN users u ON m.user_id = u.id
        WHERE m.id = %s
    ''', (medicine_id,))
    medicine = cur.fetchone()
    cur.close()
    conn.close()
    if medicine:
        return jsonify({'success': True, 'medicine': dict(medicine)})
    return jsonify({'success': False, 'message': 'Medicine not found'})

@app.route('/update-medicine/<int:medicine_id>', methods=['POST'])
@login_required
def update_medicine(medicine_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM medicines WHERE id = %s AND user_id = %s', (medicine_id, session['user']['id']))
        medicine = cur.fetchone()
        if not medicine:
            msg = 'Medicine not found or unauthorized'
            success = False
        else:
            name = request.form.get('name')
            quantity = request.form.get('quantity')
            quantity_unit = request.form.get('quantity_unit')
            expiry_date = request.form.get('expiry_date')
            donation_type = request.form.get('donation_type')
            price = request.form.get('price')
            if price == '' or price is None:
                price = None
            else:
                try:
                    price = float(price)
                except ValueError:
                    error_msg = 'Invalid price value.'
                    print(f"[ERROR] {error_msg}")
                    return jsonify({'success': False, 'message': error_msg})
            city = request.form.get('city')
            area = request.form.get('area')
            pincode = request.form.get('pincode')
            if not pincode or not pincode.isdigit() or len(pincode) != 6:
                error_msg = 'Please enter a valid 6-digit pincode.'
                print(f"[ERROR] {error_msg}")  # Terminal मध्ये दिसेल
                return jsonify({'success': False, 'message': error_msg})
            description = request.form.get('description')
            image_path = medicine['image_path']
            if 'image' in request.files:
                image = request.files['image']
                if image.filename != '':
                    if image_path:
                        try:
                            os.remove(os.path.join('static', image_path))
                        except:
                            pass
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
            msg = 'Medicine updated successfully!'
            success = True
    except Exception as e:
        print(f"[ERROR] {str(e)}")  # Terminal मध्ये दिसेल
        conn.rollback()
        msg = f'Error updating medicine: {str(e)}'
        success = False
    finally:
        cur.close()
        conn.close()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success, 'message': msg})
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
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
    cur.execute('SELECT * FROM findmedicine WHERE id = %s AND user_id = %s',
                (request_id, session['user']['id']))
    request_row = cur.fetchone()
    if request_row:
        cur.execute('DELETE FROM findmedicine WHERE id = %s', (request_id,))
        conn.commit()
        msg = 'Request deleted successfully!'
        success = True
    else:
        msg = 'Request not found or unauthorized'
        success = False
    cur.close()
    conn.close()
    # AJAX (fetch) असेल तर JSON द्या
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success, 'message': msg})
    # नॉर्मल form submit असेल तर redirect
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('my_activities'))

@app.route('/dashboard')
@login_required
@role_required('ngo')
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    
    last_24_hours = datetime.utcnow() - timedelta(hours=24)
    
    # Medicines (Listed)
    cur.execute('''
        SELECT m.id, u.fullname as user_name, m.name as medicine_name, m.quantity, m.quantity_unit, 
               m.expiry_date, m.donation_type, m.price, m.city, m.status, m.created_at
        FROM medicines m
        JOIN users u ON m.user_id = u.id
        WHERE m.created_at >= %s
        ORDER BY m.created_at DESC
    ''', (last_24_hours,))
    medicines = cur.fetchall()
    for med in medicines:
        med['activity_type'] = 'Listed'
    
    # Requests (Requested)
    cur.execute('''
        SELECT f.id, u.fullname as user_name, f.medicine_name, f.quantity, NULL as quantity_unit, 
               NULL as expiry_date, NULL as donation_type, NULL as price, NULL as city, f.status, f.created_at
        FROM findmedicine f
        JOIN users u ON f.user_id = u.id
        WHERE f.created_at >= %s
        ORDER BY f.created_at DESC
    ''', (last_24_hours,))
    requests = cur.fetchall()
    for req in requests:
        req['activity_type'] = 'Requested'
    
    # Combine and sort by created_at desc
    recent_activities = medicines + requests
    recent_activities.sort(key=lambda x: x['created_at'], reverse=True)
    
    # बाकीचे stats जसेच्या तसे
    cur.execute('SELECT COUNT(*) as total FROM users')
    total_users = cur.fetchone()['total']
    cur.execute('SELECT COUNT(*) as regular FROM users WHERE role = %s', ('volunteer',))
    regular_users = cur.fetchone()['regular']
    cur.execute('SELECT COUNT(*) as org FROM users WHERE role IN (%s, %s)', ('ngo', 'medical_org'))
    organizers = cur.fetchone()['org']
    
    cur.close()
    conn.close()
    
    return render_template('dashboard.html', 
      recent_activities=recent_activities,
      total_users=total_users,
      regular_users=regular_users,
      organizers=organizers,
      fullname=session['user']['fullname'] if 'user' in session and 'fullname' in session['user'] else None)

# (Google OAuth routes removed)

@app.route('/block-user/<int:user_id>', methods=['POST'])
@login_required
@role_required('ngo')
def block_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('UPDATE users SET is_blocked = TRUE WHERE id = %s', (user_id,))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'User blocked successfully'
        })
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        cur.close()
        conn.close()

@app.route('/unblock-user/<int:user_id>', methods=['POST'])
@login_required
@role_required('ngo')
def unblock_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('UPDATE users SET is_blocked = FALSE WHERE id = %s', (user_id,))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'User unblocked successfully'
        })
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        cur.close()
        conn.close()

@app.route('/get-all-users', methods=['GET'])
@login_required
@role_required('ngo')
def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('''
            SELECT id, fullname, email, role, is_blocked, created_at 
            FROM users 
            ORDER BY created_at DESC
        ''')
        users = cur.fetchall()
        
        # Convert is_blocked to string
        users_list = []
        for user in users:
            user_dict = dict(user)
            user_dict['is_blocked'] = 'Yes' if user_dict['is_blocked'] else 'No'
            users_list.append(user_dict)
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'users': users_list
        })
    except Exception as e:
        cur.close()
        conn.close()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/get-all-medicines')
@login_required
@role_required('ngo')
def get_all_medicines():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('''
            SELECT m.*, u.fullname as user_name
            FROM medicines m
            JOIN users u ON m.user_id = u.id
            ORDER BY m.created_at DESC
        ''')
        medicines = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'medicines': [dict(medicine) for medicine in medicines]
        })
    except Exception as e:
        cur.close()
        conn.close()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/get-all-requests')
@login_required
@role_required('ngo')
def get_all_requests():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('''
            SELECT f.*, u.fullname as user_name
            FROM findmedicine f
            JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
        ''')
        requests = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'requests': [dict(request) for request in requests]
        })
    except Exception as e:
        cur.close()
        conn.close()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/accept-medicine/<int:id>', methods=['POST'])
@login_required
@role_required('ngo')
def accept_medicine(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('UPDATE medicines SET status = %s WHERE id = %s', ('Accepted', id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Medicine accepted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/reject-medicine/<int:id>', methods=['POST'])
@login_required
@role_required('ngo')
def reject_medicine(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('UPDATE medicines SET status = %s WHERE id = %s', ('Rejected', id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Medicine rejected successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/accept-request/<int:id>', methods=['POST'])
@login_required
@role_required('ngo')
def accept_request(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('UPDATE findmedicine SET status = %s WHERE id = %s', ('Accepted', id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Request accepted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/reject-request/<int:id>', methods=['POST'])
@login_required
@role_required('ngo')
def reject_request(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('UPDATE findmedicine SET status = %s WHERE id = %s', ('Rejected', id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Request rejected successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

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

@app.route('/get-requested-medicine/<int:request_id>')
@login_required
def get_requested_medicine(request_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM findmedicine WHERE id = %s AND user_id = %s', (request_id, session['user']['id']))
    req = cur.fetchone()
    cur.close()
    conn.close()
    if req:
        return jsonify({'success': True, 'request': req})
    else:
        return jsonify({'success': False, 'message': 'Request not found or unauthorized'})

@app.route('/update-medicine-request/<int:request_id>', methods=['POST'])
@login_required
def update_medicine_request(request_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM findmedicine WHERE id = %s AND user_id = %s', (request_id, session['user']['id']))
    req = cur.fetchone()
    if not req:
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Request not found or unauthorized'})
    try:
        medicine_name = request.form.get('medicine_name')
        quantity = request.form.get('quantity')
        purpose = request.form.get('purpose')
        message = request.form.get('message')
        address = request.form.get('address')
        contact = request.form.get('contact')
        cur.execute('''
            UPDATE findmedicine SET medicine_name=%s, quantity=%s, purpose=%s, message=%s, address=%s, contact=%s
            WHERE id=%s
        ''', (medicine_name, quantity, purpose, message, address, contact, request_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/firebase-login', methods=['POST'])
def firebase_login():
    data = request.get_json()
    email = data.get('email')
    fullname = data.get('fullname')
    uid = data.get('uid')
    if not email or not fullname or not uid:
        return jsonify({'success': False, 'message': 'Missing user info'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cur.fetchone()
        if not user:
            # New user, create
            cur.execute('INSERT INTO users (fullname, email, password, role) VALUES (%s, %s, %s, %s) RETURNING id, role',
                        (fullname, email, generate_password_hash(uid), 'volunteer'))
            user_row = cur.fetchone()
            user_id = user_row['id']
            role = user_row['role']
            conn.commit()
        else:
            user_id = user['id']
            role = user['role']
        # Session set
        session['user'] = {
            'id': user_id,
            'email': email,
            'fullname': fullname
        }
        session['role'] = role
        return jsonify({'success': True, 'redirect': url_for('index')})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    setup_database()
    port = int(os.environ.get("PORT", 5000))  
    app.run(host='0.0.0.0', port=port)
