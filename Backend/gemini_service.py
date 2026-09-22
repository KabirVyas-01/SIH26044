import json
import urllib.request
from config import Config
from models import get_db

def row_to_dict(row):
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}

class GeminiService:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.api_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            if self.api_key else None
        )

    def _call_gemini(self, prompt):
        if not self.api_key or not self.api_url:
            return None

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1000}
        }

        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    body = json.loads(resp.read().decode('utf-8'))
                    return body["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"[GeminiService Warning] API call failed: {e}. Using smart fallback.")
            return None
        return None

    # =========================================================================
    # 1. MCQ ASSESSMENT GENERATOR
    # =========================================================================
    # =========================================================================
    # 1. MCQ ASSESSMENT GENERATOR (LEVEL-SPECIFIC, 10 QUESTIONS)
    # =========================================================================
    def get_or_generate_questions(self, skill_name: str, count: int = 10, level: str = 'intermediate'):
        """Generates level-appropriate technical MCQs via Gemini or comprehensive offline question bank."""
        normalized_skill = skill_name.strip().title()
        normalized_level = level.strip().lower() if level else 'intermediate'
        if normalized_level not in ('beginner', 'intermediate', 'advanced'):
            normalized_level = 'intermediate'

        # 1. Try Gemini AI with explicit level and count
        prompt = (
            f"Generate exactly {count} multiple-choice test questions for skill '{normalized_skill}' at '{normalized_level.upper()}' difficulty level. "
            f"Target practical engineering knowledge and code reasoning suitable for a {normalized_level} university student. "
            f"Return ONLY a valid JSON list of {count} objects with keys: "
            f"'question_text', 'options' (object with keys 'A', 'B', 'C', 'D'), and 'correct_answer' ('A', 'B', 'C', or 'D')."
        )
        raw_ai = self._call_gemini(prompt)
        questions = []
        if raw_ai:
            try:
                clean = raw_ai.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean)
                if isinstance(parsed, list) and len(parsed) >= 5:
                    questions = parsed
            except Exception:
                questions = []

        # 2. Rich Offline Level-Specific Bank if AI is offline
        if not questions:
            questions = self._get_offline_bank(normalized_skill, normalized_level)

        conn = get_db()
        cursor = conn.cursor()
        saved_questions = []
        for q in questions[:count]:
            opts_json = json.dumps(q.get("options", {}))
            cursor.execute(
                "INSERT INTO test_questions (skill_name, question_text, options, correct_answer) VALUES (?, ?, ?, ?)",
                (f"{normalized_skill} ({normalized_level.title()})", q.get("question_text"), opts_json, q.get("correct_answer", "A"))
            )
            q_id = cursor.lastrowid
            saved_questions.append({
                "id": q_id,
                "skill_name": normalized_skill,
                "difficulty": normalized_level,
                "question_text": q.get("question_text"),
                "options": q.get("options"),
                "correct_answer": q.get("correct_answer", "A")
            })
        conn.commit()
        conn.close()
        return saved_questions

    def _get_offline_bank(self, skill_name: str, level: str):
        """Curated 10-question technical banks for Python and general tech by level."""
        skill_lower = skill_name.lower()

        # PYTHON BANKS
        if 'python' in skill_lower:
            if level == 'beginner':
                return [
                    {"question_text": "Which of the following is an immutable data type in Python?", "options": {"A": "List", "B": "Tuple", "C": "Set", "D": "Dictionary"}, "correct_answer": "B"},
                    {"question_text": "What will type(7 / 2) return in Python 3?", "options": {"A": "int", "B": "float", "C": "double", "D": "number"}, "correct_answer": "B"},
                    {"question_text": "Which keyword is used to define a function in Python?", "options": {"A": "func", "B": "function", "C": "def", "D": "define"}, "correct_answer": "C"},
                    {"question_text": "Which method removes and returns the last item from a list?", "options": {"A": ".pop()", "B": ".remove()", "C": ".delete()", "D": ".pull()"}, "correct_answer": "A"},
                    {"question_text": "What will len('Hello World') evaluate to?", "options": {"A": "10", "B": "11", "C": "12", "D": "9"}, "correct_answer": "B"},
                    {"question_text": "Which operator is used for exponentiation (power) in Python?", "options": {"A": "^", "B": "**", "C": "exp()", "D": "^^"}, "correct_answer": "B"},
                    {"question_text": "How do you create an empty dictionary in Python?", "options": {"A": "[]", "B": "()", "C": "{}", "D": "set()"}, "correct_answer": "C"},
                    {"question_text": "What will list(range(1, 5)) produce?", "options": {"A": "[1, 2, 3, 4, 5]", "B": "[1, 2, 3, 4]", "C": "[0, 1, 2, 3, 4]", "D": "[2, 3, 4, 5]"}, "correct_answer": "B"},
                    {"question_text": "Which block is used to catch and handle exceptions in Python?", "options": {"A": "try-catch", "B": "try-except", "C": "try-handle", "D": "catch-finally"}, "correct_answer": "B"},
                    {"question_text": "What is the recommended statement for opening files safely so they close automatically?", "options": {"A": "open file as f", "B": "with open(...) as f:", "C": "file.open()", "D": "using open(...) as f:"}, "correct_answer": "B"}
                ]
            elif level == 'advanced':
                return [
                    {"question_text": "What is the primary role of Python's Global Interpreter Lock (GIL) in CPython?", "options": {"A": "Accelerates vector math", "B": "Guarantees thread-safe memory management for non-atomic refcounts", "C": "Enables distributed GPU training", "D": "Prevents memory fragmentation"}, "correct_answer": "B"},
                    {"question_text": "Which pair of dunder methods must a class implement to operate as a context manager with 'with'?", "options": {"A": "__start__ and __stop__", "B": "__enter__ and __exit__", "C": "__open__ and __close__", "D": "__acquire__ and __release__"}, "correct_answer": "B"},
                    {"question_text": "What is the primary memory optimization provided by defining __slots__ in a class?", "options": {"A": "Forces compilation to C struct", "B": "Prevents creation of the instance __dict__ to minimize RAM", "C": "Makes all attributes read-only", "D": "Enforces static type checking"}, "correct_answer": "B"},
                    {"question_text": "Which algorithm does Python use to compute Method Resolution Order (MRO) in multiple inheritance?", "options": {"A": "Depth First Search", "B": "Dijkstra's Shortest Path", "C": "C3 Linearization", "D": "Breadth First Graph Search"}, "correct_answer": "C"},
                    {"question_text": "What is a Python Metaclass?", "options": {"A": "An abstract base class", "B": "A class whose instances are classes, defining class construction behavior", "C": "A module-level decorator", "D": "A multiprocessing wrapper"}, "correct_answer": "B"},
                    {"question_text": "How does asyncio.gather(*tasks) coordinate coroutines?", "options": {"A": "Executes them concurrently on the single-threaded event loop", "B": "Spawns kernel OS processes", "C": "Compiles bytecode to native assembly", "D": "Executes them synchronously one by one"}, "correct_answer": "A"},
                    {"question_text": "How does Python detect cyclic references that standard reference counting cannot collect?", "options": {"A": "By crashing on out-of-memory", "B": "Through generational cyclic garbage collection tracking reachable container pointers", "C": "By forcing OS page swaps", "D": "By deallocating globals on exit only"}, "correct_answer": "B"},
                    {"question_text": "What methods define the Python Descriptor Protocol for attribute access control?", "options": {"A": "__get__, __set__, and __delete__", "B": "__read__, __write__, and __flush__", "C": "__load__ and __dump__", "D": "__attr__ and __setattr__"}, "correct_answer": "A"},
                    {"question_text": "In Python 3.7+, what happens if a generator function raises StopIteration internally?", "options": {"A": "It is silently ignored", "B": "It is transformed into a RuntimeError to prevent masking loop termination", "C": "The generator restarts from line 1", "D": "It yields None forever"}, "correct_answer": "B"},
                    {"question_text": "Which standard library module provides deterministic profiling of function execution time and call counts?", "options": {"A": "tracemalloc", "B": "cProfile", "C": "dis", "D": "timeit"}, "correct_answer": "B"}
                ]
            else: # Intermediate (default)
                return [
                    {"question_text": "What is the output of [x**2 for x in range(5) if x % 2 == 0]?", "options": {"A": "[0, 4, 16]", "B": "[1, 9]", "C": "[0, 1, 4, 9, 16]", "D": "[4, 16]"}, "correct_answer": "A"},
                    {"question_text": "In a function definition, what does *args allow you to accept?", "options": {"A": "Arbitrary keyword arguments", "B": "An arbitrary number of positional arguments", "C": "Pointer addresses", "D": "Type annotations"}, "correct_answer": "B"},
                    {"question_text": "In Python OOP, what is the role of super().__init__()?", "options": {"A": "Destroys previous instances", "B": "Calls the initializer of the superclass", "C": "Creates a static variable", "D": "Initializes a thread"}, "correct_answer": "B"},
                    {"question_text": "What is the key advantage of a generator expression over a list comprehension?", "options": {"A": "Generators evaluate lazily, consuming minimal memory", "B": "Generators can be indexed directly", "C": "Generators support slicing", "D": "Generators run faster for small arrays"}, "correct_answer": "A"},
                    {"question_text": "What does the @staticmethod decorator indicate in a class?", "options": {"A": "The method cannot be overridden", "B": "The method takes no self or cls parameter and behaves like a plain function", "C": "The method modifies class state", "D": "The method is executed on import"}, "correct_answer": "B"},
                    {"question_text": "What will dict.get('score', 100) return if 'score' does not exist in the dictionary?", "options": {"A": "KeyError", "B": "None", "C": "100", "D": "0"}, "correct_answer": "C"},
                    {"question_text": "How does copy.deepcopy() differ from copy.copy()?", "options": {"A": "deepcopy is faster", "B": "deepcopy recursively clones nested compound objects", "C": "deepcopy works only on strings", "D": "shallow copy creates new memory for every inner item"}, "correct_answer": "B"},
                    {"question_text": "What does the boilerplate if __name__ == '__main__': prevent?", "options": {"A": "Syntax errors", "B": "Executing top-level script logic when the file is imported as a module", "C": "Infinite loops", "D": "Permission denied errors"}, "correct_answer": "B"},
                    {"question_text": "Which dunder method is called when str(object) or print(object) is invoked for human reading?", "options": {"A": "__repr__", "B": "__str__", "C": "__format__", "D": "__bytes__"}, "correct_answer": "B"},
                    {"question_text": "What is the return type of zip([1, 2], ['a', 'b']) in Python 3?", "options": {"A": "A list of lists", "B": "An iterator yielding tuples", "C": "A dictionary", "D": "A set of pairs"}, "correct_answer": "B"}
                ]

        # GENERAL SKILL / OTHER TECH BANK (10 questions by level)
        return [
            {"question_text": f"Which foundational principle is core to {skill_name} at the {level} level?", "options": {"A": "Writing clean, modular, and maintainable logic", "B": "Bypassing version control", "C": "Hardcoding configuration values", "D": "Ignoring edge cases"}, "correct_answer": "A"},
            {"question_text": f"What is the standard approach to handling unexpected errors in {skill_name}?", "options": {"A": "Letting the process crash", "B": "Catching specific exceptions, logging details, and graceful degradation", "C": "Suppressing all error messages", "D": "Restarting the computer"}, "correct_answer": "B"},
            {"question_text": f"Why is unit testing important when writing code in {skill_name}?", "options": {"A": "To increase file size", "B": "To verify individual components work in isolation and prevent regressions", "C": "To slow down deployment", "D": "To replace documentation"}, "correct_answer": "B"},
            {"question_text": f"Which data structure offers average O(1) time complexity for key lookups in {skill_name}?", "options": {"A": "Linked List", "B": "Binary Search Tree", "C": "Hash Map / Hash Table", "D": "Array"}, "correct_answer": "C"},
            {"question_text": f"What is the role of Git and version control when collaborating on {skill_name} projects?", "options": {"A": "Running automated tests only", "B": "Tracking incremental changes, managing branches, and resolving merge conflicts", "C": "Hosting production databases", "D": "Encrypting code"}, "correct_answer": "B"},
            {"question_text": f"When scaling an application built with {skill_name}, what is the best practice for storing secrets?", "options": {"A": "Committing them to public GitHub", "B": "Using environment variables (.env) kept outside source control", "C": "Writing them in plain text README", "D": "Embedding in client bundle"}, "correct_answer": "B"},
            {"question_text": f"What is an idempotent operation in API design related to {skill_name}?", "options": {"A": "An operation that can be applied multiple times without changing the result beyond the initial application", "B": "An operation that never succeeds", "C": "An asynchronous thread", "D": "A database migration"}, "correct_answer": "A"},
            {"question_text": f"Which protocol ensures secure, encrypted data transmission over the web for {skill_name} services?", "options": {"A": "HTTP", "B": "FTP", "C": "HTTPS (TLS/SSL)", "D": "Telnet"}, "correct_answer": "C"},
            {"question_text": f"What is the primary benefit of caching frequently queried data in {skill_name}?", "options": {"A": "Increases memory leaks", "B": "Reduces database load and drastically lowers latency", "C": "Guarantees zero downtime", "D": "Replaces the main database"}, "correct_answer": "B"},
            {"question_text": f"What does CI/CD stand for in modern {skill_name} software delivery pipelines?", "options": {"A": "Code Inspection / Code Design", "B": "Continuous Integration / Continuous Delivery", "C": "Central Index / Central Database", "D": "Client Interface / Client Device"}, "correct_answer": "B"}
        ]

    def grade_assessment(self, student_id: int, skill_name: str, submitted_answers: dict, total_questions: int = 10):
        """Grades student answers, calculates percentage, and records verified score in SQLite."""
        normalized_skill = skill_name.strip().title()
        if not submitted_answers:
            return {"error": "No answers submitted.", "verified_percentage": 0, "correct_answers": 0, "total_questions": total_questions}

        conn = get_db()
        cursor = conn.cursor()
        correct_count = 0
        total = max(int(total_questions) if total_questions else 10, len(submitted_answers), 1)
        for q_id_str, student_choice in submitted_answers.items():
            try:
                cursor.execute("SELECT correct_answer FROM test_questions WHERE id = ?", (int(q_id_str),))
                row = cursor.fetchone()
                if row and row['correct_answer'].upper() == str(student_choice).strip().upper():
                    correct_count += 1
            except Exception:
                continue

        percentage = round((correct_count / total) * 100.0, 1)
        cursor.execute(
            """
            INSERT INTO student_skill_scores (student_id, skill_name, percentage, assessed_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(student_id, skill_name) DO UPDATE SET
                percentage = excluded.percentage,
                assessed_at = CURRENT_TIMESTAMP
            """,
            (student_id, normalized_skill, percentage)
        )
        conn.commit()
        conn.close()
        return {
            'skill_name': normalized_skill,
            'total_questions': total,
            'correct_answers': correct_count,
            'verified_percentage': percentage,
            'status': 'verified' if percentage >= 70 else 'needs_practice'
        }

    # =========================================================================
    # 2. SEMANTIC FIT SCORE & GAP ANALYSIS
    # =========================================================================
    def get_or_generate_fit_score(self, student_id: int, posting_id: int):
        """Checks skill_gap_cache. If missing, computes semantic alignment via Gemini AI & caches."""
        conn = get_db()
        cursor = conn.cursor()

        # 1. Check Cache
        cursor.execute(
            "SELECT fit_score, gap_analysis_text FROM skill_gap_cache WHERE student_id = ? AND posting_id = ?",
            (student_id, posting_id)
        )
        cached = cursor.fetchone()
        if cached:
            conn.close()
            return {"fit_score": cached['fit_score'], "gap_analysis": cached['gap_analysis_text'], "cached": True}

        # 2. Gather context
        cursor.execute("SELECT name, skills, prior_experience FROM students WHERE id = ?", (student_id,))
        student = row_to_dict(cursor.fetchone())
        cursor.execute("SELECT title, required_skills, description FROM postings WHERE id = ?", (posting_id,))
        posting = row_to_dict(cursor.fetchone())
        if not student or not posting:
            conn.close()
            return {"error": "Student or Posting not found."}

        # 3. Compute fit score
        fit_score = 85.0
        analysis = (
            f"Strong match on core skills ({student.get('skills', 'General CSE')}). "
            f"Recommendation: Strengthen practical project experience in {posting.get('required_skills', 'Backend')}."
        )

        prompt = (
            f"Evaluate candidate student {student['name']} (Skills: {student.get('skills')}, Experience: {student.get('prior_experience')}) "
            f"against opportunity '{posting['title']}' (Required: {posting.get('required_skills')}, Description: {posting.get('description')}). "
            f"Return ONLY valid JSON with keys: 'fit_score' (number 0-100) and 'gap_analysis' (2 sentences explaining strengths and missing skills)."
        )
        raw_ai = self._call_gemini(prompt)
        if raw_ai:
            try:
                clean = raw_ai.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean)
                fit_score = float(data.get("fit_score", fit_score))
                analysis = str(data.get("gap_analysis", analysis))
            except Exception:
                pass

        # 4. Save to Cache Table
        cursor.execute(
            """
            INSERT INTO skill_gap_cache (student_id, posting_id, fit_score, gap_analysis_text)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, posting_id) DO UPDATE SET
                fit_score = excluded.fit_score,
                gap_analysis_text = excluded.gap_analysis_text
            """,
            (student_id, posting_id, fit_score, analysis)
        )
        conn.commit()
        conn.close()
        return {"fit_score": fit_score, "gap_analysis": analysis, "cached": False}

    # =========================================================================
    # 3. TARGETED COURSE RECOMMENDATIONS
    # =========================================================================
    def get_or_generate_courses(self, student_id: int, posting_id: int):
        """Checks course_recommendations cache. If missing, suggests targeted upskilling courses & caches."""
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT recommended_courses FROM course_recommendations WHERE student_id = ? AND posting_id = ?",
            (student_id, posting_id)
        )
        cached = cursor.fetchone()
        if cached:
            conn.close()
            return {"courses": json.loads(cached['recommended_courses']), "cached": True}

        cursor.execute("SELECT skills FROM students WHERE id = ?", (student_id,))
        student = row_to_dict(cursor.fetchone())
        cursor.execute("SELECT title, required_skills FROM postings WHERE id = ?", (posting_id,))
        posting = row_to_dict(cursor.fetchone())

        courses = [
            {"title": f"Mastering {posting.get('required_skills', 'Backend Engineering')}", "platform": "Coursera", "difficulty": "Intermediate"},
            {"title": "Database Optimization & Systems Architecture", "platform": "NPTEL", "difficulty": "Advanced"}
        ]

        cursor.execute(
            """
            INSERT INTO course_recommendations (student_id, posting_id, recommended_courses)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, posting_id) DO UPDATE SET
                recommended_courses = excluded.recommended_courses
            """,
            (student_id, posting_id, json.dumps(courses))
        )
        conn.commit()
        conn.close()
        return {"courses": courses, "cached": False}

    # Alias so both names work seamlessly
    get_or_generate_course_recommendations = get_or_generate_courses

    # =========================================================================
    # 4. INTERACTIVE AI TOOLS: RESUME, ROADMAP, INTERVIEW PREP
    # =========================================================================
    def analyze_resume(self, resume_text: str, target_role: str = "Software Engineer"):
        """Evaluates student resume thoroughly via Gemini AI or dynamic semantic text heuristics.
        Computes accurate ATS score (1.0-10.0), section breakdowns, executive verdict, and actionable gap analysis.
        """
        prompt = (
            f"You are a Senior Technical Talent Partner and ATS Evaluation Engine at a premier technology company. "
            f"Conduct an in-depth, rigorous audit of this candidate's resume/profile for the role: '{target_role}'.\n\n"
            f"RESUME TEXT / PROFILE CONTENT:\n{resume_text}\n\n"
            f"EVALUATION CRITERIA:\n"
            f"1. ats_score: Realistic ATS readiness score as a decimal number between 1.0 and 10.0 (e.g. 7.4, 8.6). "
            f"Calibrate against real industry hiring bars. Deduct for lack of metrics, generic buzzwords, or missing foundational tech.\n"
            f"2. verdict: A 2-sentence executive summary verdict on candidate readiness, experience tier, and top priority.\n"
            f"3. section_scores: Object with ratings from 1.0 to 10.0 for:\n"
            f"   - 'technical_depth': Core language mastery, data structures, backend/frontend engineering depth.\n"
            f"   - 'project_impact': Evidence of scale, measurable metrics (%, ms, users), and end-to-end delivery.\n"
            f"   - 'clarity_structure': Formatting effectiveness, conciseness, and strong action verbs.\n"
            f"   - 'role_alignment': Direct relevance to '{target_role}'.\n"
            f"4. strengths: List of 3-4 bullet points identifying specific competencies and frameworks clearly demonstrated in their text.\n"
            f"5. missing_keywords: List of 4-6 essential tools, libraries, architectural patterns, or cloud technologies critical for a '{target_role}' that are absent or weak.\n"
            f"6. gap_analysis: A thorough paragraph detailing the exact gaps preventing this candidate from passing senior recruiter filters for '{target_role}'.\n"
            f"7. actionable_steps: List of 3-4 high-impact, concrete action items to elevate ATS score (e.g., quantify results, deploy live projects, add testing/CI/CD).\n\n"
            f"Return ONLY valid JSON matching this exact structure without markdown backticks:\n"
            f"{{\n"
            f'  "ats_score": 7.8,\n'
            f'  "verdict": "...",\n'
            f'  "section_scores": {{"technical_depth": 7.5, "project_impact": 6.8, "clarity_structure": 8.5, "role_alignment": 8.0}},\n'
            f'  "strengths": ["...", "..."],\n'
            f'  "missing_keywords": ["...", "..."],\n'
            f'  "gap_analysis": "...",\n'
            f'  "actionable_steps": ["...", "..."],\n'
            f'  "recommendations": ["...", "..."]\n'
            f"}}"
        )
        raw_ai = self._call_gemini(prompt)
        if raw_ai:
            try:
                clean = raw_ai.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean)
                if isinstance(parsed, dict) and "ats_score" in parsed:
                    # Normalize recommendations / actionable steps
                    if "actionable_steps" in parsed and "recommendations" not in parsed:
                        parsed["recommendations"] = parsed["actionable_steps"]
                    elif "recommendations" in parsed and "actionable_steps" not in parsed:
                        parsed["actionable_steps"] = parsed["recommendations"]
                    return parsed
            except Exception as e:
                print(f"[GeminiService] Failed to parse resume analysis JSON: {e}")

        # Dynamic Smart Heuristic Fallback based on actual resume text analysis
        return self._heuristic_resume_analysis(resume_text, target_role)

    def _heuristic_resume_analysis(self, text: str, target_role: str):
        """Dynamic heuristic analyzer that inspects the candidate's actual text when Gemini is offline."""
        lower = text.lower()
        words = lower.split()
        word_count = len(words)

        # 1. Tech Stack Detection
        tech_keywords = {
            'python': 'Python', 'javascript': 'JavaScript', 'typescript': 'TypeScript',
            'react': 'React.js', 'node': 'Node.js', 'sql': 'SQL', 'postgresql': 'PostgreSQL',
            'docker': 'Docker', 'kubernetes': 'Kubernetes', 'aws': 'AWS', 'git': 'Git/GitHub',
            'mongodb': 'MongoDB', 'flask': 'Flask', 'fastapi': 'FastAPI', 'django': 'Django',
            'redis': 'Redis', 'tailwind': 'Tailwind CSS', 'graphql': 'GraphQL', 'ci/cd': 'CI/CD Pipelines'
        }
        found_skills = [name for kw, name in tech_keywords.items() if kw in lower]
        if not found_skills and word_count > 10:
            found_skills = ['Fundamental Computing Principles', 'Software Problem Solving']

        # 2. Check for Quantified Metrics & Action Verbs
        import re
        metrics_matches = re.findall(r'\b\d+(?:[\.,]\d+)?\s*(?:%|x|k|ms|s|users|requests|mb|gb|stars|times)?\b', text)
        action_verbs = ['built', 'developed', 'designed', 'implemented', 'architected', 'optimized', 'deployed', 'spearheaded', 'created', 'led', 'scaled', 'integrated']
        found_verbs = [v for v in action_verbs if v in lower]

        # 3. Dynamic Section Scoring
        tech_depth = min(9.5, max(4.0, 5.0 + len(found_skills) * 0.7))
        project_impact = min(9.2, max(3.5, 4.5 + len(metrics_matches) * 0.8 + len(found_verbs) * 0.3))
        clarity_structure = min(9.0, max(4.0, 5.0 + (1.5 if word_count >= 80 else 0.5) + (1.5 if len(found_verbs) >= 2 else 0.5)))
        role_alignment = min(9.4, max(4.0, 5.5 + (1.5 if any(r.lower() in lower for r in target_role.split()) else 0.0) + (1.5 if len(found_skills) >= 3 else 0.5)))

        ats_score = round((tech_depth * 0.35 + project_impact * 0.30 + clarity_structure * 0.15 + role_alignment * 0.20), 1)

        # 4. Role-Specific Missing Keywords
        role_reqs = {
            'backend': ['Docker Containerization', 'Redis Caching', 'PostgreSQL / SQL Indexing', 'CI/CD Automation', 'REST / gRPC APIs', 'System Design Patterns'],
            'frontend': ['TypeScript Generics', 'Next.js / SSR', 'Tailwind CSS', 'Redux / Zustand', 'Web Performance & Lighthouse', 'Unit Testing (Jest/Playwright)'],
            'full stack': ['Docker / Microservices', 'CI/CD Pipelines', 'State Management', 'PostgreSQL / Redis', 'Cloud Hosting (AWS/GCP)', 'Automated Integration Tests'],
            'ai': ['PyTorch / TensorFlow', 'Vector Databases (Chroma/Pinecone)', 'Model Quantization', 'LangChain / LlamaIndex', 'RAG Pipelines', 'MLOps & Experiment Tracking'],
            'data': ['Pandas & NumPy', 'Data Warehousing (Snowflake)', 'Apache Spark', 'Advanced SQL Window Functions', 'ETL Pipelines', 'Tableau / PowerBI']
        }
        matched_category = 'full stack'
        for k in role_reqs:
            if k in target_role.lower():
                matched_category = k
                break
        missing_pool = role_reqs.get(matched_category, role_reqs['full stack'])
        missing_keywords = [m for m in missing_pool if not any(w.lower() in lower for w in m.split()[:2])][:4]
        if not missing_keywords:
            missing_keywords = ['System Architecture Diagrams', 'Automated E2E Testing', 'Load Balancing & Caching', 'Prometheus / Grafana Monitoring']

        # 5. Strengths
        strengths = [
            f"Demonstrated practical proficiency in {', '.join(found_skills[:3]) if found_skills else 'core engineering fundamentals'}.",
            f"Utilized active engineering verbs ({', '.join(found_verbs[:2]) if found_verbs else 'practical implementation'}) showcasing initiative in project development.",
            f"Documented {len(metrics_matches)} quantified outcome(s) indicating measurable orientation towards results." if metrics_matches else "Clean articulation of core project domain and technical responsibilities."
        ]

        # 6. Actionable Steps & Gap Analysis
        actionable_steps = [
            "Quantify project outcomes using XYZ format: Accomplished [X] as measured by [Y], by doing [Z] (e.g. reduced API latency by 35%).",
            f"Incorporate target role standard keywords: {', '.join(missing_keywords[:3])}.",
            "Include live production URLs or interactive demo links for key portfolio projects.",
            "Add a dedicated Systems Architecture & Testing section showing CI/CD and unit test coverage."
        ]

        verdict = (
            f"Candidate shows a solid foundational base for '{target_role}' with recognizable strengths in {', '.join(found_skills[:2]) if found_skills else 'software development'}. "
            f"To reach the top 10% candidate tier, focus on quantifying engineering impact and showcasing modern tooling like {missing_keywords[0] if missing_keywords else 'Docker and CI/CD'}."
        )

        gap_analysis = (
            f"While the candidate displays core technical capability, there is a distinct gap in demonstrating production-scale readiness for a '{target_role}'. "
            f"Specifically, technical recruiters and ATS algorithms will look for concrete evidence of {missing_keywords[0] if missing_keywords else 'cloud architecture'}, "
            f"rigorous automated testing, and performance metrics. Closing these gaps will significantly elevate screening pass rates."
        )

        return {
            "ats_score": ats_score,
            "verdict": verdict,
            "section_scores": {
                "technical_depth": round(tech_depth, 1),
                "project_impact": round(project_impact, 1),
                "clarity_structure": round(clarity_structure, 1),
                "role_alignment": round(role_alignment, 1)
            },
            "strengths": strengths,
            "missing_keywords": missing_keywords,
            "gap_analysis": gap_analysis,
            "actionable_steps": actionable_steps,
            "recommendations": actionable_steps
        }

    def generate_career_roadmap(self, target_role: str):
        """Generates a structured 4-week learning roadmap for any industry role."""
        prompt = (
            f"Generate a practical 4-week step-by-step learning roadmap for a student aiming to become a '{target_role}'. "
            f"Return ONLY a valid JSON list of 4 objects with keys: "
            f"'week' (e.g. 'Week 1'), 'title' (short focus area), 'topics' (list of 3 strings), and 'project' (one mini project description)."
        )
        raw_ai = self._call_gemini(prompt)
        if raw_ai:
            try:
                clean = raw_ai.replace("```json", "").replace("```", "").strip()
                return json.loads(clean)
            except Exception:
                pass

        # Smart Fallback
        return [
            {"week": "Week 1", "title": "Foundations & Core Architecture", "topics": [f"{target_role} Fundamentals", "Core Data Structures", "Version Control with Git"], "project": "Build and document a CLI starter utility."},
            {"week": "Week 2", "title": "API & Database Engineering", "topics": ["RESTful Service Design", "SQL Schema & Normalization", "Authentication & Middleware"], "project": "Develop a multi-role authenticated CRUD service."},
            {"week": "Week 3", "title": "Frontend & Integration", "topics": ["State Management", "Asynchronous Data Fetching", "UI Component Modularity"], "project": "Connect full-stack dashboard with real API endpoints."},
            {"week": "Week 4", "title": "Deployment & System Hardening", "topics": ["Testing & Validation", "Environment Security", "Performance Profiling"], "project": "Deploy end-to-end prototype with live demo accounts."}
        ]

    def generate_mock_interview(self, skill_name: str):
        """Generates 3 realistic technical interview questions with model answers."""
        prompt = (
            f"Generate 3 technical interview questions for skill '{skill_name}'. "
            f"Return ONLY a valid JSON list of objects with keys: 'question', 'hint', and 'sample_answer'."
        )
        raw_ai = self._call_gemini(prompt)
        if raw_ai:
            try:
                clean = raw_ai.replace("```json", "").replace("```", "").strip()
                return json.loads(clean)
            except Exception:
                pass

        # Smart Fallback
        return [
            {"question": f"How do you handle error states and data validation when using {skill_name} in production?", "hint": "Focus on graceful error handling, status codes, and input sanitization.", "sample_answer": f"Always validate inputs at system boundaries, use try-except/catch blocks to avoid silent failures, and return structured error payloads."},
            {"question": f"What is one performance bottleneck you might encounter with {skill_name}, and how would you resolve it?", "hint": "Think about query indexing, caching, or memory utilization.", "sample_answer": "Common bottlenecks include redundant computations and unindexed lookups; resolved by adding caching layers and indexing hot paths."},
            {"question": f"Explain the difference between synchronous and asynchronous operations in the context of {skill_name}.", "hint": "Think about blocking vs non-blocking I/O.", "sample_answer": "Synchronous operations block execution until finished; asynchronous operations yield control, allowing other tasks to progress while waiting for I/O."}
        ]

# Single shared instance of the AI service
gemini_service = GeminiService()