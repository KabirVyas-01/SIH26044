from collections import Counter
from flask import Blueprint, request, jsonify, session
from models import get_db
from auth_utils import role_required

institute_bp = Blueprint('institute', __name__, url_prefix='/api/institute')

def row_to_dict(row):
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}

@institute_bp.route('/list', methods=['GET'])
def get_public_institutes_list():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, admin_tpo_contact FROM institutes ORDER BY name ASC")
    institutes = [row_to_dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'institutes': institutes}), 200
@institute_bp.route('/verifications/pending', methods=['GET'])
@role_required('institute')
def get_pending_verifications():
    """List students claiming affiliation with this college awaiting ID verification."""
    institute_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email, college, university_roll_no, verification_status, created_at
        FROM students
        WHERE institute_id = ? AND verification_status IN ('pending', 'unverified')
        ORDER BY created_at ASC
        """,
        (institute_id,)
    )
    pending_students = [row_to_dict(r) for r in cursor.fetchall()]

    # Attach their uploaded ID card documents
    for st in pending_students:
        cursor.execute("SELECT id, document_type, file_url FROM student_documents WHERE student_id = ?", (st['id'],))
        st['documents'] = [row_to_dict(r) for r in cursor.fetchall()]

    conn.close()
    return jsonify({'pending_count': len(pending_students), 'students': pending_students}), 200

@institute_bp.route('/verifications/<int:student_id>', methods=['POST'])
@role_required('institute')
def verify_student(student_id):
    """Approve or reject a student's University ID authenticity."""
    institute_id = session['user_id']
    data = request.get_json() or {}
    new_status = data.get('status', '').strip().lower()

    if new_status not in ('verified', 'rejected'):
        return jsonify({'error': "Status must be 'verified' or 'rejected'."}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, university_roll_no FROM students WHERE id = ? AND institute_id = ?", (student_id, institute_id))
    student = row_to_dict(cursor.fetchone())
    if not student:
        conn.close()
        return jsonify({'error': 'Student not found or not affiliated with your institute.'}), 404

    cursor.execute(
        "UPDATE students SET verification_status = ?, verified_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_status, student_id)
    )
    conn.commit()
    conn.close()

    return jsonify({
        'message': f"Student {student['name']} (Roll: {student.get('university_roll_no')}) has been {new_status}!",
        'student_id': student_id,
        'verification_status': new_status
    }), 200

@institute_bp.route('/dashboard', methods=['GET'])
@role_required('institute')
def get_dashboard():
    institute_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM students WHERE institute_id = ?", (institute_id,))
    total_students = cursor.fetchone()['total']

    # 2. How many are university verified?
    cursor.execute("SELECT COUNT(*) AS verified FROM students WHERE institute_id = ? AND verification_status = 'verified'", (institute_id,))
    verified_students = cursor.fetchone()['verified']

    # 3. Placement statistics across all applications
    cursor.execute(
        """
        SELECT 
            COUNT(a.id) AS total_applications,
            SUM(CASE WHEN a.status = 'selected' THEN 1 ELSE 0 END) AS selected_count,
            SUM(CASE WHEN a.status = 'shortlisted' THEN 1 ELSE 0 END) AS shortlisted_count
        FROM applications a
        JOIN students s ON a.student_id = s.id
        WHERE s.institute_id = ?
        """,
        (institute_id,)
    )
    stats_row = row_to_dict(cursor.fetchone())

    # 4. Average skill score of students who took assessments
    cursor.execute(
        """
        SELECT AVG(sc.percentage) AS avg_score
        FROM student_skill_scores sc
        JOIN students s ON sc.student_id = s.id
        WHERE s.institute_id = ?
        """,
        (institute_id,)
    )
    avg_score_row = cursor.fetchone()
    avg_score = round(avg_score_row['avg_score'], 2) if avg_score_row['avg_score'] is not None else 0.0

    conn.close()

    return jsonify({
        'institute_stats': {
            'enrolled_students': total_students,
            'verified_students': verified_students,
            'average_skill_score': avg_score,
            'total_applications_sent': stats_row.get('total_applications', 0),
            'students_selected_for_jobs': stats_row.get('selected_count', 0),
            'students_shortlisted': stats_row.get('shortlisted_count', 0)
        }
    }), 200

@institute_bp.route('/analytics/skill-demand', methods=['GET'])
@role_required('institute')
def get_skill_demand_analytics():
    """Aggregate required skills from all active industry postings to inform curriculum alterations."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT required_skills FROM postings WHERE industry_id IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()

    skill_counter = Counter()
    for r in rows:
        skills_str = r['required_skills'] or ""
        for s in skills_str.split(','):
            cleaned = s.strip().title()
            if cleaned:
                skill_counter[cleaned] += 1

    top_demanded_skills = [
        {'skill': skill, 'postings_count': count}
        for skill, count in skill_counter.most_common(10)
    ]

    return jsonify({
        'message': 'Industry skill demand trend analytics generated!',
        'top_in_demand_skills': top_demanded_skills
    }), 200