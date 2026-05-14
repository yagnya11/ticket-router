from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict


class TicketStatus(str, Enum):
  NEW = "NEW"
  ROUTED = "ROUTED"
  ASSIGNED = "ASSIGNED"
  IN_PROGRESS = "IN_PROGRESS"
  RESOLVED = "RESOLVED"

class Priority(str, Enum):
  P1 = "P1"
  P2 = "P2"
  P3 = "P3"

class Ticket(Basemodel):
  model_config = ConfigDict(extra="allow")
  id: str = Field(default=None, description="ticket id assigned from upstream source")
  title: str = Field(default="api", description="where the ticket came from: servicenow/jira/api")
  description: str
  priority: Priority = Priority.P3
  department: Optional[str]
  location: Optional[str]
  status: TicketStatus = TicketStatus.NEW
  created_at: datetime = Field(default_factory=lambda: datetime.datetime.now(timezone.ist))

  raw: Optional[Dict[str, Any]] = Field(
      default=None,
      description="Optional raw payload from upstream system"
  )

  @property
  def text(self) -> str:
    """
    Routing-friendly text field: title + description in lowercase.
    """
    return f"{self.title} {self.description}".lower().strip()

class Rule(Basemodel):
  id: str = Field(default_factory=lambda: str(uuid4()))
  name: str

  condtions: Dict[str, Any]
  actions: Dict[str, Any]

class RoutingDescision(Basemodel):
  team: Optional[str] = None
  reason: Dict[str, Any] = Field(default_factory=dict)