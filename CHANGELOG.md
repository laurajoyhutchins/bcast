# Changelog

All notable changes to BCAST's public technical surface will be documented here.

## Unreleased

### Added

- public product positioning and architecture boundary;
- source-rights, contribution, security, and conduct policies;
- pre-1.0 compatibility and provider-neutral identifier rules;
- publication guardrails and completed public-cutover record;
- `bcast.package/0.1.0`, the first maintained package contract;
- companion JSON Schema for `bcast.package/0.1.0`;
- explicit normative-authority rules: the human-readable standard wins over conflicting companion artifacts;
- project-authored synthetic valid and invalid conformance fixture taxonomy;
- deterministic local conformance validation, including cross-record invariants that JSON Schema alone cannot express;
- explicit migration boundary from `building-code-ast-alpha`;
- publication-safety audit record for repository history and the maintained public tree.

### Changed

- normalized the first unreleased pre-1.0 package coordinate from `0.1` to semantic-version form `0.1.0` before any tagged BCAST release;
- renamed the package specification, schema, and synthetic fixtures to carry the same `0.1.0` identity consistently.

BCAST became public on August 26, 2026. No public service API or tagged BCAST release exists yet; the package contract remains a pre-1.0 draft.