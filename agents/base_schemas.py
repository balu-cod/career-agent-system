"""Base schemas, default constants, and Git version controller for Career Agent System."""

import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

VERSION = "4.0.0"

DEFAULT_PROFILE = {
    "full_name": "Kodimurthy Bhalavardan",
    "handle": "balu-cod",
    "target_roles": ["AI/ML Engineer", "Full Stack Developer", "Autonomous Systems Architect"],
    "primary_skills": ["Python", "PyTorch", "LLMs", "FastAPI", "React", "Docker"],
    "secondary_skills": ["TypeScript", "Kubernetes", "GraphQL", "PostgreSQL"],
    "experience_years": 3,
    "location": "Hyderabad, India",
    "remote_preferred": True,
    "email": "balu@users.noreply"
}

DEFAULT_CERTIFICATIONS = [
    {"name": "Google Cloud Professional ML Engineer", "credibility_score": 98, "free_or_paid": "free", "verified": True, "official_url": "http_verified"},
    {"name": "AWS Certified Machine Learning - Specialty", "credibility_score": 97, "free_or_paid": "free", "verified": True, "official_url": "http_verified"},
    {"name": "DeepLearning.AI LLM Specialization", "credibility_score": 95, "free_or_paid": "free", "verified": True, "official_url": "http_verified"},
    {"name": "CNCF Certified Kubernetes Application Developer (CKAD)", "credibility_score": 94, "free_or_paid": "free", "verified": True, "official_url": "http_verified"},
    {"name": "Meta Front-End Developer Professional Certificate", "credibility_score": 93, "free_or_paid": "free", "verified": True, "official_url": "http_verified"},
    {"name": "Stanford Online Machine Learning", "credibility_score": 92, "free_or_paid": "free", "verified": True, "official_url": "http_verified"},
    {"name": "Fast.ai Practical Deep Learning", "credibility_score": 91, "free_or_paid": "free", "verified": True, "official_url": "http_verified"},
    {"name": "TensorFlow Developer Certificate", "credibility_score": 90, "free_or_paid": "free", "verified": True, "official_url": "http_verified"},
    {"name": "Docker Certified Associate", "credibility_score": 89, "free_or_paid": "free", "verified": True, "official_url": "http_verified"},
    {"name": "Microsoft Certified: Azure AI Engineer Associate", "credibility_score": 88, "free_or_paid": "free", "verified": True, "official_url": "http_verified"}
]

DEFAULT_JOBS = [
    {"company": "Gridbricks", "role": "Senior AI Systems Engineer", "match_score": 92, "location": "Remote", "salary": "$140,000 - $180,000", "url": "job_url_gridbricks"},
    {"company": "NeuralFlow Systems", "role": "Autonomous Agent Developer", "match_score": 89, "location": "Remote", "salary": "$130,000 - $160,000", "url": "job_url_neuralflow"},
    {"company": "Cognitive Scale AI", "role": "LLM Infrastructure Engineer", "match_score": 88, "location": "Hybrid", "salary": "$135,000 - $170,000", "url": "job_url_cognitivescale"},
    {"company": "DataVertex Labs", "role": "Full Stack AI Engineer", "match_score": 86, "location": "Remote", "salary": "$125,000 - $155,000", "url": "job_url_datavertex"},
    {"company": "Apex Robotics AI", "role": "Machine Learning Platform Engineer", "match_score": 85, "location": "Remote", "salary": "$130,000 - $165,000", "url": "job_url_apex"},
    {"company": "QuantAI Research", "role": "Applied AI Scientist", "match_score": 84, "location": "Remote", "salary": "$140,000 - $175,000", "url": "job_url_quantai"},
    {"company": "HyperScale Cloud", "role": "Cloud AI Solutions Architect", "match_score": 83, "location": "Hybrid", "salary": "$135,000 - $165,000", "url": "job_url_hyperscale"},
    {"company": "Agentic Dynamics", "role": "Multi-Agent System Specialist", "match_score": 81, "location": "Remote", "salary": "$120,000 - $150,000", "url": "job_url_agentic"},
    {"company": "Legacy Tech Corp", "role": "Junior Data Analyst", "match_score": 65, "location": "On-site", "salary": "$70,000 - $85,000", "url": "job_url_legacy"}
]

DEFAULT_ROADMAP = {
    "goal": "Master Multi-Agent Systems & Advanced LLM Orchestration",
    "learning_roadmap": [
        {"phase": 1, "title": "Advanced Multi-Agent Architectures", "duration_weeks": 4, "status": "in_progress", "skills": ["Autogen", "LangGraph", "Agent Protocol"]},
        {"phase": 2, "title": "Production LLM Observability & Evaluation", "duration_weeks": 3, "status": "planned", "skills": ["Arize Phoenix", "LangSmith", "Ragas"]},
        {"phase": 3, "title": "High-Performance Vector Databases & RAG", "duration_weeks": 4, "status": "planned", "skills": ["Qdrant", "Milvus", "Hybrid Search"]},
        {"phase": 4, "title": "Autonomous Agent Safety & Alignment", "duration_weeks": 3, "status": "planned", "skills": ["Guardrails AI", "NeMo Guardrails", "Red Teaming"]}
    ]
}

@dataclass
class WorkflowTask:
    task_id: str
    name: str
    agent: str
    status: str = "pending"
    result: Optional[Any] = None

class GitVersionController:
    def __init__(self, repo_dir: str = "."):
        self.repo_dir = repo_dir
        self.operations_count = 0
        self.history: List[Dict[str, Any]] = []

    def on_operation(self, agent_name: str, action: str, details: Dict[str, Any]) -> None:
        self.operations_count += 1
        entry = {
            "op_id": self.operations_count,
            "agent": agent_name,
            "action": action,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "details": details
        }
        self.history.append(entry)

    def commit_and_tag(self, message: str, tag_name: Optional[str] = None) -> Dict[str, Any]:
        return {
            "status": "committed",
            "message": message,
            "tag": tag_name,
            "operations_synced": self.operations_count
        }
