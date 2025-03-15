from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'fee_system'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in first', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Role-based access control
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Access denied: Admin privileges required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        
        if result > 0:
            user = cur.fetchone()
            cur.close()
            
            # Verify password
            try:
                if check_password_hash(user['password'], password):
                    session['logged_in'] = True
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['full_name'] = user['full_name']
                    session['role'] = user['role']
                    
                    flash(f'Welcome back, {user["full_name"]}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid password', 'danger')
            except Exception as e:
                flash('An error occurred while logging in', 'danger')
                print(e)
                session['logged_in'] = True
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['role'] = user['role']
                
                flash(f'Welcome back, {user["full_name"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password', 'danger')
        else:
            cur.close()
            flash('Username not found', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if session['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

# Admin routes
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) as total FROM students")
    total_students = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM student_fees WHERE status = 'pending'")
    pending_payments = cur.fetchone()['total']

    cur.execute("""
        SELECT p.*, u.full_name, f.name as fee_name
        FROM payments p
        JOIN student_fees sf ON p.student_fee_id = sf.id
        JOIN students s ON sf.student_id = s.id
        JOIN users u ON s.user_id = u.id
        JOIN fee_structure fs ON sf.fee_structure_id = fs.id
        JOIN fee_categories f ON fs.category_id = f.id
        ORDER BY p.payment_date DESC
        LIMIT 5
    """)
    recent_payments = cur.fetchall()

    cur.close()

    return render_template(
        'admin/dashboard.html', 
        total_students=total_students,
        pending_payments=pending_payments,
        recent_payments=recent_payments,
        current_date=datetime.now().strftime('%d-%m-%Y')  # Pass date to template
    )

    
    cur.close()
    
    return render_template('admin/dashboard.html', 
                          total_students=total_students,
                          pending_payments=pending_payments,
                          recent_payments=recent_payments)

@app.route('/admin/students', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_students():
    if request.method == 'POST':
        # Add new student
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        full_name = request.form['full_name']
        email = request.form['email']
        roll_number = request.form['roll_number']
        class_name = request.form['class']
        section = request.form['section']
        parent_name = request.form['parent_name']
        parent_phone = request.form['parent_phone']
        address = request.form['address']
        
        cur = mysql.connection.cursor()
        
        # Check if username or email already exists
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", [username, email])
        if cur.fetchone():
            flash('Username or email already exists', 'danger')
            return redirect(url_for('admin_students'))
        
        # Check if roll number already exists
        cur.execute("SELECT * FROM students WHERE roll_number = %s", [roll_number])
        if cur.fetchone():
            flash('Roll number already exists', 'danger')
            return redirect(url_for('admin_students'))
        
        # Insert user
        cur.execute("""
            INSERT INTO users (username, password, full_name, role, email)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password, full_name, 'student', email))
        
        user_id = cur.lastrowid
        
        # Insert student
        cur.execute("""
            INSERT INTO students (user_id, roll_number, class, section, parent_name, parent_phone, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, roll_number, class_name, section, parent_name, parent_phone, address))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Student added successfully', 'success')
        return redirect(url_for('admin_students'))
    
    # Get all students
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.*, u.username, u.full_name, u.email
        FROM students s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.roll_number
    """)
    students = cur.fetchall()
    cur.close()
    
    return render_template('admin/students.html', students=students)

@app.route('/admin/fee_structure', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_fee_structure():
    if request.method == 'POST':
        # Add new fee structure
        category_id = request.form['category_id']
        class_name = request.form['class']
        amount = request.form['amount']
        academic_year = request.form['academic_year']
        due_date = request.form['due_date']
        
        cur = mysql.connection.cursor()
        
        # Check if this fee structure already exists
        cur.execute("""
            SELECT * FROM fee_structure 
            WHERE category_id = %s AND class = %s AND academic_year = %s
        """, (category_id, class_name, academic_year))
        
        if cur.fetchone():
            flash('Fee structure already exists for this category, class and academic year', 'danger')
            return redirect(url_for('admin_fee_structure'))
        
        # Insert fee structure
        cur.execute("""
            INSERT INTO fee_structure (category_id, class, amount, academic_year, due_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (category_id, class_name, amount, academic_year, due_date))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Fee structure added successfully', 'success')
        return redirect(url_for('admin_fee_structure'))
    
    # Get all fee structures and categories
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM fee_categories")
    categories = cur.fetchall()
    
    cur.execute("""
        SELECT fs.*, fc.name as category_name
        FROM fee_structure fs
        JOIN fee_categories fc ON fs.category_id = fc.id
        ORDER BY fs.academic_year DESC, fs.class
    """)
    fee_structures = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/fee_structure.html', 
                          categories=categories,
                          fee_structures=fee_structures)

@app.route('/admin/allocate_fees', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_allocate_fees():
    if request.method == 'POST':
        student_id = request.form['student_id']
        fee_structure_id = request.form['fee_structure_id']
        
        cur = mysql.connection.cursor()
        
        # Check if already allocated
        cur.execute("""
            SELECT * FROM student_fees
            WHERE student_id = %s AND fee_structure_id = %s
        """, (student_id, fee_structure_id))
        
        if cur.fetchone():
            flash('Fee already allocated to this student', 'danger')
            return redirect(url_for('admin_allocate_fees'))
        
        # Allocate fee
        cur.execute("""
            INSERT INTO student_fees (student_id, fee_structure_id)
            VALUES (%s, %s)
        """, (student_id, fee_structure_id))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Fee allocated successfully', 'success')
        return redirect(url_for('admin_allocate_fees'))
    
    # Get students and fee structures
    cur = mysql.connection.cursor()
    
    cur.execute("""
        SELECT s.id, s.roll_number, u.full_name, s.class
        FROM students s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.roll_number
    """)
    students = cur.fetchall()
    
    cur.execute("""
        SELECT fs.id, fc.name as category, fs.class, fs.amount, fs.academic_year, fs.due_date
        FROM fee_structure fs
        JOIN fee_categories fc ON fs.category_id = fc.id
        ORDER BY fs.due_date DESC
    """)
    fee_structures = cur.fetchall()
    
    # Get allocated fees
    cur.execute("""
        SELECT sf.*, s.roll_number, u.full_name as student_name, 
               fc.name as fee_name, fs.amount, fs.due_date, fs.academic_year,
               fs.class
        FROM student_fees sf
        JOIN students s ON sf.student_id = s.id
        JOIN users u ON s.user_id = u.id
        JOIN fee_structure fs ON sf.fee_structure_id = fs.id
        JOIN fee_categories fc ON fs.category_id = fc.id
        ORDER BY sf.allocated_at DESC
    """)
    allocated_fees = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/allocate_fees.html',
                          students=students,
                          fee_structures=fee_structures,
                          allocated_fees=allocated_fees)

@app.route('/admin/payments')
@login_required
@admin_required
def admin_payments():
    cur = mysql.connection.cursor()
    
    # Get all payments
    cur.execute("""
        SELECT p.*, u.full_name as student_name, s.roll_number,
               fc.name as fee_name, fs.academic_year, fs.class
        FROM payments p
        JOIN student_fees sf ON p.student_fee_id = sf.id
        JOIN students s ON sf.student_id = s.id
        JOIN users u ON s.user_id = u.id
        JOIN fee_structure fs ON sf.fee_structure_id = fs.id
        JOIN fee_categories fc ON fs.category_id = fc.id
        ORDER BY p.payment_date DESC
    """)
    payments = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/payments.html', payments=payments)

# Student routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if session['role'] != 'student':
        return redirect(url_for('admin_dashboard'))
    
    cur = mysql.connection.cursor()
    
    # Get student details
    cur.execute("""
        SELECT s.*, u.email
        FROM students s
        JOIN users u ON s.user_id = u.id
        WHERE u.id = %s
    """, [session['user_id']])
    student = cur.fetchone()
    
    # Get fee summary
    cur.execute("""
        SELECT 
            SUM(fs.amount) as total_fees,
            SUM(CASE WHEN sf.status = 'paid' THEN fs.amount ELSE 0 END) as paid_fees,
            COUNT(CASE WHEN sf.status = 'pending' THEN 1 END) as pending_count
        FROM student_fees sf
        JOIN students s ON sf.student_id = s.id
        JOIN fee_structure fs ON sf.fee_structure_id = fs.id
        WHERE s.user_id = %s
    """, [session['user_id']])
    fee_summary = cur.fetchone()
    
    # Get upcoming fees
    cur.execute("""
        SELECT sf.*, fc.name as fee_name, fs.amount, fs.due_date, fs.academic_year
        FROM student_fees sf
        JOIN students s ON sf.student_id = s.id
        JOIN fee_structure fs ON sf.fee_structure_id = fs.id
        JOIN fee_categories fc ON fs.category_id = fc.id
        WHERE s.user_id = %s AND sf.status != 'paid'
        ORDER BY fs.due_date
        LIMIT 5
    """, [session['user_id']])
    upcoming_fees = cur.fetchall()
    
    cur.close()
    
    return render_template('student/dashboard.html',
                         student=student,
                         fee_summary=fee_summary,
                         upcoming_fees=upcoming_fees)

@app.route('/student/pay_fees', methods=['GET', 'POST'])
@login_required
def student_pay_fees():
    if session['role'] != 'student':
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        student_fee_id = request.form['student_fee_id']
        amount = float(request.form['amount'])
        payment_method = request.form['payment_method']
        transaction_id = request.form.get('transaction_id', '')
        notes = request.form.get('notes', '')
        
        cur = mysql.connection.cursor()
        
        # Get the fee record
        cur.execute("""
            SELECT sf.*, fs.amount
            FROM student_fees sf
            JOIN fee_structure fs ON sf.fee_structure_id = fs.id
            JOIN students s ON sf.student_id = s.id
            WHERE sf.id = %s AND s.user_id = %s
        """, (student_fee_id, session['user_id']))
        
        fee = cur.fetchone()
        if not fee:
            flash('Invalid fee selected', 'danger')
            return redirect(url_for('student_pay_fees'))
        
        # Add payment
        cur.execute("""
            INSERT INTO payments (student_fee_id, amount, payment_method, transaction_id, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (student_fee_id, amount, payment_method, transaction_id, notes))
        
        # Update fee status
        # Get total paid amount
        cur.execute("""
            SELECT SUM(amount) as total_paid
            FROM payments
            WHERE student_fee_id = %s
        """, [student_fee_id])
        
        total_paid = cur.fetchone()['total_paid']
        
        # Update status based on payment
        status = 'pending'
        if total_paid >= fee['amount']:
            status = 'paid'
        elif total_paid == fee['amount']:
            status = 'paid'
        elif total_paid > 0:
            status = 'partial'
            
        cur.execute("""
            UPDATE student_fees
            SET status = %s
            WHERE id = %s
        """, (status, student_fee_id))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Payment recorded successfully', 'success')
        return redirect(url_for('student_payment_history'))
    
    # Get pending fees
    cur = mysql.connection.cursor()
    
    cur.execute("""
        SELECT sf.id, fc.name as fee_name, fs.amount, fs.due_date, 
               fs.academic_year, sf.status,
               (SELECT SUM(amount) FROM payments WHERE student_fee_id = sf.id) as paid_amount
        FROM student_fees sf
        JOIN students s ON sf.student_id = s.id
        JOIN fee_structure fs ON sf.fee_structure_id = fs.id
        JOIN fee_categories fc ON fs.category_id = fc.id
        WHERE s.user_id = %s AND sf.status != 'paid'
        ORDER BY fs.due_date
    """, [session['user_id']])
    
    pending_fees = cur.fetchall()
    
    # Calculate remaining amounts
    for fee in pending_fees:
        if fee['paid_amount'] is None:
            fee['paid_amount'] = 0
        fee['remaining'] = fee['amount'] - fee['paid_amount']
    
    cur.close()
    
    return render_template('student/pay_fees.html', pending_fees=pending_fees)

@app.route('/student/payment_history')
@login_required
def student_payment_history():
    if session['role'] != 'student':
        return redirect(url_for('admin_dashboard'))
    
    cur = mysql.connection.cursor()
    
    # Get student ID
    cur.execute("SELECT id FROM students WHERE user_id = %s", [session['user_id']])
    student_id = cur.fetchone()['id']
    
    # Get payment history
    cur.execute("""
        SELECT p.*, fc.name as fee_name, fs.academic_year, sf.status
        FROM payments p
        JOIN student_fees sf ON p.student_fee_id = sf.id
        JOIN fee_structure fs ON sf.fee_structure_id = fs.id
        JOIN fee_categories fc ON fs.category_id = fc.id
        WHERE sf.student_id = %s
        ORDER BY p.payment_date DESC
    """, [student_id])
    
    payments = cur.fetchall()
    
    # Get fee summary
    cur.execute("""
        SELECT 
            COUNT(DISTINCT sf.id) as total_fees,
            SUM(fs.amount) as total_amount,
            SUM(CASE WHEN sf.status = 'paid' THEN fs.amount ELSE 0 END) as paid_amount,
            COUNT(CASE WHEN sf.status = 'paid' THEN 1 END) as paid_count,
            COUNT(CASE WHEN sf.status = 'pending' THEN 1 END) as pending_count,
            COUNT(CASE WHEN sf.status = 'partial' THEN 1 END) as partial_count
        FROM student_fees sf
        JOIN fee_structure fs ON sf.fee_structure_id = fs.id
        WHERE sf.student_id = %s
    """, [student_id])
    
    summary = cur.fetchone()
    
    cur.close()
    
    return render_template('student/payment_history.html', 
                         payments=payments, 
                         summary=summary)

if __name__ == '__main__':
    app.run(debug=True)