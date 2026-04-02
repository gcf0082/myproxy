---
name: myproxy-query
description: Query and filter HTTP traffic captured by myproxy proxy. Use this skill whenever the user wants to query, search, filter, or view recorded HTTP requests and responses from the myproxy tool. This includes showing recent requests, filtering by URL/method/status/headers/time, or customizing output fields.
---

# myproxy Query Skill

This skill helps query and filter HTTP traffic captured by the myproxy proxy tool.

## Command Usage

The query command is invoked via:
```bash
python -m myproxy.cli query [OPTIONS]
```

## Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--db` | TEXT | proxy.db | Database path |
| `--url` | TEXT | - | Filter by URL containing string |
| `--method` | TEXT | - | Filter by HTTP method (GET, POST, etc.) |
| `--status` | INTEGER | - | Filter by status code |
| `--req-header` | TEXT | - | Filter by request header (format: 'HeaderName:value') |
| `--resp-header` | TEXT | - | Filter by response header (format: 'HeaderName:value') |
| `--start-time` | TEXT | - | Filter after this time (ISO format: 2024-01-01T00:00:00) |
| `--end-time` | TEXT | - | Filter before this time (ISO format: 2024-01-01T23:59:59) |
| `--seconds` | INTEGER | - | Filter requests within last N seconds |
| `--limit` | INTEGER | 10 | Maximum number of results |
| `--fields` | TEXT | method,url,req_time,req_size,resp_size,status | Fields to display |

## Available Fields

- `method` - HTTP method (GET, POST, etc.)
- `url` - Full request URL
- `req_time` - Request timestamp (human-readable, millisecond precision)
- `req_headers` - Request headers (JSON format)
- `req_body` - Request body content
- `req_size` - Request body size in bytes
- `resp_headers` - Response headers (JSON format)
- `resp_body` - Response body content
- `resp_size` - Response body size in bytes
- `status` - HTTP status code

## Output Format

Results are output in JSONL format (one JSON object per line):
```json
{"method": "GET", "url": "https://example.com/api", "req_time": "2026-04-02 17:48:37.607", "req_size": 0, "resp_size": 1234, "status": 200}
```

## Examples

### Default query (latest 10 records)
```bash
python -m myproxy.cli query
```

### Query recent 60 seconds
```bash
python -m myproxy.cli query --seconds 60
```

### Filter by status code
```bash
python -m myproxy.cli query --status 200
```

### Filter by HTTP method
```bash
python -m myproxy.cli query --method POST
```

### Filter by URL containing string
```bash
python -m myproxy.cli query --url api
```

### Filter by request header
```bash
python -m myproxy.cli query --req-header "Content-Type:application/json"
```

### Filter by response header
```bash
python -m myproxy.cli query --resp-header "Content-Type:application/json"
```

### Filter by time range
```bash
python -m myproxy.cli query --start-time "2026-04-02T00:00:00" --end-time "2026-04-02T23:59:59"
```

### Custom output fields
```bash
python -m myproxy.cli query --fields method,url,req_headers,resp_headers,status
```

### Show request and response bodies
```bash
python -m myproxy.cli query --fields method,url,req_body,resp_body,status
```

### Combine multiple filters
```bash
python -m myproxy.cli query --method GET --status 200 --seconds 300 --limit 20
```

## Common Use Cases

1. **View recent traffic**: `python -m myproxy.cli query`
2. **Check for errors**: `python -m myproxy.cli query --status 500`
3. **Find specific API call**: `python -m myproxy.cli query --url /api/users`
4. **Debug POST requests**: `python -m myproxy.cli query --method POST --fields method,url,req_body,resp_body,status`
5. **Monitor last minute**: `python -m myproxy.cli query --seconds 60`