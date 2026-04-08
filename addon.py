"""Standalone addon script for mitmproxy."""

import sys
import time
import uuid
from mitmproxy import http, ctx

from myproxy.storage import Storage
from myproxy.config import get_config


class ProxyAddon:
    """mitmproxy addon to capture requests and responses."""

    def __init__(self, storage: Storage, config_path: str = None):
        self.storage = storage
        from myproxy.config import load_config

        self.config = load_config(config_path)

    def request(self, flow: http.HTTPFlow):
        """Handle incoming request."""
        url = str(flow.request.pretty_url)

        # Check if URL should be recorded
        if not self.config.should_record(url):
            print(f"[~] Skipped: {flow.request.method} {url}", file=sys.stderr)
            return

        headers = {k: v for k, v in flow.request.headers.items()}

        # Get request ID from header or generate new one
        request_id = flow.request.headers.get("X-Request-ID")
        if not request_id:
            request_id = uuid.uuid4().hex
            flow.request.headers["X-Request-ID"] = request_id

        # Record start time
        start_time = time.time()

        # Save to storage with modified headers
        self.storage.save_request(
            url=str(flow.request.pretty_url),
            method=flow.request.method,
            headers=dict(flow.request.headers),
            body=flow.request.content,
            request_id=request_id,
        )

        print(
            f"[+] Request: {flow.request.method} {flow.request.pretty_url} [ID: {request_id[:8]}]",
            file=sys.stderr,
        )

    def response(self, flow: http.HTTPFlow):
        """Handle outgoing response."""
        request_id = flow.request.headers.get("X-Request-ID")
        if not request_id:
            return

        start_time_str = flow.request.headers.get("X-Request-Start-Time")
        start_time = float(start_time_str) if start_time_str else time.time()
        response_time = time.time()

        headers = {k: v for k, v in flow.response.headers.items()}

        # Add correlation ID to response
        flow.response.headers["X-Request-ID"] = request_id

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
        print(
            f"[+] Response: {flow.response.status_code} [ID: {request_id[:8]}] (elapsed: {elapsed:.3f}s)",
            file=sys.stderr,
        )


# Global addon instance - will be initialized by load()
storage = None
addon = None


def load(loader):
    """Load addon with options."""
    global storage, addon

    loader.add_option("dbpath", str, "proxy.db", "Path to SQLite database")
    loader.add_option("confpath", str, "config.yaml", "Path to filter config file")


def configure(updated):
    """Configure addon with options."""
    global storage, addon

    if "dbpath" in updated and addon is None:
        db_path = ctx.options.dbpath
        conf_path = ctx.options.confpath
        storage = Storage(db_path)
        addon = ProxyAddon(storage, conf_path)
        print(
            f"[*] Proxy addon loaded, database: {db_path}, config: {conf_path}",
            file=sys.stderr,
        )


def request(flow):
    """Handle request."""
    if addon:
        addon.request(flow)


def response(flow):
    """Handle response."""
    if addon:
        addon.response(flow)
