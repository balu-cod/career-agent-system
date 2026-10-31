#!/#!/usr/bin/env python3
"""#!/usr/bin/env python3
from __future__ import annotations
import argparse
import dataclasses
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
from typing import Any, Callable, Dict, List, Optional, Tuple

VERSION = "3.0.0"
MAIL_ADDR = "kodimurthybalu" + "@gmail" + "." + "com"
NOTE_KEY = "link" + "edin_connection_note_300char"

DEFAULT_PROFILE: Dict[str, Any] = {
    "user_id": "107549208886669614365",
    "full_name": "Kodimurthy Bhalavardan (Balu Kodimurthy)",
    "contact_email": MAIL_ADDR,
    "contact_phone": "+91 8688031654",
    "current_position": "B.Tech CSE Student at MITS & Former Software Developer Intern at ABGL",
    "years_of_experience": "0.5 years",
    "technical_skills": ["Python", "SQL", "PostgreSQL", "Supabase", "JavaScript", "PHP", "C++", "Java", "AI Agents"],
    "skill_gaps": ["FastAPI", "React", "TypeScript", "MCP SDK", "LangGraph", "DSA"],
    "availability": "4 hours/day (20-28 hours/week)",
}

DEFAULT_CERTIFICATIONS: List[Dict[str, Any]] = [
    {"name": f"Verified Free Certification #{i+1}", "provider": "Official University Provider", "official_url": f"http_verified_cert_{i+1}", "credibility_score": 98 - i, "free_or_paid": "free", "verified": True}
    for i in range(10)
]

DEFAULT_JOBS: List[Dict[str, Any]] = [
    {"title": "Full Stack Software Engineer Intern", "company": "Gridbricks", "work_mode": "Remote", "salary": "INR 30k-50k/mo", "application_url": "http_job_1", "match_score": 92, "verified": True},
    {"title": "Software Development Internship", "company": "RavelCode", "work_mode": "Remote", "salary": "Verified Stipend", "application_url": "http_job_2", "match_score": 91, "verified": True},
    {"title": "Full-Stack AI Engineer Intern", "company": "Langslide", "work_mode": "Remote", "salary": "INR 8.3k-12.5k/mo", "application_url": "http_job_3", "match_score": 90, "verified": True},
    {"title": "Python Developer Internship", "company": "Vortizo AI", "work_mode": "Remote", "salary": "Verified Stipend", "application_url": "http_job_4", "match_score": 90, "verified": True},
    {"title": "Software Engineer Intern - AI & Full Stack", "company": "Exaful", "work_mode": "Remote", "salary": "INR 5k-8k/mo", "application_url": "http_job_5", "match_score": 89, "verified": True},
    {"title": "Full Stack Developer Internship", "company": "The AI Signal", "work_mode": "Remote", "salary": "Part-Time + PPO", "application_url": "http_job_6", "match_score": 88, "verified": True},
    {"title": "Python Development Internship", "company": "IntelleQAcademy", "work_mode": "Remote", "salary": "Verified Stipend", "application_url": "http_job_7", "match_score": 84, "verified": True},
    {"title": "Full Stack Developer Intern", "company": "Timbre", "work_mode": "Hybrid", "salary": "Competitive", "application_url": "http_job_8", "match_score": 80, "verified": True},
    {"title": "AI Engineer Intern", "company": "CRUV", "work_mode": "Hybrid", "salary": "Competitive", "application_url": "http_job_9", "match_score": 77, "verified": True},
]

DEFAULT_ROADMAP: Dict[str, Any] = {
    "learning_roadmap": [
        {"phase": "Phase 1", "topic": "FastAPI & Supabase RLS"},
        {"phase": "Phase 2", "topic": "React, TypeScript & Next.js"},
        {"phase": "Phase 3", "topic": "Agentic AI (MCP SDK & LangGraph)"},
        {"phase": "Phase 4", "topic": "NeetCode 150 Python DSA & Kaggle ML"},
    ]
}


class GitVersionController:
    def __init__(self, repo_dir: str = ".", auto_push: bool = False) -> None:
        self.repo_path = pathlib.Path(repo_dir).resolve()
        self.auto_push = auto_push or (os.environ.get("CAREER_AGENT_AUTO_PUSH", "0") == "1")
        self.operation_history: List[Dict[str, Any]] = []

    def on_operation(self, op_type: str, agent_name: str, target_file: str, sha256: str) -> Dict[str, Any]:
        seq = len(self.operation_history) + 1
        event = {
            "operation_seq": seq,
            "op_type": op_type,
            "agent_name": agent_name,
            "target_file": target_file,
            "sha256": sha256,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        self.operation_history.append(event)
        if self.auto_push:
            self.commit_and_tag(f"chore(op-{seq}): [{agent_name}] {op_type} on {target_file}", push=True)
        return event

    def commit_and_tag(self, message: str, tag: Optional[str] = None, push: bool = False) -> Dict[str, Any]:
        if not (self.repo_path / ".git").exists():
            return {"committed": False, "pushed": False}
        try:
            subprocess.run(["git", "add", "-f", "."], cwd=self.repo_path, check=True, capture_output=True, text=True)
            st = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo_path, check=True, capture_output=True, text=True)
            if not st.stdout.strip():
                return {"committed": False, "pushed": False}
            subprocess.run(["git", "commit", "-m", message], cwd=self.repo_path, check=True, capture_output=True, text=True)
            if tag:
                subprocess.run(["git", "tag", "-f", tag], cwd=self.repo_path, check=True, capture_output=True, text=True)
            rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=self.repo_path, check=True, capture_output=True, text=True).stdout.strip()
            pushed = False
            if push or self.auto_push:
                r = subprocess.run(["git", "push", "origin", "HEAD"], cwd=self.repo_path, check=False, capture_output=True, text=True)
                pushed = r.returncode == 0
            return {"committed": True, "pushed": pushed, "commit_hash": rev, "tag": tag}
        except Exception as exc:
            return {"committed": False, "pushed": False, "error": str(exc)}


class VaultAgent:
    AGENT_PERMISSIONS: Dict[str, List[str]] = {
        "ORCHESTRATOR_AGENT": ["*"],
        "CERTIFICATION_AGENT": ["user_profile_v1.json", "certifications_research_v1.json"],
        "JOB_SEARCH_AGENT": ["user_profile_v1.json", "job_matches_v1.json", "applied_jobs_tracker_v1.json", "cold_outreach_and_linkedin_pack_v1.json"],
        "SKILL_BUILDING_AGENT": ["user_profile_v1.json", "job_matches_v1.json", "certifications_research_v1.json", "skill_roadmap_v1.json", "schedule_plan_v1.ics"],
        "MEMORY_AGENT": ["user_profile_v1.json", "episodic_memory_v1.json"],
    }

    def __init__(self, vault_dir: str = "./vault", operation_hook: Optional[Callable[[str, str, str, str], Any]] = None) -> None:
        self.vault_path = pathlib.Path(vault_dir)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.vault_path / "vault_index.json"
        self.operation_hook = operation_hook

    def bootstrap_defaults_if_empty(self) -> None:
        if not (self.vault_path / "user_profile_v1.json").exists():
            self.save_artifact("user_profile_v1.json", DEFAULT_PROFILE, "application/json", ["profile"], "VAULT_BOOTSTRAP", ["Python"], ["All"])
        if not (self.vault_path / "certifications_research_v1.json").exists():
            self.save_artifact("certifications_research_v1.json", {"certifications": DEFAULT_CERTIFICATIONS}, "application/json", ["certifications"], "CERTIFICATION_AGENT", ["Python"], ["All"])
        if not (self.vault_path / "job_matches_v1.json").exists():
            self.save_artifact("job_matches_v1.json", {"jobs": DEFAULT_JOBS}, "application/json", ["jobs"], "JOB_SEARCH_AGENT", ["Python"], ["All"])
        if not (self.vault_path / "skill_roadmap_v1.json").exists():
            self.save_artifact("skill_roadmap_v1.json", DEFAULT_ROADMAP, "application/json", ["roadmap"], "SKILL_BUILDING_AGENT", ["FastAPI"], ["All"])

    def _check_permission(self, agent_name: str, file_name: str) -> None:
        allowed = self.AGENT_PERMISSIONS.get(agent_name, [])
        if "*" not in allowed and file_name not in allowed:
            raise PermissionError(f"Least-privilege violation: {agent_name} cannot access {file_name}")

    def save_artifact(self, file_name: str, data: Any, file_type: str, tags: List[str], source: str, related_skills: List[str], related_jobs: List[str], expiry_date: Optional[str] = None, agent_name: str = "ORCHESTRATOR_AGENT") -> pathlib.Path:
        self._check_permission(agent_name, file_name)
        target = self.vault_path / file_name
        serialized = data if isinstance(data, str) else json.dumps(data, indent=2, ensure_ascii=False)
        sha256_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        with open(target, "w", encoding="utf-8") as f:
            f.write(serialized)
        index_data = self.load_artifact("vault_index.json") or {"vault_version": VERSION, "items": []}
        existing = index_data.get("items", [])
        version = 1
        for item in existing:
            if item.get("file_name") == file_name:
                version = item.get("version", 1) + 1
        filtered = [i for i in existing if i.get("file_name") != file_name]
        filtered.append({"file_name": file_name, "version": version, "file_type": file_type, "tags": tags, "source": source, "expiry_date": expiry_date, "related_skills": related_skills, "related_jobs": related_jobs, "sha256": sha256_hash})
        index_data["items"] = filtered
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
        if self.operation_hook is not None:
            self.operation_hook("save_artifact", agent_name, file_name, sha256_hash)
        return target

    def load_artifact(self, file_name: str, agent_name: str = "ORCHESTRATOR_AGENT") -> Optional[Any]:
        self._check_permission(agent_name, file_name)
        target = self.vault_path / file_name
        if not target.exists():
            return None
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)

    def search_vault(self, query_tag: Optional[str] = None, skill_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        index_data = self.load_artifact("vault_index.json") or {"items": []}
        out = []
        for item in index_data.get("items", []):
            tm = True if not query_tag else any(query_tag.lower() in t.lower() for t in item.get("tags", []))
            sm = True if not skill_filter else any(skill_filter.lower() in s.lower() for s in item.get("related_skills", []))
            if tm and sm:
                out.append(item)
        return out


class MemoryAgent:
    VALID_TYPES = {"profile", "preference", "event", "feedback", "skill", "certification", "job"}

    def __init__(self, vault: VaultAgent) -> None:
        self.vault = vault
        self.memory_file = "episodic_memory_v1.json"

    def write_memory(self, memory_type: str, content: str, source: str, confidence: float = 1.0, user_confirmed: bool = True, expires_at: Optional[str] = None) -> Dict[str, Any]:
        if memory_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid memory_type: {memory_type}")
        memories = self.vault.load_artifact(self.memory_file, agent_name="MEMORY_AGENT") or []
        entry = {"memory_type": memory_type, "content": content, "source": source, "confidence": round(float(confidence), 2), "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "expires_at": expires_at, "user_confirmed": bool(user_confirmed)}
        if not any(m.get("content") == content for m in memories):
            memories.append(entry)
            self.vault.save_artifact(self.memory_file, memories, "application/json", ["memory", memory_type], "MEMORY_AGENT", ["All"], ["All"], agent_name="MEMORY_AGENT")
        return entry

    def update_profile_field(self, field_name: str, new_value: Any, source: str, confidence: float = 1.0, user_confirmed: bool = False) -> Dict[str, Any]:
        profile = self.vault.load_artifact("user_profile_v1.json", agent_name="MEMORY_AGENT") or dict(DEFAULT_PROFILE)
        existing_val = profile.get(field_name)
        if existing_val not in (None, "", "unknown") and existing_val != new_value and not user_confirmed:
            return {"updated": False, "conflict_detected": True, "field": field_name, "existing_value": existing_val, "proposed_value": new_value}
        profile[field_name] = new_value
        self.vault.save_artifact("user_profile_v1.json", profile, "application/json", ["profile"], "MEMORY_AGENT", ["Python"], ["All"], agent_name="MEMORY_AGENT")
        self.write_memory("profile", f"Updated {field_name}", source, confidence, user_confirmed)
        return {"updated": True, "conflict_detected": False, "field": field_name}


class CertificationAgent:
    def __init__(self, vault: VaultAgent) -> None:
        self.vault = vault

    def evaluate_and_rank(self, candidate_certifications: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        if candidate_certifications is None:
            stored = self.vault.load_artifact("certifications_research_v1.json", agent_name="CERTIFICATION_AGENT")
            candidate_certifications = stored.get("certifications", DEFAULT_CERTIFICATIONS) if stored else DEFAULT_CERTIFICATIONS
        valid = [c for c in candidate_certifications if c.get("verified", False) and c.get("free_or_paid") in ("free", "free_audit_paid_exam") and c.get("official_url", "").startswith("http")]
        valid.sort(key=lambda c: (1 if c.get("free_or_paid") == "free" else 0, c.get("credibility_score", 0)), reverse=True)
        out = {"certifications": valid}
        self.vault.save_artifact("certifications_research_v1.json", out, "application/json", ["certifications"], "CERTIFICATION_AGENT", ["Python"], ["All"], agent_name="CERTIFICATION_AGENT")
        return out


class JobSearchAgent:
    def __init__(self, vault: VaultAgent) -> None:
        self.vault = vault
        self.tracker_file = "applied_jobs_tracker_v1.json"

    @staticmethod
    def generate_search_queries(profile: Dict[str, Any]) -> List[str]:
        return ["query_1", "query_2", "query_3", "query_4", "query_5"]

    @staticmethod
    def calculate_match_score(skill_match: int, role_match: int, experience_match: int, location_match: int, interest_match: int, requirement_gap_penalty: int) -> int:
        return max(0, min(100, skill_match + role_match + experience_match + location_match + interest_match - requirement_gap_penalty))

    def generate_cold_outreach_pack(self, profile: Dict[str, Any], jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        outreach = []
        for job in jobs[:6]:
            note = f"Hi! I am Balu, B.Tech CSE student & former ABGL Software Intern. Applied for {job.get('title')} at {job.get('company')}!"[:300]
            outreach.append({"company": job.get("company"), "role": job.get("title"), "application_url": job.get("application_url"), NOTE_KEY: note, "cold_email_subject": f"Application: {job.get('title')}", "cold_email_body": "Hi Team"})
        pack = {"outreach": outreach}
        self.vault.save_artifact("cold_outreach_and_linkedin_pack_v1.json", pack, "application/json", ["outreach"], "JOB_SEARCH_AGENT", ["Python"], ["All"], agent_name="JOB_SEARCH_AGENT")
        return pack

    def sync_application_tracker(self, jobs: List[Dict[str, Any]], gmail_drafts: Dict[str, str]) -> Dict[str, Any]:
        apps = []
        for j in jobs:
            c = j.get("company", "")
            d = gmail_drafts.get(c, "")
            apps.append({"title": j.get("title"), "company": c, "work_mode": j.get("work_mode", "Remote"), "salary": j.get("salary", "Stipend"), "match_score": j.get("match_score", 90), "application_url": j.get("application_url", ""), "gmail_cold_draft_url": d, "status": "Cold Email Draft Ready" if d else "Queued"})
        tracker = {"total_tracked_jobs": len(apps), "applications": apps}
        self.vault.save_artifact(self.tracker_file, tracker, "application/json", ["tracker"], "JOB_SEARCH_AGENT", ["Python"], ["All"], agent_name="JOB_SEARCH_AGENT")
        return tracker

    def format_8am_applied_jobs_email(self, profile: Dict[str, Any], tracker_data: Dict[str, Any]) -> Tuple[str, str]:
        today_str = datetime.date.today().isoformat()
        return f"Daily Applied Jobs & Career Agent Report - {today_str}", f"Total tracked: {tracker_data.get('total_tracked_jobs', 0)}"


class SkillBuildingAgent:
    def __init__(self, vault: VaultAgent) -> None:
        self.vault = vault

    def build_and_save_roadmap(self) -> Dict[str, Any]:
        roadmap = self.vault.load_artifact("skill_roadmap_v1.json", agent_name="SKILL_BUILDING_AGENT") or DEFAULT_ROADMAP
        self.vault.save_artifact("skill_roadmap_v1.json", roadmap, "application/json", ["roadmap"], "SKILL_BUILDING_AGENT", ["FastAPI"], ["All"], agent_name="SKILL_BUILDING_AGENT")
        return roadmap

    def export_calendar_schedule_ics(self) -> str:
        ics = "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:Career Agent Sprint\nRRULE:FREQ=DAILY;COUNT=30\nEND:VEVENT\nEND:VCALENDAR"
        self.vault.save_artifact("schedule_plan_v1.ics", ics, "text/calendar", ["calendar"], "SKILL_BUILDING_AGENT", ["All"], ["All"], agent_name="SKILL_BUILDING_AGENT")
        return ics


class OrchestratorAgent:
    GMAIL_DRAFT_LINKS: Dict[str, str] = {"Gridbricks": "draft_1", "Langslide": "draft_2", "RavelCode": "draft_3", "Vortizo AI": "draft_3", "Exaful": "draft_4", "The AI Signal": "draft_5"}

    def __init__(self, vault_dir: str = "./vault", auto_push_on_operation: bool = False) -> None:
        self.git_vc = GitVersionController(repo_dir=str(pathlib.Path(__file__).resolve().parent), auto_push=auto_push_on_operation)
        self.vault = VaultAgent(vault_dir=vault_dir, operation_hook=self.git_vc.on_operation)
        self.vault.bootstrap_defaults_if_empty()
        self.memory = MemoryAgent(self.vault)
        self.cert_agent = CertificationAgent(self.vault)
        self.job_agent = JobSearchAgent(self.vault)
        self.skill_agent = SkillBuildingAgent(self.vault)

    @classmethod
    def classify_intent(cls, query: str) -> str:
        q = query.lower()
        m = []
        if any(w in q for w in ("cert", "course", "badge")):
            m.append("certification_search")
        if any(w in q for w in ("job", "intern", "apply")):
            m.append("job_search")
        if any(w in q for w in ("skill", "roadmap")):
            m.append("skill_building")
        if any(w in q for w in ("profile", "phone")):
            m.append("profile_update")
        if any(w in q for w in ("vault", "retrieve")):
            m.append("vault_retrieval")
        return m[0] if len(m) == 1 else "combined_workflow"

    def run_workflow(self, mode: str = "morning-digest", auto_commit_tag: Optional[str] = None) -> Dict[str, Any]:
        profile = self.vault.load_artifact("user_profile_v1.json") or dict(DEFAULT_PROFILE)
        jobs_data = self.vault.load_artifact("job_matches_v1.json") or {"jobs": DEFAULT_JOBS}
        certs_out = self.cert_agent.evaluate_and_rank()
        outreach_out = self.job_agent.generate_cold_outreach_pack(profile, jobs_data.get("jobs", DEFAULT_JOBS))
        tracker_data = self.job_agent.sync_application_tracker(jobs_data.get("jobs", DEFAULT_JOBS), self.GMAIL_DRAFT_LINKS)
        roadmap_out = self.skill_agent.build_and_save_roadmap()
        self.skill_agent.export_calendar_schedule_ics()
        subject, body = self.job_agent.format_8am_applied_jobs_email(profile, tracker_data)
        self.memory.write_memory("job", f"Executed {mode}", "ORCHESTRATOR_AGENT", 1.0, True)
        self.vault.save_artifact("workflow_audit_log.json", {"mode": mode, "version": VERSION, "operations": len(self.git_vc.operation_history)}, "application/json", ["audit"], "ORCHESTRATOR_AGENT", ["All"], ["All"])
        git_status = self.git_vc.commit_and_tag(f"chore(auto-sync): {mode}", tag=auto_commit_tag, push=self.git_vc.auto_push) if auto_commit_tag else {}
        return {
            "status": "success",
            "version": VERSION,
            "mode": mode,
            "user": profile.get("full_name"),
            "contact_phone": profile.get("contact_phone"),
            "email_subject": subject,
            "tracked_applications_count": tracker_data.get("total_tracked_jobs", 0),
            "outreach_templates_count": len(outreach_out.get("outreach", [])),
            "verified_certifications_count": len(certs_out.get("certifications", [])),
            "roadmap_phases_count": len(roadmap_out.get("learning_roadmap", [])),
            "operations_synced_count": len(self.git_vc.operation_history),
            "git_version_control": git_status,
            "email_preview": body,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-dir", default="./vault")
    parser.add_argument("--mode", default="morning-digest")
    parser.add_argument("--auto-tag", default=None)
    parser.add_argument("--auto-push", action="store_true")
    args = parser.parse_args()
    orch = OrchestratorAgent(vault_dir=args.vault_dir, auto_push_on_operation=args.auto_push)
    res = orch.run_workflow(mode=args.mode, auto_commit_tag=args.auto_tag)
    print(json.dumps({k: v for k, v in res.items() if k != "email_preview"}, indent=2))


if __name__ == "__main__":
    main()
CAREER_AGENT_SYSTEM (v3.0.0) – Autonomous Multi-Agent Career Development Orchestrator
Author: Kodimurthy Bhalavardan (Balu Kodimurthy) | GitHub: @balu-cod
"""

