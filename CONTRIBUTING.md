# Contributing to BCAST

BCAST's public repository exists to improve interoperability around its public contracts. Contributions should strengthen that surface without importing the private compiler or regulatory corpus into GitHub.

## Appropriate contributions

Contributions may include:

- documentation fixes and clarifications;
- public schema and API-contract improvements;
- thin client SDK improvements;
- deterministic conformance tooling;
- synthetic or clearly redistributable fixtures;
- interoperability proposals;
- bug reports against published public contracts.

## Out of scope

Do not submit:

- licensed or restricted building-code or standards content;
- bulk publisher-derived data;
- provider credentials, tokens, entitlements, private responses, or account-specific locators;
- production provider adapters or provider-to-BCAST mappings;
- production normalized datasets or reviewed corpus records;
- private review evidence, acceptance decisions, or reviewer annotations;
- production normalization or graph-compilation logic;
- unreviewed regulatory interpretations presented as authoritative BCAST output.

See [`docs/source-and-rights.md`](docs/source-and-rights.md) for the source and redistribution policy.

## Contributor preflight

Before opening a pull request, confirm all of the following:

- [ ] I have the right to publish every example, fixture, and excerpt in this change.
- [ ] The change contains no credentials, entitlements, private provider data, or account-specific access information.
- [ ] The change contains no production corpus, production provider mapping, private review evidence, or private compiler logic.
- [ ] Any example is synthetic, public-domain, or accompanied by clear redistribution permission.
- [ ] I have identified whether the change affects a public contract.
- [ ] If a public contract changes, I have described the compatibility impact.

When source rights are uncertain, omit the material and describe the interoperability problem without reproducing the source.

## Licensing of contributions

Unless explicitly stated otherwise, contributions intentionally submitted for inclusion in BCAST are submitted under the Apache License, Version 2.0, consistent with Section 5 of that license.

Contributors must have the authority to grant the rights required for their contributions. Do not submit third-party material merely because you can access it or because BCAST interoperates with it. The source and redistribution requirements in [`docs/source-and-rights.md`](docs/source-and-rights.md) continue to apply.

## Public contract changes

Public contract proposals should describe consumer meaning rather than private implementation. Provider-specific object shapes should not become canonical BCAST structures merely because they are convenient upstream representations.

Before 1.0, breaking changes are possible, but they should still be explicit and documented. After 1.0, compatibility follows the repository's published compatibility policy.

## Review standard

Changes are reviewed for technical correctness, interoperability value, source rights, product-boundary compliance, and compatibility impact. A useful feature may still be rejected from this repository if it belongs in the private compilation product instead.
