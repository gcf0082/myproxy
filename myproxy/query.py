"""Query module for filtering and displaying proxy data."""

import json
from datetime import datetime, timedelta
from typing import Any, Optional

from myproxy.storage import Storage


# Default fields to display
DEFAULT_FIELDS = ["method", "url", "req_size", "resp_size", "status"]

# All available fields
ALL_FIELDS = ["method", "url", "req_headers", "req_body", "req_size", "resp_headers", "resp_body", "resp_size", "status"]

# Body truncation threshold
BODY_TRUNCATE_SIZE = 1024


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


def _print_custom(results: list[dict[str, Any]], fields: list[str]):
    """Print results with custom fields."""
    for row in results:
        # Calculate body sizes
        req_size = len(row.get("request_body") or b"")
        resp_size = len(row.get("response_body") or b"")

        line_parts = []
        for f in fields:
            if f == "method":
                line_parts.append(row.get("method", ""))
            elif f == "url":
                line_parts.append(row.get("url", ""))
            elif f == "req_headers":
                headers = row.get("request_headers", {})
                line_parts.append(json.dumps(headers, indent=2))
            elif f == "req_body":
                body = row.get("request_body", b"")
                line_parts.append(_truncate_body(body))
            elif f == "req_size":
                line_parts.append(str(req_size))
            elif f == "resp_headers":
                headers = row.get("response_headers", {})
                line_parts.append(json.dumps(headers, indent=2))
            elif f == "resp_body":
                body = row.get("response_body", b"")
                line_parts.append(_truncate_body(body))
            elif f == "resp_size":
                line_parts.append(str(resp_size))
            elif f == "status":
                line_parts.append(str(row.get("status_code", "N/A")))

        print(" | ".join(line_parts))