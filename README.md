# BCAST

BCAST is a provider-neutral representation and interface layer for compiled building-code information.

```text
source providers -> private BCAST compilation -> public BCAST contracts -> downstream tools
```

This repository is the future public technical surface for BCAST. It is **not** the production compiler and does not contain BCAST's proprietary compiled regulatory corpus.

## What BCAST is

BCAST turns heterogeneous building-code and standards inputs into coherent, versioned regulatory packages that downstream software can consume through stable public contracts.

Publishers, standards organizations, governments, and other lawful providers remain authoritative for their source publications. BCAST's public model is provider-neutral: provider IDs, URLs, API object types, and source-specific hierarchy conventions are inputs and provenance, not canonical downstream identity.

## What this repository contains

The public surface is intended to contain:

- package and API specifications;
- stable identity and compatibility rules;
- thin client SDKs;
- deterministic conformance tooling;
- synthetic or clearly redistributable examples;
- integration, security, contribution, and rights documentation.

## What this repository does not contain

This repository does not contain:

- production provider adapters;
- provider credentials, entitlements, or private responses;
- licensed or restricted source content;
- normalized production datasets;
- BCAST's reviewed regulatory corpus;
- cross-publisher or cross-edition production mappings;
- private review evidence;
- production normalization, graph compilation, or package-materialization logic.

The durable boundary is:

> **Open protocol. Open clients. Open validation. Closed compilation. Proprietary compiled corpus.**

## Status

BCAST is pre-1.0. No public package schema or service API has been released yet, and compatibility rules may evolve before 1.0.

This repository remains private while its public surface, licensing model, and publication checks are established. Visibility should not change until the publication checklist is complete.

## Repository map

- [`docs/product-boundary.md`](docs/product-boundary.md) — public/private product boundary
- [`docs/architecture.md`](docs/architecture.md) — public-facing architecture
- [`docs/source-and-rights.md`](docs/source-and-rights.md) — source and redistribution rules
- [`docs/roadmap.md`](docs/roadmap.md) — public-surface milestones
- [`spec/`](spec/) — consumer-facing contract rules
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — acceptable contribution scope
- [`SECURITY.md`](SECURITY.md) — security and sensitive-data reporting

The archived `building-code-ast-alpha` repository is historical research and implementation state. It is not an active upstream branch of BCAST and is not migrated wholesale into this repository.