# BCAST Public Surface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish `laurajoyhutchins/bcast` as a credible future public technical surface for BCAST without exposing the private compiler, provider integrations, or compounding regulatory corpus.

**Architecture:** The repository is an interface boundary around a private regulatory compilation product. The first milestone publishes product identity, public/private boundaries, source-rights policy, contribution/security rules, compatibility and identifier contracts, and publication gates. It deliberately does not publish provider adapters, production schemas, corpus data, package materialization logic, or a license chosen by inertia.

**Tech Stack:** Markdown documentation, GitHub repository conventions, GitHub pull requests/branch workflow. No runtime dependency or production code is introduced in this milestone.

**Spec:** `docs/superpowers/specs/2026-08-24-public-surface-design.md`

## Global Constraints

- Open protocol. Open clients. Open validation. Closed compilation. Proprietary compiled corpus.
- The repository remains private until a deliberate license is selected and the publication gate passes.
- Do not copy `building-code-ast-alpha` wholesale or import its Git history.
- Do not add production provider adapters, licensed/restricted source text, normalized provider datasets, production mappings, reviewed corpus data, cross-publisher graphs, cross-edition correspondence, private review evidence, or compilation heuristics.
- Do not create empty directories merely to advertise future features.
- Public contracts must be provider-neutral and consumer-facing.
- Pre-1.0 public contracts are explicitly unstable.
- Public examples must be synthetic or clearly redistributable.

---

### Task 1: Establish the public product identity and boundary

**Files:**
- Create: `README.md`
- Create: `docs/product-boundary.md`
- Create: `docs/architecture.md`
- Create: `docs/roadmap.md`

**Interfaces:**
- Consumes: approved public-surface design spec.
- Produces: the canonical public explanation of BCAST, its architecture boundary, and the scope of the public repository.

- [ ] **Step 1: Write `README.md`**

The README must state, in the first screenful, that BCAST provides a provider-neutral representation and interfaces for compiled building-code information. It must explicitly say that this repository is the public technical surface, not the production compiler or corpus. Include a compact flow:

```text
source providers -> private BCAST compilation -> public BCAST contracts -> downstream tools
```

Include sections: `What BCAST is`, `What this repository contains`, `What this repository does not contain`, `Status`, and `Repository map`. Mark the project pre-1.0 and the repo private until publication criteria are satisfied.

- [ ] **Step 2: Write `docs/product-boundary.md`**

Define the durable split:

```text
PUBLIC: protocol, schemas, API contracts, client SDKs, conformance validators, synthetic examples
PRIVATE: provider adapters, source entitlements, normalization, reviewed corpus, semantic graph construction, package materialization
```

State that provider IDs and provider object models are evidence/inputs, never canonical BCAST identity.

- [ ] **Step 3: Write `docs/architecture.md`**

Document only the public-facing architecture. The diagram must terminate the private side at a single `BCAST compilation service` boundary and describe downstream public package/API/client contracts without revealing internal compilation stages beyond the conceptual categories already approved in the spec.

- [ ] **Step 4: Write `docs/roadmap.md`**

Define three public milestones only:

1. `M0 — Public surface foundation`: identity, boundaries, policies, compatibility rules.
2. `M1 — First package contract`: minimal provider-neutral schema plus synthetic examples and deterministic conformance validation.
3. `M2 — Consumer API`: read-oriented OpenAPI contract and thin SDK generation.

Explicitly exclude production provider ingestion and corpus expansion from the public roadmap.

- [ ] **Step 5: Verify Task 1**

Check that no Task 1 file claims the repository contains the BCAST compiler, promises redistributable publisher content, or describes alpha as an active upstream. Confirm every mention of Code Connect/NFPA LiNK, if any, is illustrative rather than an implementation commitment.

- [ ] **Step 6: Commit Task 1**

Commit message:

```text
Define BCAST public product surface
```

---

### Task 2: Establish source-rights, security, and contribution guardrails

