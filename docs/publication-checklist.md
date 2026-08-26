# Publication Checklist

BCAST must remain private until every incomplete item below is complete.

Evidence for completed publication-safety checks is recorded in [`publication-audit-2026-08-25.md`](publication-audit-2026-08-25.md). Completed items reflect the repository state audited through `45abcaadfa1d354e40aee5155fce73035fe58569`; checks that are inherently time-sensitive remain open until immediately before the visibility change.

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

- [ ] The licensing model for public BCAST artifacts has been selected deliberately.
- [ ] A corresponding `LICENSE` file is present.
- [ ] The license text and surrounding documentation make clear that BCAST does not sublicense third-party publisher or standards content beyond rights actually held.

## Compatibility and release readiness

- [x] Every machine-consumed public contract currently present has an explicit version.
- [x] Compatibility impact of the initial package contract has been reviewed and documented as pre-1.0.
- [x] Pre-1.0 instability is clearly communicated until a `1.0.0` public contract exists.
- [ ] Review tags and releases immediately before publication and confirm none imply package/API compatibility that has not been explicitly documented.

## Final publication review

- [ ] Review repository topics, description, homepage links, issue templates, pull-request template, and security links exactly as they will appear to a public visitor.
- [ ] Re-run secret scanning and source-rights review immediately before the visibility change.
- [x] Confirm the maintained public tree contains no empty scaffolding that implies unsupported contracts or SDKs.
- [x] Confirm the public roadmap contains only consumer-facing work and does not expose the private compilation frontier.
- [ ] Confirm the repository head still descends only from the audited public-safe history and review every post-audit commit.
- [ ] Repository visibility may be changed to public only after every preceding item is complete.