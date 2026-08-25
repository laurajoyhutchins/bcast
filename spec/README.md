# BCAST Public Specifications

This directory contains consumer-facing BCAST contracts and the rules that govern them.

The public specification surface may contain:

- canonical package schemas;
- read-oriented service API definitions;
- identifier rules;
- compatibility/versioning rules;
- deterministic conformance requirements.

It does **not** specify private ingestion, provider adaptation, source normalization, review workflow, graph construction, confidence machinery, or package-build operations.

## Current status

BCAST is pre-1.0.

The first maintained package contract is:

- [`package-0.1.md`](package-0.1.md) — semantic contract and deterministic identity rules;
- [`schemas/package-0.1.schema.json`](schemas/package-0.1.schema.json) — JSON Schema for `bcast.package/0.1`.

There is not yet a public OpenAPI service contract. An `openapi/` directory should be created only when there is a real maintained service interface to place in it.

Other public rules:

- [`compatibility.md`](compatibility.md) — how public contracts evolve;
- [`identifiers.md`](identifiers.md) — provider-neutral identity principles.

Concrete formats belong here only when downstream consumers have a real interface to depend on. Private compiler representations are not promoted into public contracts merely because they already exist.
