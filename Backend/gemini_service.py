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

    def _call_gemini(self, prompt, max_tokens=2500):
        if not self.api_key or not self.api_url:
            return None

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": max_tokens}
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

        # 1. Try Gemini AI with explicit level, count, and strict skill-specific prompt
        prompt = (
            f"You are a Senior Technical Examiner and Software Engineering Director.\n"
            f"Generate exactly {count} multiple-choice technical verification questions SPECIFICALLY testing '{normalized_skill}' at '{normalized_level.upper()}' difficulty level.\n"
            f"CRITICAL RULES:\n"
            f"1. Every question MUST be directly relevant to '{normalized_skill}' — testing its specific syntax, standard libraries, APIs, runtime behavior, data types, memory characteristics, or architectural design patterns.\n"
            f"2. Under NO circumstance should you generate generic software questions like 'What is unit testing?' or 'Why use version control?'.\n"
            f"3. Calibrate depth to '{normalized_level.upper()}':\n"
            f"   - Beginner: Syntax, basic operators, fundamental idioms, common built-in methods.\n"
            f"   - Intermediate: Real-world patterns, error handling, performance nuances, standard packages.\n"
            f"   - Advanced: Internals, concurrency, low-level mechanics, optimizations, architectural trade-offs.\n"
            f"4. Provide 4 realistic options (keys 'A', 'B', 'C', 'D') with one unambiguous correct answer ('A', 'B', 'C', or 'D').\n"
            f"Return ONLY a valid JSON list of {count} objects with keys: 'question_text', 'options' (object with 'A', 'B', 'C', 'D'), and 'correct_answer'."
        )
        raw_ai = self._call_gemini(prompt)
        questions = []
        if raw_ai:
            try:
                clean = raw_ai.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean)
                if isinstance(parsed, list) and len(parsed) >= 4:
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
        """Curated skill-specific technical banks for top languages and frameworks by difficulty."""
        sk = skill_name.lower()

        # 1. PYTHON
        if 'python' in sk:
            if level == 'beginner':
                return [
                    {"question_text": "Which of the following is an immutable data type in Python?", "options": {"A": "List", "B": "Tuple", "C": "Set", "D": "Dictionary"}, "correct_answer": "B"},
                    {"question_text": "What will type(7 / 2) return in Python 3?", "options": {"A": "int", "B": "float", "C": "double", "D": "number"}, "correct_answer": "B"},
                    {"question_text": "Which keyword is used to define a function in Python?", "options": {"A": "func", "B": "function", "C": "def", "D": "define"}, "correct_answer": "C"},
                    {"question_text": "Which method removes and returns the last item from a list in Python?", "options": {"A": ".pop()", "B": ".remove()", "C": ".delete()", "D": ".pull()"}, "correct_answer": "A"},
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
            else: # Intermediate
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

        # 2. REACT & FRONTEND
        elif any(k in sk for k in ('react', 'frontend', 'redux', 'next')):
            if level == 'beginner':
                return [
                    {"question_text": "What is JSX in React development?", "options": {"A": "A new browser engine", "B": "A syntax extension allowing HTML-like markup inside JavaScript", "C": "A database query language", "D": "A CSS preprocessor"}, "correct_answer": "B"},
                    {"question_text": "Which React hook is used to declare state variables in a functional component?", "options": {"A": "useEffect", "B": "useMemo", "C": "useState", "D": "useReducer"}, "correct_answer": "C"},
                    {"question_text": "Why must every element in a dynamically rendered list have a unique 'key' prop?", "options": {"A": "To add CSS styling", "B": "To help React identify which items have changed, added, or removed during diffing", "C": "To prevent browser caching", "D": "To sort elements automatically"}, "correct_answer": "B"},
                    {"question_text": "How is data typically passed from a parent component down to a child component in React?", "options": {"A": "Through props", "B": "Through local storage", "C": "Through global window variables", "D": "Through SQL queries"}, "correct_answer": "A"},
                    {"question_text": "Which hook is designed to handle side effects like data fetching or subscriptions?", "options": {"A": "useState", "B": "useEffect", "C": "useRef", "D": "useContext"}, "correct_answer": "B"},
                    {"question_text": "What happens when a React component's state is updated via its setter function?", "options": {"A": "The browser completely reloads", "B": "The component and its children re-render with updated state", "C": "The component is permanently unmounted", "D": "The database updates automatically"}, "correct_answer": "B"},
                    {"question_text": "What is a React Fragment (<>...</>) used for?", "options": {"A": "Grouping multiple elements without adding an extra DOM node", "B": "Speeding up API requests", "C": "Compiling TypeScript", "D": "Creating animation frames"}, "correct_answer": "A"},
                    {"question_text": "How do you bind a button click event in React JSX?", "options": {"A": "onclick='handleClick()'", "B": "onClick={handleClick}", "C": "click={handleClick}", "D": "on:click={handleClick}"}, "correct_answer": "B"},
                    {"question_text": "Can a child component directly mutate its received props in React?", "options": {"A": "Yes, anytime", "B": "No, props are strictly read-only and immutable", "C": "Only if they are numbers", "D": "Only inside useEffect"}, "correct_answer": "B"},
                    {"question_text": "What is the recommended syntax for conditional rendering in JSX?", "options": {"A": "if-else tags", "B": "Ternary operator (condition ? <A/> : <B/>) or logical AND (&&)", "C": "switch-case tags", "D": "while loops"}, "correct_answer": "B"}
                ]
            else: # Intermediate / Advanced
                return [
                    {"question_text": "What is React's Virtual DOM Reconciliation algorithm based on?", "options": {"A": "O(n^3) matrix multiplication", "B": "A heuristic diffing algorithm that compares Fiber trees in O(n) linear time", "C": "Direct innerHTML string replacement", "D": "Browser shadow DOM duplication"}, "correct_answer": "B"},
                    {"question_text": "How does useCallback differ from useMemo in React?", "options": {"A": "useCallback memoizes a function reference; useMemo memoizes a computed value", "B": "useCallback runs on server; useMemo runs on client", "C": "useMemo is only for strings", "D": "There is no difference"}, "correct_answer": "A"},
                    {"question_text": "What does returning a function from inside useEffect accomplish?", "options": {"A": "Triggers an immediate error", "B": "Defines a cleanup function that runs before unmount or prior to the next effect execution", "C": "Forces a synchronous re-render", "D": "Saves state to local storage"}, "correct_answer": "B"},
                    {"question_text": "What is a 'stale closure' bug in React functional components?", "options": {"A": "CSS style inheritance bug", "B": "When an effect or callback captures outdated state/props due to omitted dependencies", "C": "When a network socket disconnects", "D": "A syntax error in JSX tags"}, "correct_answer": "B"},
                    {"question_text": "What does the useRef hook provide that useState does not?", "options": {"A": "A mutable .current object whose changes persist without triggering component re-renders", "B": "Automatic API re-fetching", "C": "Two-way data binding", "D": "Global browser cookies"}, "correct_answer": "A"},
                    {"question_text": "What problem does the React Context API solve?", "options": {"A": "Database normalization", "B": "Eliminates prop drilling by making state accessible across deep component trees", "C": "Server-side load balancing", "D": "Automated E2E testing"}, "correct_answer": "B"},
                    {"question_text": "What is the difference between controlled and uncontrolled input elements?", "options": {"A": "Controlled inputs have their value driven by React state; uncontrolled rely on DOM refs", "B": "Controlled inputs cannot be typed into", "C": "Uncontrolled inputs are deprecated in HTML5", "D": "Controlled inputs do not support validation"}, "correct_answer": "A"},
                    {"question_text": "When should useLayoutEffect be preferred over useEffect?", "options": {"A": "For long-running background API calls", "B": "When measuring DOM layout synchronously before browser paint to prevent layout flickering", "C": "When logging telemetry to the server", "D": "Only when rendering SVG graphics"}, "correct_answer": "B"},
                    {"question_text": "What does React 18's startTransition API allow developers to do?", "options": {"A": "Mark state updates as non-urgent transitions so urgent interactions remain responsive", "B": "Animate CSS opacity automatically", "C": "Restart the React server", "D": "Upgrade npm packages at runtime"}, "correct_answer": "A"},
                    {"question_text": "What does the React.memo higher-order component do?", "options": {"A": "Caches HTTP responses", "B": "Prevents component re-rendering if its props have not shallowly changed", "C": "Validates prop types with schema", "D": "Compiles JSX to WebAssembly"}, "correct_answer": "B"}
                ]

        # 3. SQL & DATABASES
        elif any(k in sk for k in ('sql', 'database', 'postgres', 'mysql', 'sqlite', 'db')):
            if level == 'beginner':
                return [
                    {"question_text": "Which SQL clause is used to filter records before any grouping or aggregation takes place?", "options": {"A": "HAVING", "B": "WHERE", "C": "ORDER BY", "D": "LIMIT"}, "correct_answer": "B"},
                    {"question_text": "What does SELECT DISTINCT column_name FROM table accomplish?", "options": {"A": "Returns only unique, non-duplicate values for the specified column", "B": "Sorts the column in reverse", "C": "Deletes duplicate rows permanently", "D": "Counts the total rows"}, "correct_answer": "A"},
                    {"question_text": "Which SQL clause sorts the returned records in ascending or descending order?", "options": {"A": "GROUP BY", "B": "ORDER BY", "C": "SORT BY", "D": "FILTER BY"}, "correct_answer": "B"},
                    {"question_text": "What is a PRIMARY KEY in a relational database table?", "options": {"A": "A key that can contain NULL values", "B": "A unique identifier for each row that cannot contain NULL values", "C": "An optional description field", "D": "A foreign reference to another database"}, "correct_answer": "B"},
                    {"question_text": "What type of SQL JOIN returns only rows that have matching values in both tables?", "options": {"A": "LEFT JOIN", "B": "FULL OUTER JOIN", "C": "INNER JOIN", "D": "CROSS JOIN"}, "correct_answer": "C"},
                    {"question_text": "Which aggregate function calculates the total number of rows matching a condition?", "options": {"A": "SUM()", "B": "COUNT()", "C": "TOTAL()", "D": "LEN()"}, "correct_answer": "B"},
                    {"question_text": "Which statement is used to insert new records into a database table?", "options": {"A": "ADD RECORD", "B": "INSERT INTO", "C": "UPDATE TABLE", "D": "APPEND ROW"}, "correct_answer": "B"},
                    {"question_text": "In a SQL LIKE pattern, which wildcard matches zero or more characters?", "options": {"A": "?", "B": "*", "C": "%", "D": "#"}, "correct_answer": "C"},
                    {"question_text": "What is the purpose of the GROUP BY clause?", "options": {"A": "Collapses rows that share the same values into summary aggregation rows", "B": "Deletes duplicate records", "C": "Creates a foreign key constraint", "D": "Limits query output to 10 rows"}, "correct_answer": "A"},
                    {"question_text": "What happens if DELETE FROM users; is executed without a WHERE clause?", "options": {"A": "Nothing happens without WHERE", "B": "All rows in the users table will be deleted", "C": "Only the first row is deleted", "D": "A syntax error is thrown"}, "correct_answer": "B"}
                ]
            else: # Intermediate / Advanced
                return [
                    {"question_text": "How does the HAVING clause differ from the WHERE clause in SQL?", "options": {"A": "HAVING filters aggregated groups after GROUP BY; WHERE filters individual rows before grouping", "B": "HAVING is for primary keys only", "C": "WHERE can only be used with subqueries", "D": "There is no difference"}, "correct_answer": "A"},
                    {"question_text": "What is the key performance difference between an Index Seek and an Index Scan?", "options": {"A": "Index Seek navigates the B-Tree directly to target rows; Index Scan reads all leaf pages", "B": "Index Scan is always faster than Seek", "C": "Index Seek locks the entire database", "D": "Index Scan requires no disk reads"}, "correct_answer": "A"},
                    {"question_text": "What does the ACID acronym guarantee in relational database transactions?", "options": {"A": "Atomicity, Consistency, Isolation, Durability", "B": "Access, Concurrency, Indexing, Delivery", "C": "Authentication, Cryptography, Integrity, Deployment", "D": "Array, Collection, Iteration, Dequeue"}, "correct_answer": "A"},
                    {"question_text": "What does ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) produce?", "options": {"A": "A sequential rank number within each department partition ordered by salary", "B": "The average salary per department", "C": "The sum of all rows", "D": "A random primary key"}, "correct_answer": "A"},
                    {"question_text": "What does a Foreign Key constraint enforce?", "options": {"A": "Referential integrity by ensuring values match a primary key in another table", "B": "Data encryption at rest", "C": "Automatic indexing on all columns", "D": "Read-only access permissions"}, "correct_answer": "A"},
                    {"question_text": "In transaction isolation levels, what is a 'Dirty Read'?", "options": {"A": "Reading uncommitted changes from another concurrent transaction that might be rolled back", "B": "Reading corrupted disk sectors", "C": "A syntax error in SELECT statement", "D": "A read that takes more than 1 second"}, "correct_answer": "A"},
                    {"question_text": "What is the difference between a LEFT JOIN and a FULL OUTER JOIN?", "options": {"A": "LEFT JOIN returns all left rows plus matching right; FULL OUTER returns all rows from both tables", "B": "FULL OUTER JOIN is only for numbers", "C": "LEFT JOIN drops unmatched left rows", "D": "They produce identical execution plans"}, "correct_answer": "A"},
                    {"question_text": "What is Database Normalization (such as 3NF) primarily designed to achieve?", "options": {"A": "Eliminate redundant data and prevent insertion, update, and deletion anomalies", "B": "Speed up full table scans", "C": "Merge all tables into a single wide table", "D": "Compress data files on disk"}, "correct_answer": "A"},
                    {"question_text": "Why can adding too many B-Tree indexes negatively impact write-heavy workloads?", "options": {"A": "Every INSERT, UPDATE, and DELETE must synchronously update all corresponding index trees", "B": "Indexes delete historical records", "C": "Indexes prevent database backups", "D": "Indexes disable foreign keys"}, "correct_answer": "A"},
                    {"question_text": "What is the purpose of running an EXPLAIN or EXPLAIN ANALYZE command?", "options": {"A": "Displays the execution plan, estimated cost, and index usage chosen by the query planner", "B": "Defragments the database tables", "C": "Exports tables to CSV format", "D": "Encrypts database passwords"}, "correct_answer": "A"}
                ]

        # 4. JAVASCRIPT & TYPESCRIPT
        elif any(k in sk for k in ('javascript', 'typescript', 'js', 'ts', 'node')):
            if level == 'beginner':
                return [
                    {"question_text": "What is the difference between let and const in modern JavaScript?", "options": {"A": "const cannot be reassigned; let can be reassigned; both are block-scoped", "B": "let is global; const is local", "C": "const is only for numbers", "D": "There is no difference"}, "correct_answer": "A"},
                    {"question_text": "What is the output of typeof null in JavaScript?", "options": {"A": "'null'", "B": "'undefined'", "C": "'object'", "D": "'boolean'"}, "correct_answer": "C"},
                    {"question_text": "What does the strict equality operator (===) check?", "options": {"A": "Checks both value and data type without implicit type conversion", "B": "Checks value only, converting types", "C": "Assigns a variable", "D": "Compares object references only"}, "correct_answer": "A"},
                    {"question_text": "What does Array.prototype.map() return in JavaScript?", "options": {"A": "A new array containing the results of applying the callback function to each item", "B": "The original mutated array", "C": "The length of the array", "D": "A single reduced value"}, "correct_answer": "A"},
                    {"question_text": "How do arrow functions (() => {}) handle the 'this' keyword?", "options": {"A": "They inherit 'this' lexically from the enclosing scope", "B": "They bind 'this' to the global window always", "C": "They rebind 'this' on every call", "D": "They cannot access variables outside"}, "correct_answer": "A"},
                    {"question_text": "What will Boolean('') and Boolean(0) evaluate to in JavaScript?", "options": {"A": "true", "B": "false", "C": "undefined", "D": "TypeError"}, "correct_answer": "B"},
                    {"question_text": "What is a Promise in JavaScript?", "options": {"A": "An object representing the eventual completion or failure of an asynchronous operation", "B": "A synchronous loop construct", "C": "A database transaction", "D": "A CSS animation wrapper"}, "correct_answer": "A"},
                    {"question_text": "Which built-in method parses a valid JSON string into a native JavaScript object?", "options": {"A": "JSON.stringify()", "B": "JSON.parse()", "C": "JSON.toObject()", "D": "JSON.decode()"}, "correct_answer": "B"},
                    {"question_text": "In TypeScript, what is the syntax to declare an array of numbers?", "options": {"A": "number[] or Array<number>", "B": "list<number>", "C": "[number]", "D": "numbers.array"}, "correct_answer": "A"},
                    {"question_text": "What does template literal syntax (`${val}`) allow in JavaScript?", "options": {"A": "String interpolation and multi-line strings enclosed in backticks", "B": "Regular expression pattern matching only", "C": "Binary bit shifting", "D": "HTML DOM sanitization"}, "correct_answer": "A"}
                ]
            else: # Intermediate / Advanced
                return [
                    {"question_text": "How does the JavaScript Event Loop prioritize the Microtask Queue versus the Macrotask Queue?", "options": {"A": "Microtasks (Promise callbacks) execute immediately after the current script, before the next macrotask (setTimeout)", "B": "Macrotasks always run first", "C": "They run concurrently on two threads", "D": "Microtasks run only when the browser tab is hidden"}, "correct_answer": "A"},
                    {"question_text": "What is a Closure in JavaScript?", "options": {"A": "A function bundled together with references to its surrounding lexical environment", "B": "A method to close browser tabs", "C": "A syntax error that prevents script execution", "D": "A CSS pseudo-selector"}, "correct_answer": "A"},
                    {"question_text": "In TypeScript, how does an 'interface' differ from a 'type' alias?", "options": {"A": "Interfaces support declaration merging; types can model unions and primitive aliases", "B": "Types are compiled to runtime objects; interfaces are deleted", "C": "Interfaces cannot have properties", "D": "Types cannot be used with functions"}, "correct_answer": "A"},
                    {"question_text": "What happens when one promise passed into Promise.all() rejects?", "options": {"A": "Promise.all immediately rejects with that error, ignoring pending promises", "B": "Promise.all returns null", "C": "It waits for all others then returns partial data", "D": "It retries the failed promise 3 times"}, "correct_answer": "A"},
                    {"question_text": "What is prototypical inheritance in JavaScript?", "options": {"A": "Objects inherit properties and methods directly from other objects via their prototype chain", "B": "Classical class inheritance compiled to C++ structs", "C": "Copying all methods into every instance memory address", "D": "Thread-safe immutable state cloning"}, "correct_answer": "A"},
                    {"question_text": "What does the TypeScript 'keyof' type operator do?", "options": {"A": "Produces a union type of string or numeric literal keys of an object type", "B": "Returns the number of keys at runtime", "C": "Deletes a property from an object", "D": "Generates a random UUID key"}, "correct_answer": "A"},
                    {"question_text": "What is variable and function hoisting in JavaScript?", "options": {"A": "Declarations are moved to the top of their scope during compilation before code execution", "B": "Uploading code to a remote server", "C": "Converting synchronous code to async", "D": "Garbage collecting unused memory"}, "correct_answer": "A"},
                    {"question_text": "What is the difference between debouncing and throttling?", "options": {"A": "Debounce delays execution until X ms of quiet time; throttle enforces execution at most once per X ms interval", "B": "Throttle cancels all calls; debounce runs them all", "C": "Debounce is only for scroll events", "D": "They are identical techniques"}, "correct_answer": "A"},
                    {"question_text": "In TypeScript, what is the key difference between 'unknown' and 'any'?", "options": {"A": "'unknown' is type-safe and requires type narrowing before operations; 'any' disables all checks", "B": "'unknown' cannot be assigned any value", "C": "'any' is only available in strict mode", "D": "'unknown' is converted to string at runtime"}, "correct_answer": "A"},
                    {"question_text": "What is the output of [1, 2, 3] + [4, 5, 6] in JavaScript?", "options": {"A": "'1,2,34,5,6' due to implicit array-to-string coercion", "B": "[1, 2, 3, 4, 5, 6]", "C": "TypeError", "D": "NaN"}, "correct_answer": "A"}
                ]

        # 5. DEVOPS, DOCKER & CLOUD
        elif any(k in sk for k in ('devops', 'docker', 'kubernetes', 'k8s', 'linux', 'cloud', 'aws', 'ci/cd')):
            if level == 'beginner':
                return [
                    {"question_text": "What is a Docker container?", "options": {"A": "A standalone, lightweight package containing application code and runtime dependencies", "B": "A virtual machine hypervisor", "C": "A database table partition", "D": "A git branch"}, "correct_answer": "A"},
                    {"question_text": "Which Dockerfile instruction specifies the base parent image?", "options": {"A": "BASE", "B": "FROM", "C": "IMAGE", "D": "START"}, "correct_answer": "B"},
                    {"question_text": "Which command builds a Docker image named 'my-app' from the current directory?", "options": {"A": "docker create my-app", "B": "docker build -t my-app .", "C": "docker compile my-app", "D": "docker image new"}, "correct_answer": "B"},
                    {"question_text": "What is the difference between a Docker Image and a Docker Container?", "options": {"A": "An image is a static read-only blueprint; a container is a runnable isolated instance", "B": "A container cannot be stopped", "C": "An image runs directly on bare metal", "D": "There is no difference"}, "correct_answer": "A"},
                    {"question_text": "Which command lists all currently running Docker containers?", "options": {"A": "docker ps", "B": "docker list", "C": "docker running", "D": "docker show"}, "correct_answer": "A"},
                    {"question_text": "What is the purpose of Docker Volumes?", "options": {"A": "Persisting container data independently of the container lifecycle", "B": "Increasing CPU speed", "C": "Compressing container logs", "D": "Encrypting network packets"}, "correct_answer": "A"},
                    {"question_text": "In 'docker run -p 8080:80 nginx', what does '-p 8080:80' mean?", "options": {"A": "Forwards host port 8080 to container port 80", "B": "Allocates 8080 MB of RAM", "C": "Runs 8080 threads", "D": "Sets priority level 80"}, "correct_answer": "A"},
                    {"question_text": "What does the Linux command 'chmod +x script.sh' do?", "options": {"A": "Grants executable permissions to script.sh", "B": "Deletes script.sh", "C": "Compresses script.sh", "D": "Renames script.sh"}, "correct_answer": "A"},
                    {"question_text": "Which protocol provides secure encrypted terminal communication with remote Linux servers?", "options": {"A": "Telnet", "B": "FTP", "C": "SSH", "D": "HTTP"}, "correct_answer": "C"},
                    {"question_text": "What is Continuous Integration (CI) in software delivery?", "options": {"A": "Automatically building and testing code changes on every commit", "B": "Manually deploying servers on weekends", "C": "Writing documentation for users", "D": "Billing clients monthly"}, "correct_answer": "A"}
                ]
            else: # Intermediate / Advanced
                return [
                    {"question_text": "What is the primary benefit of Multi-Stage Docker builds?", "options": {"A": "Dramatically reduces final image size by discarding build tools and intermediate artifacts", "B": "Allows multiple containers to run in one pod", "C": "Encrypts source code with AES-256", "D": "Eliminates need for Docker daemon"}, "correct_answer": "A"},
                    {"question_text": "In Kubernetes, what is a Pod?", "options": {"A": "The smallest deployable unit representing one or more closely coupled containers", "B": "A physical server in a data center", "C": "A virtual private cloud network", "D": "A database storage volume"}, "correct_answer": "A"},
                    {"question_text": "How does a Kubernetes Service differ from an Ingress resource?", "options": {"A": "A Service manages internal L4 load balancing; an Ingress manages external L7 HTTP/HTTPS routing", "B": "Services are only for databases", "C": "An Ingress can only route TCP traffic", "D": "They are deprecated synonyms"}, "correct_answer": "A"},
                    {"question_text": "What does Infrastructure as Code (IaC) with tools like Terraform accomplish?", "options": {"A": "Declaratively provisions and versions cloud resources through reproducible configuration code", "B": "Compiles JavaScript to C++", "C": "Monitors CPU fan speeds", "D": "Generates mock database records"}, "correct_answer": "A"},
                    {"question_text": "What does the Docker container restart policy 'unless-stopped' ensure?", "options": {"A": "Restarts container automatically on failure or reboot unless explicitly stopped by user", "B": "Restarts container every 5 minutes", "C": "Prevents the container from ever terminating", "D": "Stops container when memory exceeds 50%"}, "correct_answer": "A"},
                    {"question_text": "What is a Reverse Proxy (like Nginx) commonly deployed for?", "options": {"A": "Load balancing, SSL/TLS termination, and caching upstream backend traffic", "B": "Compiling kernel drivers", "C": "Writing SQL migration scripts", "D": "Managing git repositories"}, "correct_answer": "A"},
                    {"question_text": "How does a Blue-Green deployment strategy achieve zero downtime?", "options": {"A": "Maintains two identical production environments, switching router traffic instantly", "B": "Deploys to 10% of users first", "C": "Shuts down the database during upgrades", "D": "Requires users to re-login"}, "correct_answer": "A"},
                    {"question_text": "What is Prometheus primarily designed for in cloud-native observability?", "options": {"A": "Scraping, storing, and alerting on numerical time-series metrics over HTTP", "B": "Storing video files", "C": "Managing user passwords", "D": "Replacing relational databases"}, "correct_answer": "A"},
                    {"question_text": "In Linux permissions, what access does 'chmod 755 filename' grant?", "options": {"A": "Read, write, execute for owner; read and execute for group and others", "B": "Full permissions for everyone", "C": "Read-only for all users", "D": "Execute only for owner"}, "correct_answer": "A"},
                    {"question_text": "What metric does the Kubernetes Horizontal Pod Autoscaler (HPA) typically scale on by default?", "options": {"A": "Observed CPU and memory utilization thresholds", "B": "Number of git commits", "C": "Total disk size of the node", "D": "Clock time of the day"}, "correct_answer": "A"}
                ]

        # 6. JAVA & OOP
        elif any(k in sk for k in ('java', 'spring', 'oop')):
            return [
                {"question_text": "In Java, what is the difference between '==' and the '.equals()' method?", "options": {"A": "'==' compares object memory references; '.equals()' compares logical object equality", "B": "They are identical in all cases", "C": "'.equals()' is only for numbers", "D": "'==' is deprecated in Java 17"}, "correct_answer": "A"},
                {"question_text": "What is the primary role of the Java Virtual Machine (JVM)?", "options": {"A": "Executes compiled Java bytecode on the host operating system", "B": "Formats source code files", "C": "Manages Git repositories", "D": "Acts as an HTTP web server"}, "correct_answer": "A"},
                {"question_text": "Why is Java considered platform independent?", "options": {"A": "Java source compiles into bytecode that executes on any operating system with a JVM", "B": "It has no dependencies", "C": "It runs inside HTML directly", "D": "It compiles directly to x86 machine code"}, "correct_answer": "A"},
                {"question_text": "What is the difference between an Abstract Class and an Interface in Java?", "options": {"A": "An abstract class can declare instance state and constructors; interfaces define contracts and default methods", "B": "Interfaces can have private instance variables", "C": "A class can extend multiple abstract classes", "D": "Abstract classes cannot have methods"}, "correct_answer": "A"},
                {"question_text": "How does Java's automatic Garbage Collection operate?", "options": {"A": "Automatically identifies and reclaims heap memory occupied by unreferenced objects", "B": "Clears all static variables on every method call", "C": "Deallocates local primitive variables on the stack", "D": "Compresses the compiled JAR file"}, "correct_answer": "A"},
                {"question_text": "How does an ArrayList differ from a LinkedList in Java?", "options": {"A": "ArrayList is backed by dynamic array with O(1) random access; LinkedList has O(1) node insertion/deletion", "B": "LinkedList is always faster for lookups", "C": "ArrayList cannot store objects", "D": "LinkedList cannot be iterated with loops"}, "correct_answer": "A"},
                {"question_text": "What does the 'final' keyword signify when applied to a Java class?", "options": {"A": "The class cannot be extended or subclassed", "B": "The class cannot be instantiated", "C": "The class runs in a background thread", "D": "All methods become private"}, "correct_answer": "A"},
                {"question_text": "What is the difference between a Checked and an Unchecked exception in Java?", "options": {"A": "Checked exceptions must be handled or declared with throws; unchecked inherit from RuntimeException", "B": "Unchecked exceptions crash the compiler", "C": "Checked exceptions are only in Spring Boot", "D": "There is no functional difference"}, "correct_answer": "A"},
                {"question_text": "In Java 8+ Streams, what is the difference between map() and filter()?", "options": {"A": "map transforms elements into new values; filter selects elements that match a predicate", "B": "map removes nulls only", "C": "filter sorts the collection", "D": "filter converts stream to array"}, "correct_answer": "A"},
                {"question_text": "What does the 'volatile' keyword guarantee in multi-threaded Java?", "options": {"A": "Guarantees that reads and writes are visible immediately across all threads without CPU cache staleness", "B": "Locks the entire class method", "C": "Makes the variable immutable", "D": "Forces execution on the GPU"}, "correct_answer": "A"}
            ]

        # 7. DATA STRUCTURES & ALGORITHMS
        elif any(k in sk for k in ('data structure', 'algorithm', 'dsa', 'tree', 'graph', 'sorting')):
            return [
                {"question_text": "What is the time complexity of searching in a sorted array using Binary Search?", "options": {"A": "O(n)", "B": "O(log n)", "C": "O(1)", "D": "O(n log n)"}, "correct_answer": "B"},
                {"question_text": "Which data structure operates strictly on a Last-In, First-Out (LIFO) basis?", "options": {"A": "Queue", "B": "Stack", "C": "Linked List", "D": "Hash Map"}, "correct_answer": "B"},
                {"question_text": "What is the worst-case time complexity of QuickSort?", "options": {"A": "O(n log n)", "B": "O(n^2)", "C": "O(n)", "D": "O(log n)"}, "correct_answer": "B"},
                {"question_text": "How does a Hash Table resolve hash collisions when two keys hash to the same bucket?", "options": {"A": "Through chaining (linked lists) or open addressing (probing)", "B": "By discarding the older entry", "C": "By restarting the server", "D": "By sorting all entries alphabetically"}, "correct_answer": "A"},
                {"question_text": "What is the fundamental difference between BFS and DFS graph traversals?", "options": {"A": "BFS explores level by level using a Queue; DFS explores depth first using a Stack or recursion", "B": "DFS is only for binary trees", "C": "BFS cannot find shortest path in unweighted graphs", "D": "They produce identical traversal orders"}, "correct_answer": "A"},
                {"question_text": "What is the time complexity of inserting into a balanced Binary Search Tree (AVL / Red-Black)?", "options": {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n^2)"}, "correct_answer": "B"},
                {"question_text": "What data structure is typically used to implement a Priority Queue efficiently?", "options": {"A": "Binary Heap", "B": "Circular Linked List", "C": "Hash Set", "D": "Adjacency Matrix"}, "correct_answer": "A"},
                {"question_text": "In Dynamic Programming, what does 'Memoization' refer to?", "options": {"A": "Top-down caching of subproblem results to avoid redundant calculations", "B": "Bottom-up iterative tabulation only", "C": "Compressing binary trees", "D": "Garbage collection in recursion"}, "correct_answer": "A"},
                {"question_text": "Which sorting algorithm is stable and guarantees O(n log n) time in all cases?", "options": {"A": "QuickSort", "B": "Merge Sort", "C": "Selection Sort", "D": "Bubble Sort"}, "correct_answer": "B"},
                {"question_text": "What is the maximum number of nodes in a binary tree of height h (where root is height 1)?", "options": {"A": "2^h - 1", "B": "2^(h-1)", "C": "h^2", "D": "2*h"}, "correct_answer": "A"}
            ]

        # 8. MACHINE LEARNING & AI
        elif any(k in sk for k in ('machine learning', 'ai', 'data science', 'deep learning', 'nlp')):
            return [
                {"question_text": "What is Overfitting in machine learning?", "options": {"A": "When a model learns training noise too closely and fails to generalize to unseen test data", "B": "When training loss is zero and validation loss is zero", "C": "When a dataset has missing columns", "D": "When model inference is too fast"}, "correct_answer": "A"},
                {"question_text": "What is the primary role of a Loss Function during model training?", "options": {"A": "Quantifies the error between model predictions and actual ground truth labels", "B": "Calculates server hosting costs", "C": "Normalizes database tables", "D": "Compresses model weights"}, "correct_answer": "A"},
                {"question_text": "How does Gradient Descent optimize neural network parameters?", "options": {"A": "Computes gradients of the loss with respect to weights and updates weights in the opposite direction", "B": "Randomly guesses weights until loss is 0", "C": "Doubles the learning rate on every epoch", "D": "Removes neurons with negative weights"}, "correct_answer": "A"},
                {"question_text": "What is the difference between Precision and Recall in classification evaluation?", "options": {"A": "Precision = TP / (TP + FP); Recall = TP / (TP + FN)", "B": "Precision is only for regression problems", "C": "Recall measures execution time", "D": "They are mathematically identical"}, "correct_answer": "A"},
                {"question_text": "Why do practitioners split data into Training, Validation, and Test sets?", "options": {"A": "Train learns weights; Validation tunes hyperparameters/prevents overfit; Test measures unbiased final performance", "B": "To duplicate records for higher accuracy", "C": "To bypass GPU memory limits", "D": "To avoid converting data to tensors"}, "correct_answer": "A"},
                {"question_text": "What is Regularization (such as L1 Lasso or L2 Ridge) used for?", "options": {"A": "Penalizes excessive weight magnitudes to prevent overfitting and encourage simpler models", "B": "Speeds up data loading", "C": "Replaces backpropagation", "D": "Removes categorical features"}, "correct_answer": "A"},
                {"question_text": "What is Transfer Learning?", "options": {"A": "Taking a model pretrained on a massive dataset and fine-tuning it for a specific downstream task", "B": "Copying data from PostgreSQL to MongoDB", "C": "Training without ground truth labels", "D": "Migrating servers across cloud providers"}, "correct_answer": "A"},
                {"question_text": "What is Data Augmentation in computer vision?", "options": {"A": "Artificially expanding dataset diversity through random crops, rotations, flips, and color jitter", "B": "Generating fake database users", "C": "Compressing JPEG images to PNG", "D": "Increasing image resolution with bicubic filter"}, "correct_answer": "A"},
                {"question_text": "What is the Vanishing Gradient problem in deep neural networks?", "options": {"A": "Gradients shrink exponentially as they backpropagate through deep layers, stalling learning in early layers", "B": "Loss becomes infinite", "C": "GPU memory runs out", "D": "Weights become NaN"}, "correct_answer": "A"},
                {"question_text": "Why are non-linear activation functions (like ReLU or GELU) essential in neural networks?", "options": {"A": "Allow the network to approximate complex non-linear mathematical mappings rather than collapsing to a linear model", "B": "Prevent memory leaks in PyTorch", "C": "Force outputs between 0 and 1 only", "D": "Accelerate CPU thread allocation"}, "correct_answer": "A"}
            ]

        # 9. DOMAIN-ACCURATE DYNAMIC FALLBACK FOR ANY OTHER SKILL
        else:
            return [
                {"question_text": f"In {skill_name}, what is the standard idiomatic practice for handling asynchronous operations and concurrency?", "options": {"A": "Using native non-blocking async constructs, promises, or coroutines", "B": "Writing synchronous infinite while loops", "C": "Bypassing the runtime scheduler", "D": "Terminating the process on any I/O delay"}, "correct_answer": "A"},
                {"question_text": f"How are external dependencies, third-party libraries, and module versions managed in {skill_name} projects?", "options": {"A": "Through the ecosystem package manifest and lockfile (e.g. package.json, requirements.txt, go.mod, Cargo.toml)", "B": "By manually pasting zip files into the root directory", "C": "By committing node binaries directly to git", "D": "Dependencies are not supported"}, "correct_answer": "A"},
                {"question_text": f"What is the primary runtime architecture or execution model of {skill_name}?", "options": {"A": "It executes instructions through an optimized engine, virtual machine, or native compiled binary", "B": "It translates code to static HTML files", "C": "It requires physical tape drives", "D": "It runs exclusively on mainframe hardware"}, "correct_answer": "A"},
                {"question_text": f"How does {skill_name} manage application state, variable scoping, and memory lifetimes?", "options": {"A": "Through defined lexical scoping rules, stack frames, and automatic garbage collection or RAII ownership", "B": "By storing all variables in global browser cookies", "C": "By writing every variable to a temporary text file", "D": "By leaking memory after every function call"}, "correct_answer": "A"},
                {"question_text": f"What is the recommended approach to error handling and boundary validation in {skill_name}?", "options": {"A": "Validating inputs at boundaries and catching typed exceptions with structured error logging", "B": "Suppressing all runtime exceptions silently", "C": "Hardcoding return values to 0 on failure", "D": "Crashing the operating system on any invalid parameter"}, "correct_answer": "A"},
                {"question_text": f"Which principle is essential when architecting scalable, maintainable applications with {skill_name}?", "options": {"A": "Separation of concerns, modular interfaces, and clean dependency inversion", "B": "Placing all application logic into a single monolithic 10,000-line file", "C": "Hardcoding production database credentials in source code", "D": "Disabling automated tests and continuous integration"}, "correct_answer": "A"},
                {"question_text": f"In {skill_name}, what mechanism ensures type safety, data integrity, and contract validation?", "options": {"A": "Static type checking, interfaces, schemas, or runtime contract validators", "B": "Comments written in English only", "C": "Variable name length restrictions", "D": "Running on Linux instead of Windows"}, "correct_answer": "A"},
                {"question_text": f"How does a developer diagnose bottlenecks, memory leaks, or high CPU usage in a {skill_name} service?", "options": {"A": "Using deterministic profilers, APM telemetry, and memory heap snapshots", "B": "By guessing and deleting random functions", "C": "By turning off the monitor", "D": "By increasing screen brightness"}, "correct_answer": "A"},
                {"question_text": f"What is the industry best practice for configuring environments (dev, staging, production) in {skill_name}?", "options": {"A": "Injecting configuration via environment variables conforming to 12-Factor App methodology", "B": "Hardcoding URLs inside compiled binaries", "C": "Sharing passwords via Slack channels", "D": "Using identical database passwords for dev and prod"}, "correct_answer": "A"},
                {"question_text": f"What strategy provides high availability and fault tolerance when deploying {skill_name} services at scale?", "options": {"A": "Horizontal scaling behind a load balancer with automated health check probes", "B": "Running on a single laptop without battery backup", "C": "Disabling TLS/SSL encryption", "D": "Restarting the server manually every hour"}, "correct_answer": "A"}
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