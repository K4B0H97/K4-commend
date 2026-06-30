"""Built-in tools for the first K4 scaffold."""


def run_tool(tool_name: str, args: dict) -> dict:
    handler = TOOL_REGISTRY.get(tool_name)
    if handler is not None:
        return handler(args)
    return {
        "tool": tool_name,
        "status": "not_implemented",
        "output": "No tool implementation is registered yet.",
    }


def file_read(args: dict) -> dict:
    return {
        "tool": "file.read",
        "status": "success",
        "path": args.get("path"),
        "output": "mock file content",
    }


def git_diff_read(args: dict) -> dict:
    return {
        "tool": "git.diff.read",
        "status": "success",
        "output": "mock git diff",
    }


def git_status_read(args: dict) -> dict:
    return {
        "tool": "git.status.read",
        "status": "success",
        "output": "mock git status",
    }


def test_result_read(args: dict) -> dict:
    return {
        "tool": "test.result.read",
        "status": "success",
        "output": "mock test result",
    }


def browser_search(args: dict) -> dict:
    return {
        "tool": "browser.search",
        "status": "success",
        "query": args.get("query"),
        "output": "mock search results",
    }


def browser_open(args: dict) -> dict:
    return {
        "tool": "browser.open",
        "status": "success",
        "url": args.get("url"),
        "output": "mock page content",
    }


def note_write(args: dict) -> dict:
    return {
        "tool": "note.write",
        "status": "success",
        "output": "mock note written",
    }


def database_schema_read(args: dict) -> dict:
    return {
        "tool": "database.schema.read",
        "status": "success",
        "database": args.get("database"),
        "output": "mock database schema",
    }


def database_query_read(args: dict) -> dict:
    return {
        "tool": "database.query.read",
        "status": "success",
        "output": "mock read-only query result",
    }


TOOL_REGISTRY = {
    "file.read": file_read,
    "git.diff.read": git_diff_read,
    "git.status.read": git_status_read,
    "test.result.read": test_result_read,
    "browser.search": browser_search,
    "browser.open": browser_open,
    "note.write": note_write,
    "database.schema.read": database_schema_read,
    "database.query.read": database_query_read,
}
