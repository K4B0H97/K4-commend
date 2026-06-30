"""Policy decisions for worker capability and tool requests."""

from k4.types import CapabilityGrant, ToolRequest


READ_ONLY_TOOLS = {
    "file.read",
    "git.diff.read",
    "git.status.read",
    "test.result.read",
}

HIGH_RISK_TOOLS = {
    "file.delete",
    "git.push",
    "network.modify",
    "secret.read",
}


def decide_tool_request(request: ToolRequest, grant: CapabilityGrant) -> str:
    tool_name = request.tool_name

    if tool_name in grant.denied_tools:
        return "deny"
    if tool_name in HIGH_RISK_TOOLS:
        return "ask_user"
    if tool_name in grant.approval_required_tools:
        return "ask_user"
    if tool_name not in grant.allowed_tools:
        return "deny"
    if tool_name in {"file.read", "file.write"}:
        return _decide_file_scope(request)
    if tool_name in READ_ONLY_TOOLS:
        return "allow"
    return "allow"


def _decide_file_scope(request: ToolRequest) -> str:
    path = request.args.get("path", "")
    if not path:
        return "deny"
    if path.startswith("E:\\K4-command"):
        return "allow"
    return "deny"
