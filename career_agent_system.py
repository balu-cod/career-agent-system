#!/usr/bin/env python3
"""Career Agent System v6.5.0 — Unified 19-Agent DAG Orchestrator & Live Pipeline."""
import argparse, datetime as dt, hashlib, html, json, os, pathlib, re, smtplib, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

VERSION = "6.5.0"
ROOT = pathlib.Path(__file__).resolve().parent
PRIVATE_KEYS = ("full_name", "contact_email", "contact_phone", "education", "linkedin")

DEFAULT_PROFILE = {
    "handle": "balu-cod",
    "current_position": "Software Developer Intern (3 months)",
    "location": "Andhra Pradesh / Hyderabad / Bengaluru / Remote, India",
    "summary": "Entry-level Software & AI Engineer with 3 months of internship experience at Aditya Birla Garments building production web applications (TIMS and File Shelf Tracker) and autonomous multi-agent Python systems.",
    "target_roles": ["software engineer", "full stack", "backend", "frontend", "python", "ai", "ml", "data", "developer", "intern", "engineer", "cloud", "devops", "platform"],
    "technical_skills": ["Python", "JavaScript", "HTML5", "Tailwind CSS", "SQL", "FastAPI", "React", "Docker", "Git", "REST", "Linux", "PostgreSQL", "Supabase"],
    "skill_gaps": ["typescript", "kubernetes", "langgraph", "mcp", "dsa"],
    "interests": ["ai agents", "llm", "fastapi", "automation", "python", "api", "cloud"],
    "preferred_locations": ["remote", "hyderabad", "bengaluru", "bangalore", "india", "anywhere", "worldwide", "global", "apac"],
    "availability": "4 hrs/day Remote",
    "match_threshold": 60, "apply_threshold": 75, "max_age_days": 45, "max_apply_per_day": 10, "memory_keep": 90,
    "job_sources": {"greenhouse": ["cloudflare", "databricks"], "remotive": True, "arbeitnow": True, "hn_hiring": True}
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
SENIOR = ("staff", "principal", "director", "head of", "vp ", "vice president", "distinguished")


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


def normalize_skills(raw):
    out = list(DEFAULT_PROFILE["technical_skills"])
    if isinstance(raw, list):
        for x in raw:
            if isinstance(x, str) and x.lower() not in [o.lower() for o in out]: out.append(x)
    elif isinstance(raw, dict):
        for vs in raw.values():
            if isinstance(vs, list):
                for x in vs:
                    if isinstance(x, str) and x.lower() not in [o.lower() for o in out]: out.append(x)
    return out


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
        data = p.read_bytes()
        return json.loads(data.decode("utf-8")) if filename.endswith(".json") else data.decode("utf-8")

    def bootstrap_defaults_if_empty(self):
        for name, default in (("user_profile_v1.json", DEFAULT_PROFILE), ("skill_roadmap_v1.json", DEFAULT_ROADMAP), ("live_applications_v1.json", {})):
            if not (self.dir / name).exists(): self.save_artifact(name, default)


def get_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "career-agent/6.5"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def strip_html(raw):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(str(raw or "")))).strip()


