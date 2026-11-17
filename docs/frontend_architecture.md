# Premium dashboard architecture

## Scope and source of truth

The React application is a new presentation layer over the existing FastAPI/SQLite and scientific pipeline. It does not replace the Python colour engine, Blender renderer, persisted CSVs, or simulation code. The existing `dashboard/app.py` remains available as a Streamlit fallback at port 8501.

The React application reads the configuration, dashboard summary, history collections, render catalog, and allow-listed artifacts through `/api/v1`. User actions POST to the existing comparison, render-job, donation-simulation, and analysis-job routes. Analysis values and impact calculations are not reconstructed in browser code. The simulation API now returns `mean.food_mass_saved_kg` and its 95% interval alongside the existing CO₂e scenarios, so the sustainability interface can show the backend result directly.

## Frontend structure

```text
frontend/
├── src/
│   ├── components/       Persistent layout, accessible primitives, R3F scene
│   ├── lib/              Typed API client, response types, CSV reader
│   ├── pages/            Overview, digital twin, colour lab, donation,
│   │                     sustainability, and results/export sections
│   ├── App.tsx           App-level API bootstrap and lazy section switching
│   └── index.css         Design tokens, responsive layout, reduced motion
├── Dockerfile            Vite build and unprivileged Nginx runtime
└── nginx.conf            SPA fallback and same-origin FastAPI proxy
```

The shell keeps the six-section navigation, API status, configuration digest, refresh, and Streamlit fallback link mounted across section changes. Each research section is lazy-loaded. The R3F scene is separately lazy-loaded and is mounted only on Overview and Digital Twin. Motion supplies short section entrance and drawer transitions; Recharts renders interactive graphs; Tailwind CSS is present in the build toolchain while project-specific layout and chart styling use explicit CSS tokens. Label artwork uses canvas textures inside Three.js; the scene avoids DOM portals so route changes remain clean.

## Route and API mapping

| Interface section | Live backend data and actions |
|---|---|
| Overview | `/health`, `/configuration`, `/dashboard`, most recent `/donation-simulations`, and backend render URLs |
| Digital Twin | `/configuration`, `/dashboard`, `/renders`, `/render-jobs`, `/render-jobs/{id}`; POST `/render-jobs` |
| Colour Laboratory | `/configuration`, `/artifacts/colour_measurements.csv`, `/artifacts/chromaticity_data.csv`, `/artifacts/figures/chromaticity_diagram.png`; POST `/colour-comparisons` |
| Donation Simulator | GET and POST `/donation-simulations`, paginated history and request-scoped observer parameters |
| Sustainability | Latest saved `/donation-simulations`, `/artifacts/sustainability_analysis.csv`, and configured factor note |
| Results & Exports | Paginated analysis, render, comparison and simulation collections; `/artifacts`; CSV/PNG downloads; `/exports/evidence-package`; POST `/analysis-jobs` |

Vite proxies `/api/*` to `http://127.0.0.1:8000` in local development. The production Nginx configuration proxies the same path to `q3-api`, avoiding an extra browser origin and CORS configuration. `VITE_API_BASE_URL` can set a deployment prefix when needed.

## Spectral Observatory scene

The interactive supermarket shelf is a presentation model loaded from `frontend/public/assets/supermarket/verdant_market.glb`; Blender exports a focused 8–9 m shelf segment from `HERO_SUPERMARKET` (about 4.1 MB). It is not a replacement for the saved `.blend` scene or Cycles outputs. Label actions and illumination conditions are read from the active project configuration. The named `Q3_LABEL_G/Y/O/R_PANEL` meshes are hit-tested so label clicks select the matching action; orbit and zoom control the camera; illumination controls adjust a visual light proxy. The selected authoritative research render still comes from the FastAPI catalog. Six authored supermarket Cycles views also appear as local render evidence across the six pages and through the API artifact allow-list.

The scene has no remote HDRI or texture dependency; its generated PBR textures are packed in the GLB. The canvas uses a capped device pixel ratio, demand-based rendering, no auto-rotation, and no animation loop. The code is lazy-loaded on Overview and Digital Twin, with an API render or local Cycles image fallback if WebGL is unavailable.

## Design and interaction rules

- Midnight graphite, restrained cyan/violet indicators, hairline separators, and the four configured label colours form the visual system. Red is emphasized in the research result view while other semantic colours retain their configured meaning.
- Space Grotesk is used for display headings, Inter for interface text, and JetBrains Mono for measurements, identifiers, and configuration digests. These are loaded as web fonts with system fallbacks.
- Navigation, selects, render selection, pagination, simulation submission, history filters, CSV/PNG downloads, evidence ZIP, and analysis/render job actions are real buttons or links. A status label reflects the API/job state; no synthetic progress percent is shown.
- Empty datasets remain empty states. The dashboard does not populate a graph or metric with a sample value when a saved file or record is unavailable.
- Observer error, synthetic print transfer, LED approximation, food mass, and emissions-factor assumptions are shown beside results. The Blender RGB scene is labelled as a visualization; CIE spectral calculations remain attributed to the Python service.
- A `prefers-reduced-motion` rule reduces transitions globally. The 3D model has no unattended movement; all camera movement follows direct user input.

The original 20 UX principles are addressed through these concrete controls: consistent navigation and tokens; readable labels, units, and hierarchy; disciplined grid and whitespace; visible controls and focus rings; immediate loading/success/error state; familiar scientific terminology; request validation; expanded observer parameters; quick defaults plus advanced controls; keyboard-operable buttons and selects; reduced-motion support; responsive breakpoints; API-backed values; provenance notes; and explicit empty and failure states. Animations are brief and never gate a request.

## Responsive behavior

The desktop layout uses a 246 px persistent sidebar and a constrained content canvas. At tablet widths, analytical grids collapse and the 3D scene moves above its controls. At mobile widths, the sidebar becomes a dismissible drawer, metric grids use two columns, tables scroll horizontally, and long forms stack. The CSS defines breakpoints at 1279, 1023, 767, and 420 px; the intended QA targets are 1440 px, 1280 px, tablet, and 390 px mobile.

## Verification

- `npm run build`: TypeScript type check and Vite production build.
- `npm test`: Vitest/Testing Library checks shell navigation across all six sections, API outage/fallback behavior, and backend refresh requests.
- Python API tests retain coverage for result persistence and request validation; the added food-mass response fields are included in the seeded donation API test.
- Playwright browser QA visited all six sections against the live API, loaded a real Blender preview, persisted a colour comparison and donation simulation, submitted a one-sample 12-condition Blender job and verified its completion, downloaded the evidence ZIP, checked responsive widths from 390 px to 1280 px for horizontal overflow, and verified the Blender PNG fallback when WebGL is unavailable. Overview and Digital Twin desktop screenshots and the mobile Overview screenshot are saved under `results/frontend_screenshots/`.

The Nginx container and Compose wiring are prepared, but Docker image/runtime verification depends on Docker being available. The local Vite + FastAPI browser run is the executable demonstration path.
