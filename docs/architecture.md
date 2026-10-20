# BCAST software architecture

The intended split mirrors Building Code Map: **one public software authority, one private regulatory-data authority**. The detailed policy and current migration status are in [Product boundary](product-boundary.md).

```text
         upstream publishers / lawful source services
                            |
           [private: access, rights, source snapshots]
                            |
                 source-specific adapter
                            |
               normalized publication input
                            |
             [public: canonical BCAST compiler]
                            |
        contract-checked, content-addressed package
                            |
              +-------------+--------------+
              |                            |
      [private: approval,             [public: local
       retention, distribution]        synthetic tests]
              |
   rights-scoped package / service
              |
        public client, CLI, API and downstream tools
```

## Ownership and dependency

- **Public BCAST** defines the package schema, provider-neutral identity, version compatibility, reusable neutral compilation/validation, navigation and consumer interfaces. It must work with synthetic or otherwise lawful user-supplied input without private modules.
- **Private BCAST** decides which source to acquire and may use provider-specific mappings, entitlements and review operations. It preserves exact evidence and makes source-specific publication decisions. It depends on a pinned public software revision.
- **Never two canonical compilers.** The private producer invokes public package assembly rather than reimplementing identity hashing, output validity or graph representation. Data-review policy and compiler correctness are independently testable.
- **No bulk corpus in public Git or Pages.** A public software distribution does not imply that package outputs or upstream bytes are publicly distributable.

## Existing public contract

The maintained 0.1.0 package/API pair is explicitly separate from the 0.2.0 pair. The human-readable specs are normative; JSON Schemas, OpenAPI, Python client and reference server are companions. The 0.2.0 package identity includes the materialized content, but API metadata alone cannot verify that digest.

The local reference server serves validated existing packages through read-only GET operations. It is not a deployed production service and does not acquire or certify regulatory sources.

## Compilation seam

The public reusable compilation unit accepts a reviewed **provider-neutral input** and returns a package or explicit errors. It owns reproducible serialization, identity, parentage constraints and conformance. The private side translates provider-native data into this input, documents unsupported source constructs, reconciles source correspondence and chooses whether any result may be retained or distributed.

Avoid introducing a generic adapter/plugin framework before the bounded eCFR migration demonstrates its need. Preserve the existing 0.2.0 consumer contract unless a real downstream requirement justifies a new version.

## Progress and verification

The public side currently has package consumption and validation but not the complete neutral compilation unit. The private eCFR path presently performs both source-specific normalization and package construction. Migration is pending. Exact-source replay, independent source text/structure audits, error-state fidelity, and public/private conformance must remain true at cutover. Code coverage percentages alone do not establish these properties.

BCAST is source representation, not jurisdictional adoption (Building Code Map) and not engineering calculation approval (Arcata).
