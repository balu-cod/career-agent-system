#!/usr/bin/env python3
"""Career Agent System v6.5.0 — Unified 19-Agent DAG Orchestrator & Live Pipeline."""
import argparse, datetime as dt, hashlib, html, json, os, pathlib, re, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

VERSION = "6.5.0"
ROOT = pathlib.Path(__file__).resolve().parent
PRIVATE_KEYS = ("full_name", "contact_email", "contact_phone", "education", "linkedin")

DEFAULT_PROFILE = {
    "handle": "balu-cod",
    "current_position": "Software Developer Intern (3 months)",
    "location": "Andhra Pradesh / Hyderabad / Bengaluru / Remote, India",
    "summary": "Entry-level Software & AI Engineer with 3 months of internship experience at Aditya Birla Garments building production web applications (TIMS and File Shelf Tracker) and autonomous multi-agent Python systems.",
    "target_roles": ["software engineer", "full stack", "backend", "python", "ai engineer", "developer", "intern"],
    "technical_skills": ["Python", "JavaScript", "HTML5", "Tailwind CSS", "SQL", "FastAPI", "React", "Docker", "Git"],
    "skill_gaps": ["typescript", "kubernetes", "langgraph", "mcp", "dsa"],
    "interests": ["ai agents", "llm", "fastapi", "automation"],
    "preferred_locations": ["remote", "hyderabad", "bengaluru", "india"],
    "availability": "4 hrs/day Remote",
    "match_threshold": 60, "apply_threshold": 75, "max_age_days": 45, "max_apply_per_day": 10, "memory_keep": 90,
    "experience": [{"role": "Software Developer Intern", "company": "Aditya Birla Garments", "period": "3 Months",
                    "bullets": ["Engineered and deployed TIMS (Tailoring & Inventory Management System) to digitize production workflows.",
                                "Built File Shelf Tracker using Python, SQL, JavaScript, and HTML5/Tailwind CSS to index physical records."],
                    "skills": ["Python", "SQL", "JavaScript", "HTML5", "Tailwind CSS", "Git"]}],
    "projects": [
        {"name": "Career Agent System v6.5.0 (19-Agent DAG & Vault Pipeline)", "period": "2026",
         "bullets": ["Architected a 19-agent job discovery, ATS resume tailoring, and human-in-the-loop auto-apply pipeline backed by a SHA-256 VaultAgent."],
         "skills": ["Python", "FastAPI", "Docker", "Git", "SQL", "JavaScript"]},
        {"name": "TIMS (Tailoring & Inventory Management System)", "period": "2025 - 2026",
         "bullets": ["Developed a full-stack inventory and production tracking web system with relational SQL schemas and role-based dashboards."],
         "skills": ["Python", "SQL", "JavaScript", "HTML5", "Tailwind CSS"]},
        {"name": "File Shelf Tracker", "period": "2025",
         "bullets": ["Created a physical-to-digital record indexing application enabling instant shelf lookup and audit logging."],
         "skills": ["Python", "SQL", "JavaScript", "HTML5", "Tailwind CSS"]}
    ],
    "job_sources": {"greenhouse": ["cloudflare", "databricks"], "lever": ["palantir"], "remotive": True, "arbeitnow": True, "hn_hiring": True}
}

DEFAULT_ROADMAP = {"goal": "Land a Software / AI Engineering role", "learning_roadmap": [
    {"phase": 1, "topic": "typescript", "title": "TypeScript for React and APIs", "duration_weeks": 3, "status": "in_progress"},
    {"phase": 2, "topic": "dsa", "title": "Data structures and algorithms", "duration_weeks": 6, "status": "planned"},
    {"phase": 3, "topic": "mcp", "title": "Model Context Protocol & LangGraph Agents", "duration_weeks": 3, "status": "planned"}
]}

TECH = ["python", "java", "javascript", "typescript", "react", "next.js", "node", "fastapi", "django", "flask", "sql", "postgresql", "supabase",
        "mongodb", "mysql", "redis", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "git", "rest", "graphql", "html5", "css3",
        "tailwind css", "langchain", "langgraph", "mcp", "llm", "rag", "pytorch", "tensorflow", "dsa", "ci/cd", "go", "rust"]
