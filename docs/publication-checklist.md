# Publication Checklist

BCAST must remain private until every item below is complete.

## Repository history

- [ ] Review the complete Git history, not only the current tree.
- [ ] Confirm no production credentials, tokens, entitlements, cookies, private provider responses, or account-specific locators have ever been committed.
- [ ] Confirm no licensed or restricted source text, tables, figures, page images, or bulk excerpts have ever been committed.
- [ ] Confirm no private corpus, production provider mapping, private review evidence, reviewer annotations, or proprietary compilation artifacts have ever been committed.
- [ ] Confirm `building-code-ast-alpha` history was not imported wholesale.

## Current tree

- [ ] README and repository description accurately describe BCAST as a provider-neutral compilation product with a public technical interface, not an open-source production compiler.
- [ ] `docs/source-and-rights.md` is present and accurately states redistribution limits.
- [ ] `CONTRIBUTING.md` rejects proprietary-source ingestion and private product assets through public pull requests.
- [ ] `SECURITY.md` provides a private path for credentials, source-content leaks, provider-access leakage, and vulnerabilities.
- [ ] Every example is synthetic, public-domain, or accompanied by clear redistribution rights.
- [ ] Public schemas and API contracts, if present, expose consumer-facing commitments only and do not mirror private compiler state or one provider's object model.
- [ ] No production provider adapter, normalization heuristic, package builder, graph compiler, or private review workflow is present.

## Licensing

- [ ] The licensing model for public BCAST artifacts has been selected deliberately.
- [ ] A corresponding `LICENSE` file is present.
- [ ] The license text and surrounding documentation make clear that BCAST does not sublicense third-party publisher or standards content beyond rights actually held.

## Compatibility and release readiness

- [ ] Every machine-consumed public contract has an explicit version.
- [ ] Compatibility impact of the initial public contracts has been reviewed.
- [ ] Pre-1.0 instability is clearly communicated until a `1.0.0` public contract exists.
- [ ] Repository tags/releases do not imply package/API compatibility that has not been explicitly documented.

## Final publication review

- [ ] Review repository topics, description, homepage links, issue templates, pull-request template, and security links as they will appear to a public visitor.
- [ ] Re-run secret scanning and source-rights review immediately before the visibility change.
- [ ] Confirm the public tree contains no empty scaffolding that implies unsupported contracts or SDKs.
- [ ] Confirm the public roadmap contains only consumer-facing work and does not expose the private compilation frontier.
- [ ] Repository visibility may be changed to public only after every preceding item is complete.
