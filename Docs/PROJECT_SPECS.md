# SIH26044 — Project Specification

## Project
AI-powered Skill Intelligence Platform for Academia–Industry Collaboration

## Objective
Build a demo platform that connects students, academicians, institutes and industry through skill mapping, skill-gap analysis, personalized upskilling, skill verification, readiness scoring and competency-based internship/placement matching.

---

# Technology Stack

## Frontend
- React.js
- Tailwind CSS
- JavaScript

## Backend
- Python
- FastAPI

## Database
- PostgreSQL

## AI / Intelligence
- Python
- NLP
- scikit-learn

## API Communication
- REST API
- JSON

## Authentication
- JWT

---

# Core Workflow

Student Profile / Resume
        ↓
AI Skill Extraction
        ↓
Skill Normalization
        ↓
AI Skill Graph
        ↓
Skill-Gap Analysis
        ↓
Personalized Roadmap
        ↓
Skill Verification
        ↓
Readiness Score
        ↓
Competency-Based Matching
        ↓
Internship / Placement

---

# Main Users

## Student
- Create profile
- Upload resume
- View extracted skills
- View skill gaps
- Get personalized roadmap
- Take assessments
- View readiness score
- Discover matched internships

## Institute
- Monitor student readiness
- View skill-demand insights
- Track student performance

## Academician
- Mentor students
- View student skill gaps
- Access industry insights
- Support industry-aligned learning

## Industry
- Define required competencies
- Find suitable candidates
- View skill-based profiles
- Post internship opportunities

---

# Demo Students

### Het Modi
Target Role: Backend Developer Intern

Strong Skills:
- Java
- DSA
- OOP

Skill Gaps:
- Spring Boot
- REST API
- Docker

Readiness Score:
72%

---

### Dhyana Joshi
Target Role: Frontend Developer Intern

Strong Skills:
- HTML
- CSS
- JavaScript

Skill Gaps:
- React
- TypeScript

Readiness Score:
78%

---

### Vraj Khatri
Target Role: Data Analyst Intern

Strong Skills:
- Python
- SQL

Skill Gaps:
- Statistics
- Power BI

Readiness Score:
67%

---

# Demo Requirements

The demo should prioritize:

1. Student Dashboard
2. Skill Extraction
3. Skill-Gap Analysis
4. Personalized Roadmap
5. Skill Verification
6. Readiness Score
7. Internship Matching

The system should use realistic seeded data.

The AI components may use lightweight NLP, keyword extraction, predefined skill mappings and similarity-based algorithms for the prototype.

Do not over-engineer the demo.

---

# UI Direction

Theme:
- Dark navy
- Blue / cyan accents
- Professional
- Modern
- Responsive

The UI should feel like a real SaaS/product platform rather than a basic college website.

---

# Important Development Rule

Frontend, backend and database should remain modular.

Do not unnecessarily modify another person's component.

All API responses must follow the API contract defined in:

docs/API_CONTRACT.md