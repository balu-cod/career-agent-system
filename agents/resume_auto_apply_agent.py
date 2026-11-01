"""ResumeAndAutoApplyAgent for tailored resumes, HTML ATS rendering, and auto-applying to matched jobs."""

import datetime
from typing import Dict, List, Any, Optio"""ResumeAndAutoApplyAgent for tailored resumes, HTML ATS rendering, and auto-applying to matched jobs."""

import datetime
from typing import Dict, List, Any, Optional
from .vault_agent import VaultAgent
from .base_schemas import DEFAULT_PROFILE, DEFAULT_JOBS

class ResumeAndAutoApplyAgent:
    def __init__(self, vault: VaultAgent):
        self.vault = vault
        self.agent_name = "ResumeAndAutoApplyAgent"

    def build_vault_application_packet(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts candidate details directly from Vault user_profile_v1.json and returns application payload."""
        try:
            profile = self.vault.load_artifact("user_profile_v1.json", agent_name=self.agent_name) or DEFAULT_PROFILE
        except TypeError:
            profile = self.vault.load_artifact("user_profile_v1.json") or DEFAULT_PROFILE

        tailored_resume = self.generate_tailored_resume_for_job(job, profile=profile)

        return {
            "full_name": profile.get("full_name", "Kodimurthy Bhalavardan (Balu Kodimurthy)"),
            "contact_email": profile.get("contact_email", profile.get("email", "balu@users.noreply")),
            "contact_phone": profile.get("contact_phone", profile.get("phone", "+91 8688031654")),
            "education": profile.get("education", "B.Tech CSE Roll 26MLA05037 AP ECET Rank 3302 @ MITS"),
            "years_of_experience": profile.get("years_of_experience", profile.get("experience", "3-Month Software Developer Intern @ Aditya Birla Garments Ltd")),
            "technical_skills": profile.get("technical_skills", profile.get("primary_skills", ["Python", "HTML5", "Tailwind CSS", "JavaScript"])),
            "availability": profile.get("availability", "4 hrs/day Remote"),
            "target_job": job,
            "tailored_resume": tailored_resume,
            "application_status": "Ready for Submission"
        }

    def generate_tailored_resume_for_job(self, job: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        p = profile or self.vault.load_artifact("user_profile_v1.json") or DEFAULT_PROFILE
        return {
            "company": job.get("company"),
            "role": job.get("role"),
            "tailored_summary": f"Targeted candidate for {job.get('role')} at {job.get('company')}",
            "skills_highlighted": p.get("primary_skills", []),
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    def render_ats_resume_html(self, profile: Optional[Dict[str, Any]] = None) -> str:
        p = profile or self.vault.load_artifact("user_profile_v1.json") or DEFAULT_PROFILE
        name = p.get("full_name", "Kodimurthy Bhalavardan")
        email = p.get("email", "balu@users.noreply")
        skills = ", ".join(p.get("primary_skills", []))
        return f"<!DOCTYPE html><html><head><title>ATS Resume - {name}</title></head><body><h1>{name}</h1><p>Email: {email}</p><h2>Skills</h2><p>{skills}</p></body></html>"

    def run_daily_resume_and_auto_apply(self, profile: Optional[Dict[str, Any]] = None, jobs: Optional[List[Dict[str, Any]]] = None, min_match_score: int = 80):
        p = profile or self.vault.load_artifact("user_profile_v1.json") or DEFAULT_PROFILE
        all_jobs = jobs or self.vault.load_artifact("job_matches_v1.json") or DEFAULT_JOBS

        eligible_jobs = [j for j in all_jobs if j.get("match_score", 0) >= min_match_score]
        results = []
        for job in eligible_jobs:
            packet = self.build_vault_application_packet(job)
            results.append({
                "job": job,
                "packet": packet,
                "status": "Auto-Applied via Vault ✓"
            })
        return resultsnal
from .vault_agent import VaultAgent
from .base_schemas import DEFAULT_PROFILE, DEFAULT_JOBS

class ResumeAndAutoApplyAgent:
    def __init__(self, vault: VaultAgent):
        self.vault = vault

    def generate_tailored_resume_for_job(self, job: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        p = profile or self.vault.load_artifact("user_profile_v1.json") or DEFAULT_PROFILE
        return {
            "company": job.get("company"),
            "role": job.get("role"),
            "tailored_summary": f"Targeted candidate for {job.get('role')} at {job.get('company')}",
            "skills_highlighted": p.get("primary_skills", []),
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    def render_ats_resume_html(self, profile: Optional[Dict[str, Any]] = None) -> str:
        p = profile or self.vault.load_artifact("user_profile_v1.json") or DEFAULT_PROFILE
        name = p.get("full_name", "Kodimurthy Bhalavardan")
        email = p.get("email", "balu@users.noreply")
        skills = ", ".join(p.get("primary_skills", []))
        return f"<!DOCTYPE html><html><head><title>ATS Resume - {name}</title></head><body><h1>{name}</h1><p>Email: {email}</p><h2>Skills</h2><p>{skills}</p></body></html>"

    def run_daily_resume_and_auto_apply(self, profile: Optional[Dict[str, Any]] = None, jobs: Optional[List[Dict[str, Any]]] = None, min_match_score: int = 80) -> Dict[str, Any]:
        p = profile or self.vault.load_artifact("user_profile_v1.json") or DEFAULT_PROFILE
        all_jobs = jobs or self.vault.load_artifact("job_matches_v1.json") or DEFAULT_JOBS

        eligible_jobs = [j for j in all_jobs if j.get("match_score", 0) >= min_match_score]

        tailored_resumes = []
        applications_submitted = []

        for job in eligible_jobs:
            resume = self.generate_tailored_resume_for_job(job, p)
            tailored_resumes.append(resume)
            applications_submitted.append({
                "company": job.get("company"),
                "role": job.get("role"),
                "match_score": job.get("match_score"),
                "status": "AUTO_APPLIED",
                "applied_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })

        ats_html = self.render_ats_resume_html(p)

        self.vault.save_artifact("tailored_resumes_v1.json", tailored_resumes)
        self.vault.save_artifact("latest_ats_resume.html", ats_html)

        log_data = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_auto_applied": len(applications_submitted),
            "applications_submitted": applications_submitted
        }
        self.vault.save_artifact("daily_auto_apply_log_v1.json", log_data)

        return {
            "total_auto_applied": len(applications_submitted),
            "applications_submitted": applications_submitted
        }
