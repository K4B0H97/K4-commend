"""Policy decisions for worker capability and tool requests."""

import os.path
from typing import Any

from k4.types import CapabilityGrant, ToolRequest


READ_ONLY_TOOLS = {
    "file.read",
    "git.diff.read",
    "git.status.read",
    "test.result.read",
    "database.query.read",
    "database.schema.read",
    "browser.search",
    "browser.open",
}

# 全局高风险工具 - 无论防火墙如何配置，这些工具永远需要用户确认
# 这是安全兜底，防止防火墙配置错误导致权限泄露
GLOBAL_HIGH_RISK_TOOLS = {
    "file.delete",
    "file.overwrite",
    "git.push",
    "git.force_push",
    "network.modify",
    "secret.read",
    "shell.run",
    "shell.exec",
    "command.run",
    "database.drop",
    "database.delete",
    "database.write",
    "system.exec",
}

# 工具参数Schema定义 - 对每个工具的参数做类型、长度、范围校验
TOOL_ARG_SCHEMAS: dict[str, dict[str, Any]] = {
    "file.read": {
        "required": ["path"],
        "string_args": {"path": {"max_length": 4096}},
    },
    "file.write": {
        "required": ["path", "content"],
        "string_args": {
            "path": {"max_length": 4096},
            "content": {"max_length": 10 * 1024 * 1024},  # 10MB
        },
    },
    "file.delete": {
        "required": ["path"],
        "string_args": {"path": {"max_length": 4096}},
    },
    "shell.run": {
        "required": ["command"],
        "string_args": {"command": {"max_length": 8192}},
    },
    "browser.search": {
        "required": ["query"],
        "string_args": {"query": {"max_length": 2048}},
    },
    "browser.open": {
        "required": ["url"],
        "string_args": {"url": {"max_length": 4096}},
    },
    "git.commit": {
        "required": ["message"],
        "string_args": {"message": {"max_length": 1024}},
    },
    "database.query.read": {
        "required": ["query"],
        "string_args": {"query": {"max_length": 65536}},
    },
    "database.query.write": {
        "required": ["query"],
        "string_args": {"query": {"max_length": 65536}},
    },
}

# 参数最大长度全局兜底
MAX_ARG_LENGTH = 10 * 1024 * 1024  # 10MB
MAX_ARGS_COUNT = 32  # 单个工具调用最多32个参数

# 项目根目录，规范化处理
PROJECT_ROOT = os.path.normpath(os.path.abspath("E:\\K4-command")).lower()


def decide_tool_request(request: ToolRequest, grant: CapabilityGrant) -> str:
    tool_name = request.tool_name

    # 1. 全局高风险工具兜底 - 永远需要用户确认，即使防火墙配置错误
    if tool_name in GLOBAL_HIGH_RISK_TOOLS:
        return "ask_user"

    # 2. 防火墙明确拒绝的工具
    if tool_name in grant.denied_tools:
        return "deny"

    # 3. 参数校验 - 参数不合法直接拒绝
    param_check = _validate_tool_args(request)
    if param_check != "allow":
        return param_check

    # 4. 防火墙配置需要审批的工具
    if tool_name in grant.approval_required_tools:
        return "ask_user"

    # 5. 不在允许列表中的工具
    if tool_name not in grant.allowed_tools:
        return "deny"

    # 6. 文件操作额外做路径范围校验
    if tool_name in {"file.read", "file.write"}:
        return _decide_file_scope(request)

    # 7. 只读工具直接允许
    if tool_name in READ_ONLY_TOOLS:
        return "allow"

    # 8. 默认拒绝 - 最小权限原则
    return "deny"


def _validate_tool_args(request: ToolRequest) -> str:
    """校验工具参数是否合法，不合法返回deny"""
    schema = TOOL_ARG_SCHEMAS.get(request.tool_name)
    args = request.args

    # 参数数量检查
    if len(args) > MAX_ARGS_COUNT:
        return "deny"

    # 如果有定义schema，按schema校验
    if schema:
        # 必填参数检查
        required = schema.get("required", [])
        for arg in required:
            if arg not in args or args[arg] is None or args[arg] == "":
                return "deny"

        # 字符串参数长度检查
        string_args = schema.get("string_args", {})
        for arg_name, rules in string_args.items():
            if arg_name in args:
                value = args[arg_name]
                if not isinstance(value, str):
                    return "deny"
                max_len = rules.get("max_length", MAX_ARG_LENGTH)
                if len(value) > max_len:
                    return "deny"

    # 全局兜底：所有字符串参数都检查最大长度
    for key, value in args.items():
        if isinstance(value, str) and len(value) > MAX_ARG_LENGTH:
            return "deny"

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
