# Product Boundary

BCAST exposes a public technical interface around a private regulatory compilation product.

The durable boundary is:

> **Open protocol. Open clients. Open validation. Closed compilation. Proprietary compiled corpus.**

## Public surface

The public repository may contain:

- public package and API contracts;
- provider-neutral identity and compatibility rules;
- client SDKs that consume public interfaces;
- deterministic conformance validators;
- synthetic or clearly redistributable fixtures;
- interoperability documentation and proposals.

## Private product

The private product contains:

- production provider adapters and credentials;
- licensed or restricted source material;
- provider-specific normalization and mapping logic;
- reviewed regulatory data;
- cross-publisher and cross-edition production relationships;
- amendment compilation and materialization;
- private review evidence and acceptance decisions;
- graph construction and package-materialization services;
- source-family recovery and production normalization heuristics.

## Provider neutrality

A provider representation is never itself a canonical BCAST representation.

Provider IDs, URLs, API object types, document coordinates, and source-specific hierarchy conventions may be retained as provenance or aliases. They must not determine canonical BCAST identity or force downstream consumers to adopt a publisher-specific model.

BCAST should be able to add or replace lawful upstream providers without unnecessarily changing downstream identity or package semantics.

## Public contract rule

Only consumer-facing commitments belong in the public contract. Internal ingestion, normalization, review, compilation, confidence, and package-build machinery remain implementation details unless a specific output field must be standardized for consumers.

Public conformance answers whether an object satisfies a published BCAST contract. It does not certify that a regulatory interpretation is substantively correct.