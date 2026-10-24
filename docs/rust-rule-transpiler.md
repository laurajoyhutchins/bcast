# Native Rust building-code rule compiler (experimental)

The reusable rule compiler and evaluator are **Rust-native**. No Python generator
or Python/Rust semantic duplication remains. BCAST's existing Python package
client is a separate compatibility product; it does not participate in rule
compilation.

**Input:** reviewed `bcast.rule_ir/0.1.0` JSON, including publication identity,
family, edition/revision, exact source object IDs and text hashes, review
references, typed predicates, explicit exceptions, and unsupported provisions.

**Output:** deterministic, standalone Rust implementing the source-independent
three-valued predicate evaluator, source-linked findings and exact-edition
selection. `Satisfied` means a reviewed predicate evaluated true; it is
**not** a legal compliance certification.

## Run

Requires Rust/Cargo with access to the `serde` and `serde_json` dependencies
for the compiler itself. The generated Rust has **no dependencies**.

```sh
cargo test --manifest-path crates/bcast-rules/Cargo.toml
cargo run --manifest-path crates/bcast-rules/Cargo.toml -- \
  examples/synthetic/reviewed-rules.json /tmp/code_rules.rs
rustc --edition=2021 --crate-type=lib /tmp/code_rules.rs -o /tmp/libcode_rules.rlib
```

The synthetic fixture includes two fictional code families and three editions.
The original Rust execution tests are retained as conformance tests and are
compiled and run by the Rust crate's integration tests. The compiler also
rejects unknown fields, missing review, duplicate edition identities,
duplicate/contradictory source classifications, invalid operand typing,
malformed decimals and unsupported expression forms.

## Architecture and authority

```text
lawfully acquired PDFs / publisher sources
                |
           Docling/adapter
                |
        BCAST 0.2 package
                |
        source-fidelity review
                |
      bcast.rule_ir/0.1.0 JSON
                |
    Rust IR parse + validation
                |
       Rust code generation
                |
        standalone Rust rules
                |
      BCM: adopted code selection
      Arcata: verified project facts
```

The compiler is edition- and code-family-neutral: it never infers a specific
code's rules or selects the latest edition. It requires an exact edition and
revision. Unsupported source provisions are explicit; missing facts and
duplicate facts fail closed. It uses bounded fixed-point numbers and explicit
unit tokens with no implicit unit conversion. A unit string being syntactically
valid does not prove UCUM dimensional compatibility.

The boundary remains **reviewed IR → Rust**, not PDF → trustworthy rules.
Neither the public fixture's illustrative SHA strings nor a review reference
prove that the source text or BCAST package was independently verified.
Those checks, rights restrictions, correspondence review, source archive,
cross-reference resolution and amendment composition belong to the upstream
controlled evidence workflow. The public repository must not contain licensed
model-code content. W3C PROV can describe the separate extraction, review,
and generation activities; it is not inferred from a string field.

BCAST owns the reusable compiler. BCM owns jurisdictional adoption and
project applicability. Arcata consumes predicates and separately verified
engineering facts. No duplicate canonical rule compiler should be introduced
in these consumers.

## Bounded source passages and SBVR-inspired semantic admission

The optional `bcast.sbvr_proposal_batch/0.1.0` input is validated against the
[JSON Schema](../spec/schemas/sbvr-proposal-batch-0.1.0.schema.json) and by
`bcast_rules::compile_combined` in the **same Rust crate**. It contains a
validated `bcast.rule_ir/0.1.0` baseline, one exact identified source edition,
bounded extracted passages, classified proposal records and a complete
accounting summary.

- Every passage has an exact whole-PDF SHA-256 anchor, 1-based PDF page, a
  four-coordinate bounded rectangle in thousandths of a PDF point, section
  locator, BCAST publication/object identities and the SHA-256 of its exact
  UTF-8 extracted text. The digest is verified from supplied bytes; the whole
  PDF hash can be verified only by the private extractor with actual PDF bytes.
