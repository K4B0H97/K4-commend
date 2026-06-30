"""Shared K4 data shapes."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Task:
    id: str
    kind: str
    requirement: str


@dataclass(frozen=True)
class FirewallProfile:
    name: str
    allowed_tools: set[str] = field(default_factory=set)
    approval_required_tools: set[str] = field(default_factory=set)
    denied_tools: set[str] = field(default_factory=set)
    network_mode: str = "local_only"
    allowed_models: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class CapabilityGrant:
    worker: str
    task_id: str
    firewall: str
    allowed_tools: set[str] = field(default_factory=set)
    approval_required_tools: set[str] = field(default_factory=set)
    denied_tools: set[str] = field(default_factory=set)
    allowed_models: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class ToolRequest:
    worker: str
    task_id: str
    tool_name: str
    args: dict = field(default_factory=dict)
    reason: str = ""
