# BCAST Standards Governance

This document governs the public BCAST standard: its normative contracts, compatibility commitments, release snapshots, citation metadata, errata, deprecation, and withdrawal.

It does not govern BCAST's private compiler, provider integrations, source acquisition, review operations, production data, or proprietary compiled corpus. Those remain product implementation decisions outside the public standards process.

## Decision authority

BCAST is currently a maintainer-led standard. The repository maintainer is the final decision authority for normative public specification changes after the change is proposed and reviewed in public repository history.

Contributors may propose changes through issues and pull requests. This policy does not create a membership organization, voting body, or standards committee. If a broader governance model becomes useful later, adopting it is itself an explicit governance change.

## Normative change process

A proposed normative change should identify:

1. the affected public contract or rule;
2. whether the change is editorial, compatible normative, or breaking normative;
3. the required contract-version impact under [`../spec/compatibility.md`](../spec/compatibility.md);
4. any migration or interoperability consequence for consumers; and
5. the conformance evidence that demonstrates the proposed meaning at the exact candidate revision.

A pull request may merge only after the repository's required checks pass and the exact candidate is reviewable. Merging a change does not, by itself, publish a standards release.

Existing contract coordinates must not be silently reinterpreted. When public meaning changes in a way that requires a new semantic version, the normative contract and its companion artifacts must move to that new version together.

## Standard status

Each released public contract has one of these statuses:

### Draft / pre-1.0

A contract below `1.0.0` is maintained but not stable. Breaking changes are permitted only when they are explicit, documented, and assigned a new contract version. Existing released coordinates remain immutable historical statements of their published meaning.

### Stable

A contract at `1.0.0` or later is stable and carries the compatibility promises in [`../spec/compatibility.md`](../spec/compatibility.md). A stability claim applies to the public contract, not to private compiler or corpus maturity.

### Deprecated

A deprecated contract remains specified for existing consumers but is no longer recommended for new integrations. Deprecation documentation must name the recommended successor or explain why no successor exists. Removing or incompatibly changing a stable deprecated contract still follows normal breaking-change rules.

### Withdrawn

A withdrawn contract is no longer maintained or recommended. Its released artifacts remain historical evidence and must not be rewritten to give the old coordinate new meaning. Withdrawal must state the reason and any available migration path.

## Editorial corrections, errata, and normative changes

An **editorial correction** changes wording, formatting, links, or examples without changing machine-observable or consumer-relevant meaning. It may be merged without changing a contract version when the existing normative meaning is unambiguous.

An **erratum** records that a released document or companion artifact contains a defect. If correcting the defect does not change the normative meaning already established by the released specification, the correction may be published as errata. The released snapshot itself remains immutable.

A **normative change** changes what a conforming producer or consumer may rely on. It must follow the compatibility and versioning rules. A companion schema, validator, example, or client cannot independently create new normative meaning; if it conflicts with the human-readable normative specification, the specification wins and the companion artifact must be corrected.

## Contract versions, Git tags, and GitHub releases

Semantic versions identify public contract meaning. Git tags and GitHub releases identify immutable repository snapshots. They are related, but they are not interchangeable.

For the package contract family, a citable release tag should use `bcast-package-v<version>` and the release title should identify the contract as `bcast.package/<version>`. Future contract families should use their own unambiguous tag prefixes.

A tag or GitHub release must not silently redefine compatibility, create a new contract version, or imply compatibility between independently versioned package and API contracts. Those relationships remain explicit in the normative specifications and compatibility documentation.

Once a tag represents a standards release, it must continue to point to the exact reviewed commit. Corrections after release require a new release or an explicit erratum; moving the existing tag is not an acceptable correction mechanism.

## Release gate for a citable standards snapshot

Before publishing a contract tag or GitHub release:

- select the exact commit to release;
- confirm the normative specification carries the intended semantic version and status;
- confirm companion schemas, examples, validators, and other versioned artifacts agree with that contract coordinate;
- run required conformance checks against that exact revision and record successful evidence;
- confirm `CHANGELOG.md` describes the release and its compatibility impact;
- confirm unresolved normative review findings are closed or explicitly documented;
- confirm citation metadata is current and does not claim a DOI, registration, or external standards-body status that BCAST does not have;
- confirm licensing and third-party source-rights boundaries remain accurate; and
- create the tag and release only from the reviewed exact revision.

The release notes should identify the contract family, semantic version, status, exact Git revision, and any compatibility or deprecation notes.

## Citation

`CITATION.cff` provides machine-readable project-level citation metadata. Its presence does not create a standards release or a stability claim.

Before a tagged standards release exists, citations should identify at least:

- BCAST;
- the public contract coordinate, such as `bcast.package/0.1.0`;
- the exact Git commit used; and
- the repository URL.

For a tagged standards release, cite the contract coordinate and immutable release tag in addition to the repository metadata.

BCAST does not currently claim a DOI or registration by an external standards body. If such an identifier is assigned later, citation metadata may record it only after the assignment is authoritative.

## Relationship to private product decisions

Public standards governance controls what BCAST promises to consumers. It does not expose or transfer decision authority over private source providers, compiler architecture, normalization heuristics, review evidence, production operations, or the proprietary compiled corpus.

A private implementation change requires a public standards change only when it changes the consumer-facing meaning or behavior promised by a public BCAST contract.