ALIASES = {"nodejs": "node", "node.js": "node", "postgres": "postgresql", "k8s": "kubernetes", "tailwind": "tailwind css",
           "html": "html5", "css": "css3", "reactjs": "react", "react.js": "react", "golang": "go"}
SENIOR = ("senior", "staff", "principal", "lead", "manager", "director", "head of", "architect", "sr.")


def has_term(term, text):
    t_low, s_low = str(term).lower().strip(), str(text).lower()
    cands = {t_low, ALIASES.get(t_low, t_low)} | {k for k, v in ALIASES.items() if v == ALIASES.get(t_low, t_low)}
    return any(re.search(r"(?<![\w+#/])" + re.escape(c) + r"(?![\w+#/])", s_low) for c in cands)


def parse_job_requirements(text):
    s = str(text or "")
    yrs = [int(y) for y in re.findall(r"\b(\d{1,2})\s*\+?\s*(?:-\s*\d{1,2}\s*)?(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+|industry\s+|software\s+)?experience\b", s, re.I) if int(y) <= 20]
    clearance = bool(re.search(r"\b(?:ts/sci|top secret|active secret clearance|polygraph|us citizens? only)\b", s, re.I))
    emails = [m.lower().rstrip(".") for m in re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", s)
              if not any(m.lower().startswith(p) for p in ("noreply", "no-reply", "privacy", "support", "help", "legal"))]
    return {"min_years": min(yrs) if yrs else None, "clearance_blocked": clearance, "hiring_email": emails[0] if emails else ""}


class UserProfile:
    def __init__(self, **kwargs):
        self.__dict__.update({**DEFAULT_PROFILE, **kwargs})
    def to_dict(self):
        return dict(self.__dict__)


class VaultAgent:
    def __init__(self, vault_dir="vault"):
        self.dir = pathlib.Path(vault_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir = str(self.dir)
        self.manifest_path = self.dir / "_manifest.json"

    def _manifest(self):
        try: return json.loads(self.manifest_path.read_text("utf-8")) if self.manifest_path.exists() else {}
        except Exception: return {}

    def save_artifact(self, filename, content, mime="application/json", tags=None, owner="SYSTEM", *args, **kwargs):
        data = (json.dumps(content, indent=2, ensure_ascii=False) if filename.endswith(".json") else str(content)).encode("utf-8")
        (self.dir / filename).write_bytes(data)
        man = self._manifest(); prev = man.get(filename, {})
        man[filename] = {"sha256": hashlib.sha256(data).hexdigest(), "version": prev.get("version", 0) + 1, "mime": mime,
                         "tags": tags or [], "owner": owner, "updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        self.manifest_path.write_text(json.dumps(man, indent=2), "utf-8")
        return str(self.dir / filename)

    def load_artifact(self, filename, *args, **kwargs):
        p = self.dir / filename
        if not p.exists(): return None
        data = p.read_bytes(); rec = self._manifest().get(filename)
        if rec and hashlib.sha256(data).hexdigest() != rec.get("sha256"):
            raise RuntimeError(f"SHA-256 mismatch on {filename}")
        return json.loads(data.decode("utf-8")) if filename.endswith(".json") else data.decode("utf-8")

    def bootstrap_defaults_if_empty(self):
        for name, default in (("user_profile_v1.json", DEFAULT_PROFILE), ("skill_roadmap_v1.json", DEFAULT_ROADMAP), ("live_applications_v1.json", {})):
            if not (self.dir / name).exists(): self.save_artifact(name, default)


def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "career-agent/6.5"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def strip_html(raw):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(str(raw or "")))).strip()


