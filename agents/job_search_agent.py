"""JobSearchAgent for managing search queries, matching, outreach templates, and application tracking."""

from typing import Dict, List, Any, Optional
from .vault_agent import VaultAgent
from .base_schemas import DEFAULT_JOBS

class JobSearchAgent:
    def __init__(self, vault: VaultAgent):
        self.vault = vault

    def generate_search_queries(self, target_roles: Optional[List[str]] = None) -> List[str]:
        roles = target_roles or ["AI Engineer", "Full Stack Developer", "Autonomous Systems Architect"]
        queries = []
        for role in roles:
            queries.extend([f"{role} remote", f"{role} senior", f"Principal {role}"])
        return queries

    def calculate_match_score(self, job: Dict[str, Any], profile: Dict[str, Any]) -> int:
        return job.get("match_score", 85)

    def generate_cold_outreach_pack(self) -> List[Dict[str, Any]]:
        templates = [
            {"template_id": 1, "title": "Direct Engineering Manager Outreach", "subject": "Exploring AI Engineering opportunities at {company}"},
            {"template_id": 2, "title": "Talent Acquisition Specialist Connect", "subject": "Application for {role} - {full_name}"},
            {"template_id": 3, "title": "Founder / CTO Direct Intro", "subject": "Autonomous Systems Architecture & AI Engineering"},
            {"template_id": 4, "title": "Referral Request to Team Member", "subject": "Quick question regarding AI/ML engineering team at {company}"},
            {"template_id": 5, "title": "Post-Application Follow-up", "subject": "Following up on my application for {role}"},
            {"template_id": 6, "title": "Technical Project Showcase", "subject": "Multi-Agent System & Automated Workflows Portfolio"}
        ]
        self.vault.save_artifact("cold_outreach_templates_v1.json", templates)
        return templates

    def sync_application_tracker(self) -> List[Dict[str, Any]]:
        jobs = self.vault.load_artifact("job_matches_v1.json") or DEFAULT_JOBS
        tracker = []
        for job in jobs:
            tracker.append({
                "company": job.get("company"),
                "role": job.get("role"),
                "status": "tracked",
                "match_score": job.get("match_score")
            })
        self.vault.save_artifact("applied_jobs_tracker_v1.json", tracker)
        return tracker

    def format_8am_applied_jobs_email(self) -> str:
        tracker = self.vault.load_artifact("applied_jobs_tracker_v1.json") or []
        count = len(tracker)
        return f"Daily 8 AM Digest: {count} applications tracked and active."
