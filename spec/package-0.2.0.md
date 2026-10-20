# BCAST Package Contract 0.2.0

Status: pre-1.0 draft; breaking successor to `bcast.package/0.1.0`.

This document is normative. Its versioned JSON Schema, validators, and examples are companions. The meaning of the 0.1.0 coordinate is preserved. Version 0.2.0 is an immutable, provider-neutral representation of a publication state and never exposes provider credentials, licensed source acquisition machinery, proprietary compilation logic, or private review evidence.

## Fields

The package contains exactly `schema_version`, `package_id`, `package_version`, `publication`, and `objects`. The schema version is exactly `bcast.package/0.2.0`. `package_version` is a human BCAST release coordinate, distinct from issuer edition.

`publication` requires `publication_id`, `namespace`, `family`, `edition`, with optional `revision`, `title`, and `issuing_body`.

Each object requires `object_id`, `kind`, `locator`, `status`, and can have `parent_id`, `label`, `content`, and `provenance`. The companion schema defines enum values and structural shapes. Objects are a flat collection; the array order carries no semantic meaning.

## Collision-resistant publication identity

`namespace` MUST be a lowercase ASCII DNS name with at least two labels, controlled by the issuing organization or a delegated publication-namespace steward. The steward MUST assign unique `family` slugs to unrelated publication families and MUST NOT reuse an existing family coordinate for a different publication. A producer MUST NOT claim control over an unrelated issuer's domain. This organizational authority cannot be mechanically proven by JSON Schema; hash equality alone is not proof of a lawful namespace claim.

The canonical `family` is a lowercase ASCII slug of letters, digits, and single separator hyphens. The `edition` and optional `revision` are case-sensitive, nonempty NFC Unicode strings without leading or trailing whitespace. Producers MUST provide canonical values. Implementations MUST reject noncanonical inputs, not silently normalize them into a different identity.

The publication digest input consists of exactly `namespace`, `family`, `edition`, and optionally `revision`. For example:

```json
{"namespace":"codes.example","family":"example-safety-code","edition":"2026"}
```

`publication_id` equals `"bcastpub:sha256:" + sha256(canonical_json(input))`.

The namespace identifies the authoritative publication-family steward, **not** the service providing source access. Acquisition provider IDs, URLs, API objects, paths, cookies, entitlements, and account coordinates MUST NOT be canonical publication identity inputs. The same publication acquired through two lawful providers retains one publication ID. An authority/domain handover does not permit silently reassigning a prior canonical namespace to unrelated content; changes must be explicitly represented as successor publication identities.

## Regulatory object identity and structure

An object's identity input consists of exactly `publication_id`, `kind`, and the publication-local `locator`:

```json
{"publication_id":"<canonical-publication-id>","kind":"section","locator":"1.1"}
```

`object_id` equals `"bcastobj:sha256:" + sha256(canonical_json(input))`. Content text, presentation labels, structural parentage and provider representations are not identity inputs. Each package MUST have unique object IDs and unique `(kind, locator)` coordinates. All parent IDs MUST resolve in the package, and parentage MUST be acyclic. Parentage and public representation changes invalidate package identity, not object identity.

## Exact package materialization identity

`package_id` is a SHA-256 digest of the entire canonical public package materialization. To calculate it:

1. Copy the entire package and omit only its top-level `package_id` property (avoiding hash self-reference).
2. Sort the `objects` array by `object_id` ascending. Do not alter any other array order, metadata, text, parentage, provenance or status.
3. Encode canonical JSON using sorted object keys, UTF-8, no insignificant whitespace, no ASCII-only escape substitution and no non-JSON numeric values. Fields in 0.2.0 do not permit floating-point numbers.
4. Prefix SHA-256 of those UTF-8 bytes with `bcastpkg:sha256:`.

The array-order normalization avoids a meaningless identity change from object enumeration order alone. **Any other difference in public package content, structure, provenance, publication metadata, or package version MUST change the package ID.** Two materially different packages MUST NOT share an exact-materialization identity. A consumer must fetch the full package to recompute the digest; metadata by itself cannot verify the package's contents.

## Status, provenance and claims

`status` has values `resolved`, `unresolved` and `unsupported`, denoting representation availability only, not correctness or applicability.

Version 0.2.0 **removes the 0.1.0 `assurance` scalar** because `unreviewed`, `reviewed` and `verified` could imply professional or regulatory certification without a defined evidentiary subject, responsible actor, validation method or invalidation rule. A producer MUST NOT include `assurance` in 0.2.0. Neither status nor schema conformance implies checked source correspondence, legal authority, regulatory interpretation, engineering approval or source completeness.

Optional `provenance` identifies a public citation and optionally an exact source-artifact SHA-256. A citation or source hash records evidence identity but does not claim the public content was compared with the source. Any future public assurance claim requires a newly versioned, narrowly scoped contract defining the claim, actor, minimum evidence, invalidation conditions and limitations. Until then, verification and regulatory approval belong to separate accountable workflows rather than a misleading field.

## Rights and exclusions

Plain-text `content` carries only the rights actually granted by the lawful source, never rights implied by this contract. Public fixtures must be synthetic or redistributable. The package does not standardize provider APIs, ingestion, retention, licensed corpora, amendment graphs, semantic links, cross-edition correspondence, private review machinery, or an IANA-registered BCAST media type.