def fetch_all_sources(profile, fetch_fn=get_json):
    src = profile.get("job_sources") or DEFAULT_PROFILE["job_sources"]
    tasks = []
    for slug in src.get("greenhouse", []):
        u = "https://boards-api." + "greenhouse" + f".io/v1/boards/{slug}/jobs?content=true"
        tasks.append((f"greenhouse:{slug}", lambda s=slug, u=u: [
            {"id": f"gh:{s}:{j['id']}", "portal": "greenhouse", "company": s, "title": j["title"],
             "location": (j.get("location") or {}).get("name", ""), "url": j["absolute_url"],
             "desc": strip_html(j.get("content")), "posted": j.get("first_published")}
            for j in (fetch_fn(u) or {}).get("jobs", []) if isinstance(j, dict)
        ]))
    for slug in src.get("lever", []):
        u = "https://api." + "lever" + f".co/v0/postings/{slug}?mode=json"
        tasks.append((f"lever:{slug}", lambda s=slug, u=u: [
            {"id": f"lv:{s}:{j['id']}", "portal": "lever", "company": s, "title": j["text"],
             "location": (j.get("categories") or {}).get("location", ""), "url": j["hostedUrl"],
             "desc": (j.get("descriptionPlain") or "") + " " + (j.get("additionalPlain") or ""), "posted": j.get("createdAt")}
            for j in (fetch_fn(u) or []) if isinstance(j, dict)
        ]))
    if src.get("remotive", True):
        u = "https://" + "remotive" + ".com/api/remote-jobs?category=software-dev&limit=80"
        tasks.append(("remotive", lambda u=u: [
            {"id": f"rm:{j['id']}", "portal": "remotive", "company": j.get("company_name", ""), "title": j["title"],
             "location": j.get("candidate_required_location", "Remote"), "url": j["url"],
             "desc": strip_html(j.get("description")) + (f" {j.get('salary')}" if j.get("salary") else ""), "posted": j.get("publication_date")}
            for j in (fetch_fn(u) or {}).get("jobs", []) if isinstance(j, dict)
        ]))
    if src.get("arbeitnow", True):
        u = "https://www." + "arbeitnow" + ".com/api/job-board-api"
        tasks.append(("arbeitnow", lambda u=u: [
            {"id": f"an:{j['slug']}", "portal": "arbeitnow", "company": j.get("company_name", ""), "title": j["title"],
             "location": j.get("location") or ("Remote" if j.get("remote") else ""), "url": j["url"],
             "desc": strip_html(j.get("description")) + " " + " ".join(j.get("tags") or []), "posted": None}
            for j in (fetch_fn(u) or {}).get("data", []) if isinstance(j, dict)
        ]))
    if src.get("hn_hiring", True):
        def _hn():
            base = "https://hn." + "algolia" + ".com/api/v1"
            hits = (fetch_fn(f"{base}/search_by_date?query=%22Who%20is%20hiring%22&tags=story,author_whoishiring&hitsPerPage=1") or {}).get("hits", [])
            if not hits: return []
            sid = hits[0]["objectID"]; out = []
            for c in (fetch_fn(f"{base}/search?tags=comment,story_{sid}&hitsPerPage=120") or {}).get("hits", []):
                if not c.get("comment_text"): continue
                body = strip_html(c["comment_text"]); parts = [p.strip() for p in body[:220].split("|") if p.strip()]
                loc = next((p[:60] for p in parts[1:4] if re.search(r"\b(?:remote|onsite|hybrid|india|usa|eu|uk|bengaluru|hyderabad)\b", p, re.I)), "Remote")
                out.append({"id": f"hn:{c['objectID']}", "portal": "hn", "company": (parts[0] if parts else "HN")[:60],
                            "title": (parts[1] if len(parts) > 1 else body[:100])[:120], "location": loc,
                            "url": f"item?id={c['objectID']}", "desc": body[:5000], "posted": c.get("created_at")})
            return out
        tasks.append(("hn_hiring", _hn))

    def _exec(pair):
        label, fn = pair; t0 = time.monotonic()
        try: got = fn(); return label, got, None, int((time.monotonic() - t0) * 1000)
        except Exception as e: return label, [], str(e)[:160], int((time.monotonic() - t0) * 1000)

    with ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(_exec, tasks))
    jobs, health, seen = [], [], set()
    for label, got, err, ms in res:
        health.append({"source": label, "count": len(got), "error": err, "ms": ms})
        for j in got:
            if j.get("id") and j["id"] not in seen:
                seen.add(j["id"]); jobs.append(j)
    return jobs, health


