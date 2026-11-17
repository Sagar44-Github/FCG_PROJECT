# Faculty demonstration guide

## Before the demonstration

1. Install the project requirements from the repository root.
2. Start FastAPI in one terminal: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`.
3. Start the primary React dashboard in a second terminal: `cd frontend; npm ci; npm run dev -- --host 127.0.0.1 --port 5173`.
4. Open `http://127.0.0.1:5173`. Swagger is available at `http://127.0.0.1:8000/docs`. The Streamlit fallback can be launched separately with `python -m streamlit run dashboard/app.py`.
5. For a live Blender render demonstration, confirm Blender is installed and set `BLENDER_EXECUTABLE` if needed. A 12-case Cycles render can take several minutes. Existing checked-in PNGs and the `.blend` remain available if time is limited.

## Suggested 8–10 minute walkthrough

### 1. Overview (1 minute)

Show API status, the generated render count, analysis run date, ΔE00 summary, and recent persisted processing jobs. Point out that the values come through the dashboard API and reflect saved CSV/database records.

### 2. Configuration and colour analysis (2 minutes)

Open **Colour Laboratory**. Show all four exact hex swatches and the three illumination conditions. Explain that configuration is read-only in the app and each comparison/job stores a configuration digest. Select red `R` to demonstrate the donate-now case. Review ΔE00, ΔL*, ΔC*, ΔH′ and the chromaticity/wavelength values. Use the CSV download control to obtain the actual table.

The **Run full colour analysis** button starts the real full pipeline and records an analysis job. It regenerates the results and figures; it does not invent progress or substitute hardcoded results.

### 3. Blender digital twin (1–2 minutes)

Open **Digital Twin**. Rotate/zoom the Blender-exported supermarket shelf, switch illuminant views, show the contact sheet and individual color/illumination previews. To demonstrate generation, start the batch and observe the persisted job ID/status. State that Blender's Cycles result is an RGB visualization; the spectral calculations are performed by the Python engine. The CIE D65 illuminant in Blender is a neutral RGB visualization, not a spectral render.

### 4. Observer and inventory simulation (2 minutes)

Open **Donation Simulator**. Start with the defaults. Identify the seed, replicate count, daily capacity, arrivals and horizon. Expand the observer parameters to show the synthetic error curve and confusion weights. Run a small seeded scenario and show the calculated confusion matrix, missed/false trigger counts, donation, discount recovery and expired units.

Explain that “perfect” recognition is a counterfactual baseline and “synthetic observer errors” are assumptions rather than participant observations. Change capacity to illustrate the model's bottleneck sensitivity.

### 5. Sustainability and exports (1–2 minutes)

Show the low/central/high emission-factor scenarios and their configured assumptions in **Sustainability**. The displayed calculation is `units saved × product mass × scenario factor`; it is not a measured reduction or life-cycle assessment. Open **Results & Exports**, review persisted histories and pagination, download a CSV/figure, and optionally download the evidence ZIP.

### 6. Engineering evidence (1 minute)

Open Swagger UI. Demonstrate `GET /api/v1/health`, `GET /api/v1/dashboard`, and a paginated collection such as `GET /api/v1/colour-comparisons?limit=5&offset=0`. Show that invalid input receives a validation response. Point to the editable and rendered UML diagrams, test report, and deployment diagram.

## Expected interpretation

- Four configured labels are the descriptive comparison set; confidence intervals across those four colors should not be generalized to a population.
- L2/L3 are parameterized LED approximations, not measurements of specific retail lamps.
- The virtual print and observer models are assumptions. This project contains no physical, store, printer, or human-participant measurements.
- Docker Compose is prepared but has not been claimed as executed unless a working Docker runtime has subsequently been used.
