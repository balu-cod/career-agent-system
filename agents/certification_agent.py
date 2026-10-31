"""CertificationAgent for evaluating and ranking verified certifications."""

from typing import Dict, List, Any, Optional
from .vault_agent import VaultAgent
from .base_schemas import DEFAULT_CERTIFICATIONS

class CertificationAgent:
    def __init__(self, vault: VaultAgent):
        self.vault = vault

    def evaluate_and_rank(self) -> List[Dict[str, Any]]:
        certs = self.vault.load_artifact("verified_certifications_v1.json")
        if not certs:
            certs = DEFAULT_CERTIFICATIONS
            self.vault.save_artifact("verified_certifications_v1.json", certs)
        
        sorted_certs = sorted(certs, key=lambda c: c.get("credibility_score", 0), reverse=True)
        self.vault.save_artifact("verified_certifications_v1.json", sorted_certs)
        return sorted_certs