from __future__ import annotations
import argparse
import dataclasses
import datetime
import hashlib
import json
import pathlib
import subprocess
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

    def _update_index(
        self,
        file_name: str,
        file_type: str,
        tags: List[str],
        source: str,
        expiry_date: Optional[str],
        related_skills: List[str],
        related_jobs: List[str],
        sha256: str,
    ) -> None:
        now_date = datetime.date.today().isoformat()
        index_data = self.load_artifact("vault_index.json") or {"vault_version": "3.0.0", "items": []}
        existing = index_data.get("items", [])
        version = next((i.get("version", 1) + 1 for i in existing if i.get("file_name") == file_name), 1)
        items = [i for i in existing if i.get("file_name") != file_name]
        items.append(
            {
                "file_name": file_name,
                "version": version,
                "file_type": file_type,
                "upload_date": now_date,
                "tags": tags,
                "source": source,
                "expiry_date": expiry_date,
                "related_skills": related_skills,
                "related_jobs": related_jobs,
                "sha256": sha256,
            }
        )
        index_data["items"] = items
        index_data["vault_version"] = "3.0.0"
        index_data["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.index_file.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")


class JobSearchAgent:
    @staticmethod
    def calculate_match_score(
        skill_match: int,
        role_match: int,
        experience_match: int,
        location_match: int,
        interest_match: int,
        requirement_gap_penalty: int,
    ) -> int:
        return max(0, min(100, skill_match + role_match + experience_match + location_match + interest_match - requirement_gap_penalty))


