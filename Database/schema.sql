PRAGMA foreign_keys = ON;

-- 1. Institutes (Universities / Colleges)
CREATE TABLE IF NOT EXISTS institutes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    admin_tpo_contact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Students
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    college TEXT,
    skills TEXT DEFAULT '',
    github_url TEXT,
    leetcode_url TEXT,
    codeforces_url TEXT,
    resume_url TEXT,
    prior_experience TEXT,
    institute_id INTEGER,
    university_roll_no TEXT,
    verification_status TEXT DEFAULT 'unverified' CHECK(verification_status IN ('unverified', 'pending', 'verified', 'rejected')),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institute_id) REFERENCES institutes(id) ON DELETE SET NULL
);

-- 3. Student Documents (Certificates, ID cards, Academic Records)
CREATE TABLE IF NOT EXISTS student_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    document_type TEXT NOT NULL CHECK(document_type IN ('certificate', 'report', 'academic_record', 'student_id_card')),
    file_url TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- 4. Industries (Companies)
CREATE TABLE IF NOT EXISTS industries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Academicians (Faculty / Professors)
CREATE TABLE IF NOT EXISTS academicians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    institute_id INTEGER,
    expertise_domain TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institute_id) REFERENCES institutes(id) ON DELETE SET NULL
);

-- 6. Postings (Job, Internship, Research, Mentorship listings)
CREATE TABLE IF NOT EXISTS postings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_id INTEGER,
    academician_id INTEGER,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT NOT NULL,
    posting_type TEXT NOT NULL CHECK(posting_type IN (
        'internship', 'job', 'certification', 'training', 
        'mentorship', 'project', 'apprenticeship', 'fdp', 
        'research_collaboration'
    )),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (industry_id) REFERENCES industries(id) ON DELETE CASCADE,
    FOREIGN KEY (academician_id) REFERENCES academicians(id) ON DELETE CASCADE
);

-- 7. Applications
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    posting_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'applied' CHECK(status IN ('applied', 'shortlisted', 'rejected', 'selected')),
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, posting_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (posting_id) REFERENCES postings(id) ON DELETE CASCADE
);

-- 8. Student Skill Scores (Verified by AI test)
CREATE TABLE IF NOT EXISTS student_skill_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    percentage REAL NOT NULL,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, skill_name),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- 9. Test Questions Cache (Reusable AI Question Bank)
CREATE TABLE IF NOT EXISTS test_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    question_text TEXT NOT NULL,
    options TEXT NOT NULL,
    correct_answer TEXT NOT NULL
);

-- 10. AI Skill Gap Cache
CREATE TABLE IF NOT EXISTS skill_gap_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    posting_id INTEGER NOT NULL,
    fit_score REAL NOT NULL,
    gap_analysis_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, posting_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (posting_id) REFERENCES postings(id) ON DELETE CASCADE
);

-- 11. AI Course Recommendations Cache
CREATE TABLE IF NOT EXISTS course_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    posting_id INTEGER NOT NULL,
    recommended_courses TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, posting_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (posting_id) REFERENCES postings(id) ON DELETE CASCADE
);

-- 12. Mentorship Feedbacks (Faculty to Student)
CREATE TABLE IF NOT EXISTS mentorship_feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    academician_id INTEGER NOT NULL,
    feedback_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (academician_id) REFERENCES academicians(id) ON DELETE CASCADE
);