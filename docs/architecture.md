# Public Architecture

BCAST defines versioned, pre-1.0 consumer-facing contracts for regulatory packages. Production compilation and provider access remain separate private implementation responsibilities.

```text
publishers / authorities / lawful providers
                 |
                 v
        +-------------------+
        | private BCAST     |
        | compilation      |
        | (not deployed)   |
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

The first maintained package contract is [`bcast.package/0.1.0`](../spec/package-0.1.0.md). It is a deliberately small pre-1.0 consumer contract for package identity, publication identity, regulatory objects, structural parentage, explicit resolution state, public assurance state, optional plain text, and source-safe provenance.

The contract describes consumer-visible output. It does not expose provider acquisition, normalization, review queues, compiler intermediate representations, graph compilation, or package-build machinery.

## Service API

The maintained [`bcast.api/0.1.0`](../spec/api-0.1.0.md) draft is read-only and declares explicit compatibility with `bcast.package/0.1.0` only. Its four GET operations retrieve package metadata, a full package, an object, and its direct structural children. The public client and local reference server exercise this contract with already-built packages; neither constitutes a deployed production service.

Discovery, amendment traversal, cross-edition relationships, production search, and provider acquisition are not part of this API. Ingestion, normalization, review, and package-build operations remain private implementation concerns.

## Client SDKs

Public SDKs should be thin consumer clients mechanically checked against the maintained contract. The current source-independent Python client reads local packages and can retrieve objects through the draft read-only API. They should not duplicate regulatory interpretation or compilation logic.

## Conformance

Public conformance tooling is deterministic and source-independent. It validates that an object or package satisfies a published contract. It does not reproduce the private compiler or independently establish regulatory correctness.

The current validator is [`conformance/validate.py`](../conformance/validate.py), exercised against project-authored synthetic data.

## Upstream independence

BCAST's public meaning must not depend on any one provider's object model. Adding or replacing an upstream provider should not break downstream contracts unless the public regulatory meaning itself changes.