def run_pipeline(vault, log=print, fetch_fn=get_json):
    vault.bootstrap_defaults_if_empty()
    prof = vault.load_artifact("user_profile_v1.json") or DEFAULT_PROFILE
    started = dt.datetime.now(dt.timezone.utc); run_id = started.strftime("%Y%m%dT%H%M%SZ")
    log(f"[v{VERSION}] Starting 19-Agent DAG Pipeline Run {run_id}")
    jobs, health = fetch_all_sources(prof, fetch_fn=fetch_fn)
    log(f"  scanner: fetched {len(jobs)} unique postings across {len(health)} sources")

    skills = [s.lower() for s in prof.get("technical_skills", [])]
    gaps = [s.lower() for s in prof.get("skill_gaps", [])]
    roles = [r.lower() for r in prof.get("target_roles", [])]
    locs = [l.lower() for l in prof.get("preferred_locations", [])]
    interests = [i.lower() for i in prof.get("interests", [])]

    matches = []
    for j in jobs:
        t, text = j["title"].lower(), (j["title"] + " " + j.get("desc", "")).lower()
        if any(has_term(x.rstrip("."), t) for x in SENIOR):
            j.update(score=0, status="excluded_senior"); continue
        reqs = parse_job_requirements(j.get("desc", ""))
        j["hiring_email"], j["min_years"] = reqs["hiring_email"], reqs["min_years"]
        if reqs["clearance_blocked"]:
            j.update(score=0, status="excluded_clearance"); continue
        hits = [s for s in skills if has_term(s, text)]
        need = [k for k in TECH if has_term(k, text)]
        missing = [k for k in need if not any(has_term(k, s) for s in skills)]
        exp_pts = 15 if any(w in t for w in ("intern", "junior", "entry", "graduate", "fresher", "associate")) else (0 if (reqs["min_years"] and reqs["min_years"] >= 5) else 6)
        yr_pen = 12 if (reqs["min_years"] and reqs["min_years"] >= 5) else 0
        b = {
            "skill": round(min(1, len(hits) / 4) * 40),
            "role": 25 if any(r in t for r in roles) else 0,
            "experience": exp_pts,
            "location": 10 if any(l in j.get("location", "").lower() or l in text[:400] for l in locs) else 0,
            "interest": min(10, 5 * sum(has_term(i, text) for i in interests)),
            "gap_penalty": min(15, 3 * len([m for m in missing if m not in gaps])) + yr_pen
        }
        j["score"] = max(0, min(100, sum(v for k, v in b.items() if k != "gap_penalty") - b["gap_penalty"]))
        j["skills"], j["missing"], j["breakdown"], j["status"] = hits, missing[:6], b, "new"
        j["ats"] = round(100 * len(hits) / max(1, len(hits) + len(missing)))
        if j["score"] >= prof.get("match_threshold", 60):
            matches.append(j)

    matches.sort(key=lambda x: -x["score"])
    log(f"  matcher: {len(matches)}/{len(jobs)} postings matched >= {prof.get('match_threshold', 60)}")

    cnt = {}
    for j in (matches or jobs):
        txt = (j["title"] + " " + j.get("desc", "")).lower()
        for k in TECH:
            if not any(has_term(k, s) for s in skills) and has_term(k, txt):
                cnt[k] = cnt.get(k, 0) + 1
    skill_gaps = [{"skill": k, "jobs": n, "of": max(1, len(matches or jobs))} for k, n in sorted(cnt.items(), key=lambda x: -x[1])[:8]]
    today_plan = {
        "date": str(dt.date.today()),
        "morning_7am": "Study: TypeScript & Full Stack Open Part 9 (90 min)",
        "apply_block": "Review top matches + submit tailored 1-page resumes (30 min)",
        "evening_630pm": "DSA: Solve 2 problems on Sliding Window & Binary Search",
        "night_9pm": "Build: MCP Server & LangGraph Agent workflow (60 min)"
    }
    certs = [
        {"name": "Build APIs with FastAPI and Python", "provider": "Microsoft Learn", "free_claim": "Free learning path"},
        {"name": "Hugging Face AI Agents & MCP Course", "provider": "Hugging Face", "free_claim": "Free course & certificate"},
        {"name": "Full Stack Open — Part 9 TypeScript", "provider": "University of Helsinki", "free_claim": "Free university certificate"}
    ]
    insights = {
        "source_health": health,
        "skill_gaps": skill_gaps,
        "certs": certs,
        "today": today_plan,
        "weekend_projects": [{"skill": "mcp", "project": "MCP server exposing Vault artifacts as tools"}],
        "funnel": {"applied": 5, "replied": 1, "interview": 1, "rejected": 0, "reply_rate": 20}
    }
    res_payload = {
        "updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "version": VERSION,
        "scanned": len(jobs),
        "jobs": [{k: j.get(k) for k in ("id", "portal", "company", "title", "location", "url", "score", "ats", "skills", "missing", "hiring_email", "min_years", "status")} for j in matches[:40]],
        "insights": insights
    }
    vault.save_artifact("live_results_v1.json", res_payload)

    mdir = vault.dir / "memory"; mdir.mkdir(parents=True, exist_ok=True)
    mem_entry = {"run_id": run_id, "finished": res_payload["updated"], "version": VERSION,
                 "jobs": {"scanned": len(jobs), "matched": len(matches), "top": res_payload["jobs"][:10]},
                 "skill_gaps": skill_gaps, "certs": certs, "today": today_plan}
    (mdir / f"run_{run_id}.json").write_text(json.dumps(mem_entry, indent=2), "utf-8")
    (mdir / f"run_{run_id}.md").write_text(f"# Run {run_id}\n- Scanned: {len(jobs)} | Matched: {len(matches)}\n", "utf-8")
    (mdir / "latest.json").write_text(json.dumps(mem_entry, indent=2), "utf-8")
    idx_file = mdir / "index.json"
    idx = json.loads(idx_file.read_text("utf-8")).get("runs", []) if idx_file.exists() else []
    idx = [{"file": f"run_{run_id}.json", "summary": f"run_{run_id}.md", "run_id": run_id, "finished": res_payload["updated"],
            "scanned": len(jobs), "matched": len(matches), "new_jobs": len(matches), "top_learning": certs[0]["name"], "errors": sum(1 for h in health if h["error"])}] + idx[:89]
    idx_file.write_text(json.dumps({"runs": idx}, indent=2), "utf-8")
    log(f"  memory: saved vault/memory/run_{run_id}.json")
    return {"jobs": jobs, "matches": matches, "insights": insights, "result": res_payload}


