# Identifier Principles

BCAST identifiers are consumer-facing identities for regulatory objects. They must remain independent of any single source provider's storage or API model.

## Provider neutrality

Canonical BCAST identity is provider-neutral.

A provider ID, URL, API object key, PDF coordinate, or source-specific hierarchy identifier may be retained as provenance or an alias. It does not become canonical BCAST identity merely because it is stable upstream.

## Identity dimensions

Canonical identity must distinguish at least:

- publication family;
- edition or revision state;
- the regulatory object represented within that publication state.

The concrete wire syntax is not yet public and will be specified with the first package contract.

## Stability

Re-ingesting the same represented regulatory object through a different lawful provider or a changed upstream API should not create a new canonical identity solely because the provider representation changed.

## Cross-edition correspondence

A provision in one edition and its successor in another edition are distinct canonical identities. Their relationship may be represented as cross-edition correspondence, continuity, replacement, split, merge, or another explicit relationship.

Identity must not be silently reused across editions to imply unchanged meaning.

## Amendments and materialization

A jurisdictional amendment must not silently overwrite the identity of the base-publication object it modifies. Base objects, amendment operations, and materialized results need distinguishable identities or provenance sufficient to reconstruct their relationship.

## Alias behavior

Provider-native aliases may change without changing canonical BCAST identity. Alias resolution is an interoperability concern, not authority transfer from the provider into the BCAST canonical namespace.