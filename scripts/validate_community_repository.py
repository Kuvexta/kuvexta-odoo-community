#!/usr/bin/env python3
"""Validate Kuvexta Community repository boundaries."""

from __future__ import annotations

import ast
import json
import logging
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "MIGRATION_MANIFEST.json"
UPSTREAM_POLICY = ROOT / "UPSTREAM_SOURCES.json"
LOGGER = logging.getLogger(__name__)
IGNORED_DIRS = {".git", ".github", "scripts"}
LOCAL_STATUSES = {"migrated_agpl"}
EXTERNAL_STATUSES = {"external_pinned_upstream_agpl"}
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")


def discover_addons() -> dict[str, dict]:
    addons: dict[str, dict] = {}
    for path in ROOT.iterdir():
        if not path.is_dir() or path.name in IGNORED_DIRS:
            continue
        manifest = path / "__manifest__.py"
        if not manifest.exists():
            continue
        value = ast.literal_eval(manifest.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"Odoo manifest must be a dict: {manifest}")
        addons[path.name] = value
    return addons


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    upstream_policy = json.loads(UPSTREAM_POLICY.read_text(encoding="utf-8"))
    planned_map = policy.get("planned_modules", {})
    planned = set(planned_map)
    upstream_sources = upstream_policy.get("sources", {})
    external = set(upstream_sources)
    addons = discover_addons()
    errors: list[str] = []

    unexpected = sorted(set(addons) - planned)
    if unexpected:
        errors.append("Unexpected addons in Community: " + ", ".join(unexpected))

    for module, status in sorted(planned_map.items()):
        if status in LOCAL_STATUSES and module not in addons:
            errors.append(f"{module}: status {status!r} requires a local addon")
        elif status in EXTERNAL_STATUSES:
            if module in addons:
                errors.append(
                    f"{module}: external pinned upstream must not be vendored locally"
                )
            if module not in external:
                errors.append(
                    f"{module}: external pinned upstream missing from UPSTREAM_SOURCES.json"
                )
        elif status not in LOCAL_STATUSES | EXTERNAL_STATUSES:
            errors.append(f"{module}: unsupported migration status {status!r}")

    for module, source in sorted(upstream_sources.items()):
        if module not in planned:
            errors.append(f"{module}: upstream source is not declared in planned_modules")
        if source.get("distribution_mode") != "external_pinned_dependency":
            errors.append(
                f"{module}: upstream distribution_mode must be external_pinned_dependency"
            )
        if source.get("license") != "AGPL-3":
            errors.append(f"{module}: Community upstream dependency must be AGPL-3")
        commit = source.get("commit", "")
        if not SHA1_RE.fullmatch(commit):
            errors.append(f"{module}: upstream commit must be a full 40-character SHA-1")
        if not source.get("repository") or "/" not in source.get("repository", ""):
            errors.append(f"{module}: upstream repository must use owner/name form")
        if source.get("module_path") != module:
            errors.append(
                f"{module}: module_path must equal addon technical name for this repository"
            )
        for required_by in source.get("required_by", []):
            if required_by not in planned:
                errors.append(
                    f"{module}: required_by {required_by!r} is not a planned Community addon"
                )

    for module, manifest in sorted(addons.items()):
        if manifest.get("license") != "AGPL-3":
            errors.append(f"{module}: Community migration requires AGPL-3")
        for dependency in manifest.get("depends", []):
            if dependency.startswith("kt_") and dependency not in planned:
                errors.append(
                    f"{module}: dependency {dependency!r} crosses out of Community"
                )
            if dependency in planned and dependency not in addons and dependency not in external:
                errors.append(
                    f"{module}: planned dependency {dependency!r} is neither local nor pinned upstream"
                )

    patch = addons.get("kt_ecommerce_barcode_search_patch")
    if patch and "ecommerce_barcode_search" not in patch.get("depends", []):
        errors.append(
            "kt_ecommerce_barcode_search_patch must retain explicit dependency "
            "on ecommerce_barcode_search"
        )

    if errors:
        for error in errors:
            LOGGER.error(error)
        return 1

    LOGGER.info(
        "Community boundary valid: %d local addon(s), %d pinned upstream source(s).",
        len(addons),
        len(external),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
