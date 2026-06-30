"""Tool gateway that enforces policy before tool execution."""

from k4.policy import decide_tool_request
from k4.tools import run_tool
from k4.types import CapabilityGrant, ToolRequest


class ToolGateway:
    """Single entry point for worker tool calls."""

    def __init__(self, event_log=None) -> None:
        self.event_log = event_log

    def request(self, request: ToolRequest, grant: CapabilityGrant) -> dict:
        decision = decide_tool_request(request, grant)
        event = {
            "worker": request.worker,
            "task_id": request.task_id,
            "tool": request.tool_name,
            "reason": request.reason,
            "decision": decision,
        }
        self._record("tool_request", event)

        if decision != "allow":
            result = {
                "tool": request.tool_name,
                "status": "blocked",
                "decision": decision,
            }
            self._record("tool_result", result)
            return result

        result = run_tool(request.tool_name, request.args)
        result["decision"] = decision
        self._record("tool_result", result)
        return result

    def _record(self, event_type: str, payload: dict) -> None:
        if self.event_log is not None:
            self.event_log.record(event_type, payload)
