# BCAST maintained cross-version interoperability evidence

This matrix records **actual maintained** package/API contracts, not an invented
stable 1.0 version. It is executable through
[`tests/test_cross_version.py`](../tests/test_cross_version.py).

| HTTP consumer / service mode | 0.1 package | 0.2 package |
| --- | --- | --- |
| `bcast.api/0.1.0` | Accepts, full package and navigation validated | Explicit `409 incompatible_version` |
| `bcast.api/0.2.0` | Explicit `409 incompatible_version` | Accepts, full package and navigation validated |
| Client configured for the wrong package version even if HTTP returns 200 | Rejects at contract validation | Rejects at contract validation |

The tests run the real public reference server and clients against both
checked-in project-authored synthetic fixtures. They also assert that
adding a namespace or deleting an `assurance` value is *not* sufficient to
upgrade/downgrade a package. Publication, object and package identities
differ by normative version; a matching human family and edition cannot
justify substituting one canonical identity for the other.

**Evidence boundary.** These are maintained compatibility behaviors, not
proof of universal interoperability, a source-authenticity certificate, a
production BCAST service or a claim that `1.0.0` is ready. The separately
maintained BCM Go `0.2.0` consumer also successfully verified a real
source-derived BCAST package through ordinary HTTP in private BCAST GCP
[run 39507466354](https://github.com/laurajoyhutchins/bcast-private/actions/runs/39507466354).
That consumer currently rejects non-ASCII edition/revision coordinates until
an explicit NFC implementation is established, and the source producer's
durable GCS archival remains pending. Neither limitation should be hidden
by passing cross-version tests.

BCAST issue [#13](https://github.com/laurajoyhutchins/bcast/issues/13)
remains the readiness gate, and [#22](https://github.com/laurajoyhutchins/bcast/issues/22)
owns the real eCFR source/consumer evidence. No contract is promoted here.