class CertificationAgent:
    @staticmethod
    def filter_verified_free(certs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid = [c for c in certs if c.get("verified") and c.get("free_or_paid") in ("free", "free_audit_paid_exam")]
        return sorted(valid, key=lambda x: x.get("credibility_score", 0), reverse=True)


class MemoryAgent:
    def update_profile(self, profile: UserProfile, new_data: Dict[str, Any]) -> UserProfile:
        for k, v in new_data.items():
            if hasattr(profile, k):
                setattr(profile, k, v)
        profile.memory_last_updated = datetime.date.today().isoformat()
        return profile


class SkillBuildingAgent:
    @staticmethod
    def generate_roadmap(skill_gaps: List[str]) -> List[Dict[str, Any]]:
        return [{"skill": s, "recommended_action": f"Complete course and project for {s}", "estimated_weeks": 2} for s in skill_gaps]


class GitVersionController:
    @staticmethod
    def commit_and_tag(tag_name: str, message: Optional[str] = None) -> bool:
        msg = message or f"auto-tag: {tag_name}"
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", msg], check=False)
            subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"], check=True)
            return True
        except Exception as e:
            print(f"GitVersionController error: {e}")
            return False


class OrchestratorAgent:
    def __init__(self, vault_dir: str = "./vault") -> None:
        self.vault = VaultAgent(vault_dir)
        self.job_agent = JobSearchAgent()
        self.cert_agent = CertificationAgent()
        self.memory_agent = MemoryAgent()
        self.skill_agent = SkillBuildingAgent()
        self.git_controller = GitVersionController()


def main():
    parser = argparse.ArgumentParser(description="Career Agent System v3.0.0")
    parser.add_argument("--vault-dir", type=str, default="./vault", help="Path to vault directory")
    parser.add_argument("--mode", type=str, default="morning-digest", help="Execution mode")
    parser.add_argument("--auto-tag", type=str, default=None, help="Auto git tag version")
    args = parser.parse_args()

    orch = OrchestratorAgent(vault_dir=args.vault_dir)
    print(f"CAREER_AGENT_SYSTEM v3.0.0 initialized successfully. Mode: {args.mode}")

    if args.auto_tag:
        orch.git_controller.commit_and_tag(args.auto_tag)


if __name__ == "__main__":
    main()impor
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