**Files:**
- Create: `docs/source-and-rights.md`
- Create: `SECURITY.md`
- Create: `CONTRIBUTING.md`
- Create: `CODE_OF_CONDUCT.md`

**Interfaces:**
- Consumes: product boundary from Task 1.
- Produces: enforceable human-facing rules for what may enter the future public repository.

- [ ] **Step 1: Write `docs/source-and-rights.md`**

State these rules explicitly:

- BCAST does not grant rights to publisher or standards content.
- Restricted/licensed source content is never accepted through the public repository.
- Source-derived examples must be synthetic, public-domain, or accompanied by clearly documented redistribution rights.
- Provider credentials, entitlements, account-specific locators, and private API responses are prohibited.
- Hashes, public identifiers, and source-safe provenance may be published only when they do not reconstruct protected content or disclose private access patterns.
- The public project-authored license, when selected, applies only to material BCAST has the right to license.

- [ ] **Step 2: Write `SECURITY.md`**

Define private reporting for credentials, source-content leaks, provider-access leakage, and vulnerabilities in public clients/conformance tooling. State that issues/PRs must not be used to disclose credentials or restricted source material.

- [ ] **Step 3: Write `CONTRIBUTING.md`**

Accept contributions for documentation, schemas, SDKs, conformance tools, synthetic/public-domain fixtures, and interoperability proposals. Reject bulk publisher content, production mappings, credentials, private review data, and unreviewed regulatory interpretations presented as authoritative BCAST output.

Include a contributor preflight checklist requiring confirmation that submitted examples are redistributable and contain no secrets/private provider data.

- [ ] **Step 4: Write `CODE_OF_CONDUCT.md`**

Use the Contributor Covenant 2.1 text only if licensing/attribution requirements are satisfied; otherwise write a concise project conduct policy without importing incompatible text. The policy must define professional technical collaboration and reporting expectations without adding product-specific legal claims.

- [ ] **Step 5: Verify Task 2**

Cross-check the four files against the `Private` section of the design spec. Every prohibited asset class in the spec must be represented either directly or by a broader rule that unambiguously covers it.

- [ ] **Step 6: Commit Task 2**

Commit message:

```text
Add BCAST public contribution and rights guardrails
```

---

### Task 3: Define pre-1.0 public contract rules without freezing a schema

**Files:**
- Create: `spec/README.md`
- Create: `spec/compatibility.md`
- Create: `spec/identifiers.md`
- Create: `CHANGELOG.md`

**Interfaces:**
- Consumes: public architecture and product boundary from Task 1.
- Produces: stable rules for how future schemas/APIs will evolve while avoiding premature schema commitments.

- [ ] **Step 1: Write `spec/README.md`**

Explain that `spec/` contains consumer-facing contracts only. State that schema and OpenAPI directories will be created only when the first maintained artifact exists. Explicitly exclude ingestion, review, normalization, and package-build contracts.

- [ ] **Step 2: Write `spec/compatibility.md`**

Define:

- Versions before `1.0.0` may contain breaking changes.
- Every published contract carries an explicit semantic version.
- Breaking changes require a major version once `1.0.0` is reached.
- Additive optional fields are non-breaking only when existing consumers can safely ignore them.
- Removing or reinterpreting a field is breaking.
- Provider-specific changes should not force downstream breaking changes unless the public BCAST meaning itself changes.
- Package/API version compatibility must be stated explicitly rather than inferred from repository tags.

Do not promise a release cadence.

- [ ] **Step 3: Write `spec/identifiers.md`**

Define principles, not a final wire format:

- canonical BCAST identity is provider-neutral;
- identity distinguishes publication family, edition/revision, and regulatory object;
- provider IDs are aliases/provenance, not canonical IDs;
- identifiers remain stable across re-ingestion when the represented regulatory object is unchanged;
- cross-edition correspondence is a relationship between distinct identities, not identity reuse;
- jurisdictional amendments and materialized results must not silently overwrite base-publication identity.

Mark concrete identifier syntax as not yet public until M1.

