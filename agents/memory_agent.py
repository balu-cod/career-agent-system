"""MemoryAgent for updating and writing memory to user profile."""

from typing import Dict, Any, Optional
from .vault_agent import VaultAgent

class MemoryAgent:
    def __init__(self, vault: VaultAgent):
        self.vault = vault

    def write_memory(self, memory_key: str, data: Any) -> Dict[str, Any]:
        profile = self.vault.load_artifact("user_profile_v1.json") or {}
        if "memories" not in profile:
            profile["memories"] = {}
        profile["memories"][memory_key] = data
        self.vault.save_artifact("user_profile_v1.json", profile)
        return {"status": "saved", "key": memory_key}

    def update_profile_field(self, field_name: str, value: Any) -> Dict[str, Any]:
        profile = self.vault.load_artifact("user_profile_v1.json") or {}
        profile[field_name] = value
        self.vault.save_artifact("user_profile_v1.json", profile)
        return {"status": "updated", "field": field_name, "value": value}
