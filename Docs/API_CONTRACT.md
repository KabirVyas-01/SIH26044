# SIH26044 API Contract

Base URL:

/api

---

## Students

### GET /api/students

Returns all demo students.

### GET /api/students/{id}

Returns a student's profile.

Example:

{
  "id": 1,
  "name": "Het Modi",
  "target_role": "Backend Developer Intern",
  "readiness_score": 72
}

---

## Skills

### GET /api/students/{id}/skills

Returns the student's skills.

Example:

[
  {
    "name": "Java",
    "proficiency": 85,
    "verified": true
  },
  {
    "name": "Spring Boot",
    "proficiency": 30,
    "verified": false
  }
]

---

## Skill Gap

### GET /api/students/{id}/gaps

Returns missing skills for the student's target role.

---

## Roadmap

### GET /api/students/{id}/roadmap

Returns the student's personalized learning roadmap.

---

## Readiness

### GET /api/students/{id}/readiness

Returns the current readiness score and contributing factors.

---

## Internship Matching

### GET /api/students/{id}/matches

Returns recommended internship opportunities with match scores.

---

## Assessment

### GET /api/assessments/{skill}

Returns assessment questions.

### POST /api/assessments/{skill}/submit

Submits assessment answers and returns the score.

---

## Resume

### POST /api/resume/analyze

Accepts a resume and returns extracted and normalized skills.