- Passage identity is `bcastpassage:sha256:<hex>`, hashing canonical sorted-key
  JSON of `artifact_sha256`, `source_object_id`, `pdf_page`,
  `bbox_millipoints` and `text_sha256`. A tampered locator, page,
  rectangle or text cannot pass Rust admission unchanged.
- Every extracted passage must be classified by at least one unique proposal.
  No orphan or duplicate IDs, no missing classifications and no mismatched
  `admitted/unresolved/rejected` accounting are accepted. An admitted
  predicate must carry a review record and zero unresolved dependencies.
- `obligation` evaluates a required predicate, `prohibition` evaluates a
  forbidden predicate, and `permission` reports `Permitted` or
  `PermissionNotEstablished`, **never treating absent permission as a
  violation**. Conditions and exceptions are three-valued. Unresolved or
  rejected proposals produce no predicates.
- A batch is compiled using `bcast-rust batch.json combined.rs` just as the
  original rule IR was compiled. `evaluate_combined` returns existing
  baseline findings plus newly admitted findings in the **same generated Rust
  compilation unit**. Source excerpts are not emitted into the generated code.

The proposal format uses OMG SBVR-style notions (modality, proposition,
condition, exception and unresolved meaning) as a design reference. It does
**not** assert full OMG SBVR conformance, XMI interoperability or legal
interpretive authority. It is intentionally a bounded contract, not a second
rules engine. `review_ref` is a required asserted record, **not** verified
review authorization; private admission policy still determines which
reviewers may approve source-derived interpretations.

Never commit protected extracted text, PDF bytes, or raw proposal batches
containing code passages to public Git. Private source operations must verify
the PDF digest, bounding boxes and correspondence and retain private evidence.

## Pinned package membership (required)

An SBVR proposal batch now **must** contain `source_package`, an exact
`bcast.package/0.2.0` materialization for the selected edition, as well as
`baseline`, `source`, `passages`, `proposals` and `accounting`.
The Rust compiler independently recomputes the package SHA-256 using
canonical JSON with sorted object IDs and no `package_id` key. It validates
source publication identity, each object's canonical coordinate ID,
provenance PDF digest, unique object IDs, parent references and member
coordinates. Every extracted passage must be present in that exact pinned
materialization. The package ID must also match the selected baseline's
package ID. Identity or membership mismatch blocks generation.

This is a **cryptographically bound metadata membership witness**, not
independent extraction fidelity or semantic review. The source package may
contain provenance-only `unresolved` records without copyrighted source
text. Such records cannot claim that code text or legal meaning is resolved.
The private source adapter checks exact owner-supplied PDF bytes and
regenerates the source package with public BCAST's canonical package builder.

## Source-scoped evidence assessment (no compliance status)

Use the generated `evaluate_evidence(namespace, family, edition, revision, facts)`
for project review. It returns an `EvidenceReport` with source publication
and package identities, the exact PDF digest, selected passages, admitted and
unresolved proposal counts, source-linked predicate findings, and an
`open_questions` array carrying unanswered semantic dependencies.
`predicate_violations` and `predicates_with_missing_facts` are reported
even when interpretation coverage is incomplete.

`EvidenceStatus` has only `IncompleteCoverage`,
`PredicateViolationObserved`, and `PredicateEvidenceOnly`.
There is **no** `Compliant` value and no implicit provision-completeness
claim. If any proposal remains unresolved/rejected, a selected package object
was not covered by a passage, or a predicate has missing facts, status is
`IncompleteCoverage` even if one or more predicates evaluate
`Satisfied`. A violation count remains visible in the same report.

The legacy `evaluate` and `evaluate_combined` return raw predicate details
for computational consumers. They are not compliance APIs. Consumers should
not collapse `Vec<Finding>` into a single pass/fail state. Normative,
edition-wide completeness and authenticated reviewer approval are separate
upstream gates and are not inferred from the absence of open questions.
