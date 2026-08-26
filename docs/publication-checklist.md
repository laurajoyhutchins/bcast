# Publication Checklist

BCAST became public on August 26, 2026. This file records the publication gates and cutover evidence.

Evidence for the original publication-safety audit is recorded in [`publication-audit-2026-08-25.md`](publication-audit-2026-08-25.md). That audit covers repository history through `45abcaadfa1d354e40aee5155fce73035fe58569`. The licensing and final pre-publication review were merged to `main` as `7251e82a4faf9bbecc504645fc2b01a4cd3f6a48`, whose tree exactly matched the reviewed publication candidate.

## Repository history

- [x] Review the complete Git history, not only the current tree.
- [x] Confirm no production credentials, tokens, entitlements, cookies, private provider responses, or account-specific locators have ever been committed.
- [x] Confirm no licensed or restricted source text, tables, figures, page images, or bulk excerpts have ever been committed.
- [x] Confirm no private corpus, production provider mapping, private review evidence, reviewer annotations, or proprietary compilation artifacts have ever been committed.
- [x] Confirm `building-code-ast-alpha` history was not imported wholesale.

## Current tree

- [x] README accurately describes BCAST as a provider-neutral compilation product with a public technical interface, not an open-source production compiler.
- [x] `docs/source-and-rights.md` is present and accurately states redistribution limits.
- [x] `CONTRIBUTING.md` rejects proprietary-source ingestion and private product assets through public pull requests.
- [x] `SECURITY.md` provides a private path for credentials, source-content leaks, provider-access leakage, and vulnerabilities.
- [x] Every maintained example is synthetic, public-domain, or accompanied by clear redistribution rights.
- [x] Public schemas and API contracts, if present, expose consumer-facing commitments only and do not mirror private compiler state or one provider's object model.
- [x] No production provider adapter, normalization heuristic, package builder, graph compiler, or private review workflow is present.
- [x] Current maintained documentation is public-facing; internal implementation-plan artifacts have been removed from the maintained tree.

## Licensing

- [x] The licensing model for public BCAST artifacts has been selected deliberately: Apache License 2.0 for BCAST-authored repository material.
- [x] A corresponding root `LICENSE` file is present with the official Apache License 2.0 text.
- [x] The license text and surrounding documentation make clear that BCAST does not sublicense third-party publisher or standards content beyond rights actually held.

## Compatibility and release readiness

- [x] Every machine-consumed public contract currently present has an explicit version.
- [x] Compatibility impact of the initial package contract has been reviewed and documented as pre-1.0.
- [x] Pre-1.0 instability is clearly communicated until a `1.0.0` public contract exists.
- [x] Tags and releases were reviewed immediately before publication: none were present, so none implied undocumented package or API compatibility.

## Final publication review

- [x] Repository topics, description, homepage links, issue templates, pull-request template, and security links were reviewed as a public visitor would see them. Description, homepage, and topics were intentionally empty rather than misleading; issue reporting and pull-request guidance enforce the public/private boundary and route sensitive disclosures to `SECURITY.md`.
- [x] A fresh credential-pattern scan and source-rights review were run immediately before publication. No credential-shaped hits were found in the maintained default-branch content; the exact licensing-candidate diff and tree were reviewed for restricted source material, private provider data, private compiler/corpus assets, and production mappings, with no such material found.
- [x] Confirm the maintained public tree contains no empty scaffolding that implies unsupported contracts or SDKs.
- [x] Confirm the public roadmap contains only consumer-facing work and does not expose the private compilation frontier.
- [x] Confirm the repository head descends only from the audited public-safe history and review every post-audit commit.
- [x] Confirm the final merged tree matches the reviewed publication candidate and change repository visibility to public.

## Post-publication controls

- [x] GitHub reports repository visibility as `public`.
- [x] Overcenter installed and verified `branch-policy-v1` with squash-only merges, automatic merged-branch deletion, and required `conformance` checks.
- [x] The `conformance` workflow was re-run after publication on a real GitHub-hosted runner and completed successfully.
