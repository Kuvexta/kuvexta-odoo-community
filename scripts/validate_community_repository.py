#!/usr/bin/env python3
"""Validate Kuvexta Community physical, upstream and license boundaries."""

from __future__ import annotations

import ast
import json
import logging
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "MIGRATION_MANIFEST.json"
UPSTREAM_POLICY = ROOT / "UPSTREAM_SOURCES.json"
LOGGER = logging.getLogger(__name__)
IGNORED_DIRS = {".git", ".github", "scripts"}
LOCAL_STATUSES = {"migrated_agpl"}
EXTERNAL_STATUSES = {"external_pinned_upstream_agpl"}
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_LICENSE = "AGPL-3"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def git_tree(module: str) -> str | None:
    if not (ROOT / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", f"HEAD:{module}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def validate_receipt(
    module: str,
    manifest: dict,
    receipt_path: Path,
    expected_source: str,
    errors: list[str],
) -> None:
    receipt = load_json(receipt_path)
    if receipt.get("module") != module:
        errors.append(f"{module}: receipt module mismatch")
    if receipt.get("source_repository") != expected_source:
        errors.append(f"{module}: receipt source_repository mismatch")
    if receipt.get("exact_tree_match") is not True:
        errors.append(f"{module}: receipt must assert exact_tree_match=true")
    source_tree = receipt.get("source_tree_sha")
    target_tree = receipt.get("target_tree_sha")
    if not source_tree or source_tree != target_tree:
        errors.append(f"{module}: receipt source/target tree SHAs must match")
    actual_tree = git_tree(module)
    if actual_tree is not None and actual_tree != target_tree:
        errors.append(
            f"{module}: receipt target_tree_sha {target_tree!r} != checked-out tree {actual_tree!r}"
        )
    receipt_license = receipt.get("effective_license") or receipt.get("license_preserved")
    if receipt_license != manifest.get("license"):
        errors.append(
            f"{module}: receipt license {receipt_license!r} != manifest license {manifest.get('license')!r}"
        )
    if receipt.get("source_deleted") is not False:
        errors.append(f"{module}: initial migration receipt must keep source_deleted=false")
    if receipt.get("relicensing") is True:
        errors.append(f"{module}: physical Community migration cannot assert relicensing=true")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    policy = load_json(POLICY)
    upstream_policy = load_json(UPSTREAM_POLICY)
    planned_map = policy.get("planned_modules", {})
    planned = set(planned_map)
    physical = set(policy.get("physical_modules", []))
    external_declared = set(policy.get("external_upstream_modules", []))
    receipts = policy.get("migration_receipts", {})
    upstream_sources = upstream_policy.get("sources", {})
    external = set(upstream_sources)
    addons = discover_addons()
    errors: list[str] = []

    if policy.get("schema_version") != 4:
        errors.append("Community MIGRATION_MANIFEST schema_version must be 4")
    if policy.get("repository_role") != "community":
        errors.append("Community repository_role must remain 'community'")
    rules = policy.get("rules", {})
    for key in ("may_depend_on_professional", "may_depend_on_vendor_adapters", "may_depend_on_internal"):
        if rules.get(key) is not False:
            errors.append(f"Community rule {key!r} must remain false")
    if rules.get("proprietary_relicensing_allowed") is not False:
        errors.append("Community proprietary relicensing must remain forbidden")
    if rules.get("vendor_upstream_source_in_repository") is not False:
        errors.append("Community must not vendor its external pinned upstream")

    actual = set(addons)
    if physical != actual:
        missing = sorted(actual - physical)
        stale = sorted(physical - actual)
        if missing:
            errors.append("physical_modules missing local addons: " + ", ".join(missing))
        if stale:
            errors.append("physical_modules declares absent addons: " + ", ".join(stale))
    if set(receipts) != physical:
        errors.append("migration_receipts keys must exactly match physical_modules")
    if external_declared != external:
        errors.append("external_upstream_modules must exactly match UPSTREAM_SOURCES.json sources")

    unexpected = sorted(actual - planned)
    if unexpected:
        errors.append("Unexpected addons in Community: " + ", ".join(unexpected))

    for module, status in sorted(planned_map.items()):
        if status in LOCAL_STATUSES and module not in addons:
            errors.append(f"{module}: status {status!r} requires a local addon")
        elif status in EXTERNAL_STATUSES:
            if module in addons:
                errors.append(f"{module}: external pinned upstream must not be vendored locally")
            if module not in external:
                errors.append(f"{module}: external pinned upstream missing from UPSTREAM_SOURCES.json")
        elif status not in LOCAL_STATUSES | EXTERNAL_STATUSES:
            errors.append(f"{module}: unsupported migration status {status!r}")

    for module, source in sorted(upstream_sources.items()):
        if module not in planned:
            errors.append(f"{module}: upstream source is not declared in planned_modules")
        if source.get("distribution_mode") != "external_pinned_dependency":
            errors.append(f"{module}: distribution_mode must be external_pinned_dependency")
        if source.get("license") != EXPECTED_LICENSE:
            errors.append(f"{module}: upstream dependency must remain {EXPECTED_LICENSE}")
        if not SHA1_RE.fullmatch(source.get("commit", "")):
            errors.append(f"{module}: upstream commit must be a full 40-character SHA")
        if not source.get("repository") or "/" not in source.get("repository", ""):
            errors.append(f"{module}: upstream repository must use owner/name form")
        if source.get("module_path") != module:
            errors.append(f"{module}: module_path must equal technical addon name")
        objects = source.get("verified_top_level_objects", {})
        if not isinstance(objects, dict) or not objects:
            errors.append(f"{module}: verified_top_level_objects must be non-empty")
        else:
            for path, sha in sorted(objects.items()):
                if not path or not SHA1_RE.fullmatch(str(sha)):
                    errors.append(f"{module}: invalid verified object SHA for {path!r}")
        for required_by in source.get("required_by", []):
            if required_by not in planned:
                errors.append(f"{module}: required_by {required_by!r} is not a planned Community addon")

    for module, manifest in sorted(addons.items()):
        if manifest.get("license") != EXPECTED_LICENSE:
            errors.append(f"{module}: Community migration requires {EXPECTED_LICENSE}")
        receipt_rel = receipts.get(module)
        if not receipt_rel:
            errors.append(f"{module}: physical migration requires a receipt")
        else:
            receipt_path = ROOT / receipt_rel
            if not receipt_path.is_file():
                errors.append(f"{module}: migration receipt missing: {receipt_rel}")
            else:
                validate_receipt(module, manifest, receipt_path, policy.get("source_repository"), errors)
        for dependency in manifest.get("depends", []):
            if dependency.startswith("kt_") and dependency not in planned:
                errors.append(f"{module}: dependency {dependency!r} crosses out of Community")
            if dependency in planned and dependency not in addons and dependency not in external:
                errors.append(f"{module}: planned dependency {dependency!r} is neither local nor pinned upstream")

    patch = addons.get("kt_ecommerce_barcode_search_patch")
    if patch and "ecommerce_barcode_search" not in patch.get("depends", []):
        errors.append("kt_ecommerce_barcode_search_patch must retain explicit upstream dependency")

    if errors:
        for error in errors:
            LOGGER.error(error)
        return 1
    LOGGER.info(
        "Community boundary valid: %d physical addon(s), %d pinned upstream source(s), receipt/fingerprints coherent.",
        len(addons),
        len(external),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
