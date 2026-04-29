# Contributing

This is the practical-file repository for **CSU2543 — Digital Images
Processing** at **Shoolini University**. The submitted file (notebooks,
web app, static build, and printed PDF) is the deliverable for the course,
so structural changes should respect the practical-format spec while
quality-of-life fixes are very welcome.

## Ground rules

- Be kind. Discussions follow the spirit of [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
- Every change must keep the **printed handbook** producing the exact
  required format on Ctrl/⌘+P (1-inch margins, justified, colour-coded
  Aim → Description / Theory → Code → Output → Analysis / Conclusion).
- Every change must keep the three deployment forms — Jupyter notebook,
  Flask app on Cloud Run, static client-side build — in sync.
- Every change must keep the lab fully **WCAG 2.2 AAA** compliant.

## How to contribute

### Bug reports

Open an issue with:

- The page or experiment (`/practical/N`, notebook number, or static page).
- Browser + OS, or Python version if it's the notebook.
- Steps to reproduce, expected behaviour, actual behaviour.
- Screenshots, especially of the printed PDF if the print layout is involved.

For **security** issues, please follow [`SECURITY.md`](SECURITY.md) instead.

### Pull requests

1. Fork the repository and create a feature branch off `main`.
2. Follow the existing code style — Python uses 4-space indentation and
   type hints where signatures are non-trivial; HTML/CSS/JS keeps the
   Bootstrap 5 conventions of [`app/templates/base.html`](app/templates/base.html).
3. Run the local Docker build and verify all three deployment forms still
   produce identical printed output (see *Verification* below).
4. Open a PR against `main` with a description of the user-visible change.

### Verification

Before submitting a PR, please run:

```bash
# 1. Local Docker build mirrors Cloud Run production
docker build -t dip-practical-test:local .
docker run -d --name dip-test -p 18080:8080 dip-practical-test:local

# 2. Smoke-test every practical page + cache
for n in 1 2 3 4 5 6 7 8; do
  curl -fsS -o /dev/null "http://localhost:18080/practical/$n"
done
for f in p1_display p5_equalize p7_impulse p8_box p8_sobel; do
  curl -fsS -o /dev/null "http://localhost:18080/static/cache/${f}.json"
done

# 3. Print preview every practical page in your browser:
#    Ctrl/⌘ + P → confirm cover, banners, page numbers, QR, watermark

docker stop dip-test && docker rm dip-test
```

If you change a notebook, also re-run the formatter so all eight notebooks
stay in lockstep:

```bash
python3 format_practicals.py        # colour-coded sections in notebooks
python3 format_templates.py         # print-only banners in templates
python3 format_print_codeoutput.py  # literal code + Output mirror in templates
```

### Conventions

- Commit messages follow the existing style: short imperative subject,
  blank line, motivation in the body. Sign with the standard
  `Co-Authored-By` trailer if you used an AI assistant.
- Don't commit secrets, generated PDFs, downloaded datasets, or
  pre-computed cache JSONs (`.gitignore` already excludes them).
- Update [`README.md`](README.md) and [`CITATION.cff`](CITATION.cff) if
  user-facing behaviour changes.

## Deploy

Maintainers redeploy to Cloud Run via:

```bash
gcloud run deploy dip-practical \
  --source . \
  --region asia-south1 \
  --memory 2Gi \
  --quiet
```

The Dockerfile bakes [`precompute.py`](precompute.py) into the image so
result figures are available on the very first request.

## Maintainers

- **Divya Mohan** (`@divyamohan1993`) — student / primary author
- **Ms. Ishani Sharma** — faculty in-charge for CSU2543 at Shoolini University

For anything course-related, please consult the faculty in-charge first.
