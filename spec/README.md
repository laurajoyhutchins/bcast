# BCAST Public Specifications

This directory contains the normative consumer-facing BCAST standard and the rules that govern it.

## Normative authority

The human-readable specification documents in this directory are normative for BCAST public contracts. Versioned package contracts, identifier rules, and compatibility rules define the meaning that conforming producers and consumers may rely on.

JSON Schemas, conformance validators, examples, generated documentation, and client implementations are companion artifacts. They exist to make the standard testable and usable, but they do not independently redefine it. If a companion artifact conflicts with the normative specification, the normative specification wins.

Requirements that span multiple records, including deterministic identity, uniqueness, parent resolution, and acyclic structural parentage, remain normative even where JSON Schema cannot express them by itself.

The public specification surface may contain:

- canonical package contracts;
- companion package schemas;
- read-oriented service API definitions;
- identifier rules;
- compatibility/versioning rules;
- deterministic conformance requirements.

It does **not** specify private ingestion, provider adaptation, source normalization, review workflow, graph construction, confidence machinery, or package-build operations.

## Current status

BCAST is pre-1.0. Its maintained contracts are drafts and may change according to [`compatibility.md`](compatibility.md).

The first maintained package contract is:

- [`package-0.1.0.md`](package-0.1.0.md) — normative semantic contract and deterministic identity rules;
- [`schemas/package-0.1.0.schema.json`](schemas/package-0.1.0.schema.json) — companion JSON Schema for `bcast.package/0.1.0`.

There is not yet a public OpenAPI service contract. An `openapi/` directory should be created only when there is a real maintained service interface to place in it.

BCAST does not currently define or claim an IANA-registered BCAST-specific media type. Media-type registration is a separate interoperability decision and any future declaration must distinguish registered from unregistered types accurately.

Other public rules:

- [`compatibility.md`](compatibility.md) — normative rules for how public contracts evolve;
- [`identifiers.md`](identifiers.md) — normative provider-neutral identity principles;
- [`../docs/standards-governance.md`](../docs/standards-governance.md) — process for normative changes, status, releases, errata, and citation.

Concrete formats belong here only when downstream consumers have a real interface to depend on. Private compiler representations are not promoted into public contracts merely because they already exist.
