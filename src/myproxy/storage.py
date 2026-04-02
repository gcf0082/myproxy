"""SQLite storage layer for proxy requests and responses."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class Storage:
    """SQLite storage for proxy data."""

    def __init__(self, db_path: str = "proxy.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                method TEXT NOT NULL,
                headers TEXT,
                body BLOB,
                timestamp TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                status_code INTEGER,
                headers TEXT,
                body BLOB,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (request_id) REFERENCES requests (id)
            )
        """)

        conn.commit()
        conn.close()

    def save_request(
        self,
        url: str,
        method: str,
        headers: dict[str, str],
        body: Optional[bytes] = None,
    ) -> int:
        """Save a request to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()
        headers_json = json.dumps(dict(headers))

        cursor.execute(
            "INSERT INTO requests (url, method, headers, body, timestamp) VALUES (?, ?, ?, ?, ?)",
            (url, method, headers_json, body, timestamp),
        )

        request_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return request_id

    def save_response(
        self,
        request_id: int,
        status_code: int,
        headers: dict[str, str],
        body: Optional[bytes] = None,
    ) -> int:
        """Save a response to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()
        headers_json = json.dumps(dict(headers))

        cursor.execute(
            "INSERT INTO responses (request_id, status_code, headers, body, timestamp) VALUES (?, ?, ?, ?, ?)",
            (request_id, status_code, headers_json, body, timestamp),
        )

        response_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return response_id

    def query(
        self,
        url_contains: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        request_header: Optional[tuple[str, str]] = None,
        response_header: Optional[tuple[str, str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query requests with filters."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT r.id, r.url, r.method, r.headers as request_headers,
                   r.body as request_body, r.timestamp as request_timestamp,
                   res.status_code, res.headers as response_headers,
                   res.body as response_body, res.timestamp as response_timestamp
            FROM requests r
            LEFT JOIN responses res ON r.id = res.request_id
            WHERE 1=1
        """
        params = []

        if url_contains:
            query += " AND r.url LIKE ?"
            params.append(f"%{url_contains}%")

        if method:
            query += " AND r.method = ?"
            params.append(method.upper())

        if status_code:
            query += " AND res.status_code = ?"
            params.append(status_code)

        if request_header:
            key, value = request_header
            # Match JSON format: "Key": "Value"
            query += " AND r.headers LIKE ?"
            params.append(f'%"{key}": "%{value}"%')

        if response_header:
            key, value = response_header
            query += " AND res.headers LIKE ?"
            params.append(f"%\"{key}\":\"%{value}%\"%")

        if start_time:
            query += " AND r.timestamp >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND r.timestamp <= ?"
            params.append(end_time.isoformat())

        query += " ORDER BY r.timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            result = dict(row)
            if result.get("request_headers"):
                result["request_headers"] = json.loads(result["request_headers"])
            if result.get("response_headers"):
                result["response_headers"] = json.loads(result["response_headers"])
            results.append(result)

        return results