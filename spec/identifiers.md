# Identifier Principles

BCAST identifiers are consumer-facing identities for regulatory objects. They remain independent of any single source provider's storage or API model.

## Provider neutrality

Canonical BCAST identity is provider-neutral.

A provider ID, URL, API object key, PDF coordinate, or source-specific hierarchy identifier may be retained as provenance or an alias. It does not become canonical BCAST identity merely because it is stable upstream.

## Identity dimensions

Canonical identity distinguishes at least:

- publication family;
- edition or revision state;
- the regulatory object represented within that publication state.

The first concrete wire syntax is defined by [`package-0.1.md`](package-0.1.md).

## 0.1 wire syntax

`bcast.package/0.1` uses deterministic SHA-256 identities over canonical JSON:

- `bcastpub:sha256:<digest>` for publication identity;
- `bcastobj:sha256:<digest>` for regulatory-object identity;
- `bcastpkg:sha256:<digest>` for one package version.

The exact canonical inputs are normative in `package-0.1.md`.

Identity inputs exclude provider coordinates, source text, source offsets, labels, and storage paths.

## Stability

Re-ingesting the same represented regulatory object through a different lawful provider or a changed upstream API should not create a new canonical identity solely because the provider representation changed.

## Cross-edition correspondence

A provision in one edition and its successor in another edition are distinct canonical identities. Their relationship may later be represented as cross-edition correspondence, continuity, replacement, split, merge, or another explicit relationship.

Identity must not be silently reused across editions to imply unchanged meaning.

## Amendments and materialization

A jurisdictional amendment must not silently overwrite the identity of the base-publication object it modifies. Base objects, amendment operations, and materialized results need distinguishable identities or provenance sufficient to reconstruct their relationship.

The 0.1 package contract does not yet standardize amendment operations.

## Alias behavior

Provider-native aliases may change without changing canonical BCAST identity. Alias resolution is an interoperability concern, not authority transfer from the provider into the BCAST canonical namespace.
