# Agent rules — Kuvexta Odoo Community

- Target/default branch: `19.0`.
- Preserve upstream copyright, license and modification notices. Community/AGPL code is never a source for proprietary relicensing.
- Distinguish physical Kuvexta addons from external pinned upstream dependencies. Prefer an explicit upstream pin over unnecessary vendorization/forking.
- `MIGRATION_MANIFEST.json` declares physical vs external state; `UPSTREAM_SOURCES.json` records exact upstream repository/commit/object fingerprints.
- Every physically migrated Kuvexta addon requires a receipt proving module, source repository, exact source/target tree identity, effective license and `source_deleted=false`.
- Community may depend on official Odoo, Foundation, Community and explicitly pinned upstream Community dependencies. It must not depend—hard or hidden optional—on Professional, Vendor Adapters or Internal.
- A dependency boundary cannot be bypassed with dynamic imports, assets, controller/model lookup, `env[...]`, `env.get(...)` or provider hooks. If an integration crosses to a forbidden layer, move it to an explicit bridge in the appropriate higher layer.
- Do not silently copy an external upstream addon into this repository when its declared mode is `external_pinned_dependency`.
- Generated inventories/fingerprints are updated from their actual source of truth; never invent hashes or current-state metrics.
- Immediately before merge, re-fetch exact PR HEAD and base, require all gates green on that HEAD, and use squash plus expected-head guard for automated merges. Base movement requires retest.
