"""Query module for filtering and displaying proxy data."""

import json
from datetime import datetime
from typing import Any, Optional

from myproxy.storage import Storage


def query_requests(
    db_path: str = "proxy.db",
    url_contains: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    request_header: Optional[str] = None,
    response_header: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100,
    verbose: bool = False,
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
        limit=limit,
    )

    if not results:
        print("No results found.")
        return

    if verbose:
        _print_verbose(results)
    else:
        _print_summary(results)


def _print_summary(results: list[dict[str, Any]]):
    """Print summary table of results."""
    print(f"{'ID':<6} {'Method':<8} {'Status':<8} {'URL':<60} {'Timestamp':<20}")
    print("-" * 110)

    for row in results:
        url = row["url"]
        if len(url) > 57:
            url = url[:57] + "..."

        status = str(row.get("status_code", "N/A"))

        print(
            f"{row['id']:<6} {row['method']:<8} {status:<8} {url:<60} {row['request_timestamp'][:19]:<20}"
        )


def _print_verbose(results: list[dict[str, Any]]):
    """Print detailed view of results."""
    for i, row in enumerate(results):
        print(f"\n{'=' * 80}")
        print(f"Request #{row['id']}")
        print(f"{'=' * 80}")

        print(f"\n[Request]")
        print(f"  Method:     {row['method']}")
        print(f"  URL:        {row['url']}")
        print(f"  Timestamp:  {row['request_timestamp']}")

        print(f"\n  Headers:")
        for key, value in row.get("request_headers", {}).items():
            print(f"    {key}: {value}")

        if row.get("request_body"):
            print(f"\n  Body: {row['request_body'][:500]}")

        status = row.get("status_code")
        if status:
            print(f"\n[Response]")
            print(f"  Status Code:      {status}")
            print(f"  Timestamp:        {row.get('response_timestamp', 'N/A')}")

            # Display timing information
            request_start = row.get("request_start_time")
            response_time = row.get("response_time")
            if request_start and response_time:
                try:
                    elapsed = float(response_time) - float(request_start)
                    print(f"  Request Start:    {request_start}")
                    print(f"  Response Time:   {response_time}")
                    print(f"  Elapsed:          {elapsed:.3f}s")
                except (ValueError, TypeError):
                    pass

            print(f"\n  Headers:")
            for key, value in row.get("response_headers", {}).items():
                print(f"    {key}: {value}")

            if row.get("response_body"):
                print(f"\n  Body: {row['response_body'][:500]}")

        if i < len(results) - 1:
            print("\n")