from functools import wraps
from flask import session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
  return generate_password_hash(password)

def verify_password(stored_hash, password):
  return check_password_hash(stored_hash, password)

def set_user_session(user_id, role, email, name):
  session['user_id']=user_id
  session['role']=role
  session['email']=email
  session['name']=name
  session.permanent=True

def clear_user_session():
  session.clear()

def get_current_user():
  if 'user_id' in session and 'role' in session:
    return{
      'user_id': session['user_id'], 'role': session['role'], 'email':session.get('email'), 'name': session.get('name')
    }
  return None

def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if 'user_id' not in session or 'role' not in session:
      return jsonify({'error':'Authentication required. Please log in.'}),401
    return f(*args, **kwargs)
  return decorated_function

def role_required(*allowed_roles):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      if 'user_id' not in session or 'role' not in session:
        return jsonify({'error':'Authentication required. Please log in.'}), 401
      current_role=session.get('role')
      if current_role not in allowed_roles:
        return jsonify({'error':f'Access denied. Required role in {list(allowed_roles)}, but you are a {current_role}.'}), 403
      return f(*args, **kwargs)
    return decorated_function
  return decorator