import json
from flask import Blueprint, request, jsonify, session
from models import get_db
from auth_utils import role_required
from gemini_service import gemini_service

student_bp = Blueprint('student', __name__, url_prefix='/api/student')

ALLOWED_DOC_TYPES = {'certificate', 'report', 'academic_record', 'student_id_card'}

def row_to_dict(row):
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}

@student_bp.route('/profile', methods=['GET'])
@role_required('student')
def get_profile():
    student_id = session['user_id']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, email, college, skills, github_url, leetcode_url, 
        codeforces_url, resume_url, prior_experience, university_roll_no, 
        verification_status, verified_at, created_at, institute_id,
        resume_score, resume_review, resume_text, desired_role
        FROM students 
        WHERE id = ?
        """,
        (student_id,)
    )
    profile = row_to_dict(cursor.fetchone())
    cursor.execute("SELECT id, document_type, file_url, uploaded_at FROM student_documents WHERE student_id = ?", (student_id,))
    documents = [row_to_dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT skill_name, percentage, assessed_at FROM student_skill_scores WHERE student_id = ?", (student_id,))
    skills = [row_to_dict(r) for r in cursor.fetchall()]

    conn.close()

    if profile:
        profile['is_verified'] = (profile.get('verification_status') == 'verified')
        profile['documents'] = documents
        profile['verified_skills'] = skills
        if profile.get('resume_review'):
            try:
                profile['resume_review_parsed'] = json.loads(profile['resume_review'])
            except Exception:
                profile['resume_review_parsed'] = None
        else:
            profile['resume_review_parsed'] = None

    return jsonify({'profile': profile}), 200

@student_bp.route('/profile', methods=['PUT'])
@role_required('student')
def update_profile():
    student_id = session['user_id']
    data = request.get_json() or {}
    fields = ['college', 'skills', 'github_url', 'leetcode_url', 'codeforces_url', 'resume_url', 'prior_experience', 'university_roll_no', 'institute_id', 'desired_role']
    updates = {}
    for f in fields:
        if f in data:
            updates[f] = data[f]

    if not updates:
        return jsonify({'message': 'No profile changes provided.'}), 200
    set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values()) + [student_id]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE students SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()

    return jsonify({'message': 'Profile updated successfully!', 'updated': updates}), 200

@student_bp.route('/documents', methods=['POST'])
@role_required('student')
def upload_document():
    student_id = session['user_id']
    data = request.get_json() or {}
    doc_type = data.get('document_type', '').strip().lower()
    file_url = data.get('file_url', '').strip()

    if not doc_type or not file_url:
        return jsonify({'error': 'document_type and file_url are required.'}), 400

    if doc_type not in ALLOWED_DOC_TYPES:
        return jsonify({'error': f'Invalid type! Allowed: {list(ALLOWED_DOC_TYPES)}'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO student_documents (student_id, document_type, file_url) VALUES (?, ?, ?)",
        (student_id, doc_type, file_url)
    )
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()

    return jsonify({
        'message': 'Document uploaded successfully!',
        'document': {'id': doc_id, 'document_type': doc_type, 'file_url': file_url}
    }), 201

@student_bp.route('/postings', methods=['GET'])
@role_required('student')
def browse_postings():
    """Look at all opportunities using an SQL JOIN to fetch company and professor names!"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.id, p.title, p.description, p.required_skills, p.posting_type, p.created_at,
        ind.company_name AS company,
        aca.name AS professor
        FROM postings p
        LEFT JOIN industries ind ON p.industry_id = ind.id
        LEFT JOIN academicians aca ON p.academician_id = aca.id
        ORDER BY p.created_at DESC
        """
    )
    postings = [row_to_dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify({'postings': postings}), 200

@student_bp.route('/postings/<int:posting_id>/apply', methods=['POST'])
@role_required('student')
def apply_to_posting(posting_id):
    student_id = session['user_id']

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO applications (student_id, posting_id, status) VALUES (?, ?, 'applied')",
            (student_id, posting_id)
        )
        conn.commit()
        app_id = cursor.lastrowid
        return jsonify({'message': 'Application submitted successfully!', 'application_id': app_id}), 201
    except Exception as e:
        conn.rollback()
        if 'UNIQUE constraint failed' in str(e):
            cursor.execute("SELECT id FROM applications WHERE student_id = ? AND posting_id = ?", (student_id, posting_id))
            row = cursor.fetchone()
            existing_id = row['id'] if row else 0
            return jsonify({'message': 'Application submitted successfully!', 'application_id': existing_id}), 200
        return jsonify({'error': 'Failed to apply.'}), 500
    finally:
        conn.close()

@student_bp.route('/applications', methods=['GET'])
@role_required('student')
def view_my_applications():
    student_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.id, a.status, a.applied_date,
        p.title, p.posting_type, p.description, p.required_skills,
        COALESCE(ind.company_name, aca.name, 'Academic / Partner Host') AS company_name,
        aca.name AS professor_name
        FROM applications a
        JOIN postings p ON a.posting_id = p.id
        LEFT JOIN industries ind ON p.industry_id = ind.id
        LEFT JOIN academicians aca ON p.academician_id = aca.id
        WHERE a.student_id = ?
        ORDER BY a.applied_date DESC
        """,
        (student_id,)
    )
    apps = [row_to_dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify({'my_applications': apps}), 200

@student_bp.route('/assessments/<skill_name>/questions', methods=['GET'])
@role_required('student')
def get_skill_questions(skill_name):
    """Fetches cached or AI-generated questions (with correct answer hidden so students can't cheat!)."""
    level = request.args.get('level', 'intermediate').strip().lower()
    try:
        count = int(request.args.get('count', 10))
    except (ValueError, TypeError):
        count = 10
    questions = gemini_service.get_or_generate_questions(skill_name, count=count, level=level)
    
    sanitized = []
    for q in questions:
        sanitized.append({
            'id': q['id'],
            'skill_name': q['skill_name'],
            'question_text': q['question_text'],
            'options': q['options']
        })
    return jsonify({'skill': skill_name, 'level': level, 'questions': sanitized}), 200

@student_bp.route('/assessments/<skill_name>/submit', methods=['POST'])
@role_required('student')
def submit_skill_test(skill_name):
    """Grades student test answers, assigns verified score percentage, and stores in SQLite!"""
    student_id = session['user_id']
    data = request.get_json() or {}
    answers = data.get('answers', {})
    total_questions = data.get('total_questions', 10)

    result = gemini_service.grade_assessment(student_id, skill_name, answers, total_questions=total_questions)
    return jsonify({'message': f"Assessment for {skill_name} completed!", 'result': result}), 200

@student_bp.route('/postings/<int:posting_id>/fit-score', methods=['GET'])
@role_required('student')
def get_job_fit_score(posting_id):
    """Returns AI semantic alignment score and gap analysis for this opportunity."""
    student_id = session['user_id']
    result = gemini_service.get_or_generate_fit_score(student_id, posting_id)
    return jsonify(result), 200

@student_bp.route('/postings/<int:posting_id>/recommendations', methods=['GET'])
@role_required('student')
def get_job_course_recommendations(posting_id):
    """Returns targeted courses to bridge skill gaps."""
    student_id = session['user_id']
    result = gemini_service.get_or_generate_courses(student_id, posting_id)
    return jsonify(result), 200

# =========================================================================
# AI TOOLS ENDPOINTS
# =========================================================================

@student_bp.route('/ai/resume-analyzer', methods=['POST'])
@role_required('student')
def ai_resume_analyzer():
    student_id = session['user_id']
    data = request.get_json() or {}
    resume_text = data.get('resume_text', '').strip()
    target_role = data.get('target_role', 'Software Engineer').strip()
    if not resume_text:
        return jsonify({'error': 'Please provide resume text or skills to analyze.'}), 400

    result = gemini_service.analyze_resume(resume_text, target_role)
    ats_score = float(result.get('ats_score', 7.5))

    # Persist score, review JSON, resume text, and desired role into SQLite
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE students
        SET resume_score = ?,
            resume_review = ?,
            resume_text = ?,
            desired_role = ?
        WHERE id = ?
        """,
        (ats_score, json.dumps(result), resume_text, target_role, student_id)
    )
    conn.commit()
    conn.close()

    return jsonify(result), 200

@student_bp.route('/ai/roadmap-generator', methods=['POST'])
@role_required('student')
def ai_roadmap_generator():
    data = request.get_json() or {}
    target_role = data.get('target_role', 'Full Stack Developer').strip()
    level = data.get('level', 'intermediate').strip()
    try:
        duration_weeks = int(data.get('duration_weeks', 4))
    except (ValueError, TypeError):
        duration_weeks = 4
    current_skills = data.get('current_skills', '').strip()

    roadmap = gemini_service.generate_career_roadmap(
        target_role=target_role,
        level=level,
        duration_weeks=duration_weeks,
        current_skills=current_skills
    )
    return jsonify({
        'target_role': target_role,
        'level': level,
        'duration_weeks': len(roadmap),
        'overview': f"Personalized {len(roadmap)}-week curriculum tailored for {target_role} ({level.capitalize()} track).",
        'roadmap': roadmap
    }), 200

@student_bp.route('/ai/interview-prep', methods=['POST'])
@role_required('student')
def ai_interview_prep():
    data = request.get_json() or {}
    skill = data.get('skill', 'Python').strip()
    level = data.get('level', 'intermediate').strip()
    round_type = data.get('round_type', 'technical').strip()

    questions = gemini_service.generate_mock_interview(
        skill_name=skill,
        level=level,
        round_type=round_type
    )
    return jsonify({
        'skill': skill,
        'level': level,
        'round_type': round_type,
        'questions': questions
    }), 200