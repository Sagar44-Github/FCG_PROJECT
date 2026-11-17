# Final software verification record

Verification on 2026-11-15 used the current project tree and actual local backend/frontend/Blender runtime. Logs are retained in `results/`.

| Check | Result | Evidence / scope |
|---|---|---|
| Python backend suite | 28 passed; 1 third-party Starlette/httpx deprecation warning | `results/phase4_backend_tests.txt`; API, validation, persistence, native XYZ output, color math, simulation, export and security boundaries |
| Frontend production build | Passed | `results/phase4_frontend_build.txt`; TypeScript + Vite production assets |
| Frontend unit tests | 3 passed | `results/phase4_frontend_tests.txt`; React navigation, refresh/API behavior and fallback handling |
| Playwright browser tests | 3 passed in 2.3 min | `results/phase4_e2e_tests.txt`; all six pages, actual API comparisons/simulation, CSV and evidence export, responsive layout, real preview/GLB, WebGL fallback, and actual 12-case Blender job |
| Research data pipeline | Completed with status code 0 | `results/phase4_pipeline_run.txt`; CSV, figures, tables and metadata regenerated from `config.json` |
| Blender RGB batch | 12 cases rendered; Blender 5.2.3 LTS, Cycles, Standard transform, 8 samples, 960×640 for measurement batch | `results/blender_run_metadata.json`; the browser E2E also submitted and retrieved a fresh 12-case job |
| Supermarket presentation images | Six final images present, 2560×1440 each | `blender/renders/supermarket/final/release_metadata.json` and PNG files |
| Dashboard screenshot set | Seven genuine Playwright captures: six 1440 px page captures and Overview at 390 px | `results/frontend_screenshots/` |

No claim is made that Docker Compose, a container image, or a cloud deployment was executed. No physical experiment, human-participant validation, or empirical model calibration was run. The screenshots are browser screenshots of the running local application; `blender/evidence/` image records are generated scene/configuration evidence, not fabricated Blender UI captures.
