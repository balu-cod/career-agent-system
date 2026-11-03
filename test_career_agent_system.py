import tempfile, unittest
from career_agent_system import (
    VERSION, DEFAULT_PROFILE, UserProfile, VaultAgent,
    has_term, parse_job_requirements, normalize_skills, run_pipeline
)

class TestCareerAgentSystemV650(unittest.TestCase):
    def test_version_and_profile(self):
        self.assertEqual(VERSION, "6.5.0")
        p = UserProfile(handle="balu-cod")
        self.assertEqual(p.to_dict()["handle"], "balu-cod")

    def test_aliases_and_requirements(self):
        self.assertTrue(has_term("kubernetes", "We deploy on K8s and Postgres"))
        self.assertTrue(has_term("postgresql", "We deploy on K8s and Postgres"))
        reqs = parse_job_requirements("Requires 6+ years of software experience. Email hiring@startup.ai")
        self.assertEqual(reqs["min_years"], 6)
        self.assertEqual(reqs["hiring_email"], "hiring@startup.ai")

    def test_normalize_skills_handles_list_and_dict(self):
        s = normalize_skills({"languages": ["Python", "Go"], "cloud": ["Docker"]})
        self.assertIn("Python", s)
        self.assertIn("Go", s)

    def test_vault_and_pipeline(self):
        v = VaultAgent(vault_dir=tempfile.mkdtemp())
        v.bootstrap_defaults_if_empty()
        fake = lambda u, timeout=15: {"jobs": [{"id": 1, "title": "Python AI Engineer Intern", "company_name": "AlphaAI", "location": {"name": "Remote India"}, "candidate_required_location": "Remote", "absolute_url": "u1", "url": "u1", "content": "Python FastAPI SQL Docker", "description": "Python FastAPI SQL Docker", "first_published": "2026-11-03T00:00:00Z"}], "data": [], "hits": []}
        ctx = run_pipeline(v, log=lambda m: None, fetch_fn=fake)
        self.assertTrue(ctx["matches"])

if __name__ == "__main__":
    unittest.main()
