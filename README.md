# BCAST

BCAST is a provider-neutral representation and interface layer for compiled building-code information.

```text
source providers -> private BCAST compilation -> public BCAST contracts -> downstream tools
```

This repository is BCAST's public technical surface. It is **not** the production compiler and does not contain BCAST's proprietary compiled regulatory corpus.

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

The first maintained package contract is [`bcast.package/0.1.0`](spec/package-0.1.0.md). The first maintained read-only API contract is [`bcast.api/0.1.0`](spec/api-0.1.0.md), explicitly compatible only with `bcast.package/0.1.0`. Both are pre-1.0 drafts exercised by deterministic public conformance checks.

The human-readable BCAST specification is normative. JSON Schemas, OpenAPI descriptions, validators, examples, generated documentation, and client implementations are companion artifacts; if a companion artifact conflicts with the normative specification, the specification wins. See [`spec/README.md`](spec/README.md).

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

## License and rights

Except where explicitly stated otherwise, BCAST-authored material in this repository is licensed under the Apache License, Version 2.0 (`Apache-2.0`).

This license applies only to material and rights that BCAST is authorized to license. It does not license or sublicense third-party building codes, standards, publisher content, provider data, or other source material referenced by BCAST.

The license also does not apply to BCAST's proprietary compiled corpus, private compiler implementation, private provider mappings or adapters, production data, or other material that is not distributed as part of this repository under Apache-2.0.

Source publications remain subject to the copyright, licensing, access, and redistribution terms of their respective rights holders. See [`docs/source-and-rights.md`](docs/source-and-rights.md).

## Status

BCAST is public and pre-1.0. Draft package and read-only API contracts exist, but no production BCAST service has been deployed and no tagged BCAST standards release exists yet. Compatibility rules may evolve before 1.0 only through explicit versioned changes.

The repository history and public surface were reviewed for publication safety before the public cutover on August 26, 2026. Apache-2.0 is the selected license for BCAST-authored public-repository material. The completed publication record is in [`docs/publication-checklist.md`](docs/publication-checklist.md).

## Validate the public contracts

```bash
python -m pip install -r conformance/requirements.txt
python -m unittest conformance.test_conformance
python conformance/validate.py \
  spec/schemas/package-0.1.0.schema.json \
  examples/synthetic/valid/package-0.1.0.json
```

Validation is deliberately source-independent. It checks the public package contract, deterministic identity/structure invariants, and the read-only API contract without invoking any private compiler or source acquisition path.

## Repository map

- [`LICENSE`](LICENSE) — Apache License 2.0 for BCAST-authored repository material
- [`CITATION.cff`](CITATION.cff) — project-level machine-readable citation metadata
- [`spec/package-0.1.0.md`](spec/package-0.1.0.md) — first public package contract
- [`spec/api-0.1.0.md`](spec/api-0.1.0.md) — first public read-only API contract
- [`spec/openapi/bcast-api-0.1.0.openapi.json`](spec/openapi/bcast-api-0.1.0.openapi.json) — companion OpenAPI 3.2 description
- [`spec/schemas/package-0.1.0.schema.json`](spec/schemas/package-0.1.0.schema.json) — companion package JSON Schema
- [`examples/synthetic/README.md`](examples/synthetic/README.md) — conformance fixture taxonomy and redistribution statement
- [`examples/synthetic/valid/package-0.1.0.json`](examples/synthetic/valid/package-0.1.0.json) — project-authored conforming fixture
- [`examples/synthetic/invalid/package-0.1.0-missing-parent.json`](examples/synthetic/invalid/package-0.1.0-missing-parent.json) — project-authored nonconforming fixture
- [`conformance/validate.py`](conformance/validate.py) — deterministic local validator
- [`docs/standards-governance.md`](docs/standards-governance.md) — normative-change, status, release, errata, and citation process
- [`docs/product-boundary.md`](docs/product-boundary.md) — public/private product boundary
- [`docs/architecture.md`](docs/architecture.md) — public-facing architecture
- [`docs/source-and-rights.md`](docs/source-and-rights.md) — source and redistribution rules
- [`docs/migration-from-alpha.md`](docs/migration-from-alpha.md) — clean migration boundary from alpha
- [`docs/publication-audit-2026-08-25.md`](docs/publication-audit-2026-08-25.md) — publication-safety audit evidence
- [`docs/publication-checklist.md`](docs/publication-checklist.md) — completed publication record
- [`docs/roadmap.md`](docs/roadmap.md) — public-surface milestones
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — acceptable contribution scope
- [`SECURITY.md`](SECURITY.md) — security and sensitive-data reporting

The archived `building-code-ast-alpha` repository is historical research and implementation state. It is not an active upstream branch of BCAST and is not migrated wholesale into this repository.
