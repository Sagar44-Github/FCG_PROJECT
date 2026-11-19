# Q3 Research Application

## Assignment and reference handoff

The repository now includes the supplied assignment/rubric, complete `Q3_Execution_Guide.md`, both supplied report ToC images, and the supplied Nigam PDF under `reference_materials/`. The guide is preserved intact; physical label/light measurements and human-participant steps are not performed because the project's direct requirements specify a software-only study. See [`report_inputs/IMPLEMENTATION_SCOPE_NOTE.md`](report_inputs/IMPLEMENTATION_SCOPE_NOTE.md) and [`report_inputs/TOC_STRUCTURE_MAPPING.md`](report_inputs/TOC_STRUCTURE_MAPPING.md).

The exact Pilarski, Jullien, Li et al. (2023), Wadhawan, and Nigam identities and source status are recorded in [`report_inputs/LITERATURE_REVIEW_NOTES.md`](report_inputs/LITERATURE_REVIEW_NOTES.md) and [`reference_materials/REFERENCE_SOURCE_REGISTER.md`](reference_materials/REFERENCE_SOURCE_REGISTER.md). Jullien's final paper, the Wadhawan 2024 arXiv preprint, and the supplied Nigam copy are locally included. Pilarski and Li have verified public full-text sources, but their PDF files could not be retrieved into this workspace. The handoff records this without substituting other papers.

**Software-Based Spectral Evaluation of Expiry-Warning Shelf Colours Under Daylight and Retail LED Illumination for Near-Expiry Donation Trigger Analysis**

This is a software-only academic research application. It combines a CIE spectral colour pipeline, a virtual print-response model, a Blender RGB scene, clearly labelled observer and inventory simulations, statistical evidence, a FastAPI/SQLite service, a premium React/TypeScript 3D dashboard, and a retained Streamlit fallback.

> Simulated model outputs are not physical print or lamp measurements, human-participant findings, observed retail donations, or measured waste/emissions reductions. L2 and L3 are parameterized LED approximations. The Blender Cycles scene provides RGB visualizations; spectral colorimetry is computed in Python.

## Research objectives

- Compare a configured digital shelf-label colour with its synthetic virtual-print representation under CIE D65 and two approximate store-LED SPDs using CIEDE2000.
- Report CIELAB and chromaticity values, dominant or complementary wavelength, and excitation purity.
- Explore sensitivity of a simulated action-classification model to ΔE00 and connect it to seeded near-expiry inventory and donation-capacity simulations.
- Produce traceable CSV, statistical, figure, and Blender evidence that can be regenerated from source.

The original four sRGB values and three illumination definitions are stored in `config.json`. The CIE source files, model assumptions, parameter-change log, and run metadata are under `data/`, `docs/`, and `results/`.

## Technology and architecture

| Layer | Implementation |
|---|---|
| Primary dashboard | React 19, TypeScript, Vite, Tailwind CSS, React Three Fiber, Drei, Motion, Recharts, Lucide; API client only |
| Fallback dashboard | Streamlit; retained as the previous functional interface |
| API and validation | FastAPI, Pydantic, versioned REST routes, OpenAPI/Swagger |
| Persistence | SQLite for comparisons, simulations, render jobs, and analysis jobs |
| Spectral and colour science | Python, NumPy, Pandas, SciPy, `colour-science`, CIE datasets |
| Simulation and statistics | NumPy, SciPy, statsmodels, fixed-seed Monte Carlo |
| Figures | Matplotlib |
| Digital twin | Blender Python API, Cycles, Standard view transform |
| Deployment preparation | Dockerfile and Compose services for API, React dashboard and Streamlit fallback |

The API, dashboard, Python and Blender execute in user space. No custom kernel-mode driver or privileged component is necessary. The API launches Blender with a fixed argument list, a server-created output directory, and a timeout. File downloads use an allow-list. The dashboard can only read the project configuration; per-run simulation overrides are stored with their results and configuration digest.

### Folder layout

```text
backend/                  FastAPI routes and SQLite repository
blender/                  saved .blend, automation and render evidence
colour_engine/            spectra, reflectance, conversions, CIEDE2000, pipeline
dashboard/                Retained Streamlit fallback (FastAPI client)
frontend/                 React/TypeScript research dashboard and 3D scene
data/                     local CIE datasets and CIEDE2000 reference cases
docs/                     assumptions, sources, guides and editable diagrams
renders/                  twelve baseline PNGs and contact sheet
results/                  CSV evidence, metadata, figures and tables
simulation/               observer and inventory Monte Carlo models
tests/                    unit and HTTP API tests
config.json               initial research parameters and model assumptions
run_pipeline.py           reproducible evidence generation entry point
```

See [architecture and API routes](docs/architecture.md), [model assumptions](docs/model_assumptions.md), and the editable/rendered diagrams under `docs/diagrams/`.

## Install and run locally

Use Python 3.11 or newer. Blender is needed only for a render batch; the other API functions can run without it.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Optional local environment settings can be copied from `.env.example` to `.env`. The API defaults to `data/q3.sqlite3`; set `Q3_DATABASE_PATH` to use another database. Set `BLENDER_EXECUTABLE` if Blender is not discoverable.