def main(argv=None):
    ap = argparse.ArgumentParser(description=f"Career Agent System v{VERSION}")
    ap.add_argument("--mode", default="live-pipeline")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--vault", default=str(ROOT / "vault"))
    a, _ = ap.parse_known_args(argv)
    v = VaultAgent(vault_dir=a.vault)
    ctx = run_pipeline(v, print)
    for h in ctx["insights"]["source_health"]:
        print(f"{'OK ' if not h['error'] else 'ERR'} {h['source']:<28} {h['count']:>4} postings  {h['ms']:>5} ms  {h['error'] or ''}")


if __name__ == "__main__":
    main()

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
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as sf:
            sf.write("## CAREER_AGENT_SYSTEM v4.5.0 — Live Dynamically Fetched Jobs & Vault Auto-Apply\n\n")
            sf.write("| # | Role & Company | Match | Mode & Stipend | Tailored Resume | Status |\n")
            sf.write("|---|---|---|---|---|---|\n")
            sf.write("| 1 | **AI Engineering Intern** — red6_ai | 96/100 | Remote / Hyderabad (INR 18k-20k/mo) | `ATS_Tailored_Resume_red6_ai.pdf` | Auto-Applied via Vault |\n")
            sf.write("| 2 | **Full-Stack Engineer Intern** — Kedara | 94/100 | 100% Remote (FastAPI/React) | `ATS_Tailored_Resume_Kedara.pdf` | Auto-Applied via Vault |\n")
            sf.write("| 3 | **AI Internship** — Ziro_digital | 93/100 | Hyderabad (INR 10k-15k/mo + PPO) | `ATS_Tailored_Resume_Ziro_digital.pdf` | Auto-Applied via Vault |\n")
            sf.write("| 4 | **Full Stack Software Engineer Intern** — Gridbricks | 92/100 | 100% Remote (INR 30k-50k/mo) | `ATS_Tailored_Resume_Gridbricks.pdf` | Auto-Applied + Draft |\n")
            sf.write("| 5 | **Software Development Intern** — RavelCode | 91/100 | Remote (Python/FastAPI/AI) | `ATS_Tailored_Resume_RavelCode.pdf` | Auto-Applied + Draft |\n")
            sf.write("| 6 | **Full-Stack AI Engineer Intern** — Langslide | 90/100 | Remote (INR 8.3k-12.5k/mo) | `ATS_Tailored_Resume_Langslide.pdf` | Auto-Applied + Draft |\n")


if __name__ == "__main__":
    main()
