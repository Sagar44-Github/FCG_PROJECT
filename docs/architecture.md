# Implemented architecture and execution model

## Components

`config.json` drives label values, illumination definitions and simulation assumptions. `colour_engine` loads the local CIE datasets, builds the D65 and parameterized LED SPDs, reconstructs smooth reflectance, applies the virtual print transfer, converts XYZ/Lab, and calculates CIEDE2000 and chromaticity. `simulation` consumes computed ΔE values for synthetic observer and inventory runs. `run_pipeline.py` writes CSV tables, metadata, statistics and figures. `blender/scripts/render_batch.py` builds the Cycles RGB scene and renders the 12 configured combinations. `backend/main.py` exposes operations through FastAPI, and `backend/database.py` persists jobs and results in SQLite. The primary browser UI is the React/TypeScript client in `frontend/`; the retained `dashboard/app.py` Streamlit client is an independent fallback. Both clients call FastAPI for status, calculations, renders and result files.

The dashboard configuration page is read-only. Analysis and render requests store the SHA-256 digest of the effective central configuration. Donation requests additionally retain request-scoped observer parameters, random seed, capacity, horizon, and replicate count, so a sensitivity run is reproducible without changing the project's initial configuration.

## User mode and kernel mode

The API, Python numerical libraries, Blender render process, and SQLite library run as ordinary user-space processes. They request files, CPU scheduling, memory, and networking through operating-system system calls. The operating-system kernel performs those privileged operations. This project requires no custom kernel-mode code: the research task uses standard file, process, and network services and does not need a device driver or privileged hardware access. Docker can further isolate the API process; it does not move project logic into kernel mode.

## API behavior

OpenAPI and Swagger UI are provided by FastAPI at `/docs`; the schema is at `/openapi.json`. Collection routes accept bounded `limit` and `offset` pagination. Render output paths are constructed from server-generated UUIDs under the project `renders/` directory; requests cannot supply file paths or shell fragments. Blender is invoked with an argument array (no shell) and a timeout. The API runs in user space and records job errors instead of returning fake results.

`POST /api/v1/analysis-jobs` starts a serialized full evidence run, records queued/running/completed/failed state in SQLite, and retains the configuration digest. `POST /api/v1/render-jobs` starts the fixed Blender batch and stores the same status lifecycle. Computed comparisons and donation simulations are saved as result resources. `/dashboard` is an aggregate of saved CSVs and database entries. `/artifacts` exposes only an explicit allow-list; the evidence ZIP is constructed from fixed source/evidence folders.

| Resource | Collection route and filters | Item/action routes |
|---|---|---|
| Analysis jobs | `GET /analysis-jobs?limit=&offset=&status=` | `POST /analysis-jobs`, `GET /analysis-jobs/{id}` |
| Render jobs | `GET /render-jobs?limit=&offset=&status=` | `POST /render-jobs`, `GET /render-jobs/{id}` |
| Colour comparisons | `GET /colour-comparisons?limit=&offset=&illumination_id=` | `POST /colour-comparisons`, `GET /colour-comparisons/{id}` |
| Donation simulations | `GET /donation-simulations?limit=&offset=&illumination_id=&recognition=` | `POST /donation-simulations`, `GET /donation-simulations/{id}` |

The four Pydantic operation/request classes and result response schemas are explicit object-oriented boundary models. Numerical components are single-responsibility modules rather than artificial classes around stateless algorithms. The SQLite module isolates parameterized SQL and converts persisted rows to API records.

## Sandbox and deployment boundary

The render endpoint accepts only the complete supported 12-case batch and a bounded sample count. It writes inside a fixed project directory, uses server-generated job IDs, does not accept uploaded files, and does not invoke a shell. Container deployment runs as an unprivileged UID, keeps the application filesystem read-only where supported, and persists only SQLite data, evidence, and renders in named volumes. Blender is optional for the API; without it a real render job enters `failed` with a diagnostic. API and numerical services continue to work.

Artifact retrieval matches a fixed allow-list; render file names must match a configured color/illumination pattern. The evidence exporter writes a server-built ZIP, never extracts user content. Simulation request ranges are bounded. A single-process guard prevents simultaneous full-analysis jobs because the scientific pipeline writes to the canonical reproducibility outputs. Render jobs use separate UUID directories.

Docker Compose now defines separate dashboard and API services, API health gating, named data/results/renders volumes, read-only service filesystems, dropped capabilities and `no-new-privileges`. Its build/runtime are not reported as validated unless `docker compose up --build` has actually run on a host with Docker.

## Dashboard integration

The React pages are presentation only: Overview requests `/dashboard`; colour comparisons call `POST /colour-comparisons`; full analysis and renders start persisted API jobs; render previews and CSV/PNG downloads are served by API allow-list routes; donation inputs are serialized to `/donation-simulations`; history views use the paginated collection endpoints. The Streamlit fallback follows the same API-owned model. Neither client reads SQLite directly or recomputes scientific values.

## Route map

The API base is `/api/v1`. Health, configuration, dashboard summary, resource collections, file artifacts and evidence export are documented in [`api_reference.md`](api_reference.md) and rendered interactively via Swagger.

## Traceability

| Research claim/output | Implementation | Reproducible evidence |
|---|---|---|
| D65 is a CIE reference SPD | `colour_engine/spectral_model.py` + local CIE CSV | `results/run_metadata.json`, `docs/spectral_sources.md` |
| LED is a model, not a measured store lamp | Gaussian bands fit to a target Planckian xy | Config, spectral documentation, measurement `source_model` |
| Print response is virtual | Bounded reflectance reconstruction + configured absorbance transfer | Config, `colour_measurements.csv`, model assumptions |
| ΔE00 and chromaticity | Conversion and formula modules | Measurement and chromaticity CSVs; published formula cases in tests |
| Trigger errors are simulated | `simulation/observer_model.py` | Trigger confusion table and explicit assumptions |
| Donation bottlenecks are simulated | `simulation/donation_model.py` | Monte Carlo output, fixed seed and capacity sensitivity figure |
| Carbon output is an alternative scenario estimate | Configured mass × emissions factor | Sustainability CSV with formula note |
| Rendering is RGB visualization | Blender scene builder | 12 PNGs, contact sheet, `.blend`, script version |

