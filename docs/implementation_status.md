# Implementation and reproducibility status

| Phase | State | Evidence |
|---|---|---|
| 1. Requirements, environment, traceability | Complete | `docs/architecture.md`, `docs/spectral_sources.md`, configuration and source records |
| 2. Blender digital twin | Complete | Blender 5.2.3 LTS generated `.blend` plus all 12 Cycles PNGs and contact sheet; two API render jobs completed with 12 cases each |
| 3. Illumination and virtual print | Complete | official local CIE datasets, parameterized LED SPDs, bounded reflectance and configured synthetic print transfer |
| 4. Color science | Complete | 12 measurement rows; CIEDE2000 reference cases and independent `colour-science` tests; chromaticity and Bradford adaptation |
| 5. Observer and donation models | Complete | seeded confusion and inventory simulations with perfect/error recognition and three capacities |
| 6. Statistical analysis and figures | Complete | CIs, paired condition comparisons, synthetic logit, Monte Carlo intervals, plots and tables |
| 7. API and SQLite integration | Complete | FastAPI routes, typed request/response schemas, query filters and pagination, SQLite persistence |
| 8. Tests and deployment preparation | Complete | Final Phase 4 suite: 28 pytest tests passed (one third-party deprecation warning); Dockerfile and Compose are prepared. Docker runtime is unverified. |
| 9. Full evidence run | Complete | `results/` and `renders/`; seeds/configuration/software versions retained |
| 10. Demonstration application | Complete | React/TypeScript dashboard with six API-backed sections, interactive R3F scene, responsive layout, real comparisons/simulations/history/render previews/exports; Streamlit is retained as fallback |
| 11. Research figures and final guidance | Complete | Eleven computation-backed plots; faculty demo guide; viva notes; API route reference |
| 12. Deployment runtime | Prepared / unverified | Compose includes dashboard and API; Docker CLI is unavailable locally, so no image/runtime test is claimed |
| 13. Phase 3 frontend verification | Complete | `npm run build`, 3 Vitest tests, and 3 Playwright tests passed, including an actual 12-case Blender render; Phase 4 repeated the production build, frontend tests, all-six-page browser workflow, exports, responsive checks, GLB interaction and WebGL fallback. Desktop screenshots (1440 px) for all six pages plus Overview mobile (390 px) are under `results/frontend_screenshots/`. |

This project has not been deployed to a cloud environment. No physical or human-subject experiment was run. Live Blender UI screenshots were not saved in the initial renderer evidence; actual `.blend`, Cycles renders, and scene-derived node/settings records are supplied and identified as such in `docs/blender_evidence.md`.

## Final live verification

- FastAPI health endpoint returned `ok`; the Streamlit health endpoint returned HTTP 200.
- A full analysis job completed through the API, and a dashboard-initiated Blender job completed all 12 configured colour/illumination cases.
- Dashboard pages (overview, colour analysis, renders, donation/sustainability, and results/export), colour comparison, donation simulation, perfect-recognition mode, and evidence export were exercised with Streamlit AppTest without application exceptions.
- Phase 4 Playwright checks exercised all six pages against FastAPI, loaded the Blender-exported GLB and actual PNG previews, persisted a colour comparison and seeded donation simulation, downloaded CSV and evidence ZIP, checked mobile layout, verified the WebGL fallback, and completed a live 12-condition Blender render job. Screenshots are saved under `results/frontend_screenshots/`.
- Current final logs: `results/phase4_backend_tests.txt`, `results/phase4_frontend_build.txt`, `results/phase4_frontend_tests.txt`, `results/phase4_e2e_tests.txt`, and `results/phase4_pipeline_run.txt`. These checks validate software behavior and reproducible model execution; they do not validate human perception or physical printer/lighting behavior.
