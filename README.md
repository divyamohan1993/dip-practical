<div align="center">

<img src="https://shooliniuniversity.com/assets/images/logo.png" alt="Shoolini University" width="160">

# Digital Images Processing — Practical File

**CSU2543** &nbsp;·&nbsp; Yogananda School of AI, Computers and Data Sciences &nbsp;·&nbsp; Shoolini University, Solan (H.P.)

[![Live](https://img.shields.io/badge/live-dip.dmj.one-2e7d32?style=flat-square&logo=googlechrome&logoColor=white)](https://dip.dmj.one)
[![Cloud Run](https://img.shields.io/badge/Cloud_Run-asia--south1-4285F4?style=flat-square&logo=googlecloud&logoColor=white)](https://dip.dmj.one)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/divyamohan1993/dip-practical/blob/main/Practical_1.ipynb)
[![License: MIT](https://img.shields.io/badge/license-MIT-1a3d6c?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![WCAG 2.2 AAA](https://img.shields.io/badge/WCAG-2.2%20AAA-4caf50?style=flat-square)](#accessibility)

A complete practical lab handbook for **CSU2543 — Digital Images Processing**, covering the eight prescribed experiments end to end. Every experiment ships in three independently-runnable forms — a Jupyter notebook, an interactive Flask web app, and a fully-static client-side build — so the same lab works in Colab, on a server, or as plain HTML files.

[**Open the lab →**](https://dip.dmj.one) &nbsp;·&nbsp; [**Practical handbook PDF →**](https://dip.dmj.one) &nbsp;·&nbsp; [Run any experiment in Colab](https://colab.research.google.com/github/divyamohan1993/dip-practical/blob/main/Practical_1.ipynb)

</div>

---

## Table of Contents

- [Course details](#course-details)
- [Experiments](#experiments)
- [Three deployment forms](#three-deployment-forms)
- [Print-ready handbook](#print-ready-handbook)
- [Architecture](#architecture)
- [Quick start](#quick-start)
- [Deploy](#deploy)
- [API reference](#api-reference)
- [Tech stack](#tech-stack)
- [Accessibility](#accessibility)
- [Security](#security)
- [Acknowledgements](#acknowledgements)
- [License](#license)

---

## Course details

| | |
| - | - |
| **Course code** | CSU2543 |
| **Course title** | Digital Images Processing |
| **Programme** | B.Tech. in Computer Science and Engineering, 8th semester |
| **Reference text** | Gonzalez & Woods, *Digital Image Processing*, 3rd Ed. |
| **University** | Shoolini University, Solan, Himachal Pradesh, India |
| **School** | Yogananda School of AI, Computers and Data Sciences |
| **Faculty in-charge** | Ms. Ishani Sharma |
| **Submitted by** | Divya Mohan &nbsp;·&nbsp; Roll&nbsp;No.&nbsp;GF202214698 |
| **Academic session** | 2025–2026 |

---

## Experiments

| # | Experiment | Reference | Notebook | Interactive | Static |
| - | ---------- | --------- | -------- | ----------- | ------ |
| 1 | Loading and displaying digital images | G&W Ch 2 | [.ipynb](Practical_1.ipynb) | [/practical/1](https://dip.dmj.one/practical/1) | [p1.html](pages/p1.html) |
| 2 | Impact of sampling rate on spatial resolution | G&W Ch 2 | [.ipynb](Practical_2.ipynb) | [/practical/2](https://dip.dmj.one/practical/2) | [p2.html](pages/p2.html) |
| 3 | Image negation, subtraction & inversion | G&W Ch 2–3 | [.ipynb](Practical_3.ipynb) | [/practical/3](https://dip.dmj.one/practical/3) | [p3.html](pages/p3.html) |
| 4 | Gamma correction & power-law transformations | G&W Ch 3 | [.ipynb](Practical_4.ipynb) | [/practical/4](https://dip.dmj.one/practical/4) | [p4.html](pages/p4.html) |
| 5 | Histogram equalization | G&W Ch 3 | [.ipynb](Practical_5.ipynb) | [/practical/5](https://dip.dmj.one/practical/5) | [p5.html](pages/p5.html) |
| 6 | Histogram matching & specification | G&W Ch 3 | [.ipynb](Practical_6.ipynb) | [/practical/6](https://dip.dmj.one/practical/6) | [p6.html](pages/p6.html) |
| 7 | 2D correlation & convolution | G&W Ch 3 | [.ipynb](Practical_7.ipynb) | [/practical/7](https://dip.dmj.one/practical/7) | [p7.html](pages/p7.html) |
| 8 | Spatial filtering — box, median, Laplacian, Sobel | G&W Ch 3 | [.ipynb](Practical_8.ipynb) | [/practical/8](https://dip.dmj.one/practical/8) | [p8.html](pages/p8.html) |

Each experiment follows the same handbook structure: **Aim → Description / Theory → Code → Output → Analysis / Conclusion** — colour-coded on screen and on the printed PDF.

---

## Three deployment forms

| Form | Where it runs | When to use it | Source |
| ---- | ------------- | -------------- | ------ |
| **Jupyter notebook** | Google Colab or local Jupyter | Auto-grading, lab assignments, deeper code experimentation | [`Practical_N.ipynb`](Practical_1.ipynb) |
| **Flask web app** | Cloud Run (current production) or any Linux VM | Interactive demos, picker-driven experimentation, server-side OpenCV | [`app/`](app/), [`Dockerfile`](Dockerfile) |
| **Static client-side build** | Cloudflare Pages, Vercel, GitHub Pages | Zero-cost hosting, fully offline-capable browser implementation | [`pages/`](pages/) |

The static build re-implements every operation client-side using the Canvas API and pure JavaScript — it is independent of the Flask code path.

---

## Print-ready handbook

Press **Ctrl/⌘ + P** on any page on the live site and you get a Chicago-style, AAA-accessible handbook ready for submission:

- **Cover page** matching Shoolini's practical-file template (title, programme, Submitted by / to, school, university, location, date)
- **Per-practical cover identifier** ("Practical 7: 2D Correlation & Convolution") shown when printing an individual practical, suppressed on the consolidated home printout
- **Universal pages** — Cover → Certificate → Acknowledgement → Index — when printing from `/`
- **Index** with all 8 experiments and `1.*, 2.*, …, 8.*` page references
- **Colour-coded section banners** — Aim (blue), Description / Theory (purple), Code (green), Output (orange), Analysis / Conclusion (red); identical palette across notebooks and the web app
- **Literal Python code** rendered in the Code section (extracted from the notebooks, not the server processors)
- **Result figures** auto-mirrored under the Output section via a `beforeprint` JS hook so every visible figure ends up in the printout
- **2"×2" QR code** on each practical's cover encoding the canonical page URL — works behind Cloudflare via Werkzeug `ProxyFix`
- **2"×2" centred dmj.one watermark** at 22% opacity on every content page (suppressed on cover via opaque background + z-index)
- **Per-practical page numbering** as `N.1, N.2, …` using CSS named-page contexts; cover unnumbered
- **1-inch margins all sides**, justified text, Times New Roman 12pt, JetBrains Mono code blocks

---

## Architecture

```
                         Cloudflare (custom domain dip.dmj.one)
                                       │
                                       ▼
                           Google Cloud Run · asia-south1
                           dip-practical (revision …008-k2t)
                                       │
                                       ▼
              ┌───────────────────────┴────────────────────────┐
              │                                                 │
        Flask + Werkzeug ProxyFix              precompute.py result cache
        Gunicorn 2 workers × 8 threads         (32 JSON figures baked into image)
              │                                                 │
              ├────── /                       Cover · Certificate · Acknowledgement · Index
              ├────── /practical/<num>        Per-practical interactive page + cover QR
              ├────── /api/p<n>/...           POST endpoints, on-demand matplotlib renders
              └────── /static/cache/...       Pre-computed result figures (instant load)
                              │
                              ▼
              app/processors/p0[1-8]_*.py    OpenCV + matplotlib · Agg backend
                              │
                              ▼
              datasets/CH02 · CH03           Auto-downloaded from imageprocessingplace.com
```

---

## Quick start

### Run the web app locally

```bash
git clone https://github.com/divyamohan1993/dip-practical.git
cd dip-practical
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python run.py
# Open http://localhost:5000
```

### Run any experiment in Colab

Click the Colab badge at the top of any [`Practical_N.ipynb`](Practical_1.ipynb) — it auto-downloads the Gonzalez & Woods dataset and runs end-to-end.

### Run the static client-side build

```bash
cd pages
python3 setup.py            # one-time: download CH02 dataset and convert .tif → .png
python3 -m http.server 8000 # serve over a local HTTP origin
# Open http://localhost:8000
```

---

## Deploy

### Cloud Run (one command, current production)

```bash
gcloud run deploy dip-practical \
  --source . \
  --region asia-south1 \
  --memory 2Gi \
  --allow-unauthenticated
```

The [`Dockerfile`](Dockerfile) runs [`precompute.py`](precompute.py) at build time so the image ships with all 32 cached result figures — pages render instantly on first hit, and printed PDFs include the figures even on the very first page load.

### Bare-metal Linux VM

```bash
chmod +x autoconfig.sh && sudo ./autoconfig.sh
```

Idempotent script that installs Python, Nginx (with microcache), systemd unit, log rotation, and UFW rules on a fresh Ubuntu 24.04 host. See [`autoconfig.sh`](autoconfig.sh) and [`deploy/nginx-site.conf`](deploy/nginx-site.conf).

### Static client-side (Cloudflare Pages / Vercel / GitHub Pages)

Deploy [`pages/`](pages/) as the build output directory — no backend required. Every operation runs in the browser via the Canvas API.

---

## API reference

All endpoints live under `/api`. Practical processors are lazy-loaded on first call. Every route returns JSON with a base64 PNG `plot` field for the rendered figure.

| Practical | Endpoints |
| --------- | --------- |
| **Common** | `GET /api/chapters` &nbsp;·&nbsp; `GET /api/chapters/<id>/images` &nbsp;·&nbsp; `GET /api/image/<filename>` |
| **P1 — Display** | `POST /api/p1/display` &nbsp;·&nbsp; `POST /api/p1/histogram` &nbsp;·&nbsp; `POST /api/p1/multi-display` |
| **P2 — Sampling** | `POST /api/p2/downsample` &nbsp;·&nbsp; `POST /api/p2/downsample-plot` &nbsp;·&nbsp; `POST /api/p2/upscale-compare` |
| **P3 — Negation / Subtract** | `GET /api/p3/pairs` &nbsp;·&nbsp; `POST /api/p3/negate` &nbsp;·&nbsp; `POST /api/p3/subtract` &nbsp;·&nbsp; `POST /api/p3/pipeline` |
| **P4 — Gamma** | `POST /api/p4/gamma` &nbsp;·&nbsp; `POST /api/p4/gamma-series` &nbsp;·&nbsp; `POST /api/p4/log-transform` &nbsp;·&nbsp; `GET /api/p4/curves` &nbsp;·&nbsp; `POST /api/p4/contrast` |
| **P5 — Equalization** | `POST /api/p5/original-histogram` &nbsp;·&nbsp; `POST /api/p5/equalize` &nbsp;·&nbsp; `POST /api/p5/transfer-function` &nbsp;·&nbsp; `POST /api/p5/multi-equalize` |
| **P6 — Matching** | `POST /api/p6/source-histogram` &nbsp;·&nbsp; `POST /api/p6/equalize-baseline` &nbsp;·&nbsp; `POST /api/p6/match` &nbsp;·&nbsp; `POST /api/p6/multi-target` &nbsp;·&nbsp; `POST /api/p6/transfer-analysis` |
| **P7 — Conv / Corr** | `GET /api/p7/impulse` &nbsp;·&nbsp; `POST /api/p7/custom` &nbsp;·&nbsp; `POST /api/p7/image-filter` &nbsp;·&nbsp; `POST /api/p7/verify` |
| **P8 — Filtering** | `POST /api/p8/box` &nbsp;·&nbsp; `POST /api/p8/median` &nbsp;·&nbsp; `POST /api/p8/box-vs-median` &nbsp;·&nbsp; `POST /api/p8/laplacian` &nbsp;·&nbsp; `POST /api/p8/sobel` |
| **Health** | `GET /health` |

---

## Tech stack

| Layer | Tools |
| ----- | ----- |
| **Backend** | Flask 3.1, Gunicorn 25, Werkzeug ProxyFix, OpenCV 4.13 (headless), Matplotlib 3.10 (Agg), NumPy 2.4, Pillow 12, qrcode 8 |
| **Static client** | Vanilla JavaScript, Canvas API, Chart.js 4, Bootstrap 5.3, MathJax 3 |
| **Print** | CSS3 Generated Content for Paged Media (target-counter, named pages, `@bottom-center`), Jinja2 conditional sections |
| **Notebooks** | Jupyter ipynb (nbformat 4.4), CSS-styled markdown preamble |
| **Hosting** | Google Cloud Run + Artifact Registry (asia-south1), Cloudflare custom domain, Google Cloud Build |
| **Dataset** | Gonzalez & Woods 3rd Edition, Chapters 02 + 03 — auto-downloaded from imageprocessingplace.com on first run |

---

## Repository layout

```
dip-practical/
├── Practical_1.ipynb … Practical_8.ipynb   # Colab-ready notebooks (one per experiment)
├── app/                                    # Flask web app
│   ├── processors/                         # OpenCV + matplotlib operations
│   │   ├── common.py                       # Shared helpers — load_image, fig_to_base64, qr_data_uri
│   │   └── p0[1-8]_*.py                    # Per-practical processors
│   ├── routes/                             # Flask blueprints — pages.py, api.py
│   ├── templates/                          # Jinja2 templates
│   │   ├── base.html                       # Shared shell with print stylesheet, watermark, cover
│   │   └── practicals/p0[1-8].html         # One template per practical
│   └── static/                             # CSS, JS, pre-computed cache JSONs (built into image)
├── pages/                                  # Fully-static Cloudflare-Pages build
│   ├── p[1-8].html                         # Standalone HTML per practical
│   ├── js/dip.js                           # Pure-JS image-processing kernel
│   └── data/                               # Pre-converted PNG dataset + manifest.json
├── deploy/nginx-site.conf                  # Production nginx config (microcache + reverse proxy)
├── Dockerfile                              # Cloud Run image — runs precompute.py at build time
├── gunicorn.cloudrun.py                    # 0.0.0.0:$PORT bind for Cloud Run
├── gunicorn.conf.py                        # 127.0.0.1:8000 + file logging for the VM deploy
├── autoconfig.sh                           # One-command provision of an Ubuntu 24.04 VM
├── precompute.py                           # Bakes every default result into /static/cache as JSON
├── format_practicals.py                    # Applies the colour-coded section format to all 8 notebooks
├── format_templates.py                     # Adds print-only section banners to all 8 web templates
└── format_print_codeoutput.py              # Embeds literal Python + Output containers in templates
```

---

## Accessibility

The lab targets **WCAG 2.2 AAA** compliance from line one:

- 7:1 minimum contrast ratio on all text
- 44×44 px minimum target size (matches WCAG 2.2 SC 2.5.8)
- Explicit ARIA labels and `aria-live` toast announcements
- Full keyboard navigation; visible focus rings; skip-to-content link
- Honours `prefers-reduced-motion`, `prefers-color-scheme`, `forced-colors`
- Captions for every figure and image in print mode

---

## Security

- All HTTP requests served over HTTPS via Cloudflare; HSTS preloaded
- `Content-Security-Policy`, `X-Content-Type-Options`, and `Referrer-Policy` headers set in [`deploy/nginx-site.conf`](deploy/nginx-site.conf)
- Werkzeug `ProxyFix` middleware honours `X-Forwarded-*` only from the Cloud Run / Cloudflare hop
- Dependency pins in [`requirements.txt`](requirements.txt) resolve every Dependabot advisory open on the default branch
- No secrets in the repo; the only outbound network call is the on-demand dataset download from imageprocessingplace.com (cached locally)

To report a vulnerability, please see [`SECURITY.md`](SECURITY.md).

---

## Acknowledgements

This lab is built as part of the coursework for **CSU2543 — Digital Images Processing** at **Shoolini University**, under the supervision of **Ms. Ishani Sharma**, Faculty In-charge, *Yogananda School of AI, Computers and Data Sciences*.

Reference dataset: Gonzalez & Woods, *Digital Image Processing*, 3rd Edition — original images courtesy of [imageprocessingplace.com](https://www.imageprocessingplace.com/).

---

## License

Distributed under the [MIT License](LICENSE). The Gonzalez & Woods dataset is the property of its respective copyright holders and is auto-downloaded for educational use only.

---

<div align="center">

<sub>**CSU2543 · Digital Images Processing** &nbsp;·&nbsp; Built with care by [**Divya Mohan**](https://github.com/divyamohan1993) (GF202214698) under [**Ms. Ishani Sharma**](mailto:ishanisharma@shooliniuniversity.com) at <strong>Shoolini University</strong>.</sub>

</div>