### Start the backend and dashboards

Open terminals in the project root. The React dashboard is the primary interface; Streamlit remains available as a fallback.

```powershell
# Terminal 1
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

```powershell
# Terminal 2 — primary React/TypeScript application
Set-Location frontend
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

Open the primary application at `http://127.0.0.1:5173`. Vite proxies `/api/v1` to FastAPI on port 8000, so the browser uses the same actual backend without a second origin.

```powershell
# Terminal 3 — retained Streamlit fallback
$env:Q3_API_URL = "http://127.0.0.1:8000"
python -m streamlit run dashboard/app.py
```

The fallback remains at `http://127.0.0.1:8501`. Swagger UI is at `http://127.0.0.1:8000/docs`; the OpenAPI document is at `/openapi.json`.

For a short step-by-step faculty presentation, including how to change lighting in both Blender and the dashboard, see [`docs/faculty_demo_guide.md`](docs/faculty_demo_guide.md).

The React 3D shelf is a lazily loaded GLB exported from the `HERO_SUPERMARKET` scene. It is a visual control surface; API calculations and all scientific result values remain backend-owned. Final store render images are provided as reproducible static PNGs and downloadable API artifacts.

Both dashboards read status and saved outputs through `GET /api/v1/dashboard`. The React pages start real API computations, retrieve render PNGs and CSVs, page through saved history, and download the evidence archive. The frontend never computes science metrics locally. If the backend is stopped, it shows a connection error rather than sample data.

Build and test the frontend:

```powershell
Set-Location frontend
npm ci
npm run build
npm test
npx playwright install chromium
npm run test:e2e
```

Playwright checks all six sections against the live API, real Blender previews, persisted comparison and donation requests, evidence download, 390–1280 px layout overflow, the WebGL fallback, and completion of a real 12-case Blender render job. Set `Q3_CHROME_EXECUTABLE` only when using an already installed browser instead of Playwright's Chromium.

### Run the scientific pipeline

```powershell
python run_pipeline.py
```

This writes the full set of 12 color/illumination measurements, spectra, trigger and inventory simulations, statistics, sustainability sensitivity, metadata, and figures under `results/`. Seeds and software versions are stored in `results/run_metadata.json`. The default capacity sweep uses 500 replicates per scenario; an API analysis job can set a different replicate count and records that request and the configuration SHA-256.

### Generate Blender renders manually

The installed Blender executable used for the checked-in outputs was Blender 5.2.3 LTS. To generate a new 12-case batch:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python blender/scripts/render_batch.py -- --output-dir renders --samples 8
python make_contact_sheet.py
```

The script reads `blender/q3_project.blend` and writes one PNG per configured color and illumination. `renders/contact_sheet.png` gives the 4×3 overview. D65 is a neutral RGB visualization inside Blender, not a Cycles spectral measurement. The Python spectral pipeline uses the CIE reference SPD. LED blackbody nodes are visualization aids only.

### Build the luxury supermarket digital twin

The detailed `HERO_SUPERMARKET` presentation scene is saved alongside the unchanged controlled scene in `blender/q3_supermarket.blend`. To rebuild and render it:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b blender/q3_project.blend --python blender/scripts/build_supermarket.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b blender/q3_supermarket.blend --python blender/scripts/render_supermarket.py -- --preview
# Review the proof frames before generating the final 2560 × 1440 image set.
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b blender/q3_supermarket.blend --python blender/scripts/render_supermarket.py
python blender/scripts/compose_supermarket_evidence.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b blender/q3_supermarket.blend --python blender/scripts/export_web_model.py
```

Final views, comparison frames, and contact sheet are saved under `blender/renders/supermarket/`. The product artwork is generated from original fictional VERDANT MARKET packaging graphics. The separate [visual-pipeline note](docs/supermarket_visual_pipeline.md) records camera, lighting, asset, and RGB/spectral limitations. The frontend's Three.js scene uses a focused 4.1 MB shelf-segment GLB exported from Blender, not a substitute rendering or calculation pipeline.

### Run tests

```powershell
python -m pytest -q
```

Tests cover conversion/CIEDE2000, published verification cases, spectrum and virtual-print constraints, deterministic simulations, API validation and persistence, pagination, render path confinement, job status, dashboard summary, export allow-listing, and evidence-package composition. The final Phase 4 test logs are `results/phase4_backend_tests.txt`, `results/phase4_frontend_build.txt`, `results/phase4_frontend_tests.txt`, and `results/phase4_e2e_tests.txt`.

## Dashboard capabilities

