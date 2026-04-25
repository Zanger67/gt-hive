"""Shared constants and utilities for PACE doc processing scripts."""

from __future__ import annotations

import re

NOISE_PATTERNS = (
    "Skip to page content",
    "Skip to chat",
    "Knowledge Article",
    "Was this article helpful?",
    "ASC Most Viewed Articles",
    "ASC Most Useful Articles",
    "Copy Permalink",
    "No content to display",
)

HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+")


def detect_cluster(name: str) -> str:
    lower = name.lower()
    has_phoenix = "phoenix" in lower
    has_ice = "ice" in lower
    if has_phoenix and not has_ice:
        return "phoenix"
    if has_ice and not has_phoenix:
        return "ice"
    return "common"


def is_noise(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped == "---":
        return True
    for pattern in NOISE_PATTERNS:
        if pattern in stripped:
            return True
    return False
