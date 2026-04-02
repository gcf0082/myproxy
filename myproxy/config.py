"""Configuration loader for myproxy filtering rules."""

import os
from pathlib import Path
from typing import Optional

import yaml


class Config:
    """Filter configuration."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = "config.yaml"

        self.config_path = config_path
        self.exclude_extensions: list[str] = []
        self.exclude_url_patterns: list[str] = []
        self.include_url_patterns: list[str] = []

        self._load()

    def _load(self):
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            print(f"[*] Config file not found: {self.config_path}, using defaults", flush=True)
            self._set_defaults()
            return

        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f) or {}

        # Load exclude rules
        exclude = config.get("exclude", {})
        self.exclude_extensions = exclude.get("extensions", [])
        self.exclude_url_patterns = exclude.get("url_patterns", [])

        # Load include rules
        include = config.get("include", {})
        self.include_url_patterns = include.get("url_patterns", [])

        print(f"[*] Config loaded: {self.config_path}", flush=True)
        print(f"    Exclude extensions: {self.exclude_extensions}", flush=True)

    def _set_defaults(self):
        """Set default filter rules."""
        self.exclude_extensions = [
            ".js", ".css", ".png", ".jpg", ".jpeg", ".gif",
            ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".map"
        ]
        self.exclude_url_patterns = ["/static/", "/assets/", "/fonts/", "/images/"]
        self.include_url_patterns = []

    def should_record(self, url: str) -> bool:
        """
        Determine if a URL should be recorded.

        Returns:
            True if the URL should be recorded, False if it should be filtered out.
        """
        # Check exclude rules first
        for ext in self.exclude_extensions:
            if url.endswith(ext):
                return False

        for pattern in self.exclude_url_patterns:
            if pattern in url:
                return False

        # Check include rules (if any)
        if self.include_url_patterns:
            for pattern in self.include_url_patterns:
                if pattern in url:
                    return True
            return False

        return True


# Global config instance
_config: Optional[Config] = None


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file."""
    global _config
    _config = Config(config_path)
    return _config


def get_config() -> Config:
    """Get the current config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config