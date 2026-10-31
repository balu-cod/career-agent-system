# CAREER_AGENT_SYSTEM (v2.0.0)

**Author:** Kodimurthy Bhalavardan (Balu Kodimurthy) (`@balu-cod`)

Autonomous Multi-Agent Career-Development Assistant for one authenticated user. Coordinates six specialized agents around a least-privilege Personal Vault:
- **ORCHESTRATOR_AGENT:** Intent classification, DAG task planning, retry-once resilience, output validation, and human-in-the-loop approval gates.
- **CERTIFICATION_AGENT:** Discovers, verifies, and ranks 100% free or student-waived certifications from universities, MOOCs, and government portals.
- **JOB_SEARCH_AGENT:** Parses resume/profile criteria, computes transparent match scores (`skill_match + role_match + experience_match + location_match + interest_match - requirement_gap_penalty`), tracks applied jobs, and generates the 8:00 AM Daily Applied Jobs Email Report.
- **SKILL_BUILDING_AGENT:** Performs skill-gap analysis and schedules Morning (7:00 AM), Evening (6:30 PM), Night (9:00 PM), and Weekend (10:00 AM) study and certification sprints.
- **MEMORY_AGENT:** Extracts durable episodic and semantic facts with confidence scores and timestamps.
- **VAULT_AGENT:** Maintains versioned, SHA-256 verified JSON/PDF/DOCX artifacts with least-privilege access control.
