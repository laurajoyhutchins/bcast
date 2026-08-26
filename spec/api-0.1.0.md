# BCAST Read-Only Consumer API Contract 0.1.0

Status: pre-1.0 draft

`bcast.api/0.1.0` is the first maintained consumer-facing HTTP API contract for retrieving BCAST packages and regulatory objects.

This document is normative. [`openapi/bcast-api-0.1.0.openapi.json`](openapi/bcast-api-0.1.0.openapi.json) is the companion OpenAPI description. The OpenAPI description makes the contract mechanically inspectable, but it does not independently redefine this specification. If the two conflict, this document and the linked normative package, identifier, compatibility, and governance rules win.

The API is read-only. It does not expose provider APIs or provider-native identifiers as canonical identity, and it does not expose source acquisition, ingestion, normalization, review, compilation, package-build, entitlement, credential, or proprietary corpus operations.

## Contract version and compatibility

The API contract coordinate is:

```text
bcast.api/0.1.0
```

It is versioned independently of package contracts.

`bcast.api/0.1.0` is compatible with exactly:

```text
bcast.package/0.1.0
```

A server implementing this API MUST NOT infer compatibility with another package contract merely because its version is newer, nearby in time, or structurally similar. An incompatible package contract produces the `incompatible_version` error defined below.

Changing the API compatibility set is a normative API change and must be versioned rather than silently changing the meaning of `bcast.api/0.1.0`.

## Transport boundary

This contract uses ordinary `application/json`. It does not define or claim a BCAST-specific registered media type.

Deployment hostname, base path, authentication, authorization, commercial entitlement, rate limits, caching policy, and source-license enforcement are deployment concerns and are not standardized here. A deployment MAY impose those controls without changing the consumer-facing meanings defined by this contract.

The absence of an authentication scheme in the companion OpenAPI description does not mean that all BCAST data is public or unrestricted.

## Canonical identifiers

`package_id` and `object_id` are the provider-neutral canonical identifiers defined by [`package-0.1.0.md`](package-0.1.0.md) and [`identifiers.md`](identifiers.md).

Provider-native IDs, source URLs, account coordinates, private locators, and adapter-specific identifiers MUST NOT be accepted as substitutes for these canonical path identifiers.

An `object_id` is resolved only within the package named by the request `package_id`. If that object is not present in that package, the result is `not_found`, even if the same canonical object happens to exist in another package.

## Operations

### `GET /packages/{package_id}/metadata`

Returns the package fields `schema_version`, `package_id`, `package_version`, and `publication`, excluding the `objects` array.

This is a projection of the package contract, not a second metadata model.

### `GET /packages/{package_id}`

Returns the complete conforming `bcast.package/0.1.0` package.

A server MUST NOT add private compiler state, provider-native coordinates, entitlement details, or operational metadata to this representation.

### `GET /packages/{package_id}/objects/{object_id}`

Returns the exact public regulatory object record from the selected package.

Objects whose public `status` is `resolved`, `unresolved`, or `unsupported` remain retrievable as records. Ordinary object retrieval MUST NOT turn `unresolved` or `unsupported` into an error when the public record itself can be returned.

### `GET /packages/{package_id}/objects/{object_id}/children`

Returns the direct structural children of the selected object: exactly those package objects whose `parent_id` equals the requested `object_id`.

Results MUST be ordered lexicographically by `object_id` so response ordering does not acquire accidental meaning from source order or private compiler behavior.

This endpoint standardizes only reverse traversal of the package contract's existing structural `parent_id` relation. It does not create semantic relationship, amendment, cross-edition, provider-alias, citation-graph, or other traversal semantics.

## Error semantics

Errors use an `application/json` object with:

- `code`: one of the stable error codes below;
- `message`: a human-readable explanation that MUST NOT be required for program logic;
- optional `resource_id`: the relevant canonical public BCAST identifier when disclosing it is appropriate.

The stable cases are:

### `not_found` — HTTP 404

The requested canonical package or object is not present in the selected public BCAST view.

A response MUST NOT disclose private provider lookup attempts, account identifiers, source locators, or compiler diagnostics.

### `unresolved` — HTTP 409

The canonical public resource is known, but a requested representation cannot be supplied because the relevant public BCAST state is `unresolved`.

This code is reserved for operations or representations that actually require resolved data. The four core retrieval operations in `bcast.api/0.1.0` MUST return an available public object record instead of converting its `status: "unresolved"` into this error.

### `unsupported` — HTTP 422

The requested public representation or capability is explicitly unsupported by the API contract or by the relevant public BCAST state.

This code MUST NOT be used as a generic substitute for `not_found`, and it MUST NOT expose a private implementation reason.

### `incompatible_version` — HTTP 409

The selected resource uses a BCAST contract version that is not declared compatible with `bcast.api/0.1.0`.

A server MUST fail explicitly rather than attempting best-effort reinterpretation under a different package contract.

The `code` field, not the HTTP status alone, distinguishes `unresolved` from `incompatible_version`.

## Source independence

A conforming implementation may serve BCAST packages assembled from different lawful providers or internal compilation methods. Public responses are defined only by the BCAST contract.

Provider changes do not change canonical API identity or API meaning unless BCAST's consumer-facing contract itself changes.

## Deliberate omissions

Version 0.1.0 does not standardize:

- mutation operations;
- search or discovery across packages;
- semantic relationship traversal;
- amendment or cross-edition traversal;
- provider-native lookup;
- source acquisition or retention;
- ingestion, normalization, review, compilation, or package materialization;
- authentication, entitlement, billing, or credential management;
- deployment URLs or service-level objectives.

Those should be added only when they become real maintained consumer commitments.

## Governance

Normative API changes follow [`../docs/standards-governance.md`](../docs/standards-governance.md) and [`compatibility.md`](compatibility.md).

Merging an API change does not by itself create a tagged standards release or imply that a production BCAST service has been deployed.
