"""Query module for filtering and displaying proxy data."""

import json
from datetime import datetime, timedelta
from typing import Any, Optional

from myproxy.storage import Storage


# Default fields to display
DEFAULT_FIELDS = ["method", "url", "req_time", "req_size", "resp_size", "status"]

# All available fields
ALL_FIELDS = ["method", "url", "req_time", "req_headers", "req_body", "req_size", "resp_headers", "resp_body", "resp_size", "status"]

# Body truncation threshold
BODY_TRUNCATE_SIZE = 1024


def _format_time(timestamp: str) -> str:
    """Format timestamp to human-readable format with millisecond precision."""
    if not timestamp:
        return ""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S") + f".{dt.microsecond // 1000:03d}"
    except (ValueError, TypeError):
        return timestamp


def query_requests(
    db_path: str = "proxy.db",
    url_contains: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    request_header: Optional[str] = None,
    response_header: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    seconds: Optional[int] = None,
    limit: int = 10,
    fields: Optional[str] = None,
):
    """Query requests with filters and display results."""
    storage = Storage(db_path)

    # Parse header filters
    req_header = None
    if request_header:
        parts = request_header.split(":", 1)
        if len(parts) == 2:
            req_header = (parts[0].strip(), parts[1].strip())

    resp_header = None
    if response_header:
        parts = response_header.split(":", 1)
        if len(parts) == 2:
            resp_header = (parts[0].strip(), parts[1].strip())

    # Parse time filters
    start_dt = None
    if start_time:
        start_dt = datetime.fromisoformat(start_time)

    end_dt = None
    if end_time:
        end_dt = datetime.fromisoformat(end_time)

    results = storage.query(
        url_contains=url_contains,
        method=method,
        status_code=status_code,
        request_header=req_header,
        response_header=resp_header,
        start_time=start_dt,
        end_time=end_dt,
        seconds=seconds,
        limit=limit,
    )

    if not results:
        print("No results found.")
        return

    # Parse fields
    display_fields = DEFAULT_FIELDS
    if fields:
        display_fields = [f.strip() for f in fields.split(",")]

    _print_custom(results, display_fields)


def _truncate_body(body: bytes | str) -> str:
    """Truncate body if larger than threshold, append '...' if truncated."""
    if not body:
        return ""

    body_str = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else str(body)
    if len(body_str) > BODY_TRUNCATE_SIZE:
        return body_str[:BODY_TRUNCATE_SIZE] + "... (truncated)"
    return body_str


def _format_value(value: Any, field: str) -> Any:
    """Format value based on field type."""
    if field in ("req_headers", "resp_headers"):
        return value or {}
    if field in ("req_body", "resp_body"):
        body = value or b""
        return _truncate_body(body)
    return value


def _print_custom(results: list[dict[str, Any]], fields: list[str]):
    """Print results in JSONL format (one JSON object per line)."""
    for row in results:
        # Calculate body sizes
        req_size = len(row.get("request_body") or b"")
        resp_size = len(row.get("response_body") or b"")

        output = {}
        for f in fields:
            if f == "method":
                output["method"] = row.get("method", "")
            elif f == "url":
                output["url"] = row.get("url", "")
            elif f == "req_time":
                output["req_time"] = _format_time(row.get("request_timestamp", ""))
            elif f == "req_headers":
                output["req_headers"] = row.get("request_headers", {})
            elif f == "req_body":
                output["req_body"] = _truncate_body(row.get("request_body", b""))
            elif f == "req_size":
                output["req_size"] = req_size
            elif f == "resp_headers":
                output["resp_headers"] = row.get("response_headers", {})
            elif f == "resp_body":
                output["resp_body"] = _truncate_body(row.get("response_body", b""))
            elif f == "resp_size":
                output["resp_size"] = resp_size
            elif f == "status":
                output["status"] = row.get("status_code", "")

        print(json.dumps(output, ensure_ascii=False))