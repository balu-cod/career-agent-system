#!/usr/bin/env python3
"""
CAREER_AGENT_SYSTEM (v2.0.0) — Autonomous Multi-Agent Career Development Orchestrator
Author: Kodimurthy Bhalavardan (Balu Kodimurthy) | GitHub: @balu-cod
"""

from __future__ import annotations
import dataclasses
import datetime
import hashlib
import json
import pathlib
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclasses.dataclass
class UserProfile:
    user_id: str
    full_name: str
    contact_email: str
    current_position: str
    years_of_experience: str
    education: List[Dict[str, str]]
    certifications: List[Dict[str, str]]
    technical_skills: List[str]
    soft_skills: List[str]
    interests: List[str]
    career_goals: str
    preferred_job_roles: List[str]
    preferred_locations: List[str]
    remote_preference: str
    salary_expectation: str
    employment_type: str
    languages: List[str]
    availability: str
    work_authorization: str
    skill_gaps: List[str]
    target_certifications: List[str]
    resume_version: str
    portfolio_links: List[str]
    memory_last_updated: str
    confidence_scores: Dict[str, float]


class VaultAgent:
    AGENT_PERMISSIONS: Dict[str, List[str]] = {
        "ORCHESTRATOR_AGENT": ["*"],
        "CERTIFICATION_AGENT": ["user_profile_v1.json", "certifications_research_v1.json"],
        "JOB_SEARCH_AGENT": ["user_profile_v1.json", "job_matches_v1.json", "applied_jobs_tracker_v1.json"],
        "SKILL_BUILDING_AGENT": ["user_profile_v1.json", "job_matches_v1.json", "skill_roadmap_v1.json"],
        "MEMORY_AGENT": ["user_profile_v1.json", "episodic_memory_v1.json"],
    }

    def __init__(self, vault_dir: str = "./vault") -> None:
        self.vault_path = pathlib.Path(vault_dir)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.vault_path / "vault_index.json"

    def _check_permission(self, agent_name: str, file_name: str) -> None:
        allowed = self.AGENT_PERMISSIONS.get(agent_name, [])
        if "*" not in allowed and file_name not in allowed:
            raise PermissionError(f"Least-privilege violation: {agent_name} cannot access {file_name}.")

    def save_artifact(
        self,
        file_name: str,
        data: Any,
        file_type: str,
        tags: List[str],
        source: str,
        related_skills: List[str],
        related_jobs: List[str],
        expiry_date: Optional[str] = None,
        agent_name: str = "ORCHESTRATOR_AGENT",
    ) -> pathlib.Path:
        self._check_permission(agent_name, file_name)
        target = self.vault_path / file_name
        serialized = json.dumps(data, indent=2, ensure_ascii=False)
        sha256_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        target.write_text(serialized, encoding="utf-8")
        self._update_index(file_name, file_type, tags, source, expiry_date, related_skills, related_jobs, sha256_hash)
        return target

    def load_artifact(self, file_name: str, agent_name: str = "ORCHESTRATOR_AGENT") -> Optional[Any]:
        self._check_permission(agent_name, file_name)
        target = self.vault_path / file_name
        return json.loads(target.read_text(encoding="utf-8")) if target.exists() else None

    def _update_index(self, file_name: str, file_type: str, tags: List[str], source: str,
                      expiry_date: Optional[str], related_skills: List[str], related_jobs: List[str], sha256: str) -> None:
        now_date = datetime.date.today().isoformat()
        index_data = self.load_artifact("vault_index.json") or {"vault_version": "2.0.0", "items": []}
        existing = index_data.get("items", [])
        version = next((i.get("version", 1) + 1 for i in existing if i.get("file_name") == file_name), 1)
        items = [i for i in existing if i.get("file_name") != file_name]
        items.append({
            "file_name": file_name, "version": version, "file_type": file_type,
            "upload_date": now_date, "tags": tags, "source": source,
            "expiry_date": expiry_date, "related_skills": related_skills,
            "related_jobs": related_jobs, "sha256": sha256
        })
        index_data["items"] = items
        index_data["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.index_file.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")


class JobSearchAgent:
    @staticmethod
    def calculate_match_score(skill_match: int, role_match: int, experience_match: int,
                              location_match: int, interest_match: int, requirement_gap_penalty: int) -> int:
        return max(0, min(100, skill_match + role_match + experience_match + location_match + interest_match - requirement_gap_penalty))


class CertificationAgent:
    @staticmethod
    def filter_verified_free(certs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid = [c for c in certs if c.get("verified") and c.get("free_or_paid") in ("free", "free_audit_paid_exam")]
        return sorted(valid, key=lambda x: x.get("credibility_score", 0), reverse=True)


class OrchestratorAgent:
    def __init__(self, vault_dir: str = "./vault") -> None:
        self.vault = VaultAgent(vault_dir)
        self.job_agent = JobSearchAgent()
        self.cert_agent = CertificationAgent()


if __name__ == "__main__":
    orch = OrchestratorAgent()
    print("CAREER_AGENT_SYSTEM v2.0.0 initialized successfully.")
