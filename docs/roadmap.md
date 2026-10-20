# BCAST Software Roadmap

This roadmap covers the **public reusable software product**, including the source-independent compiler. Private source acquisition, rights review, restricted mappings, evidence and production corpus are not public deliverables. This ownership is the target architecture, not a completed migration. See [Product boundary](product-boundary.md).

## M0 — Public surface foundation

Status: complete; repository public as of August 26, 2026.

Deliverables:

- clear BCAST product positioning;
- public/private product boundary;
- public architecture;
- source-and-rights policy;
- contribution and security policy;
- compatibility and identifier principles;
- publication checklist.

Exit condition: the repository distinguishes reusable public software from controlled source data and does not imply that the source corpus is redistributable.

## M1 — First package contract

Status: draft implementation baseline complete; no tagged package release yet.

Implemented baseline:

- normative `bcast.package/0.1.0` semantic contract;
- companion JSON Schema for `bcast.package/0.1.0`;
- project-authored synthetic valid and invalid conformance fixtures;
- deterministic local conformance validation;
- provider-neutral identity wire rules;
- explicit precedence of the normative specification over companion artifacts;
- explicit alpha-to-public migration boundary.

Before a stable 1.0 contract, changes remain governed by the pre-1.0 compatibility policy and must be explicit and versioned rather than silently reinterpreting an existing contract coordinate.

## M2 — Standards governance and citable releases

Status: governance baseline complete; no tagged standards release yet.

Implemented baseline:

- maintainer-led normative-change governance with an explicit public/private decision boundary;
- draft, stable, deprecated, and withdrawn standard statuses;
- editorial correction, errata, and normative-change rules;
- explicit mapping between semantic contract versions and repository tags/releases;
- exact-revision release gates with conformance and changelog evidence;
- machine-readable citation metadata without implied DOI or standards-body registration.

Exit condition: a future BCAST contract can be released and cited without a Git tag or GitHub release silently inventing compatibility semantics.

## M3 — Consumer API and source-independent client stack

Status: draft contract and source-independent implementation baseline complete; no production service deployment yet.

Implemented baseline:

- normative `bcast.api/0.1.0` read-only contract;
- companion OpenAPI 3.2 description;
- package metadata and full-package retrieval;
- canonical object retrieval;
- direct structural-child traversal derived only from normative `parent_id`;
- deterministic public error taxonomy;
- exact declared compatibility with `bcast.package/0.1.0`;
- source-independent mechanical contract tests in the public conformance suite;
- installable Python client and CLI for local `bcast.package/0.1.0` validation, object retrieval, and direct-child traversal;
- public deterministic publication, object, and package identity helpers derived from the normative package contract;
- standard-library HTTP client for all four `bcast.api/0.1.0` GET operations and stable problem semantics;
- local read-only reference server over already-built conforming package files;
- end-to-end client/server regression tests for unresolved record retrieval, not-found problems, and deterministic child ordering;
- packaged schema parity checks so the client cannot silently drift from the maintained companion schema in the same revision.

The API contract and public consumer stack deliberately do not standardize or implement provider lookup, semantic relationship traversal, amendment graphs, cross-edition traversal, mutation, private source-acquisition operations, authentication, entitlement, source acquisition, or production deployment URLs. The local reference server is a conformance and integration aid, not the production BCAST service.

## M4 — Reusable public package builder

Status: planned; current bounded eCFR producer still mixes generic package construction with source-specific normalization in the private repository.

- Implement the smallest source-independent normalized publication input and deterministic 0.2.0 package builder needed to reproduce the accepted synthetic package and eCFR results.
- Keep canonical identity, content hashing, structural rules and public validation in the public software authority, not a duplicate private producer.
- Demonstrate synthetic compilation with no private data, credentials or imports.
- Migrate private ingestion to invoke the exact pinned public builder, prove source/package replay and failure equivalence, then remove duplicate private package assembly.
- Keep acquisition, source-specific restricted mappings, production evidence, GCS retention, rights approval and corpus publication operations private.

Do not introduce a general provider plugin framework or change a normative consumer contract unless a concrete demonstrated use case requires it.

## Outside the public software roadmap

- Live Code Connect, NFPA LiNK or other controlled-provider acquisition and entitlement management.
- Licensed-source retention, source-specific private mappings, private evidence and review decisions.
- Maintained production regulatory corpus, release approvals, generation-pinned storage and rights-scoped distribution.
- Source-specific fidelity checks against non-redistributable inputs and operational integration infrastructure.
