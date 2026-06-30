"""Static configuration for K4's first runnable control loop."""

from k4.types import FirewallProfile


FIREWALL_PROFILES = {
    "coding": FirewallProfile(
        name="coding",
        allowed_tools={
            "file.read",
            "git.diff.read",
            "git.status.read",
            "test.result.read",
        },
        approval_required_tools={
            "file.write",
            "shell.run",
            "git.commit",
        },
        denied_tools={
            "file.delete",
            "git.push",
            "network.modify",
            "secret.read",
        },
        network_mode="project_only",
        allowed_models={"deepseek", "local"},
    ),
    "research": FirewallProfile(
        name="research",
        allowed_tools={
            "browser.search",
            "browser.open",
            "note.write",
        },
        approval_required_tools={
            "model.call",
        },
        denied_tools={
            "file.write",
            "file.delete",
            "shell.run",
            "git.push",
            "secret.read",
        },
        network_mode="external_allowed",
        allowed_models={"deepseek", "gateway"},
    ),
    "database": FirewallProfile(
        name="database",
        allowed_tools={
            "database.schema.read",
            "database.query.read",
        },
        approval_required_tools={
            "database.query.write",
        },
        denied_tools={
            "database.drop",
            "database.delete",
            "secret.read",
        },
        network_mode="private_only",
        allowed_models={"deepseek", "local"},
    ),
}


WORKER_DEFINITIONS = {
    "requirement_worker": {
        "skills": ["requirements", "planning"],
    },
    "code_worker": {
        "skills": ["coding", "debugging"],
    },
    "review_worker": {
        "skills": ["code_review", "risk_analysis"],
    },
    "research_worker": {
        "skills": ["research", "source_checking"],
    },
    "database_worker": {
        "skills": ["database", "schema_analysis"],
    },
}


WORKER_REQUESTABLE_TOOLS = {
    "requirement_worker": {"file.read"},
    "code_worker": {"file.read", "file.write"},
    "review_worker": {"git.diff.read", "git.status.read", "test.result.read"},
    "research_worker": {"browser.search", "browser.open", "note.write"},
    "database_worker": {"database.schema.read", "database.query.read"},
}


TASK_WORKER_MAP = {
    "code_review": "review_worker",
    "implementation": "code_worker",
    "web_research": "research_worker",
    "database_read": "database_worker",
}


TASK_TOOL_MAP = {
    "requirement_analysis": "file.read",
    "code_review": "git.diff.read",
    "implementation": "file.write",
    "web_research": "browser.search",
    "database_read": "database.schema.read",
}


SUPPORTED_TASK_KINDS = set(TASK_TOOL_MAP)


TOOL_ARGS_MAP = {
    "file.read": {"path": "E:\\K4-command\\README.md"},
    "file.write": {"path": "E:\\K4-command\\README.md"},
    "browser.search": {"query": "K4 agent firewall"},
    "database.schema.read": {"database": "default"},
}
