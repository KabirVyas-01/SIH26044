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