- **Overview:** immersive Blender-derived shelf-label scene, shared D65/LED appearance switch, live API/SQLite status, rendering conditions, saved red-warning ΔE00, simulated miss rate, latest persisted sustainability output, and recent database jobs.
- **Digital twin:** orbit/zoom Blender GLB shelf, clickable labels, shared D65/LED controls, controlled-scene PNG/contact-sheet previews, six supermarket Cycles images, batch controls, job status, and render history.
- **Colour laboratory:** compute API comparisons; inspect ΔE00, ΔL*, ΔC*, ΔH′, CIELAB, Bradford-adapted XYZ, xy chromaticity, dominant wavelength and excitation purity; explore condition comparisons and the generated CIE diagram.
- **Donation simulator:** configure bounded Monte Carlo requests and observer assumptions; inspect persisted confusion matrices, missed/false triggers, donation/discount/expiry/capacity outcomes, intervals, and sensitivity scenarios.
- **Sustainability:** inspect API-returned saved units and food mass, low/central/high factor scenarios, pipeline capacity sensitivity, provenance, and modeled SDG outcome mapping.
- **Results & exports:** browse paginated API history with filters, search and preview artifacts, download CSV/PNG outputs, start a full analysis job, and retrieve the evidence ZIP.

The Streamlit application at port 8501 remains an independent fallback; it has not been removed.

## API quick reference

All routes are under `/api/v1`. Collection routes use bounded `limit` and `offset` pagination.

| Method and route | Purpose |
|---|---|
| `GET /health`, `/configuration`, `/dashboard` | Service, read-only settings with digest, and actual saved evidence summary |
| `POST /analysis-jobs`; `GET /analysis-jobs[/{id}]` | Queue full pipeline, inspect status and saved job result |
| `POST /render-jobs`; `GET /render-jobs[/{id}]` | Start actual Blender batch and inspect status |
| `GET /renders`, `/renders/{render_id}/{filename}` | List and serve safe render previews |
| `POST, GET /colour-comparisons`; `GET /colour-comparisons/{id}` | Compute and retrieve comparisons; list supports `illumination_id` filtering |
| `POST, GET /donation-simulations`; `GET /donation-simulations/{id}` | Execute, list, and retrieve seeded donation simulations; list can filter by illumination and recognition |
| `GET /artifacts`, `/artifacts/{name}` | List/download fixed evidence files, including CSV and PNG figures |
| `GET /exports/evidence-package` | Download a ZIP package of the generated evidence, frontend source, screenshots, and completed API render batches |

Invalid IDs, unsupported files, unknown configuration keys, out-of-range values, and unsupported render options return HTTP error responses. No route accepts arbitrary shell commands, uploaded files, or output paths.

## Deployment preparation

```powershell
docker compose up --build
```

Compose defines FastAPI on port 8000, the retained Streamlit fallback on port 8501, and the React dashboard on port 3000. The React Nginx server proxies API requests to FastAPI. Docker was unavailable during local implementation, so image builds and container runtime remain unverified. No cloud deployment is claimed.

Frontend architecture, route-to-API mapping, WebGL fallback, accessibility and responsive layout details are documented in `docs/frontend_architecture.md`.

## Evidence and scientific interpretation

- `results/colour_measurements.csv`, `delta_e_summary.csv`, `chromaticity_data.csv`, `trigger_rates.csv`, `trigger_simulation.csv`, `donation_simulation.csv`, `sustainability_analysis.csv`, and `statistical_summary.csv` are generated from the computation, not dashboard constants.
- Eleven figures in `results/figures/` cover four-color ΔE00, red warning comparisons/components, CIE xy and sRGB gamut, dominant wavelength/purity, trigger-error sensitivity, confusion matrices, capacity, near-expiry outcomes, and sustainability-factor sensitivity.
- Confidence intervals over the four fixed colors are descriptive. Trigger and donation intervals quantify Monte Carlo output under synthetic assumptions only.
- The configured food-mass/emissions calculation is an alternative sensitivity model, not an LCA or Nigam's original equation. The 1.5/2.5/3.5 kg CO₂e/kg factors are explicit illustrative scenarios around the unchanged central assumption and are not source-measured product factors.
- Configuration history is recorded in `docs/config_history.md`; spectral provenance is recorded in `docs/spectral_sources.md`.

The supplied execution guide, assignment/rubric, ToC images, and Nigam paper are now preserved in `reference_materials/`; `report_inputs/` contains the Claude research brief, source notes, faculty mapping, results/limitations, and scope reconciliation. The single organized handoff package records the remaining two local paper-PDF gaps and their verified full-text links.

## Important: which Blender file to open

For the supermarket demonstration, open **`blender/q3_supermarket.blend`**. It contains the fully modelled retail scene and the separate controlled research measurement scene. The file **`blender/q3_project.blend`** is the compact 12-condition measurement source; it is intentionally a plain shelf test fixture, not the cinematic supermarket.

The supermarket file opens in the hero-camera view. To switch its visible store lighting:

1. Open Blender's **Scripting** workspace.
2. In the Text Editor, open the embedded **Q3 Lighting Lab.py** text and press **Run Script** once.
3. Return to the 3D View, press **N**, and select **Q3 Research**.
4. Click **L1 D65**, **L2 4000 K**, or **L3 3000 K**. The scene lights and world update; press **F12** to render the current camera under that condition.

These Blender/Three.js lighting controls are intentionally visible RGB presentation presets, not spectral lamp emulation or measured store-light data. The dashboard shows the actual twelve Blender condition renders beside the interactive model; the Python colour-science analysis is the numerical source of truth.
