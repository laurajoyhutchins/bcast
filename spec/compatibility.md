# Compatibility and Versioning

BCAST public contracts are versioned independently of the private compiler implementation.

## Pre-1.0

Versions before `1.0.0` may contain breaking changes. Breaking changes must still be explicit, documented, and versioned rather than silently reinterpreting an existing contract.

## Contract versions

Every published package schema, API contract, or other machine-consumed public contract must carry an explicit semantic version.

Once a contract reaches `1.0.0`:

- removing a field or operation is breaking;
- changing the meaning of an existing field or value is breaking;
- narrowing previously accepted input is breaking unless the prior behavior was explicitly invalid;
- additive optional fields are non-breaking only when conforming existing consumers can safely ignore them;
- new enum values are non-breaking only when the contract already requires consumers to tolerate unknown values;
- correcting documentation without changing machine-observable meaning is non-breaking.

## Provider changes

Changes to upstream providers should not force downstream breaking changes merely because a provider renamed an object, changed an API shape, or was replaced. A public BCAST contract changes when BCAST's consumer-facing meaning changes.

## Package and API compatibility

Compatibility between a package version and a service/API version must be stated explicitly. Consumers must not infer compatibility solely from Git tags, repository releases, or date proximity.

The first declared relation is exact:

```text
bcast.api/0.1.0 -> bcast.package/0.1.0
```

`bcast.api/0.1.0` does not imply compatibility with any other package contract. A conforming API implementation must return its documented `incompatible_version` error rather than reinterpret a package under an undeclared contract.

Package and API contracts evolve independently. Adding, removing, or changing a declared compatibility relation is itself a normative contract change and must be versioned rather than silently changing an existing coordinate.

## No implied release cadence

Versioning describes compatibility, not schedule. This policy does not promise a release cadence or provider-update interval.
