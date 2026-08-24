# Public Roadmap

This roadmap covers the public technical surface only. It does not describe private provider ingestion, corpus growth, review operations, or compilation internals.

## M0 — Public surface foundation

Establish the repository boundary before publishing product contracts.

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

Publish the smallest useful provider-neutral package contract.

Deliverables:

- versioned package schema;
- deliberately synthetic or clearly redistributable examples;
- deterministic local conformance validation;
- compatibility notes for the first package version.

The schema should expose only consumer-facing commitments that are ready to be maintained. It should not mirror a publisher API or expose private compiler state.

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