#!/usr/bin/env python3
"""
Clean and index local PACE documentation exports.

Examples:
  uv run python scripts/pace_doc_pipeline.py rebuild --profile internal
  uv run python scripts/pace_doc_pipeline.py rebuild --profile public
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from pace_doc_common import HEADING_RE, detect_cluster, is_noise

PERMALINK_RE = re.compile(r"\[\u00b6\]\([^)]+\)")
MOZ_LINK_RE = re.compile(r"\[([^\]]+)\]\(moz-extension://[^)]+\)")
MOZ_IMAGE_RE = re.compile(r"!\[[^\]]*]\(moz-extension://[^)]+\)")
MOZ_URL_RE = re.compile(r"moz-extension://[^\s)>\"]+")
HTML_IMAGE_RE = re.compile(r"<img\b[^>]*>", flags=re.IGNORECASE)
MULTISPACE_RE = re.compile(r"\s+")

TOPIC_KEYWORDS = {
    "slurm": ("slurm", "sbatch", "salloc", "srun", "qos", "partition"),
    "storage": ("storage", "scratch", "quota", "tmpdir", "local disk"),
    "transfer": ("globus", "scp", "sftp", "transfer"),
    "ondemand": ("ondemand", "jupyter", "interactive apps"),
    "resources": ("node", "gpu", "cpu", "resources", "constraint"),
    "migration": ("migration", "rhel9", "rhel7"),
    "training": ("workshop", "training calendar", "orientation"),
}


@dataclass
class DocMeta:
    filename: str
    title: str
    cluster: str
    topics: list[str]
    word_count: int
    quality_score: int
    fingerprint: str
    canonical: bool
    duplicate_of: str | None


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def profile_docs_root(profile: str, explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve(strict=False)
        return path

    if profile == "internal":
        return repo_root() / "docs" / "PACE Documentation"
    return repo_root() / "docs" / "derived" / profile / "PACE Documentation"


def missing_docs_message(profile: str, docs_dir: Path) -> str:
    if profile == "public":
        return (
            f"Public docs directory not found for profile `{profile}`: {docs_dir}. "
            "Run `python3 scripts/build_doc_views.py --profile public --delete` first."
        )
    return f"Docs directory not found for profile `{profile}`: {docs_dir}"


def references_root(profile: str) -> Path:
    if profile == "internal":
        return skill_root() / "references"
    return skill_root() / "references" / profile


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        parts = text.split("\n---\n", 1)
        if len(parts) == 2:
            return parts[1]
    return text


def infer_topics(text: str) -> list[str]:
    lower = text.lower()
    topics: list[str] = []
    for topic, words in TOPIC_KEYWORDS.items():
        if any(word in lower for word in words):
            topics.append(topic)
    return sorted(topics)


def quality_score(filename: str, title: str, topics: Iterable[str], word_count: int) -> int:
    lower_name = filename.lower()
    lower_title = title.lower()

    score = 0
    if "using slurm on phoenix" in lower_name:
        score += 8
    if "phoenix cluster resources" in lower_name:
        score += 6
    if "storage guide" in lower_name:
        score += 6
    if "using globus" in lower_name:
        score += 5
    if "workshop" in lower_name or "training calendar" in lower_name:
        score -= 6
    if "getting started with phoenix cluster" in lower_name:
        score -= 3

    for topic in topics:
        if topic in {"slurm", "resources", "storage", "transfer"}:
            score += 2
        if topic == "training":
            score -= 2

    if word_count < 120:
        score -= 2
    if word_count > 350:
        score += 1
    if "knowledge article" in lower_title:
        score -= 1
    return score


def normalize_for_hash(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    lowered = MULTISPACE_RE.sub(" ", lowered).strip()
    return lowered


def clean_line(raw: str) -> str:
    line = raw.replace("\u00a0", " ")
    line = PERMALINK_RE.sub("", line)
    line = MOZ_IMAGE_RE.sub("", line)
    line = MOZ_LINK_RE.sub(r"\1", line)
    line = HTML_IMAGE_RE.sub("", line)
    line = MOZ_URL_RE.sub("", line)
    line = re.sub(r"\(\s*\)", "", line)
    return line.rstrip()


def clean_text(raw_text: str) -> str:
    text = strip_frontmatter(raw_text)
    out_lines: list[str] = []
    prev_blank = False
    for raw in text.splitlines():
        line = clean_line(raw)
        if is_noise(line):
            if not prev_blank:
                out_lines.append("")
                prev_blank = True
            continue
        if line.strip():
            out_lines.append(line)
            prev_blank = False
        elif not prev_blank:
            out_lines.append("")
            prev_blank = True
    return "\n".join(out_lines).strip() + "\n"


def title_from_cleaned(filename: str, cleaned: str) -> str:
    for line in cleaned.splitlines():
        if HEADING_RE.match(line):
            return re.sub(r"^\s*#+\s*", "", line).strip()
    return Path(filename).stem


def build_metadata(docs_dir: Path) -> tuple[list[DocMeta], dict[str, str]]:
    docs = sorted(docs_dir.glob("*.md"), key=lambda p: p.name.lower())
    metas: list[DocMeta] = []
    cleaned_map: dict[str, str] = {}
    groups: dict[str, list[DocMeta]] = defaultdict(list)

    for path in docs:
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw = path.read_text(encoding="latin-1")
        cleaned = clean_text(raw)
        cleaned_map[path.name] = cleaned
        title = title_from_cleaned(path.name, cleaned)
        words = re.findall(r"\b[\w/-]+\b", cleaned)
        topics = infer_topics(cleaned)
        fingerprint = hashlib.sha256(
            normalize_for_hash(cleaned).encode("utf-8")
        ).hexdigest()[:16]

        meta = DocMeta(
            filename=path.name,
            title=title,
            cluster=detect_cluster(path.name),
            topics=topics,
            word_count=len(words),
            quality_score=quality_score(path.name, title, topics, len(words)),
            fingerprint=fingerprint,
            canonical=False,
            duplicate_of=None,
        )
        metas.append(meta)
        groups[fingerprint].append(meta)

    for _, group in groups.items():
        group.sort(
            key=lambda m: (
                -m.quality_score,
                "(1)" in m.filename,
                len(m.filename),
                m.filename.lower(),
            )
        )
        canonical = group[0]
        canonical.canonical = True
        for duplicate in group[1:]:
            duplicate.canonical = False
            duplicate.duplicate_of = canonical.filename

    metas.sort(key=lambda m: (m.cluster, -m.quality_score, m.filename.lower()))
    return metas, cleaned_map


def write_cleaned_docs(cleaned_map: dict[str, str], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, cleaned in cleaned_map.items():
        (out_dir / name).write_text(cleaned, encoding="utf-8")


def write_index_json(metas: list[DocMeta], out_file: Path, profile: str) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "profile": profile,
        "default_cluster": "phoenix",
        "items": [asdict(meta) for meta in metas],
    }
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_index_md(metas: list[DocMeta], out_file: Path, profile: str) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# PACE Doc Index")
    lines.append("")
    lines.append("- Generated automatically by `scripts/pace_doc_pipeline.py`.")
    lines.append(f"- Profile: `{profile}`.")
    lines.append("- Default cluster: `phoenix`.")
    lines.append("- ICE usage: backup/fallback only.")
    lines.append("")

    def emit_section(title: str, cluster: str) -> None:
        lines.append(f"## {title}")
        lines.append("")
        section = [meta for meta in metas if meta.cluster == cluster and meta.canonical]
        section.sort(key=lambda meta: (-meta.quality_score, meta.filename.lower()))
        if not section:
            lines.append("- None")
            lines.append("")
            return
        for meta in section:
            topics = ", ".join(meta.topics) if meta.topics else "general"
            lines.append(
                f"- `{meta.filename}` | score `{meta.quality_score}` | "
                f"topics: {topics} | words: {meta.word_count}"
            )
        lines.append("")

    emit_section("Phoenix Canonical Docs (Research-First)", "phoenix")
    emit_section("ICE Backup Docs", "ice")

    lines.append("## Duplicates Suppressed")
    lines.append("")
    duplicates = [meta for meta in metas if meta.duplicate_of]
    if not duplicates:
        lines.append("- None")
    else:
        duplicates.sort(key=lambda meta: meta.filename.lower())
        for meta in duplicates:
            lines.append(f"- `{meta.filename}` -> `{meta.duplicate_of}`")
    lines.append("")

    out_file.write_text("\n".join(lines), encoding="utf-8")


def resolve_default_outputs(profile: str) -> tuple[Path, Path, Path]:
    root = references_root(profile)
    return root / "cleaned_docs", root / "doc-index.json", root / "doc-index.md"


def rebuild(args: argparse.Namespace) -> int:
    docs_dir = profile_docs_root(profile=args.profile, explicit=args.docs_root)
    if not docs_dir.exists() or not docs_dir.is_dir():
        print(missing_docs_message(args.profile, docs_dir))
        return 1

    metas, cleaned_map = build_metadata(docs_dir)

    default_clean_dir, default_index_json, default_index_md = resolve_default_outputs(args.profile)
    clean_dir = Path(args.clean_dir).expanduser() if args.clean_dir else default_clean_dir
    index_json = Path(args.index_json).expanduser() if args.index_json else default_index_json
    index_md = Path(args.index_md).expanduser() if args.index_md else default_index_md

    write_cleaned_docs(cleaned_map, clean_dir)
    write_index_json(metas, index_json, profile=args.profile)
    write_index_md(metas, index_md, profile=args.profile)

    canonical = sum(1 for meta in metas if meta.canonical)
    duplicates = sum(1 for meta in metas if meta.duplicate_of)
    print(f"Profile: {args.profile}")
    print(f"Processed {len(metas)} docs.")
    print(f"Canonical docs: {canonical}")
    print(f"Duplicates suppressed: {duplicates}")
    print(f"Wrote cleaned docs: {clean_dir}")
    print(f"Wrote index JSON: {index_json}")
    print(f"Wrote index Markdown: {index_md}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean and index PACE markdown docs")
    sub = parser.add_subparsers(dest="command", required=True)

    rebuild_parser = sub.add_parser("rebuild", help="Rebuild cleaned docs and index files")
    rebuild_parser.add_argument(
        "--profile",
        choices=("internal", "public"),
        default="internal",
        help="Profile used for docs source and output destination",
    )
    rebuild_parser.add_argument(
        "--docs-root",
        help="Docs source directory (defaults to canonical docs for internal and derived docs for public)",
    )
    rebuild_parser.add_argument(
        "--clean-dir",
        help="Output folder for cleaned markdown docs",
    )
    rebuild_parser.add_argument(
        "--index-json",
        help="Output path for JSON index",
    )
    rebuild_parser.add_argument(
        "--index-md",
        help="Output path for markdown index",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "rebuild":
        return rebuild(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
