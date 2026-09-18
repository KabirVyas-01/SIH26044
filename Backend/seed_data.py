import json
from config import Config
from models import init_db, get_db
from auth_utils import hash_password

def seed():
    print("[Seed] Initializing database tables...")
    init_db()

    conn = get_db()
    cursor = conn.cursor()
    default_pw = hash_password("Password123!")

    cursor.execute(
        """
        INSERT OR IGNORE INTO institutes (name, email, password_hash, admin_tpo_contact)
        VALUES (?, ?, ?, ?)
        """,
        ("The Maharaja Sayajirao University of Baroda", "tnp@msu.edu", default_pw, "+91-9876543210 (Head TNP)")
    )
    cursor.execute("SELECT id FROM institutes WHERE email = 'tnp@msu.edu'")
    inst_id = cursor.fetchone()["id"]

    cursor.execute(
        """
        INSERT OR IGNORE INTO academicians (name, email, password_hash, institute_id, expertise_domain)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("xyz", "xyz@msu.edu", default_pw, inst_id, "Data Science")
    )
    cursor.execute("SELECT id FROM academicians WHERE email = 'xyz@msu.edu'")
    acad_id = cursor.fetchone()["id"]

    cursor.execute(
        """
        INSERT OR IGNORE INTO industries (company_name, email, password_hash)
        VALUES (?, ?, ?)
        """,
        ("Adora Technologies", "recruitment@adoratech.io", default_pw)
    )
    cursor.execute("SELECT id FROM industries WHERE email = 'recruitment@adoratech.io'")
    ind_id = cursor.fetchone()["id"]

    # 4. Seed Verified Student (Aditi)
    cursor.execute(
        """
        INSERT OR IGNORE INTO students (
            name, email, password_hash, college, skills, 
            github_url, university_roll_no, verification_status, verified_at, institute_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'verified', CURRENT_TIMESTAMP, ?)
        """,
        (
            "Kareena", "kareena@college.edu", default_pw, 
            "The Maharaja Sayajirao University of Baroda", "Python, Flask, SQLite, Data Structures",
            "https://github.com/kareena", "MSU-2026-CS-001", inst_id
        )
    )
    cursor.execute("SELECT id FROM students WHERE email = 'kareena@college.edu'")
    student_id = cursor.fetchone()["id"]

    cursor.execute(
        "INSERT OR IGNORE INTO student_skill_scores (student_id, skill_name, percentage) VALUES (?, ?, ?)",
        (student_id, "Python", 90.0)
    )
    cursor.execute(
        "INSERT OR IGNORE INTO student_skill_scores (student_id, skill_name, percentage) VALUES (?, ?, ?)",
        (student_id, "Sql", 85.0)
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO postings (industry_id, title, description, required_skills, posting_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            ind_id,
            "Backend Engineer Intern (Python/API)",
            "Build scalable RESTful API microservices using Python, Flask, and SQLite databases.",
            "Python, Flask, SQL, REST APIs",
            "internship"
        )
    )
    cursor.execute("SELECT id FROM postings WHERE title = 'Backend Engineer Intern (Python/API)'")
    job_id = cursor.fetchone()["id"]

    cursor.execute(
        """
        INSERT OR IGNORE INTO postings (academician_id, title, description, required_skills, posting_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            acad_id,
            "Undergraduate Research Assistant - Cloud Consensus",
            "Investigating scalable distributed consensus protocols across edge cloud networks.",
            "Python, Distributed Systems, Linux",
            "research_collaboration"
        )
    )

    cursor.execute(
        "INSERT OR IGNORE INTO applications (student_id, posting_id, status) VALUES (?, ?, 'shortlisted')",
        (student_id, job_id)
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO mentorship_feedbacks (student_id, academician_id, feedback_text)
        VALUES (?, ?, ?)
        """,
        (student_id, acad_id, "Kareena demonstrated exceptional grasp of database schemas and REST API design. Highly recommended for backend roles!")
    )

    # 9. Seed AI Semantic Gap Cache & Recommendations
    cursor.execute(
        """
        INSERT OR IGNORE INTO skill_gap_cache (student_id, posting_id, fit_score, gap_analysis_text)
        VALUES (?, ?, ?, ?)
        """,
        (
            student_id, job_id, 88.5,
            "Strong 90% verified Python and 85% SQL foundation aligns directly with backend requirements. Recommendation: Add containerization (Docker) to reach 95%+ readiness."
        )
    )

    courses_sample = json.dumps([
        {"title": "Docker & Kubernetes Architecture", "platform": "Coursera", "difficulty": "Intermediate"},
        {"title": "Advanced SQL & Indexing Internals", "platform": "NPTEL", "difficulty": "Advanced"}
    ])
    cursor.execute(
        """
        INSERT OR IGNORE INTO course_recommendations (student_id, posting_id, recommended_courses)
        VALUES (?, ?, ?)
        """,
        (student_id, job_id, courses_sample)
    )

    conn.commit()
    conn.close()

    print("\n[Seed] Successfully populated realistic mock data!")
    print("=" * 65)
    print("Ready-to-Test Demo Credentials (Password for all: 'Password123!'):")
    print("1.Student (Verified):    kareena@college.edu")
    print("2.Industry Partner:      recruitment@adoratech.io")
    print("3.Faculty Professor:     xyz@msu.edu")
    print("4.College TPO Admin:     tnp@msu.edu")
    print("=" * 65)

if __name__ == '__main__':
    seed()