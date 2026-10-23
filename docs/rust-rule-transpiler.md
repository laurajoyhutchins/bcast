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
