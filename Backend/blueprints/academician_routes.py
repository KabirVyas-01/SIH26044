from flask import Blueprint, request, jsonify, session
from models import get_db
from auth_utils import role_required

academician_bp = Blueprint('academician', __name__, url_prefix='/api/academician')

ALLOWED_ACADEMIC_POSTING_TYPES = {
    'research_collaboration', 'fdp', 'project', 'mentorship',
    'internship', 'opportunity', 'research', 'fellowship', 'research_assistantship'
}

def row_to_dict(row):
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}

@academician_bp.route('/postings', methods=['POST'])
@role_required('academician')
def create_posting():
    academician_id = session['user_id']
    data = request.get_json() or {}

    title = data.get('title', '').strip() or data.get('opportunity_title', '').strip()
    description = data.get('description', '').strip() or 'Research and academic project opportunity for students.'
    required_skills = data.get('required_skills', '').strip() or data.get('skills', '').strip() or 'Research, Problem Solving'
    posting_type = data.get('posting_type', '').strip().lower()

    if not title:
        return jsonify({'error': 'Opportunity title is required.'}), 400

    if not posting_type or posting_type not in ALLOWED_ACADEMIC_POSTING_TYPES:
        posting_type = 'project'

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO postings (academician_id, title, description, required_skills, posting_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (academician_id, title, description, required_skills, posting_type)
    )
    conn.commit()
    posting_id = cursor.lastrowid
    conn.close()

    return jsonify({
        'message': 'Academic opportunity posted successfully!',
        'posting': {'id': posting_id, 'title': title, 'posting_type': posting_type}
    }), 201

@academician_bp.route('/postings', methods=['GET'])
@role_required('academician')
def list_my_postings():
    academician_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT p.id, p.title, p.description, p.required_skills, p.posting_type, p.created_at,
COUNT(a.id) AS total_applicants
        FROM postings p
        LEFT JOIN applications a ON p.id = a.posting_id
        WHERE p.academician_id = ?
        GROUP BY p.id
        ORDER BY p.created_at DESC
        """,
        (academician_id,)
    )
    postings = [row_to_dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify({'postings': postings}), 200

@academician_bp.route('/students/<int:student_id>/feedback', methods=['POST'])
@role_required('academician')
def give_mentorship_feedback(student_id):
    academician_id = session['user_id']
    data = request.get_json() or {}
    feedback_text = data.get('feedback_text', '').strip()

    if not feedback_text:
        return jsonify({'error': 'feedback_text is required.'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM students WHERE id = ?", (student_id,))
    student = row_to_dict(cursor.fetchone())
    if not student:
        conn.close()
        return jsonify({'error': 'Student not found.'}), 404

    cursor.execute(
        """
        INSERT INTO mentorship_feedbacks (student_id, academician_id, feedback_text)
        VALUES (?, ?, ?)
        """,
        (student_id, academician_id, feedback_text)
    )
    conn.commit()
    feedback_id = cursor.lastrowid
    conn.close()

    return jsonify({
        'message': f"Mentorship feedback sent to {student['name']}!",
        'feedback_id': feedback_id
    }), 201

@academician_bp.route('/feedbacks', methods=['GET'])
@role_required('academician')
def list_my_feedbacks():
    academician_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT mf.id, mf.feedback_text, mf.created_at,
s.id AS student_id, s.name AS student_name, s.email AS student_email, s.college
        FROM mentorship_feedbacks mf
        JOIN students s ON mf.student_id = s.id
        WHERE mf.academician_id = ?
        ORDER BY mf.created_at DESC
        """,
        (academician_id,)
    )
    feedbacks = [row_to_dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify({'feedbacks': feedbacks}), 200