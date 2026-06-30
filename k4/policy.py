"""Policy decisions for worker capability and tool requests."""

import os.path

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

# 项目根目录，规范化处理
PROJECT_ROOT = os.path.normpath(os.path.abspath("E:\\K4-command")).lower()


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
    
    try:
        # 规范化绝对路径，处理..、./、相对路径等
        norm_path = os.path.normpath(os.path.abspath(path)).lower()
    except (OSError, ValueError):
        # 非法路径直接拒绝
        return "deny"
    
    # 必须是项目根目录本身，或者项目根目录下的子路径（加os.sep防止前缀绕过）
    # 例如 E:\K4-command-evil 不会匹配 E:\K4-command\
    if norm_path == PROJECT_ROOT or norm_path.startswith(PROJECT_ROOT + os.sep):
        return "allow"
    return "deny"
