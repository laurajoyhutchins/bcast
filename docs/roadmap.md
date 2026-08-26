# Public Roadmap

This roadmap covers the public technical surface only. It does not describe private provider ingestion, corpus growth, review operations, or compilation internals.

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

Exit condition: the repository can explain what BCAST exposes without implying that the production compiler or corpus is open source.

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

## M3 — Consumer API and thin client

Status: draft contract baseline and first local client complete; no production service deployment yet.

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
- packaged schema parity checks so the client cannot silently drift from the maintained companion schema in the same revision.

The API contract and thin client deliberately do not standardize or implement provider lookup, semantic relationship traversal, amendment graphs, cross-edition traversal, mutation, private compilation operations, authentication, entitlement, source acquisition, or deployment URLs.

## Outside the public roadmap

The following are private product work and are intentionally not tracked here as public deliverables:

- production Code Connect, NFPA LiNK, or other provider ingestion;
- licensed-source acquisition and retention;
- provider normalization and identity reconciliation;
- reviewed semantic corpus expansion;
- cross-publisher and cross-edition production graph construction;
- amendment compilation;
- package-materialization internals;
- private review and verification operations.
