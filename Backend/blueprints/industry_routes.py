from flask import Blueprint, request, jsonify, session
from models import get_db
from auth_utils import role_required

industry_bp = Blueprint('industry', __name__, url_prefix='/api/industry')

ALLOWED_POSTING_TYPES = {'job', 'internship', 'project', 'apprenticeship', 'certification', 'training'}

def row_to_dict(row):
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}

@industry_bp.route('/postings', methods=['POST'])
@role_required('industry')
def create_posting():
    industry_id = session['user_id']
    data = request.get_json() or {}

    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    required_skills = data.get('required_skills', '').strip()
    posting_type = data.get('posting_type', '').strip().lower()

    if not title or not description or not required_skills or not posting_type:
        return jsonify({'error': 'title, description, required_skills, and posting_type are required.'}), 400

    if posting_type not in ALLOWED_POSTING_TYPES:
        return jsonify({'error': f'Invalid posting_type. Allowed: {list(ALLOWED_POSTING_TYPES)}'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO postings (industry_id, title, description, required_skills, posting_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (industry_id, title, description, required_skills, posting_type)
    )
    conn.commit()
    posting_id = cursor.lastrowid
    conn.close()

    return jsonify({
        'message': 'Opportunity posted successfully!',
        'posting': {
            'id': posting_id,
            'title': title,
            'posting_type': posting_type,
            'required_skills': required_skills
        }
    }), 201

@industry_bp.route('/postings', methods=['GET'])
@role_required('industry')
def list_my_postings():
    industry_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT p.id, p.title, p.description, p.required_skills, p.posting_type, p.created_at,
        COUNT(a.id) AS total_applicants
        FROM postings p
        LEFT JOIN applications a ON p.id = a.posting_id
        WHERE p.industry_id = ?
        GROUP BY p.id
        ORDER BY p.created_at DESC
        """,
        (industry_id,)
    )
    postings = [row_to_dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify({'postings': postings}), 200


@industry_bp.route('/postings/<int:posting_id>/applicants', methods=['GET'])
@role_required('industry')
def get_applicants(posting_id):
    industry_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title FROM postings WHERE id = ? AND industry_id = ?", (posting_id, industry_id))
    posting = row_to_dict(cursor.fetchone())
    if not posting:
        conn.close()
        return jsonify({'error': 'Posting not found or unauthorized.'}), 404

    cursor.execute(
        """
        SELECT a.id AS application_id, a.status, a.applied_date,
        s.id AS student_id, s.name, s.email, s.college, s.skills,
        s.github_url, s.leetcode_url, s.resume_url, s.university_roll_no,
        s.verification_status
        FROM applications a
        JOIN students s ON a.student_id = s.id
        WHERE a.posting_id = ?
        ORDER BY a.applied_date DESC
        """,
        (posting_id,)
    )
    applicants = [row_to_dict(r) for r in cursor.fetchall()]

    for app in applicants:
        s_id = app['student_id']
        app['is_university_verified'] = (app.get('verification_status') == 'verified')

        
        cursor.execute("SELECT skill_name, percentage FROM student_skill_scores WHERE student_id = ?", (s_id,))
        app['verified_skills'] = [row_to_dict(r) for r in cursor.fetchall()]

        
        cursor.execute("SELECT document_type, file_url FROM student_documents WHERE student_id = ?", (s_id,))
        app['documents'] = [row_to_dict(r) for r in cursor.fetchall()]

    conn.close()

    return jsonify({
        'posting': posting,
        'applicant_count': len(applicants),
        'applicants': applicants
    }), 200

@industry_bp.route('/applications/<int:application_id>/status', methods=['PATCH'])
@role_required('industry')
def update_applicant_status(application_id):
    industry_id = session['user_id']
    data = request.get_json() or {}
    new_status = data.get('status', '').strip().lower()

    if new_status not in ('shortlisted', 'rejected', 'selected'):
        return jsonify({'error': "Status must be 'shortlisted', 'rejected', or 'selected'."}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT a.id 
        FROM applications a
        JOIN postings p ON a.posting_id = p.id
        WHERE a.id = ? AND p.industry_id = ?
        """,
        (application_id, industry_id)
    )
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Application not found or unauthorized.'}), 404

    cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, application_id))
    conn.commit()
    conn.close()

    return jsonify({
        'message': f"Applicant status updated to '{new_status}'!",
        'application_id': application_id,
        'new_status': new_status
    }), 200