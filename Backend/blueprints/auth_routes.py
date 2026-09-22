from flask import Blueprint, request, jsonify, session
import random
import time
from models import get_db
from auth_utils import hash_password, verify_password, set_user_session, clear_user_session, get_current_user, login_required

# Create the Blueprint with prefix '/api/auth'
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# =========================================================================
# 1. STUDENT SIGNUP
# =========================================================================

@auth_bp.route('/students/signup', methods=['POST'])
def student_signup():
    # request.get_json() unboxes the incoming JSON cardboard box!
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    college = data.get('college', '').strip()
    skills = data.get('skills', '').strip()
    university_roll_no = data.get('university_roll_no', '').strip() or None
    institute_id = data.get('institute_id')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required.'}), 400

    # Scramble the password using our security blender!
    pwd_hash = hash_password(password)

    conn = get_db()
    cursor = conn.cursor()

    # Validate institute_id exists in institutes table, otherwise set to None
    valid_institute_id = None
    if institute_id:
        try:
            inst_num = int(institute_id)
            cursor.execute("SELECT id FROM institutes WHERE id = ?", (inst_num,))
            if cursor.fetchone():
                valid_institute_id = inst_num
        except (ValueError, TypeError):
            valid_institute_id = None

    try:
        cursor.execute("SELECT id FROM students WHERE LOWER(email) = LOWER(?)", (email,))
        existing = cursor.fetchone()
        if existing:
            student_id = existing['id']
            cursor.execute(
                """
                UPDATE students
                SET name = ?, password_hash = ?, college = COALESCE(?, college), skills = COALESCE(?, skills),
                    university_roll_no = COALESCE(?, university_roll_no), institute_id = COALESCE(?, institute_id)
                WHERE id = ?
                """,
                (name, pwd_hash, college, skills, university_roll_no, valid_institute_id, student_id)
            )
            conn.commit()
            set_user_session(student_id, 'student', email, name)
            return jsonify({
                'message': 'Student logged in successfully!',
                'user': {
                    'id': student_id,
                    'name': name,
                    'email': email,
                    'role': 'student',
                    'university_roll_no': university_roll_no
                }
            }), 200

        cursor.execute(
            """
            INSERT INTO students (name, email, password_hash, college, skills, university_roll_no, institute_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, email, pwd_hash, college, skills, university_roll_no, valid_institute_id)
        )
        conn.commit()
        student_id = cursor.lastrowid
        print(f"[AUTH SIGNUP SUCCESS] Student successfully saved to database: {name} ({email}) ID={student_id}")

        # Log the student in immediately by setting the session
        set_user_session(student_id, 'student', email, name)

        return jsonify({
            'message': 'Student registered and logged in successfully!',
            'user': {
                'id': student_id,
                'name': name,
                'email': email,
                'role': 'student',
                'university_roll_no': university_roll_no
            }
        }), 201

    except Exception as e:
        conn.rollback()
        print(f"[AUTH SIGNUP ERROR] Registration failed: {e}")
        cursor.execute("SELECT id FROM students WHERE LOWER(email) = LOWER(?)", (email,))
        existing = cursor.fetchone()
        if existing:
            student_id = existing['id']
            set_user_session(student_id, 'student', email, name)
            return jsonify({
                'message': 'Student logged in successfully!',
                'user': {
                    'id': student_id,
                    'name': name,
                    'email': email,
                    'role': 'student',
                    'university_roll_no': university_roll_no
                }
            }), 200
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    finally:
        conn.close()

# =========================================================================
# 2. STUDENT LOGIN
# =========================================================================

@auth_bp.route('/students/login', methods=['POST'])
def student_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
    student = cursor.fetchone()
    conn.close()

    print(f"[AUTH LOGIN] Attempt for email: {email}")

    # If not found in students, check other roles (academician, industry, institute)
    if not student:
        for tbl, r_name, name_col in [('academicians', 'academician', 'name'), ('industries', 'industry', 'company_name'), ('institutes', 'institute', 'name')]:
            conn_other = get_db()
            cur_other = conn_other.cursor()
            cur_other.execute(f"SELECT * FROM {tbl} WHERE email = ?", (email,))
            other_user = cur_other.fetchone()
            conn_other.close()
            if other_user and verify_password(other_user['password_hash'], password):
                print(f"[AUTH LOGIN SUCCESS] Found in {tbl}, logging in as {r_name}!")
                set_user_session(other_user['id'], r_name, other_user['email'], other_user[name_col])
                return jsonify({
                    'message': f"Welcome back, {other_user[name_col]}!",
                    'user': {'id': other_user['id'], 'name': other_user[name_col], 'email': other_user['email'], 'role': r_name}
                }), 200

        print(f"[AUTH LOGIN FAILED] '{email}' does not exist in the database.")
        return jsonify({'error': 'Invalid email or password. Please check your credentials or click Register to create an account.'}), 401

    if not verify_password(student['password_hash'], password):
        print(f"[AUTH LOGIN FAILED] Incorrect password for '{email}'.")
        return jsonify({'error': 'Invalid email or password.'}), 401

    print(f"[AUTH LOGIN SUCCESS] Logged in: {student['name']} ({email})")
    set_user_session(student['id'], 'student', student['email'], student['name'])
    return jsonify({
        'message': f"Welcome back, {student['name']}!",
        'user': {
            'id': student['id'],
            'name': student['name'],
            'email': student['email'],
            'role': 'student'
        }
    }), 200

@auth_bp.route('/industries/signup', methods=['POST'])
def industry_signup():
    data = request.get_json() or {}
    company_name = data.get('company_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    if not company_name or not email or not password:
        return jsonify({'error': 'Company name, email, and password are required.'}), 400
    pwd_hash = hash_password(password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, company_name FROM industries WHERE LOWER(email) = LOWER(?)", (email,))
        existing = cursor.fetchone()
        if existing:
            industry_id = existing['id']
            cursor.execute("UPDATE industries SET company_name = ?, password_hash = ? WHERE id = ?", (company_name, pwd_hash, industry_id))
            conn.commit()
            set_user_session(industry_id, 'industry', email, company_name)
            return jsonify({
                'message': 'Industry partner logged in successfully!',
                'user': {'id': industry_id, 'name': company_name, 'email': email, 'role': 'industry'}
            }), 200

        cursor.execute(
            "INSERT INTO industries (company_name, email, password_hash) VALUES (?, ?, ?)",
            (company_name, email, pwd_hash)
        )
        conn.commit()
        industry_id = cursor.lastrowid
        set_user_session(industry_id, 'industry', email, company_name)
        return jsonify({
            'message': 'Industry partner registered successfully!',
            'user': {'id': industry_id, 'name': company_name, 'email': email, 'role': 'industry'}
        }), 201
    except Exception as e:
        conn.rollback()
        cursor.execute("SELECT id, company_name FROM industries WHERE LOWER(email) = LOWER(?)", (email,))
        existing = cursor.fetchone()
        if existing:
            set_user_session(existing['id'], 'industry', email, existing['company_name'])
            return jsonify({
                'message': 'Industry partner logged in successfully!',
                'user': {'id': existing['id'], 'name': existing['company_name'], 'email': email, 'role': 'industry'}
            }), 200
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    finally:
        conn.close()

@auth_bp.route('/industries/login', methods=['POST'])
def industry_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM industries WHERE email = ?", (email,))
    industry = cursor.fetchone()
    conn.close()
    if not industry or not verify_password(industry['password_hash'], password):
        return jsonify({'error': 'Invalid email or password.'}), 401
    set_user_session(industry['id'], 'industry', industry['email'], industry['company_name'])
    return jsonify({
        'message': f"Welcome back, {industry['company_name']}!",
        'user': {'id': industry['id'], 'name': industry['company_name'], 'email': industry['email'], 'role': 'industry'}
    }), 200

@auth_bp.route('/institutes/signup', methods=['POST'])
def institute_signup():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    admin_tpo_contact = data.get('admin_tpo_contact', '').strip()
    if not name or not email or not password:
        return jsonify({'error': 'Institute name, email, and password are required.'}), 400
    pwd_hash = hash_password(password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM institutes WHERE LOWER(email) = LOWER(?)", (email,))
        existing = cursor.fetchone()
        if existing:
            institute_id = existing['id']
            cursor.execute("UPDATE institutes SET name = ?, password_hash = ?, admin_tpo_contact = COALESCE(?, admin_tpo_contact) WHERE id = ?", (name, pwd_hash, admin_tpo_contact, institute_id))
            conn.commit()
            set_user_session(institute_id, 'institute', email, name)
            return jsonify({
                'message': 'Institute logged in successfully!',
                'user': {'id': institute_id, 'name': name, 'email': email, 'role': 'institute'}
            }), 200

        cursor.execute(
            "INSERT INTO institutes (name, email, password_hash, admin_tpo_contact) VALUES (?, ?, ?, ?)",
            (name, email, pwd_hash, admin_tpo_contact)
        )
        conn.commit()
        institute_id = cursor.lastrowid
        set_user_session(institute_id, 'institute', email, name)
        return jsonify({
            'message': 'Institute registered successfully!',
            'user': {'id': institute_id, 'name': name, 'email': email, 'role': 'institute'}
        }), 201
    except Exception as e:
        conn.rollback()
        cursor.execute("SELECT id, name FROM institutes WHERE LOWER(email) = LOWER(?)", (email,))
        existing = cursor.fetchone()
        if existing:
            set_user_session(existing['id'], 'institute', email, existing['name'])
            return jsonify({
                'message': 'Institute logged in successfully!',
                'user': {'id': existing['id'], 'name': existing['name'], 'email': email, 'role': 'institute'}
            }), 200
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    finally:
        conn.close()

@auth_bp.route('/institutes/login', methods=['POST'])
def institute_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM institutes WHERE email = ?", (email,))
    institute = cursor.fetchone()
    conn.close()
    if not institute or not verify_password(institute['password_hash'], password):
        return jsonify({'error': 'Invalid email or password.'}), 401
    set_user_session(institute['id'], 'institute', institute['email'], institute['name'])
    return jsonify({
        'message': f"Welcome back, {institute['name']}!",
        'user': {'id': institute['id'], 'name': institute['name'], 'email': institute['email'], 'role': 'institute'}
    }), 200

@auth_bp.route('/academicians/signup', methods=['POST'])
def academician_signup():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    expertise_domain = data.get('expertise_domain', '').strip()
    institute_id = data.get('institute_id')
    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required.'}), 400
    pwd_hash = hash_password(password)
    conn = get_db()
    cursor = conn.cursor()

    valid_institute_id = None
    if institute_id:
        try:
            inst_num = int(institute_id)
            cursor.execute("SELECT id FROM institutes WHERE id = ?", (inst_num,))
            if cursor.fetchone():
                valid_institute_id = inst_num
        except (ValueError, TypeError):
            valid_institute_id = None

    try:
        cursor.execute("SELECT id, name FROM academicians WHERE LOWER(email) = LOWER(?)", (email,))
        existing = cursor.fetchone()
        if existing:
            academician_id = existing['id']
            cursor.execute(
                """
                UPDATE academicians
                SET name = ?, password_hash = ?, institute_id = COALESCE(?, institute_id), expertise_domain = COALESCE(?, expertise_domain)
                WHERE id = ?
                """,
                (name, pwd_hash, valid_institute_id, expertise_domain, academician_id)
            )
            conn.commit()
            set_user_session(academician_id, 'academician', email, name)
            return jsonify({
                'message': 'Academician logged in successfully!',
                'user': {'id': academician_id, 'name': name, 'email': email, 'role': 'academician'}
            }), 200

        cursor.execute(
            "INSERT INTO academicians (name, email, password_hash, institute_id, expertise_domain) VALUES (?, ?, ?, ?, ?)",
            (name, email, pwd_hash, valid_institute_id, expertise_domain)
        )
        conn.commit()
        academician_id = cursor.lastrowid
        set_user_session(academician_id, 'academician', email, name)
        return jsonify({
            'message': 'Academician registered successfully!',
            'user': {'id': academician_id, 'name': name, 'email': email, 'role': 'academician'}
        }), 201
    except Exception as e:
        conn.rollback()
        cursor.execute("SELECT id, name FROM academicians WHERE LOWER(email) = LOWER(?)", (email,))
        existing = cursor.fetchone()
        if existing:
            set_user_session(existing['id'], 'academician', email, existing['name'])
            return jsonify({
                'message': 'Academician logged in successfully!',
                'user': {'id': existing['id'], 'name': existing['name'], 'email': email, 'role': 'academician'}
            }), 200
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    finally:
        conn.close()
@auth_bp.route('/academicians/login', methods=['POST'])
def academician_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM academicians WHERE email = ?", (email,))
    academician = cursor.fetchone()
    conn.close()
    if not academician or not verify_password(academician['password_hash'], password):
        return jsonify({'error': 'Invalid email or password.'}), 401
    set_user_session(academician['id'], 'academician', academician['email'], academician['name'])
    return jsonify({
        'message': f"Welcome back, Prof. {academician['name']}!",
        'user': {'id': academician['id'], 'name': academician['name'], 'email': academician['email'], 'role': 'academician'}
    }), 200

# =========================================================================
# 3. CURRENT USER & LOGOUT
# =========================================================================

@auth_bp.route('/me', methods=['GET'])
@login_required
def who_am_i():
    """Returns details of the currently logged-in user."""
    user = get_current_user()
    return jsonify({'user': user}), 200

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logs the user out."""
    clear_user_session()
    return jsonify({'message': 'Logged out successfully.'}), 200

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

OTP_STORE = {}

DEMO_DOMAINS = {'example.com', 'test.com', 'demo.com', 'sample.com', 'college.edu', 'msu.edu'}

def send_real_email_otp(to_email: str, otp_code: str) -> bool:
    """Attempts to dispatch an actual email via SMTP if credentials are configured."""
    smtp_email = getattr(Config, 'SMTP_EMAIL', '')
    smtp_password = getattr(Config, 'SMTP_PASSWORD', '').replace(' ', '')
    smtp_server = getattr(Config, 'SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(getattr(Config, 'SMTP_PORT', 587))

    if not smtp_email or not smtp_password:
        print(f"[Email Dispatcher] SMTP credentials not set in config.py. OTP for {to_email} is: {otp_code}")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{otp_code} is your VidyaSarthi Verification Code"
        msg['From'] = f"VidyaSarthi Verification <{smtp_email}>"
        msg['To'] = to_email

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; border: 1px solid #E1D6AE; border-radius: 12px; background-color: #FDFBF7;">
            <h2 style="color: #2C3524; margin-bottom: 8px;">VidyaSarthi Verification</h2>
            <p style="color: #6B7660; font-size: 14px;">Use the following 6-digit code to verify your account registration:</p>
            <div style="margin: 24px 0; padding: 14px; background: #2C3524; color: #F2E8CF; font-size: 28px; font-weight: bold; letter-spacing: 6px; text-align: center; border-radius: 8px;">
                {otp_code}
            </div>
            <p style="color: #6B7660; font-size: 12px;">This code will expire in 10 minutes. If you did not request this, please ignore this email.</p>
        </div>
        """
        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, to_email, msg.as_string())
        server.quit()
        print(f"[Email Dispatcher] Successfully sent live email to {to_email}!")
        return True
    except Exception as e:
        print(f"[Email Dispatcher Error] Could not send live email to {to_email}: {e}")
        return False

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Generates a 6-digit OTP. Sends real email for actual inboxes, and demo assist for demo domains."""
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if not email or '@' not in email:
        return jsonify({'error': 'A valid email address is required.'}), 400

    otp_code = str(random.randint(100000, 999999))
    expires_at = time.time() + 600
    OTP_STORE[email] = {
        'otp': otp_code,
        'expires_at': expires_at
    }

    domain = email.split('@')[-1]
    is_demo = domain in DEMO_DOMAINS or 'demo' in email or 'test' in email

    # Attempt to send real email
    email_dispatched = send_real_email_otp(email, otp_code)

    response_payload = {
        'message': f'Verification OTP sent to {email}!'
    }

    # Only include demo_otp if it's explicitly a demo domain OR real dispatch was not configured
    if is_demo or not email_dispatched:
        response_payload['demo_otp'] = otp_code
        response_payload['is_demo'] = True
    else:
        response_payload['is_demo'] = False

    return jsonify(response_payload), 200
@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verifies the 6-digit code before allowing account creation."""
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    otp = data.get('otp', '').strip()
    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required.'}), 400
    record = OTP_STORE.get(email)
    if not record:
        return jsonify({'error': 'No OTP request found for this email. Please request a new one.'}), 400
    if time.time() > record['expires_at']:
        del OTP_STORE[email]
        return jsonify({'error': 'OTP has expired. Please request a new one.'}), 400
    if record['otp'] != otp:
        return jsonify({'error': 'Invalid OTP code. Please try again.'}), 400
    # Clean up after successful verification
    del OTP_STORE[email]
    return jsonify({'message': 'Email verified successfully!'}), 200

RESET_OTP_STORE = {}

def send_password_reset_email(to_email: str, otp_code: str) -> bool:
    """Attempts to dispatch an actual password reset email via SMTP if credentials are configured."""
    smtp_email = getattr(Config, 'SMTP_EMAIL', '')
    smtp_password = getattr(Config, 'SMTP_PASSWORD', '').replace(' ', '')
    smtp_server = getattr(Config, 'SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(getattr(Config, 'SMTP_PORT', 587))

    if not smtp_email or not smtp_password:
        print(f"[Password Reset Dispatcher] SMTP credentials not set in config.py. Reset OTP for {to_email} is: {otp_code}")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{otp_code} is your VidyaSarthi Password Reset Code"
        msg['From'] = f"VidyaSarthi Security <{smtp_email}>"
        msg['To'] = to_email

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; border: 1px solid #E1D6AE; border-radius: 12px; background-color: #FDFBF7;">
            <h2 style="color: #2C3524; margin-bottom: 8px;">VidyaSarthi Password Reset</h2>
            <p style="color: #6B7660; font-size: 14px;">We received a request to reset your VidyaSarthi account password. Use the following 6-digit code:</p>
            <div style="margin: 24px 0; padding: 14px; background: #2C3524; color: #F2E8CF; font-size: 28px; font-weight: bold; letter-spacing: 6px; text-align: center; border-radius: 8px;">
                {otp_code}
            </div>
            <p style="color: #6B7660; font-size: 12px;">This code will expire in 10 minutes. If you did not request a password reset, please ignore this email.</p>
        </div>
        """
        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, to_email, msg.as_string())
        server.quit()
        print(f"[Password Reset Dispatcher] Successfully sent reset email to {to_email}!")
        return True
    except Exception as e:
        print(f"[Password Reset Dispatcher Error] Could not send reset email to {to_email}: {e}")
        return False

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Initiates password reset by sending a 6-digit OTP to the user's email."""
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if not email or '@' not in email:
        return jsonify({'error': 'A valid email address is required.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    user_found = False
    stakeholder_table = None

    # Search all stakeholder tables to find the account
    for tbl in ['students', 'industries', 'institutes', 'academicians']:
        cursor.execute(f"SELECT id, email FROM {tbl} WHERE LOWER(email) = LOWER(?)", (email,))
        row = cursor.fetchone()
        if row:
            user_found = True
            stakeholder_table = tbl
            break
    conn.close()

    if not user_found:
        return jsonify({'error': 'No registered account found with this email address.'}), 404

    otp_code = str(random.randint(100000, 999999))
    expires_at = time.time() + 600  # 10 minutes
    RESET_OTP_STORE[email] = {
        'otp': otp_code,
        'expires_at': expires_at,
        'table': stakeholder_table
    }

    domain = email.split('@')[-1]
    is_demo = domain in DEMO_DOMAINS or 'demo' in email or 'test' in email

    # Send real email via SMTP if configured
    email_dispatched = send_password_reset_email(email, otp_code)

    payload = {
        'message': f'Password reset OTP sent to {email}!'
    }
    if is_demo or not email_dispatched:
        payload['demo_otp'] = otp_code
        payload['is_demo'] = True
    else:
        payload['is_demo'] = False

    return jsonify(payload), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Verifies OTP and resets the user's password across all stakeholder tables."""
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    otp = data.get('otp', '').strip()
    new_password = data.get('new_password', '').strip()

    if not email or not otp or not new_password:
        return jsonify({'error': 'Email, OTP, and new password are required.'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long.'}), 400

    record = RESET_OTP_STORE.get(email)
    if not record:
        return jsonify({'error': 'No reset request found for this email. Please request a new code.'}), 400

    if time.time() > record['expires_at']:
        del RESET_OTP_STORE[email]
        return jsonify({'error': 'OTP has expired. Please request a new one.'}), 400

    if record['otp'] != otp:
        return jsonify({'error': 'Invalid OTP code. Please try again.'}), 400

    new_hash = hash_password(new_password)
    target_table = record.get('table')

    conn = get_db()
    cursor = conn.cursor()
    updated = False

    tables_to_try = [target_table] if target_table else ['students', 'industries', 'institutes', 'academicians']
    for tbl in tables_to_try:
        if not tbl:
            continue
        cursor.execute(f"UPDATE {tbl} SET password_hash = ? WHERE LOWER(email) = LOWER(?)", (new_hash, email))
        if cursor.rowcount > 0:
            updated = True
            break

    conn.commit()
    conn.close()

    # Clear OTP after successful reset
    del RESET_OTP_STORE[email]

    if not updated:
        return jsonify({'error': 'Account not found to update password.'}), 404

    return jsonify({'message': 'Password has been successfully reset! You can now log in with your new password.'}), 200

# =========================================================================
# 11. DYNAMIC ROLE-SPECIFIC NOTIFICATIONS
# =========================================================================

@auth_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Returns dynamic, role-relevant notifications based on database state and current session."""
    user = get_current_user()
    conn = get_db()
    cursor = conn.cursor()
    notifications = []

    if not user:
        # Default helpful onboarding notifications for visitors
        notifications = [
            {
                "id": "notif-guest-1",
                "text": "Welcome to VidyaSarthi! Register or log in to verify technical skills and track applications.",
                "tag": "Welcome",
                "type": "info",
                "time": "Just now"
            },
            {
                "id": "notif-guest-2",
                "text": "Explore active internships and research listings across premier institutes and companies.",
                "tag": "Opportunities",
                "type": "info",
                "time": "1h ago"
            },
            {
                "id": "notif-guest-3",
                "text": "Skill assessments now support 10 timed questions with AI verification badges.",
                "tag": "Assessment",
                "type": "success",
                "time": "Today"
            }
        ]
        conn.close()
        return jsonify({'notifications': notifications}), 200

    role = user.get('role')
    user_id = user.get('user_id')

    if role == 'student':
        # 1. Student Info
        cursor.execute(
            """
            SELECT s.name, s.college, s.verification_status, s.university_roll_no, 
                   s.resume_score, s.desired_role, inst.name as inst_name
            FROM students s
            LEFT JOIN institutes inst ON s.institute_id = inst.id
            WHERE s.id = ?
            """,
            (user_id,)
        )
        st = cursor.fetchone()
        inst_label = (st['inst_name'] if st and st['inst_name'] else (st['college'] if st and st['college'] else 'your university'))

        if st:
            status = st['verification_status'] or 'unverified'
            if status == 'verified':
                notifications.append({
                    "id": "notif-st-ver",
                    "text": f"Institutional roll number verified by {inst_label}! Verified student badge active on your profile.",
                    "tag": "Institute",
                    "type": "success",
                    "time": "Verified"
                })
            elif status == 'pending':
                roll_disp = f" (Roll: {st['university_roll_no']})" if st['university_roll_no'] else ""
                notifications.append({
                    "id": "notif-st-ver-pending",
                    "text": f"Your institutional verification request{roll_disp} is currently under review by {inst_label}.",
                    "tag": "Verification",
                    "type": "warning",
                    "time": "Pending"
                })
            else:
                notifications.append({
                    "id": "notif-st-ver-prompt",
                    "text": "Submit your university roll number in Profile to request official institutional verification.",
                    "tag": "Action Required",
                    "type": "info",
                    "time": "Prompt"
                })

            # Resume Score Status
            r_score = st['resume_score']
            if r_score and float(r_score) > 0:
                notifications.append({
                    "id": "notif-st-resume",
                    "text": f"Gemini ATS Audit: Resume rated {float(r_score):.1f}/10 for {st['desired_role'] or 'Software Engineer'}. View detailed gap analysis in AI Tools.",
                    "tag": "AI ATS",
                    "type": "success",
                    "time": "Updated"
                })
            else:
                notifications.append({
                    "id": "notif-st-resume-prompt",
                    "text": "Analyze your resume with Gemini AI in the AI Tools Hub to compute ATS score and find skill gaps.",
                    "tag": "AI Tools",
                    "type": "info",
                    "time": "Recommended"
                })

        # 2. Verified Skills
        cursor.execute(
            """
            SELECT skill_name, percentage, assessed_at 
            FROM student_skill_scores 
            WHERE student_id = ? 
            ORDER BY assessed_at DESC LIMIT 2
            """,
            (user_id,)
        )
        skill_rows = cursor.fetchall()
        for idx, sk in enumerate(skill_rows):
            notifications.append({
                "id": f"notif-st-skill-{idx}",
                "text": f"Verified skill credential earned: {sk['skill_name']} test passed with {sk['percentage']}% score.",
                "tag": "Skill Badge",
                "type": "success",
                "time": "Verified"
            })

        # 3. Applications
        cursor.execute(
            """
            SELECT a.status, a.applied_date, p.title, ind.company_name, aca.name as prof_name
            FROM applications a
            JOIN postings p ON a.posting_id = p.id
            LEFT JOIN industries ind ON p.industry_id = ind.id
            LEFT JOIN academicians aca ON p.academician_id = aca.id
            WHERE a.student_id = ?
            ORDER BY a.applied_date DESC LIMIT 2
            """,
            (user_id,)
        )
        app_rows = cursor.fetchall()
        for idx, app in enumerate(app_rows):
            org = app['company_name'] or app['prof_name'] or 'Host'
            status_text = app['status'].capitalize()
            notifications.append({
                "id": f"notif-st-app-{idx}",
                "text": f"Application for '{app['title']}' at {org} is marked as '{status_text}'.",
                "tag": "Application",
                "type": "info",
                "time": "Recent"
            })

        # 4. Recent Matching Postings
        cursor.execute(
            """
            SELECT p.title, p.posting_type, ind.company_name 
            FROM postings p
            LEFT JOIN industries ind ON p.industry_id = ind.id
            ORDER BY p.created_at DESC LIMIT 2
            """
        )
        post_rows = cursor.fetchall()
        for idx, pst in enumerate(post_rows):
            comp = pst['company_name'] or 'Partner'
            notifications.append({
                "id": f"notif-st-post-{idx}",
                "text": f"New {pst['posting_type'].capitalize()} posted: '{pst['title']}' by {comp}.",
                "tag": "Opportunity",
                "type": "info",
                "time": "New"
            })

    elif role == 'industry':
        cursor.execute(
            """
            SELECT s.name, s.college, p.title, a.applied_date
            FROM applications a
            JOIN postings p ON a.posting_id = p.id
            JOIN students s ON a.student_id = s.id
            WHERE p.industry_id = ?
            ORDER BY a.applied_date DESC LIMIT 3
            """,
            (user_id,)
        )
        applicant_rows = cursor.fetchall()
        for idx, app in enumerate(applicant_rows):
            clg = f" from {app['college']}" if app['college'] else ""
            notifications.append({
                "id": f"notif-ind-app-{idx}",
                "text": f"New candidate: {app['name']}{clg} applied for '{app['title']}'.",
                "tag": "Applicants",
                "type": "success",
                "time": "Recent"
            })

        cursor.execute("SELECT COUNT(DISTINCT student_id) as count FROM student_skill_scores WHERE percentage >= 70")
        verified_count = cursor.fetchone()['count'] or 0
        notifications.append({
            "id": "notif-ind-talent",
            "text": f"{verified_count} verified students have earned >=70% on technical skill assessments in the talent database.",
            "tag": "Talent Pool",
            "type": "info",
            "time": "Live"
        })

        cursor.execute("SELECT COUNT(*) as count FROM postings WHERE industry_id = ?", (user_id,))
        active_posts = cursor.fetchone()['count'] or 0
        notifications.append({
            "id": "notif-ind-posts",
            "text": f"You have {active_posts} active listings live and receiving student applications.",
            "tag": "Postings",
            "type": "info",
            "time": "Status"
        })

    elif role == 'academician':
        cursor.execute(
            """
            SELECT s.name, p.title, a.applied_date
            FROM applications a
            JOIN postings p ON a.posting_id = p.id
            JOIN students s ON a.student_id = s.id
            WHERE p.academician_id = ?
            ORDER BY a.applied_date DESC LIMIT 3
            """,
            (user_id,)
        )
        applicant_rows = cursor.fetchall()
        for idx, app in enumerate(applicant_rows):
            notifications.append({
                "id": f"notif-aca-app-{idx}",
                "text": f"Student {app['name']} applied to collaborate on '{app['title']}'.",
                "tag": "Research",
                "type": "success",
                "time": "Recent"
            })

        notifications.append({
            "id": "notif-aca-status",
            "text": "Academic research and mentorship listings synchronized across regional universities.",
            "tag": "Network",
            "type": "info",
            "time": "Active"
        })

    elif role == 'institute':
        cursor.execute("SELECT COUNT(*) as count FROM students WHERE institute_id = ? AND verification_status = 'pending'", (user_id,))
        pending_count = cursor.fetchone()['count'] or 0

        cursor.execute("SELECT COUNT(*) as count FROM students WHERE institute_id = ? AND verification_status = 'verified'", (user_id,))
        verified_count = cursor.fetchone()['count'] or 0

        cursor.execute("SELECT COUNT(*) as count FROM students WHERE institute_id = ?", (user_id,))
        total_students = cursor.fetchone()['count'] or 0

        if pending_count > 0:
            notifications.append({
                "id": "notif-inst-pending",
                "text": f"{pending_count} student verification request(s) awaiting roll number review in the Verification Portal.",
                "tag": "Pending Action",
                "type": "warning",
                "time": "Urgent"
            })

        notifications.append({
            "id": "notif-inst-verified",
            "text": f"{verified_count} of {total_students} registered students have been officially verified by your institution.",
            "tag": "Verification",
            "type": "success",
            "time": "Overview"
        })

        notifications.append({
            "id": "notif-inst-tpo",
            "text": "Campus Placement Readiness Index updated with latest student skill test scores.",
            "tag": "TPO Analytics",
            "type": "info",
            "time": "Today"
        })

    conn.close()
    return jsonify({'notifications': notifications}), 200
