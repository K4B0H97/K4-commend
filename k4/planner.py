"""Requirement parsing and task planning."""

import json
from dataclasses import dataclass
from typing import Protocol

from k4.config import SUPPORTED_TASK_KINDS
from k4.types import Task


@dataclass(frozen=True)
class PlanTemplate:
    """A deterministic plan template for one business firewall."""

    firewall: str
    task_kinds: tuple[str, ...]


class Planner(Protocol):
    """Planner interface shared by rule-based and future LLM planners."""

    def create_plan(self, requirement: str, firewall_name: str) -> list[Task]:
        ...


DEFAULT_PLAN_TEMPLATES = {
    "coding": PlanTemplate(
        firewall="coding",
        task_kinds=("requirement_analysis", "code_review"),
    ),
    "research": PlanTemplate(
        firewall="research",
        task_kinds=("web_research",),
    ),
    "database": PlanTemplate(
        firewall="database",
        task_kinds=("database_read",),
    ),
}


class RuleBasedPlanner:
    """Creates plans from registered templates instead of branching per feature."""

    def __init__(self, templates: dict[str, PlanTemplate] | None = None) -> None:
        self.templates = templates or DEFAULT_PLAN_TEMPLATES

    def create_plan(self, requirement: str, firewall_name: str = "coding") -> list[Task]:
        template = self.templates.get(firewall_name, self.templates["coding"])
        return [
            Task(
                id=f"task_{index:03d}",
                kind=task_kind,
                requirement=requirement,
            )
            for index, task_kind in enumerate(template.task_kinds, start=1)
        ]


class LLMPlanner:
    """Creates plans from an LLM advisor while keeping K4 validation in code."""

    def __init__(self, provider) -> None:
        self.provider = provider

    def create_plan(self, requirement: str, firewall_name: str = "coding") -> list[Task]:
        response = self.provider.chat_json(
            system_prompt=_planner_system_prompt(firewall_name),
            user_prompt=requirement,
        )
        return _tasks_from_llm_response(response, requirement)


default_planner = RuleBasedPlanner()


def create_plan(requirement: str, firewall_name: str = "coding") -> list[Task]:
    return default_planner.create_plan(requirement, firewall_name)


def _planner_system_prompt(firewall_name: str) -> str:
    allowed_kinds = sorted(SUPPORTED_TASK_KINDS)
    example = {
        "tasks": [
            {"kind": "requirement_analysis"},
            {"kind": "code_review"},
        ]
    }
    return (
        "You are K4's planning advisor. Output strict json only. "
        "You may suggest task kinds, but you cannot create tools, permissions, "
        "workers, models, or firewall rules. "
        f"The active firewall is {firewall_name!r}. "
        f"Allowed task kinds are: {allowed_kinds}. "
        f"Example JSON output: {json.dumps(example)}"
    )


def _tasks_from_llm_response(response: dict, requirement: str) -> list[Task]:
    raw_tasks = response.get("tasks")
    if not isinstance(raw_tasks, list):
        raise ValueError("LLM planner response must contain a tasks list.")

    tasks = []
    for index, raw_task in enumerate(raw_tasks, start=1):
        if not isinstance(raw_task, dict):
            raise ValueError("Each LLM task must be a JSON object.")
        kind = raw_task.get("kind")
        if kind not in SUPPORTED_TASK_KINDS:
            raise ValueError(f"Unsupported LLM task kind: {kind!r}")
        tasks.append(
            Task(
                id=f"task_{index:03d}",
                kind=kind,
                requirement=requirement,
            )
        )

    if not tasks:
        raise ValueError("LLM planner returned no tasks.")
    return tasks
