# Security Policy

## Supported versions

The `main` branch of this repository is the only supported version. Production
deployments mirror `main` via Google Cloud Build → Cloud Run. There are no
maintenance branches.

| Branch | Supported |
| ------ | --------- |
| `main` | ✅ |
| Anything else | ❌ |

## Reporting a vulnerability

If you believe you have found a security issue in this lab, please:

1. **Do not open a public GitHub issue.** Public disclosure before a fix is
   in production puts users at risk.
2. Email **contact@dmj.one** with the subject `[security] dip-practical`.
   Include a description, reproduction steps, and the affected URL or
   commit hash. PGP key available on request.
3. You will receive an acknowledgement within **72 hours**.
4. Coordinated disclosure: a fix is rolled to production before any public
   advisory. We will credit reporters on request.

## Hardening already in place

- Cloudflare in front of the origin; HTTPS only; HSTS preloaded.
- Werkzeug `ProxyFix` is configured to trust `X-Forwarded-*` from the
  Cloud Run / Cloudflare hop only — see [`app/__init__.py`](app/__init__.py).
- Strict `Content-Security-Policy`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: strict-origin-when-cross-origin`, and
  `Permissions-Policy` headers — see
  [`deploy/nginx-site.conf`](deploy/nginx-site.conf).
- No secrets in the repository. The only outbound call is the one-time
  dataset download from imageprocessingplace.com, cached locally.
- Dependency pins in [`requirements.txt`](requirements.txt) resolve every
  Dependabot advisory open on `main` at release time.

## Out of scope

- Issues that require physical access to the user's device.
- Self-XSS that requires the user to paste attacker-controlled scripts
  into their browser console.
- Known limitations of unauthenticated public demos (e.g. compute-time
  exhaustion via repeated POSTs); rate limiting lives at the Cloudflare
  edge, not in this codebase.
