"""Standalone addon script for mitmproxy."""

import sys
from mitmproxy import http, ctx
from mitmproxy.addons import eventstore

# Add src to path
sys.path.insert(0, "/root/projects/myproxy/src")

from myproxy.storage import Storage


class ProxyAddon:
    """mitmproxy addon to capture requests and responses."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self._request_map = {}  # flow_id -> request_id

    def request(self, flow: http.HTTPFlow):
        """Handle incoming request."""
        headers = {k: v for k, v in flow.request.headers.items()}

        request_id = self.storage.save_request(
            url=str(flow.request.pretty_url),
            method=flow.request.method,
            headers=headers,
            body=flow.request.content,
        )

        self._request_map[id(flow)] = request_id
        print(f"[+] Request: {flow.request.method} {flow.request.pretty_url}", file=sys.stderr)

    def response(self, flow: http.HTTPFlow):
        """Handle outgoing response."""
        request_id = self._request_map.get(id(flow))
        if request_id is None:
            return

        headers = {k: v for k, v in flow.response.headers.items()}

        self.storage.save_response(
            request_id=request_id,
            status_code=flow.response.status_code,
            headers=headers,
            body=flow.response.content,
        )
        print(f"[+] Response: {flow.response.status_code}", file=sys.stderr)


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