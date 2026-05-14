from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, ConfigDict, model_validator

class Priority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

def now_ist() -> datetime:
    return datetime.now(ZoneInfo("Asia/Kolkata"))

class Ticket(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    internal_ticket_id: str = Field(default_factory=lambda: str(uuid4()))
    source: str = Field(default="api")

    ticket_id: str

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)

    priority: Priority

    department: str = Field(min_length=1)
    location: str = Field(min_length=1)

    created_at: datetime = Field(default_factory=now_ist)

    @property
    def text(self) -> str:
        """Routing-friendly searchable text."""
        return f"{self.title} {self.description}".lower().strip()

    @model_validator(mode="after")
    def normalize(self) -> "Ticket":
        self.source = (self.source or "api").lower().strip()
        self.department = self.department.strip()
        self.location = self.location.strip()
        self.title = self.title.strip()
        self.description = self.description.strip()
        
        return self