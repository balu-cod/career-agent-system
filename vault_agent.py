"""VaultAgent for managing persistent JSON and HTML artifacts."""

import os
import json
from typing import Dict, List, Any, Optional
from .base_schemas import DEFAULT_PROFILE, DEFAULT_CERTIFICATIONS, DEFAULT_JOBS, DEFAULT_ROADMAP

AGENT_PERMISSIONS = {
    "MEMORY_AGENT": ["user_profile_v1.json"],
    "CERTIFICATION_AGENT": ["verified_certifications_v1.json"],
    "JOB_SEARCH_AGENT": ["job_matches_v1.json", "applied_jobs_tracker_v1.json", "cold_outreach_templates_v1.json"],
    "SKILL_BUILDING_AGENT": ["skill_roadmap_v1.json", "learning_calendar_v1.ics"],
    "RESUME_AND_AUTO_APPLY_AGENT": [
        "user_profile_v1.json",
        "job_matches_v1.json",
        "applied_jobs_tracker_v1.json",
        "tailored_resumes_v1.json",
        "latest_ats_resume.html",
        "daily_auto_apply_log_v1.json"
    ]
}

class VaultAgent:
    def __init__(self, vault_dir: str = "vault"):
        self.vault_dir = vault_dir
        os.makedirs(self.vault_dir, exist_ok=True)
        self.permissions = AGENT_PERMISSIONS

    def bootstrap_defaults_if_empty(self) -> Dict[str, Any]:
        results = {}
        profile_path = os.path.join(self.vault_dir, "user_profile_v1.json")
        if not os.path.exists(profile_path):
            self.save_artifact("user_profile_v1.json", DEFAULT_PROFILE)
            results["profile"] = "created"
        
        certs_path = os.path.join(self.vault_dir, "verified_certifications_v1.json")
        if not os.path.exists(certs_path):
            self.save_artifact("verified_certifications_v1.json", DEFAULT_CERTIFICATIONS)
            results["certifications"] = "created"
            
        jobs_path = os.path.join(self.vault_dir, "job_matches_v1.json")
        if not os.path.exists(jobs_path):
            self.save_artifact("job_matches_v1.json", DEFAULT_JOBS)
            results["jobs"] = "created"

        roadmap_path = os.path.join(self.vault_dir, "skill_roadmap_v1.json")
        if not os.path.exists(roadmap_path):
            self.save_artifact("skill_roadmap_v1.json", DEFAULT_ROADMAP)
            results["roadmap"] = "created"
            
        return results

    def save_artifact(self, filename: str, content: Any) -> str:
        path = os.path.join(self.vault_dir, filename)
        if filename.endswith(".json"):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(content))
        return path

    def load_artifact(self, filename: str) -> Any:
        path = os.path.join(self.vault_dir, filename)
        if not os.path.exists(path):
            return None
        if filename.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

    def search_vault(self, query: str) -> List[Dict[str, Any]]:
        results = []
        if not os.path.exists(self.vault_dir):
            return results
        for filename in os.listdir(self.vault_dir):
            path = os.path.join(self.vault_dir, filename)
            if os.path.isfile(path):
                try:
                    content = self.load_artifact(filename)
                    if query.lower() in str(content).lower():
                        results.append({"filename": filename, "content": content})
                except Exception:
                    pass
        return results
