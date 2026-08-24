# BCAST Public Specifications

This directory contains consumer-facing BCAST contracts and the rules that govern them.

The public specification surface may eventually include:

- canonical package schemas;
- read-oriented service API definitions;
- identifier rules;
- compatibility/versioning rules;
- deterministic conformance requirements.

It does **not** specify private ingestion, provider adaptation, source normalization, review workflow, graph construction, confidence machinery, or package-build operations.

## Current status

BCAST is pre-1.0. No package schema or OpenAPI contract has been released yet.

The repository will create `schemas/` and `openapi/` only when there is a real maintained contract to place in them. Empty directories and placeholder schemas are intentionally avoided.

Current public rules:

- [`compatibility.md`](compatibility.md) — how public contracts evolve;
- [`identifiers.md`](identifiers.md) — provider-neutral identity principles.

Concrete wire formats should be introduced only when downstream consumers have a real interface to depend on.