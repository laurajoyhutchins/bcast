# Reviewed regulatory rules to Rust (experimental 0.1)

This compiler is a *source-independent lowering stage*, not an automatic legal-text
interpreter. It is usable with different model codes and editions because their
publication identity and source locators are data, not branch logic in the
compiler. It emits standalone, dependency-free Rust source.

```text
lawfully supplied publication -> Docling/source adapter -> BCAST 0.2 package
                     |                                     |
              exact source text                      section identity
                     +----------------+--------------------+
                                      |
                         interpretation + review
                                      |
                         bcast.rule_ir/0.1.0 JSON
                                      |
                              bcast-rust CLI
                                      |
                    typed Rust rule evaluator + source refs
                                      |
                          BCM selects adopted edition
                                      |
                   Arcata/project data supplies typed facts
```

The upstream review is **not optional**. A provision may use legal terms,
cross-references, tables, footnotes, exceptions, amendments, occupancy/permit
scope, discretionary review, or external technical standards. These must never
be silently translated into true or false by a language model or a regex. A
reviewer must record the intended semantic rule and its source identity. When
that cannot be done, emit an `unsupported` object rather than a guessed rule.

## Run

Install the public BCAST package, then:

```sh
bcast-rust examples/synthetic/reviewed-rules.json /tmp/code_rules.rs
rustc --edition=2021 --crate-type=lib /tmp/code_rules.rs -o /tmp/libcode_rules.rlib
```

The fixture contains fictional rules from **two code families and three
editions**, not actual provisions of any published model code. Its synthetic
source identifiers and hashes are illustrative, not verified hashes of a real
BCAST package. Tests also exercise emitted Rust through `rustc --test`.

The emitted library exports `EDITIONS`, `Fact`, `Value`, `Decision`, `Finding`,
and `evaluate(namespace, family, edition, revision, facts)`.
`evaluate` returns `None` when the exact requested edition/revision is absent.
A known edition returns findings only for the rules and explicitly unsupported
source objects admitted in that edition's IR. It **never** means that the full
publication has been translated, nor that every applicable requirement has
been found. A `Satisfied` finding means only that its *reviewed computational
predicate* was satisfied by supplied facts, not legal compliance.

## Input contract: `bcast.rule_ir/0.1.0`

The input contains `schema_version` and a nonempty `editions` array. Each
edition contains a `publication` with `namespace`, `family`, `edition`, and
`publication_id` (optional exact `revision`), a `package_id`, and two arrays:
`rules` and `unsupported`. The edition coordinate is exact and must be unique;
no automatic newer-edition fallback or application of amendments is allowed.
Each rule has a unique `id`, a `source` (`object_id`, `locator`, `text_sha256`),
a `review` (`reviewer`, `review_ref`) and a `must` expression. Optional `when`
and `unless` expressions represent scope and exceptions. Every unsupported
source has the same source identity and an explanatory `reason`.

Expressions are nested `{ "all": [expr, ...] }`, `{ "any": [expr, ...] }`,
`{ "not": expr }`, or a typed comparison:

```json
{
  "fact": "egress.clear_width",
  "op": "ge",
  "value": {"quantity": {"decimal": "36.0", "unit": "[in_i]"}}
}
```

Other operands are `{"text":"assembly"}` and `{"bool":true}`. Valid
operators are `eq`, `ne`, `lt`, `le`, `gt`, `ge`; text and boolean operands
allow only `eq` and `ne`. All quantities are **exact decimal representations**
with an explicit unit token, not `f64`. The compiler preserves the supplied
UCUM-style unit literal and deliberately performs **no implicit conversion**.
Unit-token syntax checking does *not* establish UCUM semantic validity or
dimensional compatibility. Consumers must obtain canonical typed facts through
a separately verified normalization layer; mismatched units yield
`InsufficientFacts`, not a false violation.

## Evaluation and evidence boundaries

- Missing, mistyped or duplicated facts yield `InsufficientFacts`; they never
  become a pass. Overflow in fixed-decimal comparison also yields unknown.
- Applicability false produces `NotApplicable`; an established exception
  produces `Excepted`; missing exception information yields `InsufficientFacts`.
- A false requirement under established applicability and no exception
  produces `Violated`. A true one produces `Satisfied`.
- Unsupported provisions retain their source identifiers and reason with
  `Unsupported`. Text is **not** copied into emitted Rust.
- The public compiler validates the *shape* of publication/package/object IDs;
  it cannot establish that these hashes match source bytes, that the source
  was lawfully acquired, or that the reviewer correctly interpreted the text.
  Producers must independently verify BCAST package materialization, source
  text hashes, review authorization and source coverage before admission.
- W3C PROV can represent extraction, interpretation/review and generation as
  separately attributed activities. The source object, source text digest,
  package identity, and review reference in this contract are the required
  link points. They are not themselves a PROV audit or approval certificate.
- BCM, not the transpiler, resolves jurisdictional adoption, amendments,
  effective dates, permit facts, and governing editions. Unresolved local
  evidence blocks a compliance conclusion.
- Keep restricted code text, source PDFs, private interpretations and
  rights decisions in authorized private storage. The public fixture is
  entirely synthetic; emitting Rust does not grant redistribution rights.

## Deliberately unsupported initially

Automatic natural-language-to-rule inference, cross-section references,
complex tables and footnotes, amendment merges, defined-term reasoning,
nontrivial temporal predicates, unit conversion, and whole-code coverage
claims. The next compiler feature should be justified by a traced real
provision and an independently reviewed expected result, not by adding a
general-purpose rules framework.