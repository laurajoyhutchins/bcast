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

Define how the public BCAST standard changes and how immutable release snapshots are identified.

Deliverables:

- maintainer-led normative-change governance with an explicit public/private decision boundary;
- draft, stable, deprecated, and withdrawn standard statuses;
- editorial correction, errata, and normative-change rules;
- explicit mapping between semantic contract versions and repository tags/releases;
- exact-revision release gates with conformance and changelog evidence;
- machine-readable citation metadata without implied DOI or standards-body registration.

Exit condition: a future BCAST contract can be released and cited without a Git tag or GitHub release silently inventing compatibility semantics.

## M3 — Consumer API

Publish a read-oriented service contract around BCAST packages.

Deliverables:

- versioned OpenAPI specification;
- package/object retrieval operations;
- supported relationship traversal;
- explicit package/API compatibility behavior;
- thin client SDK generation or mechanical contract checking.

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
