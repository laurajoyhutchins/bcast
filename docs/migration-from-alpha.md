# Migration from `building-code-ast-alpha`

`building-code-ast-alpha` is archived historical research and implementation state. `bcast` is its public-safe successor surface, not a continuation of the alpha Git history.

The migration follows one rule: preserve product concepts that belong in a public consumer contract, not the machinery that produced them.

## Re-specified in BCAST

The first public package contract re-specifies a small set of alpha concepts from current product requirements:

- provider-neutral publication identity;
- deterministic regulatory-object identity;
- structural object kinds and parentage;
- explicit unsupported or unresolved states;
- source-safe provenance;
- explicit assurance as a consumer-facing product guarantee.

These concepts are implemented cleanly in `bcast`. Alpha source files and commit history are not imported.

## Intentionally left in alpha or private systems

The following do not cross the public boundary:

- licensed or restricted source text and page images;
- retained source objects and private storage locators;
- provider-specific acquisition or hydration;
- OCR and source-family recovery logic;
- `source-text/v1` producer/adaptor machinery;
- production normalization heuristics;
- private review corpora and acceptance evidence;
- production graph compilation and package materialization;
- production provider mappings;
- proprietary verification evidence.

The archived repository remains useful as historical evidence for how those ideas evolved, but it is not an active dependency or upstream branch.

## Compatibility boundary

Downstream consumers should depend on the contracts under `spec/`, not on alpha Python classes, CLI commands, internal schemas, filenames, or generated artifacts.

No compatibility promise is made from alpha internals to BCAST public contracts. Compatibility begins with explicitly versioned BCAST contracts.
