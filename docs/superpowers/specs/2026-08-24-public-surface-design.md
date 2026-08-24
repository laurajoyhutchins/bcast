# BCAST Public Surface Design

Date: 2026-08-24
Status: Proposed architecture

## Purpose

`laurajoyhutchins/bcast` is the future public technical surface for BCAST.

BCAST is a provider-neutral regulatory compilation product. Upstream publishers and authorities provide source publications or machine-readable source data; BCAST normalizes, links, reviews, versions, and materializes that information into coherent regulatory packages for downstream tools.

The public repository must be useful enough to support real integrations without exposing the private compilation system or the compounding regulatory corpus.

## Governing boundary

The public/private split is:

> Open protocol. Open clients. Open validation. Closed compilation. Proprietary compiled corpus.

The public repository defines how consumers interact with BCAST outputs. It does not contain the production machinery or data required to reproduce those outputs.

### Public

The repository may contain:

- product and protocol documentation;
- canonical public package and API schemas;
- OpenAPI specifications for supported service interfaces;
- stable identifier and versioning rules;
- client SDKs whose only responsibility is consuming public BCAST interfaces;
- local conformance validators for public package contracts;
- synthetic fixtures and deliberately public examples;
- contribution, security, compatibility, and release policies;
- public changelog and roadmap information appropriate for consumers;
- small interoperability reference implementations when they do not encode production compilation behavior.

### Private

The repository must not contain:

- publisher credentials, entitlements, tokens, or private provider locators;
- production provider adapters, including Code Connect, NFPA LiNK, or equivalent ingestion logic;
- licensed or restricted source content;
- normalized provider datasets produced from licensed sources;
- provider-specific production mappings into canonical BCAST identities;
- the full reviewed semantic corpus;
- cross-publisher relationship datasets;
- cross-edition identity and semantic-change datasets;
- amendment materialization datasets;
- private review corpora, review queues, acceptance decisions, or reviewer annotations;
- production normalization heuristics or source-family recovery logic whose accumulated behavior constitutes product know-how;
- package-construction or graph-compilation services;
- internal confidence/review machinery beyond public output fields and public validation semantics;
- proprietary verification evidence that would allow reconstruction of the private compilation process.

## Product model

BCAST does not define source authority. Publishers, standards organizations, governments, and other lawful providers remain authoritative for source publications.

BCAST's product is the provider-neutral compiled representation produced from those inputs, subject to source rights and contractual constraints.

The conceptual flow is:

```text
publisher / authority sources
        |
        v
private provider adapters
        |
        v
private normalization + semantic compilation
        |
        v
private reviewed regulatory graph
        |
        v
BCAST package materialization
        |
        +--> public package contract
        +--> public API contract
        +--> public client SDKs
```

A provider representation is never itself a canonical BCAST representation. Provider IDs, URLs, PDF coordinates, API object types, and source-specific hierarchy conventions are evidence and adapter inputs, not downstream authority.

## Public contract responsibilities

### Canonical package contract

The public package contract should eventually define the minimum interoperable BCAST object model required by downstream consumers. It should include only fields that are stable product commitments.

Expected categories include:

- package identity and version;
- publication and edition identity;
- canonical regulatory object identities;
- structural relationships;
- semantic relationship types exposed to consumers;
- provenance references sufficient to explain source origin without leaking private provider details;
- review or assurance state as a public product guarantee;
- change/version metadata;
- explicit unsupported or unresolved states where appropriate.

The contract must not encode one publisher's object model as the canonical shape.

### API contract

The service API should expose consumer operations rather than internal compilation stages. Early public interfaces should favor read-oriented operations such as:

- retrieve package metadata;
- retrieve a regulatory object by canonical identity;
- traverse supported public relationships;
- inspect package/version compatibility;
- validate a package or response against public contracts.

Do not expose internal ingestion, normalization, review, or package-build endpoints in the public specification merely because they exist internally.

### Client SDKs

Public SDKs should be thin clients generated from or mechanically checked against the API contract wherever practical.

SDKs must not contain shadow business logic that duplicates server-side regulatory interpretation, normalization, or compilation.

### Conformance tooling

Local validators are valuable public infrastructure. They should answer whether an object or package conforms to the published BCAST contract, not whether the underlying regulatory interpretation is correct.

Public validation must remain deterministic and source-independent.

## Repository structure

