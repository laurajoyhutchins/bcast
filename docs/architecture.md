# Public Architecture

BCAST presents stable consumer-facing contracts around a private regulatory compilation service.

```text
publishers / authorities / lawful providers
                 |
                 v
        +-------------------+
        | private BCAST     |
        | compilation      |
        | service          |
        +-------------------+
                 |
                 v
        +-------------------+
        | BCAST public     |
        | package contract |
        +-------------------+
            |          |
            v          v
       service API   conformance
            |
            v
       client SDKs
            |
            v
      downstream tools
```

## Architectural boundary

The public repository begins at the output boundary of the private BCAST compilation service.

The private side may ingest heterogeneous provider data, normalize source structure, reconcile identities, review semantic relationships, build graphs, and materialize packages. Those activities are not public interfaces and are intentionally not specified here.

The public side defines only what downstream consumers need to rely on:

1. canonical package semantics;
2. provider-neutral identifiers;
3. compatibility and versioning rules;
4. read-oriented service interfaces;
5. deterministic contract conformance;
6. thin client behavior.

## Package contract

The package contract will eventually define the minimum interoperable representation of compiled regulatory information. It should expose stable consumer meaning rather than internal compiler state.

No production package schema is published yet.

## Service API

The future public service API should be read-oriented. Candidate operations include retrieving package metadata, retrieving a regulatory object by canonical identity, traversing public relationships, and checking compatibility.

Ingestion, normalization, review, and package-build operations are private and should not appear in the public API merely because an internal endpoint exists.

## Client SDKs

Public SDKs should be thin clients generated from, or mechanically checked against, the service contract wherever practical. They should not duplicate regulatory interpretation or compilation logic.

## Conformance

Public conformance tooling should be deterministic and source-independent. It validates that an object or response satisfies a published contract. It does not reproduce the private compiler or independently establish regulatory correctness.

## Upstream independence

BCAST's public meaning must not depend on any one provider's object model. Adding or replacing an upstream provider should not break downstream contracts unless the public regulatory meaning itself changes.