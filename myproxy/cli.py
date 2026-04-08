"""CLI interface for myproxy."""

import click

from myproxy.proxy import run_proxy
from myproxy.query import query_requests


@click.group()
def cli():
    """MyProxy - HTTPS proxy tool with mitmproxy."""
    pass


@click.command()
@click.option(
    "--port",
    default=8080,
    type=int,
    help="Proxy port (default: 8080)",
)
@click.option(
    "--db",
    default=None,
    help="Database path (default: proxy.db in current directory)",
)
@click.option(
    "--config",
    default="config.yaml",
    help="Config file path (default: config.yaml)",
)
def start(port: int, db: str | None, config: str):
    """Start the proxy server."""
    if db is None:
        db = "proxy.db"
    click.echo(f"Starting proxy on port {port}...")
    click.echo(f"Database: {db}")
    click.echo(f"Config: {config}")
    click.echo("Make sure to install the mitmproxy CA certificate.")
    click.echo("Visit http://mitm.it to download certificates.")

    run_proxy(port=port, db_path=db, config_path=config)


@cli.command()
@click.option(
    "--db",
    default=None,
    help="Database path (default: proxy.db in current directory)",
)
@click.option(
    "--request_id",
    "request_id",
    help="Query by request ID",
)
@click.option(
    "--url",
    "url_contains",
    help="Filter by URL containing this string",
)
@click.option(
    "--method",
    help="Filter by HTTP method (GET, POST, etc.)",
)
@click.option(
    "--status",
    "status_code",
    type=int,
    help="Filter by status code",
)
@click.option(
    "--req-header",
    "request_header",
    help="Filter by request header (format: 'HeaderName:value')",
)
@click.option(
    "--resp-header",
    "response_header",
    help="Filter by response header (format: 'HeaderName:value')",
)
@click.option(
    "--start-time",
    help="Filter requests after this time (ISO format: 2024-01-01T00:00:00)",
)
@click.option(
    "--end-time",
    help="Filter requests before this time (ISO format: 2024-01-01T23:59:59)",
)
@click.option(
    "--seconds",
    type=int,
    help="Filter requests within last N seconds",
)
@click.option(
    "--limit",
    default=10,
    type=int,
    help="Maximum number of results (default: 10)",
)
@click.option(
    "--fields",
    help="Fields to display (comma-separated: request_id,method,url,req_headers,req_body,req_size,resp_headers,resp_body,resp_size,status)",
)
def query(
    db: str | None,
    request_id: str | None,
    url_contains: str | None,
    method: str | None,
    status_code: int | None,
    request_header: str | None,
    response_header: str | None,
    start_time: str | None,
    end_time: str | None,
    seconds: int | None,
    limit: int,
    fields: str | None,
):
    """Query captured requests and responses."""
    if db is None:
        db = "proxy.db"
    query_requests(
        db_path=db,
        request_id=request_id,
        url_contains=url_contains,
        method=method,
        status_code=status_code,
        request_header=request_header,
        response_header=response_header,
        start_time=start_time,
        end_time=end_time,
        seconds=seconds,
        limit=limit,
        fields=fields,
    )


def main():
    """Entry point for the CLI."""
    cli()