- [ ] **Step 4: Write `CHANGELOG.md`**

Start with `Unreleased` and record the public-surface foundation. State that no public package or API contract has yet been released.

- [ ] **Step 5: Verify Task 3**

Ensure no JSON schema, OpenAPI file, package payload, or provider-specific identifier syntax has been introduced. Confirm the compatibility rules are internally consistent with pre-1.0 status.

- [ ] **Step 6: Commit Task 3**

Commit message:

```text
Define BCAST public compatibility rules
```

---

### Task 4: Add repository workflow guardrails and publication checklist

**Files:**
- Create: `.github/PULL_REQUEST_TEMPLATE.md`
- Create: `.github/ISSUE_TEMPLATE/config.yml`
- Create: `docs/publication-checklist.md`

**Interfaces:**
- Consumes: rights/contribution rules from Task 2 and compatibility rules from Task 3.
- Produces: repeatable review prompts that reduce accidental leakage before the repository becomes public.

- [ ] **Step 1: Write `.github/PULL_REQUEST_TEMPLATE.md`**

Require PR authors to check:

```text
[ ] No restricted/licensed source content is included.
[ ] No credentials, entitlements, private provider responses, or account-specific locators are included.
[ ] No production corpus, provider mapping, private review evidence, or compilation logic is included.
[ ] Examples are synthetic or have documented redistribution rights.
[ ] Public contract changes include compatibility impact.
```

Also require a short `Public contract impact` field with values `none`, `additive`, or `breaking`.

- [ ] **Step 2: Write `.github/ISSUE_TEMPLATE/config.yml`**

Keep blank issues enabled while adding a contact link or instruction directing security/source-rights disclosures to `SECURITY.md`. Do not create issue forms that solicit copyrighted source excerpts.

- [ ] **Step 3: Write `docs/publication-checklist.md`**

Mirror the publication gate from the design spec as an executable checklist. Include repository-history review, secrets/provider-locator review, restricted-source review, corpus/mapping/review-data review, README/description accuracy, source-rights policy, contribution policy, deliberate license choice plus `LICENSE`, synthetic/redistributable examples, stable public-schema review, and final visibility change.

The final item must be:

```text
[ ] Repository visibility may be changed to public only after every preceding item is complete.
```

- [ ] **Step 4: Verify Task 4**

Confirm the PR template blocks all asset classes excluded by the design spec and that publication remains explicitly gated on a future license decision.

- [ ] **Step 5: Commit Task 4**

Commit message:

```text
Add BCAST public repository guardrails
```

---

### Task 5: Final repository review

**Files:**
- Review all tracked files.
- Do not create `LICENSE`, `spec/schemas/`, `spec/openapi/`, `examples/`, `sdk/`, or `conformance/` unless a real maintained artifact now exists.

**Interfaces:**
- Consumes: all prior tasks.
- Produces: a private-but-publication-oriented repository whose initial history contains no product-corpus leakage.

- [ ] **Step 1: Review the complete tree**

Verify that every file is appropriate for a future public repository and that no content was copied wholesale from `building-code-ast-alpha`.

- [ ] **Step 2: Review product claims**

Check that BCAST is described as a provider-neutral regulatory compilation product and public technical interface, not as an authoritative publisher, legal authority, or open-source compiler.

- [ ] **Step 3: Review publication state**

Confirm the repository remains private, unarchived, and without a license until the licensing decision is made.

- [ ] **Step 4: Review repository metadata**

If the available GitHub integration supports repository metadata mutation, set the description to:

```text
Public contracts, clients, and conformance tools for BCAST's provider-neutral building-code compilation platform.
```

Do not change visibility to public in this plan.

- [ ] **Step 5: Record completion**

Update `CHANGELOG.md` under `Unreleased` only if implementation materially differs from the planned foundation. Otherwise leave the Task 3 entry as the release record.

- [ ] **Step 6: Commit final review fixes if any**

Use a narrowly descriptive commit message based on the actual corrections. Do not create an empty commit.
