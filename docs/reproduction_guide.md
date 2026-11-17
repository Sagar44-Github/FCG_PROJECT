# Reproduction guide

## Fixed data and model inputs

Retain the supplied `config.json` unchanged to reproduce the current run. Its seed is `20261115`; local CIE CSVs are under `data/`; their identities and working wavelength grid are recorded in `docs/spectral_sources.md`. No external network download is needed for the scientific pipeline.

## Regenerate evidence

Run `python run_pipeline.py` at the project root. The process writes the 12 row colour table, illuminant and reflectance spectra, summary tables, deterministic observer trials, 500-replicate donation/capacity outputs, sustainability sensitivity, metadata and Matplotlib figures to `results/`. For the Blender controlled scene, run the command in `README.md`; it creates the 12 RGB measurement visualization PNGs and contact sheet. For presentation renders and GLB, follow `docs/supermarket_visual_pipeline.md` and `README.md`.

Run tests using `python -m pytest -q` and, in `frontend/`, `npm ci`, `npm run build`, `npm test`, and `npm run test:e2e`. The provided Phase 4 logs record the executed test session; rerunning may create additional SQLite jobs and UUID render directories.

## Reproducibility and interpretation

`results/run_metadata.json` records config snapshot, seed, data checksums and versions. `results/blender_run_metadata.json` records the controlled Blender run. Rendered PNGs are RGB visualization outputs; only the Python spectral engine calculates colorimetry. The emission factors, print transfer, LED spectra and observer curve are model assumptions. Current seed/config data reproduce software outputs, not physical or human observations.
