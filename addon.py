"""Standalone addon script for mitmproxy."""

import sys
import time
from mitmproxy import http, ctx
from mitmproxy.addons import eventstore

# Add src to path
sys.path.insert(0, "/root/projects/myproxy/src")

from myproxy.storage import Storage


class ProxyAddon:
    """mitmproxy addon to capture requests and responses."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self._request_map = {}  # flow_id -> (request_id, start_time)

    def request(self, flow: http.HTTPFlow):
        """Handle incoming request."""
        headers = {k: v for k, v in flow.request.headers.items()}

        # Record start time
        start_time = time.time()

        request_id = self.storage.save_request(
            url=str(flow.request.pretty_url),
            method=flow.request.method,
            headers=headers,
            body=flow.request.content,
        )

        # Store request_id and start time
        self._request_map[id(flow)] = (request_id, start_time)

        print(f"[+] Request: {flow.request.method} {flow.request.pretty_url}", file=sys.stderr)

    def response(self, flow: http.HTTPFlow):
        """Handle outgoing response."""
        data = self._request_map.get(id(flow))
        if data is None:
            return

        request_id, start_time = data
        response_time = time.time()

        headers = {k: v for k, v in flow.response.headers.items()}

        # Add timing headers to response
        flow.response.headers["X-Request-Start-Time"] = str(start_time)
        flow.response.headers["X-Response-Time"] = str(response_time)

        # Calculate elapsed time
        elapsed = response_time - start_time
        flow.response.headers["X-Elapsed-Time"] = f"{elapsed:.3f}s"

        self.storage.save_response(
            request_id=request_id,
            status_code=flow.response.status_code,
            headers=headers,
            body=flow.response.content,
            request_start_time=str(start_time),
            response_time=str(response_time),
        )
        print(f"[+] Response: {flow.response.status_code} (elapsed: {elapsed:.3f}s)", file=sys.stderr)


# Global addon instance - will be initialized by load()
storage = None
addon = None


def load(loader):
    """Load addon with options."""
    global storage, addon

    loader.add_option(
        "dbpath", str, "proxy.db",
        "Path to SQLite database"
    )


def configure(updated):
    """Configure addon with options."""
    global storage, addon

    if "dbpath" in updated and addon is None:
        db_path = ctx.options.dbpath
        storage = Storage(db_path)
        addon = ProxyAddon(storage)
        print(f"[*] Proxy addon loaded, database: {db_path}", file=sys.stderr)


def request(flow):
    """Handle request."""
    if addon:
        addon.request(flow)


def response(flow):
    """Handle response."""
    if addon:
        addon.response(flow)