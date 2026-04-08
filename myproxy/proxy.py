"""mitmproxy addon for intercepting and storing HTTP/HTTPS traffic."""

import sys
import time
import uuid
from mitmproxy import http, ctx

from myproxy.storage import Storage


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

        self.storage.save_request(
            url=str(flow.request.pretty_url),
            method=flow.request.method,
            headers=dict(flow.request.headers),
            body=flow.request.content,
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


def run_proxy(
    port: int = 8080, db_path: str = "proxy.db", config_path: str = "config.yaml"
):
    """Run the mitmproxy server."""
    storage = Storage(db_path)
    addon = ProxyAddon(storage, config_path)

    from mitmproxy import options
    from mitmproxy.master import Master
    import asyncio

    opts = options.Options(
        listen_host="0.0.0.0",
        listen_port=port,
        ssl_insecure=True,
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    m = Master(opts, loop)
    m.addons.add(addon)

    print(f"Starting proxy on port {port}")
    print(f"Database: {db_path}")
    print("Press Ctrl+C to stop")

    try:
        loop.run_until_complete(m.run())
    except KeyboardInterrupt:
        print("Shutting down proxy...")
        loop.run_until_complete(m.shutdown())
    finally:
        loop.close()


def main():
    """Entry point when run as script with mitmdump."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--db", default="proxy.db")
    parser.add_argument("--conf", default="config.yaml")
    args = parser.parse_args()

    run_proxy(port=args.port, db_path=args.db, config_path=args.conf)


if __name__ == "__main__":
    main()
