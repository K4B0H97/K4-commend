"""Main controller for task orchestration."""

from k4 import planner as planner_module
from k4.config import TASK_TOOL_MAP, TOOL_ARGS_MAP
from k4.event_log import EventLog
from k4.gateway import ToolGateway
from k4.profiles import select_firewall_profile
from k4.types import CapabilityGrant, Task
from k4.workers import Worker, WorkerRegistry, default_tools_for


class K4Controller:
    """Coordinates planning, worker assignment, tool policy, and delivery."""

    def __init__(self, planner: planner_module.Planner | None = None) -> None:
        self.planner = planner or planner_module.RuleBasedPlanner()
        self.worker_registry = WorkerRegistry()
        self.event_log = EventLog()
        self.tool_gateway = ToolGateway(self.event_log)

    def run(self, requirement: str, firewall_name: str | None = None) -> dict:
        firewall = select_firewall_profile(requirement, firewall_name)
        plan = self.planner.create_plan(requirement, firewall.name)
        results = []

        for task in plan:
            worker = self.worker_registry.pick(task)
            grant = self.create_grant(worker, task, firewall)
            tool_name, tool_args = self.tool_for_task(task)
            result = worker.run(task, grant, self.tool_gateway, tool_name, tool_args)
            self.event_log.record("task_result", result)
            results.append(result)

        return {
            "requirement": requirement,
            "firewall": firewall.name,
            "status": self._status_for(results),
            "plan": [task.__dict__ for task in plan],
            "results": results,
            "events": self.event_log.all(),
        }

    def create_grant(self, worker: Worker, task: Task, firewall) -> CapabilityGrant:
        allowed, approval_required, denied = default_tools_for(worker.name, firewall)
        return CapabilityGrant(
            worker=worker.name,
            task_id=task.id,
            firewall=firewall.name,
            allowed_tools=allowed,
            approval_required_tools=approval_required,
            denied_tools=denied,
            allowed_models=set(firewall.allowed_models),
        )

    def tool_for_task(self, task: Task) -> tuple[str, dict]:
        tool_name = TASK_TOOL_MAP.get(task.kind, "git.status.read")
        return tool_name, dict(TOOL_ARGS_MAP.get(tool_name, {}))

    def _status_for(self, results: list[dict]) -> str:
        decisions = {
            result["tool_result"].get("decision")
            for result in results
        }
        if "ask_user" in decisions:
            return "needs_approval"
        if "deny" in decisions:
            return "blocked"
        return "completed"
