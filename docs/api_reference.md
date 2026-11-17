# API reference

FastAPI runs at `http://127.0.0.1:8000`. Swagger UI is `/docs`, OpenAPI is `/openapi.json`, and all application routes are versioned under `/api/v1`.

## Service and configuration

| Method | Route | Response |
|---|---|---|
| GET | `/health` | Service state, project version, SQLite and user-space mode |
| GET | `/configuration` | Read-only `config.json`, SHA-256 digest, configuration mutability note |
| GET | `/dashboard` | Actual saved summary, render inventory, job history and evidence timestamp |

The API does not expose a configuration mutation endpoint. Analysis/render job requests retain the effective config digest. Donation simulation results additionally retain all request-scoped observer and scenario parameters. The `mean.food_mass_saved_kg` and `ci95_percentile.food_mass_saved_kg` values are derived from simulated saved units multiplied by configured average product mass; they are modeled outputs, not measured waste reductions.

## Computation and job resources

| Method | Route | Request/query |
|---|---|---|
| POST | `/analysis-jobs` | `donation_replicates` (1–2000; default 500). Returns `202` and a queued job. |
| GET | `/analysis-jobs` | `limit` 1–200, `offset` ≥0, optional `status` |
| GET | `/analysis-jobs/{job_id}` | Persisted full-analysis status/result/error |
| POST | `/render-jobs` | `render_all` must be true; `samples` 1–256. The server fixes the script and output directory. |
| GET | `/render-jobs` | `limit`, `offset`, optional `status` |
| GET | `/render-jobs/{job_id}` | Persisted Blender job status/result/error |
| POST | `/colour-comparisons` | `colour_id`, `illumination_id`; persists a newly computed comparison |
| GET | `/colour-comparisons` | `limit`, `offset`, optional `illumination_id` |
| GET | `/colour-comparisons/{comparison_id}` | One persisted comparison |
| POST | `/donation-simulations` | illumination, recognition, capacity, horizon, arrivals, replicates, seed, optional `observer_parameters` |
| GET | `/donation-simulations` | `limit`, `offset`, optional `illumination_id` and `recognition` |
| GET | `/donation-simulations/{simulation_id}` | One persisted simulation, confusion matrix, Monte Carlo intervals and sustainability scenarios |

Observer override fields: `base_error_probability`, `maximum_additional_error_probability`, `delta_e_midpoint`, `delta_e_scale`, and `confusion_weights` (`adjacent`, `nonadjacent`). Probabilities are validated; midpoint is nonnegative; scale and relative confusion weights are positive. The full effective values and config digest are part of the persisted result.

## Results and files

| Method | Route | Behavior |
|---|---|---|
| GET | `/renders` | Lists existing baseline and completed job PNGs |
| GET | `/renders/{render_id}/{filename}` | Serves validated color/illumination PNG or baseline contact sheet |
| GET | `/artifacts` | Lists allow-listed result files and availability/size |
| GET | `/artifacts/{name}` | Downloads one available allow-listed CSV, JSON or PNG |
| GET | `/exports/evidence-package` | Generates a ZIP of code, assumptions, local CIE datasets, frontend/screenshots, generated outputs and completed API render batches |

Paths are resolved from a fixed server allow-list and checked to stay within project directories. The API accepts no arbitrary paths, uploads, or command strings.

## Errors and status codes

- `200`: retrieval succeeded.
- `201`: a synchronous comparison or donation simulation was created.
- `202`: render or full-analysis job was accepted; check its resource for status.
- `404`: missing job, result, render, or artifact.
- `409`: a full analysis is already queued/running.
- `422`: invalid schema, unsupported color/illumination, invalid filter, or unsupported render option.
- `500`: unexpected computation or persistence failure, with a non-sensitive response detail and server-side traceback logging.

Collection resources return `{total, limit, offset, items}`. SQLite queries use parameterized values and sort newest first.
