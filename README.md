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

The public surface contains or is intended to contain:

- versioned package and API specifications;
- stable identity and compatibility rules;
- thin client SDKs;
- deterministic conformance tooling;
- synthetic or clearly redistributable examples;
- integration, security, contribution, and rights documentation.

The first maintained package contract is [`bcast.package/0.1`](spec/package-0.1.md). It is a pre-1.0 private-preview contract and is exercised by a synthetic fixture plus deterministic local conformance validation.

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

BCAST is pre-1.0. The first package contract now exists, but no public service API has been released and compatibility rules may evolve before 1.0.

This repository remains private while its licensing model and publication checks are completed. Visibility should not change until the publication checklist passes.

## Validate the synthetic package

```bash
python -m pip install -r conformance/requirements.txt
python conformance/validate.py   spec/schemas/package-0.1.schema.json   examples/synthetic/package-0.1.json
```

Validation is deliberately source-independent. It checks the public contract and deterministic identity/structure invariants without invoking any private compiler or source acquisition path.

## Repository map

- [`spec/package-0.1.md`](spec/package-0.1.md) — first public package contract
- [`spec/schemas/package-0.1.schema.json`](spec/schemas/package-0.1.schema.json) — package JSON Schema
- [`examples/synthetic/package-0.1.json`](examples/synthetic/package-0.1.json) — project-authored synthetic fixture
- [`conformance/validate.py`](conformance/validate.py) — deterministic local validator
- [`docs/product-boundary.md`](docs/product-boundary.md) — public/private product boundary
- [`docs/architecture.md`](docs/architecture.md) — public-facing architecture
- [`docs/source-and-rights.md`](docs/source-and-rights.md) — source and redistribution rules
- [`docs/migration-from-alpha.md`](docs/migration-from-alpha.md) — clean migration boundary from alpha
- [`docs/roadmap.md`](docs/roadmap.md) — public-surface milestones
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — acceptable contribution scope
- [`SECURITY.md`](SECURITY.md) — security and sensitive-data reporting

The archived `building-code-ast-alpha` repository is historical research and implementation state. It is not an active upstream branch of BCAST and is not migrated wholesale into this repository.
