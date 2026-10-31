#!/usr/bin/env python3
"""#!/usr/bin/env python3
"""
Unit tests for CAREER_AGENT_SYSTEM (v3.0.0)
Testing VaultAgent, MemoryAgent, CertificationAgent, JobSearchAgent, SkillBuildingAgent, GitVersionController, and OrchestratorAgent.
"""

import os
import shutil
import tempfile
import unittest

from career_agent_system import (
    VaultAgent,
    MemoryAgent,
    CertificationAgent,
    JobSearchAgent,
    SkillBuildingAgent,
    GitVersionController,
    OrchestratorAgent,
    UserProfile,
)


class TestVaultAgent(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.vault = VaultAgent(vault_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_and_load_artifact_allowed(self):
        data = {"key": "value"}
        filepath = self.vault.save_artifact("test_doc.json", data, classification="PUBLIC")
        self.assertTrue(os.path.exists(filepath))
        loaded = self.vault.load_artifact("test_doc.json")
        self.assertEqual(loaded, data)


class TestMemoryAgent(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryAgent()

    def test_remember_and_recall(self):
        self.memory.remember("pref", "remote_work")
        self.assertEqual(self.memory.recall("pref"), "remote_work")


class TestCertificationAgent(unittest.TestCase):
    def setUp(self):
        self.agent = CertificationAgent()

    def test_recommendations(self):
        recs = self.agent.recommend_certifications(["Python", "AWS"])
        self.assertIsInstance(recs, list)


class TestJobSearchAgent(unittest.TestCase):
    def setUp(self):
        self.agent = JobSearchAgent()

    def test_search_jobs(self):
        jobs = self.agent.search_jobs("Software Engineer")
        self.assertIsInstance(jobs, list)


class TestSkillBuildingAgent(unittest.TestCase):
    def setUp(self):
        self.agent = SkillBuildingAgent()

    def test_suggest_skills(self):
        skills = self.agent.suggest_skills("Data Science")
        self.assertIsInstance(skills, list)


class TestGitVersionController(unittest.TestCase):
    def setUp(self):
        self.controller = GitVersionController()

    def test_get_version(self):
        ver = self.controller.get_current_version()
        self.assertIsNotNone(ver)


class TestOrchestratorAgent(unittest.TestCase):
    def setUp(self):
        self.profile = UserProfile(name="Test User", target_role="Engineer")
        self.orchestrator = OrchestratorAgent(self.profile)

    def test_run_workflow(self):
        res = self.orchestrator.run_full_workflow()
        self.assertIsNotNone(res)


if __name__ == "__main__":
    unittest.main()
Unit tests for CAREER_AGENT_SYSTEM (v2.0.0)
Testing VaultAgent, CertificationAgent, JobSearchAgent, and OrchestratorAgent.
"""

import os
import shutil
import tempfile
import unittest

from career_agent_system import (
    VaultAgent,
    CertificationAgent,
    JobSearchAgent,
    OrchestratorAgent,
    UserProfile,
)


class TestVaultAgent(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.vault = VaultAgent(vault_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_and_load_artifact_allowed(self):
        data = {"key": "value"}
        path = self.vault.save_artifact(
            file_name="user_profile_v1.json",
            data=data,
            file_type="json",
            tags=["profile"],
            source="test",
            related_skills=["python"],
            related_jobs=["developer"],
            agent_name="JOB_SEARCH_AGENT",
        )
        self.assertTrue(path.exists())

        loaded = self.vault.load_artifact("user_profile_v1.json", agent_name="JOB_SEARCH_AGENT")
        self.assertEqual(loaded, data)

    def test_permission_denied_least_privilege(self):
        with self.assertRaises(PermissionError):
            self.vault.load_artifact("episodic_memory_v1.json", agent_name="CERTIFICATION_AGENT")

    def test_orchestrator_wildcard_permission(self):
        data = {"status": "ok"}
        self.vault.save_artifact(
            file_name="any_file.json",
            data=data,
            file_type="json",
            tags=["test"],
            source="test",
            related_skills=[],
            related_jobs=[],
            agent_name="ORCHESTRATOR_AGENT",
        )
        loaded = self.vault.load_artifact("any_file.json", agent_name="ORCHESTRATOR_AGENT")
        self.assertEqual(loaded, data)


class TestJobSearchAgent(unittest.TestCase):
    def test_calculate_match_score_normal(self):
        score = JobSearchAgent.calculate_match_score(
            skill_match=20,
            role_match=20,
            experience_match=20,
            location_match=15,
            interest_match=15,
            requirement_gap_penalty=10,
        )
        self.assertEqual(score, 80)

    def test_calculate_match_score_bounds(self):
        high_score = JobSearchAgent.calculate_match_score(30, 30, 30, 30, 30, 0)
        self.assertEqual(high_score, 100)

        low_score = JobSearchAgent.calculate_match_score(0, 0, 0, 0, 0, 50)
        self.assertEqual(low_score, 0)


class TestCertificationAgent(unittest.TestCase):
    def test_filter_verified_free(self):
        certs = [
            {"name": "Cert A", "verified": True, "free_or_paid": "free", "credibility_score": 80},
            {"name": "Cert B", "verified": False, "free_or_paid": "free", "credibility_score": 95},
            {"name": "Cert C", "verified": True, "free_or_paid": "paid", "credibility_score": 90},
            {"name": "Cert D", "verified": True, "free_or_paid": "free_audit_paid_exam", "credibility_score": 95},
        ]
        filtered = CertificationAgent.filter_verified_free(certs)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["name"], "Cert D")
        self.assertEqual(filtered[1]["name"], "Cert A")


class TestOrchestratorAgent(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_orchestrator_initialization(self):
        orch = OrchestratorAgent(vault_dir=self.test_dir)
        self.assertIsNotNone(orch.vault)
        self.assertIsNotNone(orch.job_agent)
        self.assertIsNotNone(orch.cert_agent)


if __name__ == "__main__":
    unittest.main()
