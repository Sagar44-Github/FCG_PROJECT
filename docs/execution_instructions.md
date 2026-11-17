# Execution instructions

1. Install Python and frontend dependencies with `docs/setup_instructions.md`.
2. Start the API from the project root: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`.
3. Start the primary dashboard in a second terminal: `cd frontend; npm run dev -- --host 127.0.0.1 --port 5173`.
4. Open `http://127.0.0.1:5173`; Swagger/OpenAPI is `http://127.0.0.1:8000/docs`.
5. The Streamlit fallback is optional: set `Q3_API_URL=http://127.0.0.1:8000` and run `python -m streamlit run dashboard/app.py`.
6. Regenerate all computational tables/figures with `python run_pipeline.py`.
7. Run the fixed render batch with `blender -b blender/q3_project.blend --python blender/scripts/render_batch.py -- --output-dir renders --samples 8` (the project configuration may use a higher sample setting for a particular run).
8. Generate the six luxury presentation renders by following `docs/supermarket_visual_pipeline.md`.

All calculations and persistent job status are API/backend-owned. Render jobs can take minutes; monitor `GET /api/v1/render-jobs/{job_id}`. Existing generated outputs are included so the application can be demonstrated without first regenerating them.
