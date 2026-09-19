from flask import Blueprint, request, jsonify, session
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

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required.'}), 400

    # Scramble the password using our security blender!
    pwd_hash = hash_password(password)

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO students (name, email, password_hash, college, skills, university_roll_no)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, email, pwd_hash, college, skills, university_roll_no)
        )
        conn.commit()
        student_id = cursor.lastrowid

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
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'A student with this email already exists.'}), 409
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

    # Check if user exists AND if password hash matches!
    if not student or not verify_password(student['password_hash'], password):
        return jsonify({'error': 'Invalid email or password.'}), 401

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
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'An industry account with this email already exists.'}), 409
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
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'An institute with this email already exists.'}), 409
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
    try:
        cursor.execute(
            "INSERT INTO academicians (name, email, password_hash, institute_id, expertise_domain) VALUES (?, ?, ?, ?, ?)",
            (name, email, pwd_hash, institute_id, expertise_domain)
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
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'An academician with this email already exists.'}), 409
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