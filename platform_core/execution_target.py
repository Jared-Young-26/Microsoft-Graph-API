from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExecutionTarget(BaseModel):
    """Execution Target."""
    model_config = ConfigDict(extra="allow")

    type: str = "local"
    host: Optional[str] = None
    port: int = 22
    user: Optional[str] = None
    key_path: Optional[str] = None
    strict_host_key_checking: bool = True
    tags: List[str] = Field(default_factory=list)
    name: Optional[str] = None

    def label(self) -> str:
        """Run label."""
        if self.type == "local":
            return "local"
        if self.type == "graph":
            return "graph"
        if self.name:
            return self.name
        host = self.host or "unknown"
        user = f"{self.user}@" if self.user else ""
        return f"{user}{host}"
