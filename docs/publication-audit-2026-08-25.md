# BCAST Publication-Safety Audit

Date: 2026-08-25
Audited repository: `laurajoyhutchins/bcast`
Audited main head: `45abcaadfa1d354e40aee5155fce73035fe58569`
Publication decision: **not yet public**

## Conclusion

The repository history through the audited head and the maintained public surface are suitable to carry forward to a future public release without rewriting Git history.

No audited commit introduced production credentials, private provider payloads, licensed or restricted source excerpts, production provider mappings, private review corpus data, compiler internals, or wholesale history from `building-code-ast-alpha`.

The remaining publication blockers are governance and final-time checks, not alpha migration cleanup:

1. select the public-artifact licensing model deliberately and add the corresponding `LICENSE`;
2. perform the final visitor-facing metadata review;
3. re-run secret/source-rights checks at the exact release head;
4. review every commit after this audited head before changing visibility.

## Scope and method

The audit reviewed the complete BCAST commit history reachable from `main` through the audited head, including the initial public-surface design history and PR #1, `Migrate alpha concepts into public-safe BCAST contract`.

The review included:

- commit-by-commit diff inspection across the complete reachable history;
- targeted repository/history searches for common credential and secret indicators;
- review for provider credentials, entitlements, cookies, account-specific locators, and private provider responses;
- review for licensed/restricted code or standards text, tables, figures, page images, and bulk excerpts;
- review for production normalized datasets, provider-to-BCAST mappings, private review data, and proprietary compilation artifacts;
- confirmation that alpha Git history was not imported wholesale;
- review of the maintained package schema, synthetic example, conformance validator, contribution policy, security policy, source-and-rights policy, compatibility rules, and migration boundary.

This is a repository publication-safety audit, not a legal opinion about third-party source rights and not a substitute for the final immediately-before-publication secret scan.

## History findings

### Credentials and private provider access

**Finding: clear.**

No audited commit contained production API keys, tokens, entitlements, cookies, account-specific locators, private provider responses, or similar access material.

### Restricted source material

**Finding: clear.**

No audited commit contained licensed/restricted building-code or standards text, tables, figures, page images, or bulk source excerpts. The maintained example is explicitly project-authored synthetic data.

### Private product data and compiler assets

**Finding: clear.**

No audited commit contained production normalized datasets, production provider mappings, reviewed regulatory corpus data, private reviewer evidence, source-family recovery code, provider acquisition logic, graph compilation services, or package-materialization machinery.

### Alpha history migration

**Finding: clear.**

`building-code-ast-alpha` was not merged, rebased, or imported as repository history. Public concepts were re-specified as new BCAST contracts. The maintained migration boundary is documented in [`migration-from-alpha.md`](migration-from-alpha.md).

## Maintained public-surface findings

The maintained repository correctly states the durable product boundary:

> **Open protocol. Open clients. Open validation. Closed compilation. Proprietary compiled corpus.**

The first maintained package contract, `bcast.package/0.1`, is provider-neutral and consumer-facing. Its public validator checks schema and deterministic cross-record invariants without invoking source acquisition or private compilation machinery.

The current synthetic fixture is project-authored and does not reproduce publisher content.

The contribution, security, and source-rights policies explicitly prevent future pull requests/issues from becoming an accidental intake path for restricted source material or private provider data.

## Current-tree cleanup

The initial `docs/superpowers/` design and implementation-plan files were safe historical planning artifacts, but they are not part of the maintained consumer surface. They are removed from the maintained tree as part of publication readiness. Their historical presence does not require history rewriting because the audited content itself is publication-safe.

## Licensing boundary

No public project license was selected during this audit. That is intentional.

A future license applies only to project-authored BCAST artifacts that BCAST has the right to license. It must not imply that BCAST sublicenses publisher, standards-organization, government, or other third-party source content beyond rights actually held.

The repository remains private until that licensing decision is explicit and the final publication checklist passes.