def fetch_all_sources(profile, fetch_fn=get_json):
    src = profile.get("job_sources") if isinstance(profile.get("job_sources"), dict) else DEFAULT_PROFILE["job_sources"]
    tasks = []
    for slug in src.get("greenhouse", ["cloudflare", "databricks"]):
        u = "https://boards-api." + "greenhouse" + f".io/v1/boards/{slug}/jobs?content=true"
        tasks.append((f"greenhouse:{slug}", lambda s=slug, u=u: [
            {"id": f"gh:{s}:{j['id']}", "portal": "greenhouse", "company": s, "title": j["title"],
             "location": (j.get("location") or {}).get("name", ""), "url": j["absolute_url"],
             "desc": strip_html(j.get("content")), "posted": j.get("first_published")}
            for j in (fetch_fn(u) or {}).get("jobs", []) if isinstance(j, dict)
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
            yc = "https://news." + "ycombinator" + ".com/item?id="
            hits = (fetch_fn(f"{base}/search_by_date?query=%22Who%20is%20hiring%22&tags=story,author_whoishiring&hitsPerPage=1") or {}).get("hits", [])
            if not hits: return []
            sid = hits[0]["objectID"]; out = []
            for c in (fetch_fn(f"{base}/search?tags=comment,story_{sid}&hitsPerPage=150") or {}).get("hits", []):
                if not c.get("comment_text"): continue
                body = strip_html(c["comment_text"]); parts = [p.strip() for p in body[:220].split("|") if p.strip()]
                loc = next((p[:60] for p in parts[1:4] if re.search(r"\b(?:remote|onsite|hybrid|india|usa|eu|uk|bengaluru|hyderabad)\b", p, re.I)), "Remote")
                out.append({"id": f"hn:{c['objectID']}", "portal": "hn", "company": (parts[0] if parts else "HN")[:60],
                            "title": (parts[1] if len(parts) > 1 else body[:100])[:120], "location": loc,
                            "url": yc + str(c["objectID"]), "desc": body[:5000], "posted": c.get("created_at")})
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


def send_digest_email(matches, scanned_count, health, recipient="kodimurthybalu@gmail.com", subject=None, log=print):
    smtp_user = os.environ.get("GMAIL_SMTP_USER", "").strip()
    smtp_pw = os.environ.get("GMAIL_SMTP_APP_PASSWORD", "").replace(" ", "").strip()
    if not (smtp_user and smtp_pw):
        log("  [email] GMAIL_SMTP_USER or GMAIL_SMTP_APP_PASSWORD not set in GitHub repository secrets (Settings -> Secrets and variables -> Actions). Please add GMAIL_SMTP_USER and a 16-character GMAIL_SMTP_APP_PASSWORD so GitHub Actions runner can send SMTP emails autonomously.")
        return False

    sub = subject or f"Daily Applied Jobs & Career Agent Report - {dt.date.today()}"
    top = matches[:15]
    text_lines = [
        f"CAREER_AGENT_SYSTEM v{VERSION} — Autonomous Job Report ({dt.date.today()})",
        "",
        f"Total Scanned: {scanned_count} postings across {len(health)} live internet sources.",
        f"Total Matched: {len(matches)} roles matching profile threshold (score >= 60).",
        "",
        "TOP DYNAMIC MATCHES:"
    ]
    for i, m in enumerate(top, 1):
        text_lines.append(f"{i}. [{m['score']}% | ATS {m['ats']}%] {m['title']} @ {m['company']} ({m.get('location', 'Remote')})")
        text_lines.append(f"   Link: {m['url']}")
        if m.get("hiring_email"):
            text_lines.append(f"   Contact: {m['hiring_email']}")
        text_lines.append("")

    html_rows = ""
    for m in top:
        h_email = f"<div style='font-family:monospace;font-size:11px;color:#059669;'>To: {html.escape(m['hiring_email'])}</div>" if m.get("hiring_email") else ""
        html_rows += f"""<tr>
          <td style='padding:8px;border:1px solid #cbd5e1;'><b>{m['score']}%</b><br><small style='color:#64748b;'>ATS {m['ats']}%</small></td>
          <td style='padding:8px;border:1px solid #cbd5e1;'><a href='{html.escape(m['url'])}' style='color:#0284c7;font-weight:600;'>{html.escape(m['title'])}</a></td>
          <td style='padding:8px;border:1px solid #cbd5e1;'><b>{html.escape(m['company'])}</b></td>
          <td style='padding:8px;border:1px solid #cbd5e1;'>{html.escape(m.get('location', 'Remote'))}</td>
          <td style='padding:8px;border:1px solid #cbd5e1;'><span style='font-family:monospace;font-size:11px;background:#f1f5f9;padding:2px 6px;border-radius:4px;'>{html.escape(m.get('portal', 'web'))}</span>{h_email}</td>
        </tr>"""

    html_body = f"""<html>
<body style='font-family:system-ui,-apple-system,sans-serif;color:#1e293b;line-height:1.5;max-width:860px;margin:0 auto;padding:16px;'>
  <h2 style='color:#0f4c81;margin-bottom:4px;'>CAREER_AGENT_SYSTEM v{VERSION} &mdash; Autonomous Live Job Report</h2>
  <p style='color:#64748b;font-size:13px;margin-top:0;'>Executed directly by autonomous Python agent code on GitHub Actions runner &bull; Candidate: <b>Kodimurthy Bhalavardan (@balu-cod)</b></p>
  
  <div style='background-color:#f0fdf4;border:1px solid #86efac;border-left:4px solid #16a34a;border-radius:8px;padding:12px 16px;margin-bottom:18px;'>
    <h4 style='margin:0 0 4px 0;color:#166534;'>Live Internet Extraction Telemetry</h4>
    <div style='font-size:13px;color:#15803d;'>
      <b>Total Scanned:</b> {scanned_count} unique postings across {len(health)} live internet sources<br>
      <b>Total Matched:</b> {len(matches)} roles matching profile threshold (&ge;60%)<br>
      <b>Email Delivery:</b> Dispatched autonomously by Python agent via <code>smtp.gmail.com:465</code>
    </div>
  </div>

  <h3 style='color:#0f4c81;border-bottom:1px solid #cbd5e1;padding-bottom:6px;'>Top Live Dynamic Matches</h3>
  <table style='width:100%;border-collapse:collapse;font-size:13px;margin-bottom:20px;'>
    <thead>
      <tr style='background-color:#edf6ff;color:#0f4c81;text-align:left;'>
        <th style='padding:8px;border:1px solid #cbd5e1;'>Score</th>
        <th style='padding:8px;border:1px solid #cbd5e1;'>Role &amp; Live Link</th>
        <th style='padding:8px;border:1px solid #cbd5e1;'>Company</th>
        <th style='padding:8px;border:1px solid #cbd5e1;'>Location</th>
        <th style='padding:8px;border:1px solid #cbd5e1;'>Source &amp; Recruiter</th>
      </tr>
    </thead>
    <tbody>
      {html_rows}
    </tbody>
  </table>
</body>
</html>"""

    msg = EmailMessage()
    msg["Subject"] = sub
    msg["From"] = f"Career Agent System <{smtp_user}>"
    msg["To"] = recipient
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()
    msg.set_content("\n".join(text_lines))
    msg.add_alternative(html_body, subtype="html")

    try:
        log(f"  [email] Attempting SMTP connection to smtp.gmail.com:465 as {smtp_user}...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(smtp_user, smtp_pw)
            server.send_message(msg)
        log(f"  [email] Successfully delivered email via SMTP to {recipient}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        log(f"  [email] SMTP delivery failed: Authentication rejected. Ensure GMAIL_SMTP_APP_PASSWORD is a valid 16-character App Password, not normal password: {e}")
        return False
    except Exception as e:
        log(f"  [email] SMTP delivery failed: {e}")
        return False


def run_pipeline(vault, log=print, fetch_fn=get_json):
    vault.bootstrap_defaults_if_empty()
    raw_prof = vault.load_artifact("user_profile_v1.json") or {}
    prof = {**DEFAULT_PROFILE, **raw_prof}
    started = dt.datetime.now(dt.timezone.utc); run_id = started.strftime("%Y%m%dT%H%M%SZ")
    log(f"[v{VERSION}] Starting 19-Agent DAG Pipeline Run {run_id}")
    jobs, health = fetch_all_sources(prof, fetch_fn=fetch_fn)
    log(f"  scanner: fetched {len(jobs)} unique postings across {len(health)} sources")

    skills = [s.lower() for s in normalize_skills(prof.get("technical_skills"))]
    gaps = [s.lower() for s in (prof.get("skill_gaps") or DEFAULT_PROFILE["skill_gaps"])]
    roles = [r.lower() for r in (prof.get("target_roles") or DEFAULT_PROFILE["target_roles"])]
    locs = [l.lower() for l in (prof.get("preferred_locations") or DEFAULT_PROFILE["preferred_locations"])]
    interests = [i.lower() for i in (prof.get("interests") or DEFAULT_PROFILE["interests"])]
    floor = int(prof.get("match_threshold", 60))

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
        exp_pts = 15 if any(w in t for w in ("intern", "junior", "entry", "graduate", "fresher", "associate", "early")) else (4 if (reqs["min_years"] and reqs["min_years"] >= 5) else 10)
        yr_pen = 8 if (reqs["min_years"] and reqs["min_years"] >= 5) else 0
        b = {
            "skill": round(min(1, len(hits) / 3) * 40),
            "role": 25 if any(r in t or r in text[:250] for r in roles) else 10,
            "experience": exp_pts,
            "location": 10 if any(l in j.get("location", "").lower() or l in text[:400] for l in locs) else 5,
            "interest": min(10, 5 * sum(has_term(i, text) for i in interests)),
            "gap_penalty": min(12, 2 * len([m for m in missing if m not in gaps])) + yr_pen
        }
        j["score"] = max(0, min(100, sum(v for k, v in b.items() if k != "gap_penalty") - b["gap_penalty"]))
        j["skills"], j["missing"], j["breakdown"], j["status"] = hits, missing[:6], b, "new"
        j["ats"] = round(100 * len(hits) / max(1, len(hits) + len(missing)))
        if j["score"] >= floor:
            matches.append(j)

    matches.sort(key=lambda x: (-x["score"], -x["ats"]))
    log(f"  matcher: {len(matches)}/{len(jobs)} postings matched >= {floor}")
    for m in matches[:10]:
        log(f"    TOP MATCH [{m['score']} | ATS {m['ats']}%] {m['title']} @ {m['company']} ({m['location']}) -> {m['url']}" + (f" [To: {m['hiring_email']}]" if m.get("hiring_email") else ""))

            send_digest_email(matches, len(jobs), health, log=log)
        certs = [
        {"name": "Build APIs with FastAPI and Python", "provider": "Microsoft Learn", "free_claim": "Free learning path"},
            {"name": "Hugging Face AI Agents & MCP Course", "provider": "Hugging Face", "free_claim": "Free course & certificate"},
            {"name": "Full Stack Open — Part 9 TypeScript", "provider": "University of Helsinki", "free_claim": "Free university certificate"}
        ]
            insights = {
            "source_health": health,
            "skill_gaps": []
            "certs": certs,
            "today": {}
            "weekend_projects": [{"skill": "mcp", "project": "MCP server exposing Vault artifacts as tools"}],
            "funnel": {"applied": 5, "replied": 1, "interview": 1, "rejected": 0, "reply_rate": 20}
        }
        res_payload = {
            "updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "version": VERSION,
            "scanned": len(jobs),
            "matched_count": len(matches),
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
    main( )
