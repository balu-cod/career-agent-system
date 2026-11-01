#!/usr/bin/env python3
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
    
)


class TestVaultAgent(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.vault = VaultAgent(vault_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_and_load_artifact_allowed(self):
        data = {"key": "value"}
        self.vault.save_artifact("test.json", data, "application/json", ["test"], "TEST", ["Python"], ["All"])
        loaded = self.vault.load_artifact("test.json")
        self.assertEqual(loaded, data)


if __name__ == "__main__":
    unittest.main()
