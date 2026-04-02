"""CLI interface for myproxy."""

import click

from myproxy.proxy import run_proxy
from myproxy.query import query_requests


@click.group()
def cli():
    """MyProxy - HTTPS proxy tool with mitmproxy."""
    pass


@cli.command()
@click.option(
    "--port",
    default=8080,
    type=int,
    help="Proxy port (default: 8080)",
)
@click.option(
    "--db",
    default="proxy.db",
    help="Database path (default: proxy.db)",
)
def start(port: int, db: str):
    """Start the proxy server."""
    click.echo(f"Starting proxy on port {port}...")
    click.echo(f"Database: {db}")
    click.echo("Make sure to install the mitmproxy CA certificate.")
    click.echo("Visit http://mitm.it to download certificates.")

    run_proxy(port=port, db_path=db)


@cli.command()
@click.option(
    "--db",
    default="proxy.db",
    help="Database path (default: proxy.db)",
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
    "--limit",
    default=100,
    type=int,
    help="Maximum number of results (default: 100)",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show full details for each request/response",
)
def query(
    db: str,
    url_contains: str | None,
    method: str | None,
    status_code: int | None,
    request_header: str | None,
    response_header: str | None,
    start_time: str | None,
    end_time: str | None,
    limit: int,
    verbose: bool,
):
    """Query captured requests and responses."""
    query_requests(
        db_path=db,
        url_contains=url_contains,
        method=method,
        status_code=status_code,
        request_header=request_header,
        response_header=response_header,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        verbose=verbose,
    )


def main():
    """Entry point for the CLI."""
    cli()