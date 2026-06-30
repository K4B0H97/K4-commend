"""Worker registry and worker definitions."""

from k4.config import TASK_WORKER_MAP, WORKER_DEFINITIONS, WORKER_REQUESTABLE_TOOLS
from k4.types import CapabilityGrant, FirewallProfile, Task, ToolRequest


class Worker:
    """A role-based executor controlled by K4."""

    def __init__(self, name: str, skills: list[str]) -> None:
        self.name = name
        self.skills = skills

    def run(
        self,
        task: Task,
        grant: CapabilityGrant,
        tool_gateway,
        tool_name: str,
        tool_args: dict,
    ) -> dict:
        request = ToolRequest(
            worker=self.name,
            task_id=task.id,
            tool_name=tool_name,
            args=tool_args,
            reason=f"{self.name} needs {tool_name} for {task.kind}.",
        )
        tool_result = tool_gateway.request(request, grant)
        return {
            "worker": self.name,
            "task_id": task.id,
            "task_kind": task.kind,
            "firewall": grant.firewall,
            "tool_result": tool_result,
        }


class WorkerRegistry:
    """Picks a worker for each task."""

    def __init__(self) -> None:
        self.workers = {
            name: Worker(name, config["skills"])
            for name, config in WORKER_DEFINITIONS.items()
        }

    def pick(self, task: Task) -> Worker:
        worker_name = TASK_WORKER_MAP.get(task.kind, "requirement_worker")
        return self.workers[worker_name]


def default_tools_for(worker_name: str, profile: FirewallProfile) -> tuple[set[str], set[str], set[str]]:
    requested_tools = WORKER_REQUESTABLE_TOOLS.get(worker_name, set())
    allowed = requested_tools & profile.allowed_tools
    approval_required = requested_tools & profile.approval_required_tools
    denied = requested_tools & profile.denied_tools
    return allowed, approval_required, denied