The initial public repository should stay deliberately small:

```text
README.md
SECURITY.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
CHANGELOG.md

spec/
  README.md
  schemas/
  openapi/
  compatibility.md
  identifiers.md

examples/
  synthetic/

sdk/
  README.md

conformance/
  README.md

docs/
  architecture.md
  product-boundary.md
  source-and-rights.md
  roadmap.md
  superpowers/specs/
```

A `LICENSE` file is added only after the public artifact licensing model is deliberately selected. Directories should exist only when they contain a real maintained artifact. Empty scaffolding should not be created merely to advertise future plans.

## Initial release scope

The first public milestone should not attempt to publish the full future object model. It should establish the repo's identity and guardrails before product contracts harden.

Initial contents should therefore include:

1. a concise README explaining what BCAST is and is not;
2. a public/product boundary document;
3. a source-and-rights policy;
4. contribution and security policies;
5. a compatibility/versioning policy skeleton that explicitly labels pre-1.0 contracts as unstable;
6. a deliberately minimal synthetic example only after the first public package schema exists;
7. no production provider adapters and no migrated corpus from `building-code-ast-alpha`.

## Migration policy from `building-code-ast-alpha`

`building-code-ast-alpha` is historical research and implementation state. It is not an upstream branch of BCAST and should not be revived as the active product repository.

Nothing should be copied wholesale.

When an alpha artifact appears useful, classify it first:

- **Public contract candidate**: re-specify it from current product requirements, then implement it cleanly in `bcast`.
- **Private compiler asset**: move or reimplement it only in the private product system.
- **Historical research evidence**: leave it in the archived alpha repository.
- **Obsolete machinery**: do not preserve it.

Git history from alpha should not be imported into the public repo simply for continuity.

## Data and moat protection rules

The public repository must optimize for interoperability without becoming a continuously updated mirror of the product corpus.

Good public evidence:

- schema examples;
- synthetic fixtures;
- aggregate capability statements;
- compatibility matrices;
- deterministic conformance tests;
- small examples sourced from clearly redistributable material.

Bad public evidence:

- exhaustive inventories of production corpus contents;
- record-level review receipts from proprietary or restricted publications;
- lists of unresolved production mappings that reveal the private compilation frontier;
- full cross-edition correspondence tables;
- full cross-publisher dependency graphs;
- source-specific production heuristics and benchmark corpora;
- operational metadata that reveals private provider accounts or access patterns.

## Contribution model

External contributions should be encouraged around public interfaces and interoperability, not private corpus production.

Appropriate contributions include:

- schema and documentation fixes;
- SDK improvements;
- conformance tooling;
- synthetic/public-domain test cases;
- interoperability proposals;
- bug reports against public contracts.

Requests to add proprietary source data, publisher-derived bulk content, private credentials, or unreviewed regulatory interpretations should be rejected by policy.

## Licensing

Do not carry the alpha repository's Apache-2.0 license forward automatically without deciding which public artifacts BCAST intends others to reuse.

The eventual license must clearly distinguish project-authored public code/specifications from third-party source material. No license choice may imply that BCAST can sublicense publisher content it does not own.

Until that decision is made, the repository should remain private and should not add a misleading license merely for completeness.

## Publication gate

Before changing repository visibility to public, verify all of the following:

- no production credentials or provider locators are present anywhere in Git history;
- no licensed or restricted source text is present anywhere in Git history;
- no private corpus, mapping, review, or compilation artifacts are present;
- repository description and README accurately describe BCAST as a public technical interface, not an open-source compiler;
- source-and-rights policy is present;
- contribution policy rejects proprietary-source ingestion through public pull requests;
- license choice has been made deliberately and the corresponding `LICENSE` file is present;
- examples are synthetic or clearly redistributable;
- public schemas expose stable consumer commitments only;
- Git history has been reviewed as part of the publication decision.

## Success criteria

The public repository is successful when:

1. a developer can understand what BCAST provides without seeing the private compiler;
2. a developer can build against the public contracts and SDKs without access to proprietary source data;
3. BCAST can replace or add upstream providers without breaking downstream identity or package semantics unnecessarily;
4. private compilation logic and the continuously reviewed corpus remain unnecessary for public conformance;
5. the repository can become public without exposing the product's compounding data moat;
6. the public surface remains smaller and more stable than the private implementation behind it.
