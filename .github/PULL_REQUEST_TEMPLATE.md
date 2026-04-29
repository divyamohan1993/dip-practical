<!--
Thanks for the PR! Please confirm the relevant boxes below before review.
See CONTRIBUTING.md for full guidelines.
-->

## Summary

<!-- 1–3 sentences on what this changes and why. -->

## Changes

- ...

## Verification

- [ ] `docker build -t dip-practical-test:local .` succeeds
- [ ] All eight `/practical/<N>` pages render (HTTP 200)
- [ ] Cache JSONs at `/static/cache/p[1-8]_*.json` resolve
- [ ] Ctrl/⌘+P preview on at least one practical shows: cover, all five
      colour-coded section banners, literal code, output figures, QR,
      watermark, page numbers
- [ ] Notebook + Flask + static deployments produce equivalent results
- [ ] Documentation updated (README / CONTRIBUTING / CITATION)

## Screenshots / printed PDF

<!-- Include screenshots, especially of the printed handbook if anything affects layout. -->
