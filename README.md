# Kuvexta Odoo Community

Community/open-source Odoo modules maintained or integrated by Kuvexta.

## Scope

This repository contains Community/AGPL work, upstream-compatible extensions and code that must remain openly distributable. Third-party copyright and license notices must be preserved exactly.

## Branch policy

- `main`: repository governance and cross-version documentation.
- `19.0`: Odoo 19 code line.

## Licensing

Licensing is declared per module and third-party component. AGPL-derived code remains AGPL-compatible and is never moved into the proprietary Professional distribution path.

## Migration status

The first Community wave is active. `kt_ecommerce_barcode_search_patch` is physically migrated under AGPL-3. Its required upstream addon, `ecommerce_barcode_search` from Cybrosys Techno Solutions, is intentionally **not vendored** in this repository: it is recorded as an external pinned AGPL-3 dependency in `UPSTREAM_SOURCES.json`.

This keeps upstream ownership explicit, avoids an unnecessary third-party fork, and makes updates auditable. Before installing the Kuvexta patch, provide the pinned `ecommerce_barcode_search` addon from `CybroOdoo/CybroAddons` at the recorded commit in the Odoo addons path.

`MIGRATION_MANIFEST.json` defines which Community addons are physical versus external upstream dependencies. `scripts/validate_community_repository.py` blocks proprietary licensing, unexpected local addons, missing pinned sources, and Community dependencies that cross into Professional.
