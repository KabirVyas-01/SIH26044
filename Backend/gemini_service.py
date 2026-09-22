import json
import re
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

    def generate_career_roadmap(self, target_role: str, level: str = 'intermediate', duration_weeks: int = 4, current_skills: str = ''):
        """Generates a structured, domain-accurate learning roadmap tailored to role, experience level, and timeline."""
        normalized_role = target_role.strip().title() if target_role else "Full Stack Developer"
        normalized_level = level.strip().lower() if level in ('beginner', 'intermediate', 'advanced') else 'intermediate'
        weeks_count = 8 if int(duration_weeks or 4) >= 6 else 4

        prompt = (
            f"You are a Principal Engineering Director and Career Architect. Generate a high-impact, highly tailored {weeks_count}-week roadmap for a student aiming for the role of '{normalized_role}' at '{normalized_level.upper()}' level.\n"
            f"Student's current baseline skills: {current_skills or 'Standard CS fundamentals'}.\n\n"
            f"CRITICAL INSTRUCTIONS:\n"
            f"1. Make the roadmap STRICTLY specific to '{normalized_role}'. Do NOT return generic web development or CRUD weeks for specialized domains like AI/ML, Data Science, Cybersecurity, DevOps, Mobile, or Systems Engineering.\n"
            f"2. Each week must contain:\n"
            f"   - 'week': 'Week 1', 'Week 2', etc.\n"
            f"   - 'title': High-impact focus area (e.g. 'Transformers & RAG Pipeline Engineering', 'Kernel Internals & Memory Architecture', 'Distributed Consensus & Raft').\n"
            f"   - 'focus': 1 concise sentence describing the core objective.\n"
            f"   - 'topics': Exactly 3-4 specific tools, libraries, architectural principles, or algorithms relevant to {normalized_role}.\n"
            f"   - 'project': A realistic, portfolio-grade mini-project deliverable with concrete requirements.\n"
            f"   - 'milestone': Measurable outcome or skill badge earned.\n"
            f"3. Calibrate difficulty to '{normalized_level.upper()}'.\n"
            f"Return ONLY a valid JSON list of {weeks_count} objects."
        )

        raw_ai = self._call_gemini(prompt)
        if raw_ai:
            try:
                clean = raw_ai.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean)
                if isinstance(parsed, list) and len(parsed) >= 3:
                    return parsed
            except Exception as e:
                print(f"[GeminiService Roadmap Warning] Parse error: {e}")

        # Domain-Accurate Curated Curriculums
        return self._get_domain_roadmap(normalized_role, normalized_level, weeks_count)

    def _get_domain_roadmap(self, role: str, level: str, weeks: int):
        """Rich curated curriculum banks for 12+ distinct industry specializations."""
        r = role.lower()
        tokens = set(re.findall(r'\b\w+\b', r))

        # 1. AI & MACHINE LEARNING
        if any(k in r for k in ('machine learning', 'deep learning', 'artificial intelligence', 'nlp', 'computer vision', 'llm', 'generative ai', 'prompt engineer')) or ('ai' in tokens or 'ml' in tokens):
            if level == 'advanced':
                base = [
                    {"week": "Week 1", "title": "Transformer Architecture & Self-Attention", "focus": "Mastering multi-head attention, positional encodings, and kv-caching.", "topics": ["FlashAttention-2", "Tensor Parallelism", "RoPE Positional Embeddings", "KV Cache Management"], "project": "Implement a miniature GPT decoder from scratch with RoPE & causal masking in PyTorch.", "milestone": "Custom Transformer Core Validated"},
                    {"week": "Week 2", "title": "Retrieval Augmented Generation (RAG) at Scale", "focus": "Building low-latency hybrid search and reranking pipelines.", "topics": ["Vector DBs (Chroma/Qdrant)", "BM25 Hybrid Retrieval", "Cross-Encoder Reranking", "Context Compression"], "project": "Build an enterprise document QA engine with sub-200ms hybrid search & citations.", "milestone": "Production RAG Pipeline Deployed"},
                    {"week": "Week 3", "title": "Fine-Tuning & Parameter Efficient Adaptation", "focus": "Adapting open-source LLMs using LoRA and QLoRA.", "topics": ["LoRA & QLoRA Quantization", "Unsloth / Axolotl", "SFT Trainer & Alignment", "Instruction Dataset Curation"], "project": "Fine-tune Llama 3 8B on a domain-specific dataset with 4-bit quantization on single GPU.", "milestone": "Fine-Tuned Checkpoint Released"},
                    {"week": "Week 4", "title": "High-Throughput Serving & MLOps", "focus": "Deploying scalable inference microservices with continuous monitoring.", "topics": ["vLLM & PagedAttention", "Triton Inference Server", "Continuous Batching", "Langfuse / MLflow Tracking"], "project": "Deploy an autoscaling inference API capable of 150 tokens/sec stream with latency tracing.", "milestone": "Certified Production LLM Engineer"}
                ]
            else:
                base = [
                    {"week": "Week 1", "title": "Math Foundations & Tensor Operations", "focus": "Mastering multidimensional array calculus, loss functions, and gradients.", "topics": ["Matrix Calculus & Backprop", "PyTorch Tensor Operations", "Autograd Internals", "Data Loaders & Batching"], "project": "Build a multi-layer perceptron neural network from scratch using raw PyTorch tensors.", "milestone": "Neural Network Fundamentals Cleared"},
                    {"week": "Week 2", "title": "Supervised Learning & Model Evaluation", "focus": "Implementing classic regression, classification, and validation.", "topics": ["Scikit-Learn Workflows", "Cross-Validation & ROC-AUC", "Regularization (L1/L2)", "Feature Scaling & Imputation"], "project": "Train and benchmark XGBoost vs Random Forest for customer churn prediction.", "milestone": "Tabular Model Specialist"},
                    {"week": "Week 3", "title": "Deep Learning & Computer Vision / NLP", "focus": "Architecting CNNs and RNNs for unstructured data processing.", "topics": ["Convolutional Networks (ResNet)", "Embeddings & Tokenization", "Transfer Learning", "HuggingFace Transformers"], "project": "Fine-tune a pretrained Vision Transformer (ViT) for image classification with 94%+ accuracy.", "milestone": "Deep Learning Portfolio Project"},
                    {"week": "Week 4", "title": "Model Packaging & Fast Inference API", "focus": "Wrapping trained checkpoints in production FastAPI microservices.", "topics": ["FastAPI Endpoints", "ONNX Runtime Optimization", "Docker Containerization", "Model Serialization (safetensors)"], "project": "Package your trained model into a containerized REST API with interactive Swagger docs.", "milestone": "End-to-End ML Service Deployed"}
                ]

        # 1. CYBERSECURITY
        elif any(k in r for k in ('security', 'cyber', 'infosec', 'pen', 'ethical', 'soc')):
            base = [
                {"week": "Week 1", "title": "Network Protocols & Traffic Inspection", "focus": "Understanding packet flows, handshakes, and diagnostic utilities.", "topics": ["TCP/IP & 3-Way Handshake", "Wireshark Packet Analysis", "DNS, ARP & ICMP Attacks", "Nmap Port Scanning & Flags"], "project": "Capture and analyze network traffic in Wireshark to detect an unauthorized port scan and ARP spoof.", "milestone": "Network Security Analyst"},
                {"week": "Week 2", "title": "Web Application Vulnerabilities (OWASP Top 10)", "focus": "Auditing and patching critical web security flaws.", "topics": ["SQL Injection (SQLi) Exploits", "Cross-Site Scripting (XSS)", "CSRF & Broken Auth", "Burp Suite Proxy Auditing"], "project": "Audit a vulnerable web application, exploit 3 OWASP vulnerabilities, and write technical patch remediation.", "milestone": "Web Security Auditor"},
                {"week": "Week 3", "title": "Linux Privilege Escalation & Cryptography", "focus": "Security hardening, SUID exploitation, and encryption schemes.", "topics": ["SUID Binaries & Cron Exploitation", "Public Key Cryptography (RSA)", "Hashing & Rainbow Tables", "AppArmor & SELinux"], "project": "Complete a capture-the-flag (CTF) machine demonstrating privilege escalation from user to root.", "milestone": "Penetration Tester Badge"},
                {"week": "Week 4", "title": "Incident Response, SIEM & Threat Hunting", "focus": "Monitoring logs, identifying anomalies, and coordinating defense.", "topics": ["SIEM Setup (Wazuh / Splunk)", "Syslog & Auditd Monitoring", "Incident Response Lifecycles", "MITRE ATT&CK Framework"], "project": "Configure a central SIEM that triggers real-time alerts when suspicious brute-force logins occur.", "milestone": "SOC Analyst Ready"}
            ]

        # 2. DATA SCIENCE & ANALYTICS
        elif any(k in r for k in ('data science', 'data scientist', 'data analyst', 'analytics', 'statistics', 'tableau', 'powerbi')) or ('bi' in tokens or 'data' in tokens):
            base = [
                {"week": "Week 1", "title": "Advanced SQL & Relational Querying", "focus": "Mastering analytical window functions, CTEs, and aggregation pipelines.", "topics": ["Window Functions (LEAD/LAG/RANK)", "Recursive CTEs", "Index Scan vs Index Seek", "Subqueries & Self-Joins"], "project": "Write an enterprise cohort retention and churn SQL report over 500k synthetic records.", "milestone": "Advanced SQL Badge"},
                {"week": "Week 2", "title": "Exploratory Data Analysis with Pandas & NumPy", "focus": "Data cleaning, vectorization, and statistical hypothesis testing.", "topics": ["Pandas Vectorized Ops", "Missing Data Imputation", "Correlation & Outlier Detection", "Hypothesis Testing (t-test, ANOVA)"], "project": "Analyze an e-commerce transaction dataset and uncover 3 statistically significant pricing insights.", "milestone": "Statistical EDA Report"},
                {"week": "Week 3", "title": "Interactive Dashboards & Business Storytelling", "focus": "Building real-time executive visual metrics and drill-down charts.", "topics": ["Tableau / PowerBI / Streamlit", "Data Storytelling & KPI Cards", "Chart Selection & Color Theory", "Interactive Filter Actions"], "project": "Build a multi-tab interactive sales executive dashboard with dynamic filtering in Streamlit.", "milestone": "Executive BI Dashboard"},
                {"week": "Week 4", "title": "Automated ETL Pipelines & Warehouse Schemas", "focus": "Designing clean dimensional star schemas and scheduling pipelines.", "topics": ["Star vs Snowflake Schema", "dbt (Data Build Tool)", "Scheduled ETL Tasks", "Data Quality Unit Tests"], "project": "Build an automated pipeline that ingests daily CSVs, validates schema, and writes to SQLite/DuckDB.", "milestone": "Junior Data Engineer Ready"}
            ]

        # 3. BACKEND ENGINEERING
        elif any(k in r for k in ('backend', 'api', 'server', 'golang', 'microservices', 'distributed')) or ('go' in tokens):
            base = [
                {"week": "Week 1", "title": "RESTful API Architecture & Schema Design", "focus": "Writing clean, type-safe API endpoints with robust relational models.", "topics": ["REST Best Practices", "Database Normalization & Foreign Keys", "Pydantic / Type Validation", "Error Handling & Status Codes"], "project": "Build a modular REST API for an institutional course catalog with pagination & filtering.", "milestone": "Production API Core"},
                {"week": "Week 2", "title": "Authentication, Session Security & Middleware", "focus": "Securing services using industry standard cryptographic tokens and rate limits.", "topics": ["JWT & HttpOnly Cookie Sessions", "Argon2 / Bcrypt Hashing", "Role-Based Access Control (RBAC)", "Rate Limiting & CORS"], "project": "Implement a secure multi-role auth service with OTP password resets and middleware guards.", "milestone": "Security Hardened Backend"},
                {"week": "Week 3", "title": "Database Optimization, Caching & Concurrency", "focus": "Eliminating query bottlenecks using indexes and memory caches.", "topics": ["B-Tree Indexes & EXPLAIN QUERY", "Redis Caching Layer", "Connection Pooling", "Database Transactions (ACID)"], "project": "Optimize database queries with indexing and add Redis cache, reducing P99 latency by 60%.", "milestone": "High Performance Engineer"},
                {"week": "Week 4", "title": "Docker Containerization, CI/CD & Deployments", "focus": "Packaging the microservice and deploying with automated pipelines.", "topics": ["Dockerfile Multi-Stage Builds", "Docker Compose Orchestration", "GitHub Actions CI/CD", "Cloud Platform Deployment (Render/AWS)"], "project": "Deploy the entire authenticated backend with automated test suites on push to main.", "milestone": "Industry-Ready Backend Developer"}
            ]

        # 4. FRONTEND ENGINEERING
        elif any(k in r for k in ('frontend', 'react', 'next', 'ui developer', 'web developer', 'vue', 'angular')):
            base = [
                {"week": "Week 1", "title": "Modern TypeScript & Component Architecture", "focus": "Mastering TypeScript generics, strict typing, and component composition.", "topics": ["TypeScript Generics & Utility Types", "Compound Component Patterns", "Custom Hooks & Pure Logic Separation", "Accessible HTML Semantics"], "project": "Build a type-safe, accessible component library (Modal, Combobox, Data Table) with zero dependencies.", "milestone": "TypeScript Component Architecture"},
                {"week": "Week 2", "title": "Global State Management & Data Fetching", "focus": "Handling complex server state, optimistic updates, and caching.", "topics": ["TanStack Query (React Query)", "Zustand Lightweight State", "Optimistic Mutations", "Cache Invalidation Strategies"], "project": "Build an interactive Kanban board with drag-and-drop, persistent server sync, and undo actions.", "milestone": "State Management Pro"},
                {"week": "Week 3", "title": "Next.js App Router & Performance Optimization", "focus": "Server Components, dynamic routing, and core web vitals.", "topics": ["React Server Components (RSC)", "Dynamic Segment Routing", "Image & Font Optimization", "Lighthouse 95+ Core Web Vitals"], "project": "Migrate a client dashboard to Next.js App Router with SSR and sub-1s initial page load.", "milestone": "Next.js SSR Specialist"},
                {"week": "Week 4", "title": "Automated Testing, Animation & Production Build", "focus": "Ensuring zero regression with component tests and polish.", "topics": ["Vitest & React Testing Library", "Playwright E2E Testing", "Framer Motion Micro-Interactions", "Bundle Analysis & Code Splitting"], "project": "Add 85%+ test coverage and silky entrance animations to a production SaaS web application.", "milestone": "Production Frontend Engineer"}
            ]

        # 5. DEVOPS & CLOUD INFRASTRUCTURE
        elif any(k in r for k in ('devops', 'cloud', 'sre', 'infrastructure', 'kubernetes', 'aws', 'docker')):
            base = [
                {"week": "Week 1", "title": "Linux Systems Internals & Shell Scripting", "focus": "Mastering POSIX command line, process management, and networking.", "topics": ["Bash Automation Scripts", "Systemd Services & Cron", "Process Management (ps/kill/top)", "SSH Keys & Firewall Rules (ufw)"], "project": "Write a bash automation suite for automated database backups, log rotation, and health monitoring.", "milestone": "Linux Administration Core"},
                {"week": "Week 2", "title": "Docker Containers & Microservice Orchestration", "focus": "Containerizing multi-tier applications and networking them safely.", "topics": ["Docker Multi-Stage Optimization", "Bridge Networks & Volumes", "Docker Compose Multi-Tier", "Container Security & Non-Root Users"], "project": "Containerize a full-stack Python + React + Postgres application with a single compose up command.", "milestone": "Containerization Specialist"},
                {"week": "Week 3", "title": "Kubernetes Clusters & Ingress Management", "focus": "Deploying resilient, self-healing pods with automated load balancing.", "topics": ["Pods, Deployments & ReplicaSets", "ClusterIP & NodePort Services", "Ingress Controllers & TLS/SSL", "ConfigMaps & Secrets"], "project": "Deploy an autoscaling microservice on local Minikube / K3s with ingress routing and health probes.", "milestone": "Kubernetes Practitioner"},
                {"week": "Week 4", "title": "Infrastructure as Code (Terraform) & CI/CD", "focus": "Automating cloud infrastructure provisioning and continuous delivery.", "topics": ["Terraform HCL Syntax", "State Files & Remote Backends", "GitHub Actions CI/CD Pipeline", "Cloud Watch & Prometheus Alerting"], "project": "Write Terraform manifests to provision cloud resources and trigger deployment automatically on Git push.", "milestone": "Certified DevOps Associate"}
            ]

        # 6. UI/UX & PRODUCT DESIGN
        elif any(k in r for k in ('ui/ux', 'ux', 'product design', 'figma', 'design')):
            base = [
                {"week": "Week 1", "title": "Design Thinking, User Research & Wireframing", "focus": "Conducting user interviews, journey maps, and low-fidelity wireframes.", "topics": ["User Persona Archetypes", "Information Architecture (IA)", "Low-Fidelity Wireframing", "Competitive Heuristic Evaluation"], "project": "Design a complete user flow wireframe solving a friction point in campus student recruitment.", "milestone": "UX Research & Wireframe Verified"},
                {"week": "Week 2", "title": "Figma Auto-Layout & Design Systems", "focus": "Building reusable components, typography scales, and token systems in Figma.", "topics": ["Auto-Layout 5.0", "Component Variants & Properties", "Color & Spacing Token Systems", "WCAG AA Contrast Compliance"], "project": "Build an end-to-end Figma UI Design System with responsive web and mobile components.", "milestone": "Design System Architect"},
                {"week": "Week 3", "title": "High-Fidelity Prototyping & Micro-Interactions", "focus": "Creating interactive clickable prototypes with realistic states.", "topics": ["Figma Smart Animate", "Interactive Component States", "Micro-Interactions & Gestures", "Accessibility Audits"], "project": "Build an interactive, clickable prototype with realistic animations and loading states.", "milestone": "Interactive Prototype Master"},
                {"week": "Week 4", "title": "Usability Testing & Design-to-Code Handoff", "focus": "Testing prototypes with real users and preparing assets for engineering.", "topics": ["Usability Testing Sessions", "System Usability Scale (SUS)", "Handoff Specs for Developers", "Case Study Portfolio Presentation"], "project": "Publish a comprehensive UI/UX case study documenting research, iterations, and final design.", "milestone": "Portfolio Ready Product Designer"}
            ]

        # 7. BLOCKCHAIN & WEB3
        elif any(k in r for k in ('blockchain', 'web3', 'solidity', 'smart contract', 'crypto', 'ethereum')):
            base = [
                {"week": "Week 1", "title": "Cryptography Foundations & Ethereum Virtual Machine", "focus": "Understanding cryptographic hashing, elliptic curves, and EVM gas mechanics.", "topics": ["SHA-256 & Keccak256", "Public-Key Cryptography", "EVM Storage vs Memory vs Calldata", "Gas Optimization Strategies"], "project": "Write a gas-optimized ERC-20 token contract with minting and burning caps.", "milestone": "EVM Fundamentals"},
                {"week": "Week 2", "title": "Solidity Smart Contract Engineering", "focus": "Developing secure, modular smart contracts using OpenZeppelin.", "topics": ["Solidity 0.8+ Syntax", "OpenZeppelin Standards (ERC-721/1155)", "Access Control (Ownable/Roles)", "Reentrancy Guard Patterns"], "project": "Develop an audited decentralized crowdfunding smart contract with milestone payouts.", "milestone": "Solidity Engineer"},
                {"week": "Week 3", "title": "Testing & Auditing with Foundry / Hardhat", "focus": "Fuzz testing, invariant testing, and security auditing.", "topics": ["Foundry (Forge/Cast)", "Fuzz Testing & Invariant Tests", "Flash Loan Attacks & Slither", "Oracle Manipulation Defense"], "project": "Write 95%+ coverage fuzz test suites for an automated market maker pool using Foundry.", "milestone": "Smart Contract Auditor"},
                {"week": "Week 4", "title": "DApp Frontend Integration (Ethers.js / Wagmi)", "focus": "Connecting client frontends with web3 wallets and smart contracts.", "topics": ["Wagmi / Viem React Hooks", "WalletConnect & MetaMask Integration", "The Graph Indexing & Subgraphs", "IPFS Decentralized Storage"], "project": "Deploy a complete decentralized application (DApp) with wallet login and live contract transactions.", "milestone": "Full Stack Web3 Developer"}
            ]

        # 7. MOBILE APP DEVELOPMENT
        elif any(k in r for k in ('mobile', 'android', 'ios', 'flutter', 'react native', 'swift', 'kotlin')):
            base = [
                {"week": "Week 1", "title": "Mobile UI Components & Responsive Layouts", "focus": "Building smooth touch-first layouts that adapt across phone and tablet screens.", "topics": ["Flexbox & Grid on Mobile", "Platform-Specific Navigation", "Safe Area & Notch Insets", "Adaptive Theming (Dark/Light)"], "project": "Build an onboarding and home screen for an educational app that renders flawlessly on iOS & Android.", "milestone": "Mobile Layout Foundations"},
                {"week": "Week 2", "title": "State Management & Asynchronous Data Fetching", "focus": "Managing offline caches and dynamic feeds.", "topics": ["Client State Patterns", "REST API Integration", "Pull-to-Refresh & Shimmers", "Async Storage / Secure Store"], "project": "Build a live job feed app with infinite scrolling, bookmarking, and local cache persistence.", "milestone": "Mobile State Engineer"},
                {"week": "Week 3", "title": "Device Hardware APIs & Push Notifications", "focus": "Connecting with camera, location, and notification services.", "topics": ["Camera & Gallery Pickers", "Geolocation & Maps SDK", "Local & Push Notifications", "Biometric Authentication (FaceID)"], "project": "Build a verified student check-in app with GPS geotagging and camera photo submission.", "milestone": "Native Feature Integration"},
                {"week": "Week 4", "title": "Offline-First Architecture & Store Release", "focus": "Local SQLite database sync and production release preparation.", "topics": ["Local SQLite / WatermelonDB", "Background Sync Tasks", "App Icon & Splash Configuration", "APK / AAB Build & Signing"], "project": "Bundle a production-signed release APK with full offline mode support and zero crash rating.", "milestone": "Published Mobile Developer"}
            ]

        # DEFAULT: FULL STACK SOFTWARE ENGINEERING
        else:
            base = [
                {"week": "Week 1", "title": "Foundations & Modular Architecture", "focus": f"Mastering core principles, version control, and modular patterns for {role}.", "topics": [f"{role} Core Fundamentals", "Git Flow & Collaborative Branching", "Modular Code Organization", "Type Safety & Linters"], "project": f"Build a clean starter project architecture demonstrating modular design for a {role}.", "milestone": "Core Foundations Verified"},
                {"week": "Week 2", "title": "Service Design & Data Modeling", "focus": "Designing resilient data schemas and authenticated API contracts.", "topics": ["Relational Database Schemas", "REST / JSON API Design", "Authentication & JWT Middleware", "Input Validation & Sanitization"], "project": "Build an authenticated multi-role CRUD service with database transactions and error handling.", "milestone": "Data & Service Architecture"},
                {"week": "Week 3", "title": "Interactive Client Integration & State", "focus": "Connecting the user experience with real-time responsive data.", "topics": ["Component Hierarchy", "Asynchronous API Fetching", "Global & Local State Management", "Responsive Mobile-First UI"], "project": "Connect full-stack client portal with live API endpoints, loading skeletons, and notifications.", "milestone": "Full Stack Integration"},
                {"week": "Week 4", "title": "Deployment, Automated Testing & System Hardening", "focus": "Hardening the application for production scale with CI/CD.", "topics": ["Automated Unit & Integration Tests", "Containerization with Docker", "Continuous Deployment Pipelines", "Performance Profiling & Auditing"], "project": f"Deploy a production-ready portfolio project showcasing all skills required of an industry {role}.", "milestone": f"Certified {role} Ready"}
            ]

        # If 8 weeks requested, extend seamlessly
        if weeks == 8 and len(base) == 4:
            extended = [
                {"week": "Week 5", "title": "Advanced Design Patterns & Architecture", "focus": f"Applying enterprise architectural patterns to {role}.", "topics": ["Domain-Driven Design (DDD)", "Event-Driven Messaging", "Clean Architecture Layers", "Decoupled Services"], "project": "Refactor application to use dependency injection and decoupled service layers.", "milestone": "Enterprise Architecture"},
                {"week": "Week 6", "title": "Performance Profiling & Deep Optimization", "focus": "Profiling latency, memory allocation, and database bottlenecks.", "topics": ["APM Profiling Tools", "Query Plan Optimization", "In-Memory Caching Strategies", "Concurrency & Threading"], "project": "Run load tests with 1000 simulated users and optimize hot paths to achieve <100ms response.", "milestone": "Performance Engineering"},
                {"week": "Week 7", "title": "Security Hardening & Compliance", "focus": "Penetration defense, secret vaults, and security audits.", "topics": ["OWASP Hardening", "Secret Rotation & Environment Security", "Static Analysis (SAST)", "Automated Security Scans"], "project": "Conduct an automated security scan and patch all high/medium severity findings.", "milestone": "Security Audit Passed"},
                {"week": "Week 8", "title": "Capstone Engineering Project & Industry Portfolio", "focus": f"Showcasing end-to-end mastery for top-tier {role} interview loops.", "topics": ["End-to-End System Documentation", "Live Cloud Deployment", "Architecture Diagrams (C4 Model)", "Technical Case Study Presentation"], "project": "Deploy complete capstone project with live demo URL, architecture documentation, and test reports.", "milestone": f"Senior {role} Ready"}
            ]
            return base + extended

        return base

    def generate_mock_interview(self, skill_name: str, level: str = 'intermediate', round_type: str = 'technical'):
        """Generates realistic, challenging technical interview questions with hints, model answers, and follow-ups."""
        normalized_skill = skill_name.strip().title() if skill_name else "Python"
        normalized_level = level.strip().lower() if level in ('beginner', 'intermediate', 'advanced') else 'intermediate'
        normalized_round = round_type.strip().lower() if round_type in ('technical', 'scenario', 'architecture') else 'technical'

        prompt = (
            f"You are a Senior Staff Engineer and Interview Bar Raiser at a premier technology company. "
            f"Generate exactly 4 realistic, high-signal interview questions for skill '{normalized_skill}' at '{normalized_level.upper()}' difficulty for a '{normalized_round.upper()}' interview round.\n\n"
            f"REQUIREMENTS:\n"
            f"1. Tailor each question specifically to '{normalized_skill}'. Do NOT use generic fill-in-the-blank question templates.\n"
            f"2. Each question object must have:\n"
            f"   - 'question': Direct, realistic technical interview question testing actual engineering judgment or mechanics.\n"
            f"   - 'level': '{normalized_level.capitalize()}'\n"
            f"   - 'category': Specific concept domain (e.g. 'Memory Management', 'Index Scan vs Seek', 'Reconciliation & Virtual DOM', 'Concurrency & Deadlocks').\n"
            f"   - 'hint': Thoughtful guiding hint showing what a candidate should consider before answering.\n"
            f"   - 'sample_answer': A comprehensive, model response demonstrating how a top engineer explains the concept clearly, citing trade-offs and code logic.\n"
            f"   - 'follow_up': A realistic follow-up question the interviewer might ask next.\n"
            f"Return ONLY a valid JSON list of 4 objects."
        )

        raw_ai = self._call_gemini(prompt)
        if raw_ai:
            try:
                clean = raw_ai.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean)
                if isinstance(parsed, list) and len(parsed) >= 2:
                    return parsed
            except Exception as e:
                print(f"[GeminiService Interview Warning] Parse error: {e}")

        # Specialized Question Banks by Skill & Level
        return self._get_domain_interview_questions(normalized_skill, normalized_level, normalized_round)

    def _get_domain_interview_questions(self, skill: str, level: str, round_type: str):
        """Rich curated question banks for top skills without repetitive templates."""
        sk = skill.lower()

        # PYTHON
        if 'python' in sk:
            if level == 'advanced':
                return [
                    {
                        "question": "How does CPython manage memory for small objects, and how does the Global Interpreter Lock (GIL) interact with multi-threaded CPU-bound programs?",
                        "level": "Advanced",
                        "category": "CPython Internals & Memory",
                        "hint": "Mention PyMalloc (arenas, pools, blocks) for objects <= 512 bytes, and explain why threads don't speed up pure CPU math.",
                        "sample_answer": "CPython uses a layered memory architecture: the OS allocates memory in 256KB arenas, divided into 4KB pools containing fixed-size blocks (up to 512 bytes) managed by PyMalloc to eliminate fragmentation. For larger allocations, standard malloc is used. Standard reference counting handles immediate cleanup, supplemented by a cyclic generational garbage collector. The GIL is a mutual exclusion lock protecting CPython internal state from concurrent modification; because non-atomic reference counts would race, only one native thread executes Python bytecode at once. In CPU-bound tasks, multithreading adds lock contention overhead with zero parallelism; true concurrency requires multiprocessing, C-extensions releasing the GIL (e.g. NumPy), or Python 3.13 free-threaded builds.",
                        "follow_up": "What happens under the hood when a Python object has a __del__ method during cyclic reference collection?"
                    },
                    {
                        "question": "What is the Descriptor Protocol in Python, and how is it used under the hood to implement @property, @staticmethod, and @classmethod?",
                        "level": "Advanced",
                        "category": "Metaprogramming & Object Model",
                        "hint": "Discuss __get__, __set__, and __delete__, and how attribute lookup order checks data descriptors before the instance __dict__.",
                        "sample_answer": "The Descriptor Protocol is defined by any class implementing at least one of __get__, __set__, or __delete__. When accessing an attribute like obj.attr, Python invokes object.__getattribute__, which first checks the class and its MRO for a data descriptor (having __set__). If found, its __get__ is called. Next, obj.__dict__ is searched. If not found, non-data descriptors (only __get__) are called. Built-in @property is a data descriptor that binds custom getter and setter functions. Standard functions and methods are non-data descriptors: calling func.__get__(obj, cls) returns a bound method with obj prepended as 'self'.",
                        "follow_up": "How does the performance of accessing a __slots__ attribute compare to a standard __dict__ attribute?"
                    },
                    {
                        "question": "Explain how Python's asyncio event loop handles coroutines, and how it differs from kernel-level multithreading.",
                        "level": "Advanced",
                        "category": "Asynchronous Concurrency",
                        "hint": "Think of cooperative multitasking, generator yield mechanics under the hood, and epoll/kqueue OS readiness notifications.",
                        "sample_answer": "Python's asyncio implements single-threaded cooperative multitasking. Coroutines are state machines created with async def that pause execution at 'await' points, yielding control back to the event loop. The event loop uses OS-level I/O multiplexing (like epoll on Linux, kqueue on macOS, or IOCP on Windows) to monitor file descriptors without blocking. When I/O completes, the OS notifies the loop, which resumes the waiting Task. Unlike kernel threads, there is no preemptive context switching, no thread stack allocation (saving megabytes of RAM), and no data races on synchronous code segments.",
                        "follow_up": "What happens if a developer calls a synchronous time.sleep() or a blocking SQL query inside an asyncio coroutine?"
                    },
                    {
                        "question": "How does Python compute the Method Resolution Order (MRO) in multiple inheritance, and what causes an 'Inconsistent MRO' error?",
                        "level": "Advanced",
                        "category": "Object-Oriented Architecture",
                        "hint": "Mention the C3 Linearization algorithm and local precedence order.",
                        "sample_answer": "Python uses the C3 Linearization algorithm to determine MRO deterministically. C3 guarantees two key properties: Local Precedence Order (subclasses appear before parents, and direct parents appear in the order specified in class definition) and Monotonicity (if A precedes B in one class MRO, A must precede B in all derived class MROs). When Python builds a class definition, it computes linearizations by merging parents' MROs. If an inheritance graph creates a cyclical conflict where a class would need to appear both before and after another class to satisfy both parent lists, Python raises a TypeError: Cannot create a consistent method resolution order (MRO).",
                        "follow_up": "How does super() determine which method to call next at runtime?"
                    }
                ]
            else:
                return [
                    {
                        "question": "What is the difference between mutable and immutable data types in Python, and how does this affect function arguments passed by reference?",
                        "level": "Intermediate",
                        "category": "Language Mechanics",
                        "hint": "Explain call-by-object-reference and what happens if you mutate a list inside a function.",
                        "sample_answer": "In Python, variables store references to objects. Immutable types (int, float, str, tuple, frozenset) cannot be modified after creation; modifying them creates a new object in memory. Mutable types (list, dict, set) can have their contents altered in-place. Python passes arguments using 'call by object reference' (or call by assignment). When you pass a mutable object like a list into a function, both the caller and the local variable reference the exact same underlying memory; modifying it (e.g. list.append()) directly affects the caller. However, reassigning the variable (param = [1, 2]) simply binds the local name to a new object without affecting the caller.",
                        "follow_up": "Why is it considered dangerous to use a mutable object like [] or {} as a default parameter in a function definition?"
                    },
                    {
                        "question": "How do Python generators work, and why are they superior to lists when processing large datasets or log files?",
                        "level": "Intermediate",
                        "category": "Memory & Performance",
                        "hint": "Contrast loading entire arrays into memory with lazy evaluation using the 'yield' keyword.",
                        "sample_answer": "Generators are special iterator functions that use the 'yield' keyword to produce values lazily on-demand. When a generator function is called, it returns a generator object without executing the body immediately. When next() is called on it, code executes until it hits 'yield', yields the value, and suspends its execution state (including local variables and instruction pointer). When processing gigabytes of log files, creating a list of lines with readlines() would exhaust RAM and cause an Out-Of-Memory error. A generator reads one line at a time, keeping memory consumption constant at O(1) regardless of file size.",
                        "follow_up": "What is the syntax difference between a list comprehension and a generator expression?"
                    },
                    {
                        "question": "Explain how Python decorators work, and write a quick example of a timer decorator that logs execution time.",
                        "level": "Intermediate",
                        "category": "Functional Patterns",
                        "hint": "Decorators are higher-order functions that take a function, wrap it, and return a new function.",
                        "sample_answer": "In Python, functions are first-class citizens: they can be passed as arguments, assigned to variables, and returned from other functions. A decorator is a higher-order function that takes a target function, wraps additional functionality around it, and returns the wrapper. Using the '@decorator_name' syntax is syntactic sugar for 'target = decorator_name(target)'. To build a timer decorator: we define a function taking 'func', define an inner '*args, **kwargs' wrapper using 'functools.wraps(func)', record start time with time.perf_counter(), call the original func, calculate elapsed time, and return the result.",
                        "follow_up": "Why is @functools.wraps(func) recommended when creating custom decorators?"
                    },
                    {
                        "question": "What is the difference between shallow copy (copy.copy) and deep copy (copy.deepcopy) in Python?",
                        "level": "Intermediate",
                        "category": "Data Structures & Memory",
                        "hint": "Focus on nested compound objects like a list of lists or dict of dicts.",
                        "sample_answer": "A shallow copy creates a new outer compound object, but inserts references into it to the exact same child objects found in the original. Thus, if a list contains inner lists, mutating an inner list in the copy also mutates the original. A deep copy, created via copy.deepcopy(), recursively traverses the entire object tree and duplicates every compound object it encounters, ensuring completely detached, independent memory addresses for all nested elements.",
                        "follow_up": "How does slicing a list with a[:] behave with respect to shallow vs deep copying?"
                    }
                ]

        # REACT & FRONTEND
        elif any(k in sk for k in ('react', 'frontend', 'javascript', 'typescript', 'next')):
            return [
                {
                    "question": "How does React's Reconciliation algorithm and Virtual DOM diffing work, and why are stable 'key' props essential?",
                    "level": "Intermediate",
                    "category": "React Internals",
                    "hint": "Explain the O(n) heuristic diffing algorithm, fiber tree comparisons, and what happens when index is used as a key in dynamic lists.",
                    "sample_answer": "React maintains an in-memory representation of the UI called the Virtual DOM (Fiber tree). When state changes, a new Virtual DOM tree is constructed. A naive tree diff algorithm is O(n^3); React optimizes this to O(n) using two heuristics: elements of different types generate completely different trees, and lists of elements can be matched across renders using stable 'key' props. If keys are missing or array indexes are used in lists that can be reordered or filtered, React matches items by index position rather than identity, causing input state mismatches, incorrect re-renders, and animation glitches.",
                    "follow_up": "What is the difference between the Render phase and the Commit phase in React 18+?"
                },
                {
                    "question": "Explain the JavaScript Event Loop, Call Stack, Microtask Queue (Promises), and Macrotask Queue (setTimeout).",
                    "level": "Intermediate",
                    "category": "JavaScript Runtime",
                    "hint": "Walk through execution order: synchronous script -> all microtasks -> render -> one macrotask.",
                    "sample_answer": "JavaScript is single-threaded with a non-blocking concurrent runtime. Synchronous code executes directly on the Call Stack. Asynchronous callbacks are delegated to browser Web APIs or Node libuv. When async tasks finish, callbacks enter queues: Microtasks (Promise.then, queueMicrotask, MutationObserver) have higher priority than Macrotasks (setTimeout, setInterval, I/O). When the Call Stack empties, the Event Loop flushes ALL pending microtasks before executing the next single macrotask. Thus, a resolved Promise.then callback always runs before a setTimeout(fn, 0) callback.",
                    "follow_up": "What happens if microtasks keep scheduling more microtasks recursively?"
                },
                {
                    "question": "What is the difference between useEffect, useLayoutEffect, and useMemo, and when should each be used?",
                    "level": "Intermediate",
                    "category": "React Hooks & Performance",
                    "hint": "Compare asynchronous execution after browser paint vs synchronous execution before paint.",
                    "sample_answer": "useEffect runs asynchronously AFTER the browser has painted the DOM changes to screen, making it ideal for API calls, subscriptions, and non-visual side effects. useLayoutEffect runs synchronously immediately AFTER React mutates the DOM but BEFORE the browser paints; it should be used exclusively for measuring DOM layout (e.g. scroll positions, tooltip coordinates) to prevent visible UI flickering. useMemo is not for side effects; it memoizes the calculated result of an expensive pure computation between renders until its dependency array changes.",
                    "follow_up": "How does useCallback relate to useMemo?"
                },
                {
                    "question": "What problem do TypeScript Generics solve, and how would you type a function that merges two objects with combined type inference?",
                    "level": "Intermediate",
                    "category": "TypeScript Type System",
                    "hint": "Show how <T, U> preserves compile-time types instead of falling back to 'any'.",
                    "sample_answer": "Generics enable creating reusable components and functions that work across a variety of types while preserving complete compile-time type safety. Instead of losing type information with 'any', generics capture the concrete types provided by callers. To merge two objects: 'function merge<T extends object, U extends object>(a: T, b: U): T & U { return { ...a, ...b }; }'. TypeScript automatically infers the intersection type 'T & U', allowing autocomplete and type checking on properties from both objects.",
                    "follow_up": "What is the key difference between 'type' and 'interface' in modern TypeScript?"
                }
            ]

        # SQL & DATABASES
        elif any(k in sk for k in ('sql', 'database', 'postgres', 'mysql', 'indexing')):
            return [
                {
                    "question": "How do B-Tree indexes accelerate SELECT queries, and what causes an index to be bypassed by the query optimizer?",
                    "level": "Intermediate",
                    "category": "Database Internals & Indexing",
                    "hint": "Explain logarithmic tree traversal, leading column matching in composite indexes, and function wrappers on indexed columns.",
                    "sample_answer": "A B-Tree index organizes table keys in a balanced tree structure where root, branch, and leaf nodes are sorted. A lookup traverses from root to leaf in O(log N) page reads, drastically faster than an O(N) full table scan. However, an index is bypassed if: 1) You wrap the column in a function (e.g. WHERE LOWER(email) = '...' unless a functional index exists), 2) You perform wildcard searches starting with % (e.g. LIKE '%term'), 3) You query secondary columns of a composite index without filtering on the leading column, or 4) The table is small enough that the optimizer calculates sequential disk scanning is cheaper than random index lookups.",
                    "follow_up": "What is the difference between a Clustered index and a Non-Clustered index?"
                },
                {
                    "question": "Explain the 4 ACID properties of relational transactions and how transaction isolation levels balance consistency vs concurrency.",
                    "level": "Intermediate",
                    "category": "Transactions & Concurrency",
                    "hint": "Atomicity, Consistency, Isolation, Durability. Mention Dirty Reads, Non-repeatable Reads, and Phantom Reads.",
                    "sample_answer": "ACID guarantees reliability: Atomicity (all operations commit or all rollback), Consistency (data satisfies all schema constraints), Isolation (concurrent transactions execute without interfering), Durability (committed data survives server crashes via WAL). SQL defines 4 isolation levels: Read Uncommitted (allows dirty reads), Read Committed (prevents dirty reads using row locks or MVCC snapshots), Repeatable Read (guarantees rows read stay identical throughout transaction; prevents non-repeatable reads), and Serializable (strict serial order; prevents phantom reads by locking ranges). Higher isolation provides stronger consistency at the cost of reduced concurrency and higher lock contention.",
                    "follow_up": "How does Multi-Version Concurrency Control (MVCC) in PostgreSQL prevent readers from blocking writers?"
                },
                {
                    "question": "What is database normalization, and when is deliberate denormalization justified in production systems?",
                    "level": "Intermediate",
                    "category": "Schema Architecture",
                    "hint": "Discuss 1NF, 2NF, 3NF elimination of redundancy, and compare with read-heavy analytics or reporting systems.",
                    "sample_answer": "Database normalization is the process of structuring relational tables to eliminate data redundancy and insertion, update, and deletion anomalies. 1NF ensures atomic values, 2NF removes partial key dependencies, and 3NF ensures no transitive dependencies (non-key columns depend only on primary key). Normalization is ideal for write-heavy OLTP systems. Deliberate denormalization is justified in read-heavy analytics (OLAP), high-scale dashboards, or caching layers where joining 6 normalized tables causes unacceptable query latency. Storing precomputed aggregates or duplicating specific columns trades disk space and write overhead for instant read response times.",
                    "follow_up": "What is the purpose of a foreign key cascade delete constraint?"
                },
                {
                    "question": "What are SQL Window Functions, and how does 'ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)' work?",
                    "level": "Intermediate",
                    "category": "Analytical SQL",
                    "hint": "Window functions perform calculations across a set of table rows related to the current row without collapsing rows like GROUP BY.",
                    "sample_answer": "Unlike GROUP BY, which collapses multiple rows into a single aggregated row, Window Functions compute metrics across a defined subset of rows while retaining individual row identities. In 'ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC)', 'PARTITION BY' divides rows into independent groups (departments), and 'ORDER BY' sorts rows within each partition. ROW_NUMBER() assigns a unique sequential integer starting at 1 to each row in the group. This is the standard pattern for solving 'top N items per category' queries.",
                    "follow_up": "How do RANK() and DENSE_RANK() differ when two rows have identical values?"
                }
            ]

        # GENERAL FALLBACK (Customized specifically for the skill)
        return [
            {
                "question": f"What architectural patterns and clean code principles are most critical when designing production applications with {skill}?",
                "level": level.capitalize(),
                "category": f"{skill} Architecture",
                "hint": f"Discuss separation of concerns, modularity, and error boundary isolation in {skill}.",
                "sample_answer": f"When scaling systems built with {skill}, adhering to Single Responsibility and Separation of Concerns is paramount. Core business domain logic should remain decoupled from external I/O protocols and frameworks. Inputs must be validated at system boundaries with structured schemas, and errors handled explicitly through domain-specific exceptions rather than generic catches. Implementing dependency injection allows mocking external services for deterministic unit tests.",
                "follow_up": f"How do you test and verify edge case handling in {skill} applications?"
            },
            {
                "question": f"How do you identify, profile, and resolve performance bottlenecks when using {skill} in high-throughput environments?",
                "level": level.capitalize(),
                "category": "Performance & Optimization",
                "hint": f"Think about CPU profiling, memory leaks, I/O latency, and caching strategies applicable to {skill}.",
                "sample_answer": f"Performance optimization in {skill} begins with empirical measurement rather than premature guessing. We profile hot paths using runtime profilers to inspect CPU hotspots and heap memory allocation graphs. Common bottlenecks typically stem from redundant I/O roundtrips, unindexed database queries, or inefficient memory retention causing GC thrashing. Resolving these involves introducing caching layers, connection pooling, and asynchronous batching.",
                "follow_up": f"What metrics would you monitor in production to detect performance regressions in {skill}?"
            },
            {
                "question": f"Explain the security best practices and common vulnerability vectors developers must guard against when building with {skill}.",
                "level": level.capitalize(),
                "category": "Security Engineering",
                "hint": "Consider input sanitization, secret management, authentication, and dependency audits.",
                "sample_answer": f"Security in {skill} requires defense-in-depth: never trusting client inputs, enforcing parameterized queries or ORM validation to prevent injection, and protecting against denial-of-service through strict payload size limits and rate limiting. Secrets and API keys must never be committed to source control, but injected via environment variables. Regularly scanning dependencies with vulnerability scanners (e.g. Snyk, Dependabot) ensures third-party vulnerabilities are patched promptly.",
                "follow_up": f"How do you handle safe secret rotation in production environments running {skill}?"
            },
            {
                "question": f"Describe a complex debugging scenario you encountered with {skill}, your methodical diagnostic process, and the permanent resolution.",
                "level": level.capitalize(),
                "category": "Real-World Troubleshooting",
                "hint": "Structure your response using the STAR method: Situation, Task, Action, Result.",
                "sample_answer": f"A classic high-impact challenge with {skill} involves intermittent race conditions or memory leaks under concurrent load. The diagnostic methodology involves reproducing the issue in an isolated staging environment using load generators, analyzing structured application logs and distributed traces to locate the exact failing component, writing a failing regression test, and applying the minimal architectural fix (e.g. idempotent retry logic or resource pooling).",
                "follow_up": f"What monitoring alerts would you configure to catch this issue before users are impacted?"
            }
        ]

# Single shared instance of the AI service
gemini_service = GeminiService()