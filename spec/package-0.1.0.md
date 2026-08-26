# BCAST Package Contract 0.1.0

Status: pre-1.0 draft

`bcast.package/0.1.0` is the first maintained consumer-facing BCAST package contract. It is intentionally smaller than the historical compiler models in `building-code-ast-alpha`.

This document is normative. The companion JSON Schema, validator, examples, generated documentation, and client implementations assist conformance and interoperability but do not supersede this specification. If a companion artifact conflicts with this document or the linked normative identifier and compatibility rules, the normative specification wins.

The contract carries only information a downstream consumer can reasonably depend on:

- package and publication identity;
- provider-neutral regulatory object identity;
- structural parentage;
- object kind and locator;
- explicit resolved, unresolved, or unsupported state;
- public assurance state;
- optional plain-text content delivered under whatever source rights govern that package;
- source-safe provenance.

It does not expose provider API objects, private locators, ingestion state, normalization heuristics, review queues, compiler intermediate representations, or package-build machinery.

## Version

Every package declares:

```json
"schema_version": "bcast.package/0.1.0"
```

The `0.1.0` contract is pre-1.0. Breaking changes may occur according to [`compatibility.md`](compatibility.md), but an existing contract version must not be silently reinterpreted.

## Deterministic identities

BCAST public identities are derived from provider-neutral facts using UTF-8 SHA-256 over canonical JSON.

Canonical JSON means:

- object keys sorted lexicographically;
- no insignificant whitespace;
- UTF-8 encoding;
- JSON strings encoded without ASCII-only escaping.

### Publication identity

Construct the identity input from:

```json
{
  "edition": "<edition>",
  "family": "<publication family>"
}
```

If the public `revision` field is present, include `"revision"` in the identity input.

Then:

```text
publication_id = "bcastpub:sha256:" + sha256(canonical_json(identity_input))
```

Provider identifiers, URLs, artifact paths, and account-specific coordinates are not identity inputs.

### Regulatory object identity

Construct:

```json
{
  "kind": "<object kind>",
  "locator": "<publication-local locator>",
  "publication_id": "<publication_id>"
}
```

Then:

```text
object_id = "bcastobj:sha256:" + sha256(canonical_json(identity_input))
```

Text, labels, source offsets, provider identifiers, and parentage are deliberately excluded. Re-extracting the same represented object from another lawful provider must not change identity solely because the provider representation changed.

### Package identity

Construct:

```json
{
  "package_version": "<package version>",
  "publication_id": "<publication_id>"
}
```

Then:

```text
package_id = "bcastpkg:sha256:" + sha256(canonical_json(identity_input))
```

The package version is a BCAST release coordinate, not a publisher identifier.

## Structure

`objects` is a flat array. Structural containment is represented by `parent_id`.

A conforming package must satisfy all of these normative deterministic checks:

- publication, package, and object IDs recompute exactly;
- object IDs are unique;
- `(kind, locator)` pairs are unique within the publication;
- every `parent_id` names another object in the package;
- an object cannot parent itself;
- structural parentage is acyclic.

The public validator implements these checks. JSON Schema validation alone does not prove these cross-record invariants.

## Content and rights

The schema can carry plain text because authorized BCAST consumers may receive source-derived content under applicable rights. The public repository itself must still contain only synthetic, public-domain, or clearly redistributable examples.

The contract does not grant rights to third-party source material. See [`../docs/source-and-rights.md`](../docs/source-and-rights.md).

## Media type

This contract does not define or claim an IANA-registered BCAST-specific media type. Transport-level media type behavior may be standardized separately if an interoperability need justifies it.

## Deliberate omissions

Version 0.1.0 does not yet standardize:

- semantic relationship arrays;
- amendment operations or materialized amendment graphs;
- cross-edition correspondence;
- provider aliases;
- source geometry;
- private confidence or review evidence;
- compiler intermediate representations.

Those should be added only when they become maintained consumer commitments.