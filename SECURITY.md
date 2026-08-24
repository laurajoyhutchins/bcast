# Security Policy

## Reporting sensitive issues

Do not open a public issue or pull request for:

- exposed credentials, tokens, entitlements, cookies, or account identifiers;
- restricted or licensed source-content leaks;
- private provider responses or account-specific locators;
- vulnerabilities that could expose private BCAST data or provider access;
- vulnerabilities in public BCAST clients or conformance tooling that could materially affect consumers.

Use GitHub's private vulnerability reporting mechanism if it is enabled for this repository. If it is not available, contact the repository owner through an existing private channel and provide only enough information to establish the issue safely.

Do not attach restricted source material to a security report unless the repository owner explicitly requests it through a private channel and the disclosure is lawful.

## Supported surface

Before the first public release, this repository is pre-1.0 and may not contain a released runtime component. Security support applies to the public technical surface that exists at the time of a report, including published client SDKs, conformance tools, schemas, and service contracts.

## Scope distinction

A disagreement about regulatory interpretation is not automatically a security vulnerability. However, a defect that causes a public BCAST client or contract validator to expose secrets, bypass access controls, mis-handle untrusted input, or materially misrepresent integrity guarantees may be security-relevant.

## Disclosure

Please allow the repository owner to investigate and coordinate a fix before public disclosure of a genuine vulnerability or sensitive-data exposure.