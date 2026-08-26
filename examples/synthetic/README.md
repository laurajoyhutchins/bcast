# Synthetic conformance fixtures

All files under this directory are project-authored synthetic BCAST fixtures. They contain no publisher or standards text and are distributed under the repository's Apache-2.0 license.

The fixture taxonomy is normative only as a conformance test convention, not as an additional source of package semantics:

- `valid/` contains examples that must satisfy the named BCAST contract and deterministic conformance rules.
- `invalid/` contains deliberately nonconforming examples that must fail at least the invariant identified by the filename or test.

The human-readable specification remains authoritative if a fixture or companion validator disagrees with it.

Compatibility fixtures may be added when BCAST has more than one maintained package-contract version.