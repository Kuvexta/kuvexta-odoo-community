#!/usr/bin/env python3
"""Validate Kuvexta Community repository boundaries."""

from __future__ import annotations

import ast
import json
import logging
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "MIGRATION_MANIFEST.json"
LOGGER = logging.getLogger(__name__)
IGNORED_DIRS = {".git", ".github", "scripts"}


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
    planned = set(policy.get("planned_modules", {}))
    addons = discover_addons()
    errors: list[str] = []

    unexpected = sorted(set(addons) - planned)
    if unexpected:
        errors.append("Unexpected addons in Community: " + ", ".join(unexpected))

    for module, manifest in sorted(addons.items()):
        if manifest.get("license") != "AGPL-3":
            errors.append(f"{module}: Community migration requires AGPL-3")
        for dependency in manifest.get("depends", []):
            if dependency.startswith("kt_") and dependency not in planned:
                errors.append(
                    f"{module}: dependency {dependency!r} crosses out of Community"
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
        "Community boundary valid: %d addon(s) present, %d planned.",
        len(addons),
        len(planned),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
