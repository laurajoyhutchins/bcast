# Public Roadmap

This roadmap covers the public technical surface only. It does not describe private provider ingestion, corpus growth, review operations, or compilation internals.

## M0 — Public surface foundation

Status: implemented in the private pre-publication repository.

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

Status: implementation baseline complete; public release still gated.

Implemented baseline:

- versioned `bcast.package/0.1` JSON Schema;
- project-authored synthetic package fixture;
- deterministic local conformance validation;
- provider-neutral identity wire rules;
- explicit alpha-to-public migration boundary.

Remaining release work is publication governance, including the deliberate license choice and final publication checklist. Those gates do not justify importing private compiler machinery into this repository.

## M2 — Consumer API

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
