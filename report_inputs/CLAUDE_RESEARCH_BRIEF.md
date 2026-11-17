# Claude research brief — Q3 expiry-warning shelf-colour study

## Source-of-truth instruction

Write from the included source code, configuration, generated CSVs, figures, test logs, and methodology documents. Treat implementation outputs as authoritative. Do not turn model outcomes into physical or human-study evidence. The supplied assignment PDF/rubric, complete execution guide, both ToC images, and Nigam paper are included. The Jullien final PDF and Wadhawan 2024 CC BY preprint are included. The exact Pilarski and Li publications have been verified, with official full-text links and notes, but their PDF binaries could not be retrieved locally; the final Wadhawan 2025 publisher PDF is also not locally included. See `SOURCE_MATERIALS_INDEX.md` and `MISSING_INPUTS.md`.

## Research question and objectives

**Operational software-only question:** What is the modeled perceptual error (ΔE) between a Blender-rendered expiry-warning colour and its virtual printed shelf-label representation under CIE D65 versus two parameterized store-LED spectra, and how does the resulting assumed observer-error probability affect simulated missed donation triggers? The original assignment wording refers to a physical shelf label and asks whether error predicts misses; physical labels and human observations are explicitly excluded by the team's software-only constraint. This implementation therefore does not make an empirical predictive claim.

The objectives are to: generate Blender label/supermarket scenes; model CIE D65 and two explicitly approximate LED SPDs; implement configurable virtual print response; calculate CIEDE2000 and related colour descriptors; investigate a stated synthetic observer and trigger confusion model; connect errors to an alternative near-expiry donation/capacity Monte Carlo model; quantify illustrative sustainability sensitivity; and provide reproducible application, API, test, and evidence outputs.

## Problem framing and contribution boundary

The software asks whether changes between configured digital label colours and a synthetic print-response under different spectra can be propagated through a transparent donation-trigger model. Its contribution is an integrated, reproducible software pipeline linking spectral colorimetry, virtual print assumptions, observer sensitivity assumptions, inventory capacity, and traceable APIs/visual evidence. This is an implementation-level contribution; compare it with the verified source identities in `LITERATURE_REVIEW_NOTES.md` and avoid a “first” claim or an empirical effect claim.

## Architecture and implementation

`config.json` is the central source for four labels, three illuminants, wavelength range, print transfer, observer assumptions, inventory assumptions, seed, and emissions sensitivity. `colour_engine/` reads the local CIE D65 and CIE 1931 2° data and computes spectra, reflectances, XYZ/Lab, CIEDE2000, chromaticity, dominant/complementary wavelength, purity and Bradford-adapted values. `simulation/` implements assumed classification confusion and inventory flow. `run_pipeline.py` generates CSVs, summary tables, figures, and run metadata. Blender scripts create both a controlled measurement scene and separate photorealistic supermarket presentation scene. Blender's Cycles output is RGB visual evidence; the spectral numerical engine is Python.

FastAPI in `backend/main.py` is the source of truth for computation, validation, artifact access, persistence, and job state. SQLite access is isolated in `backend/database.py`. The React/TypeScript dashboard in `frontend/` consumes API routes for all displayed science values and actions. The prior Streamlit UI remains a fallback. Vite/Nginx provides the frontend; Docker configuration is prepared but runtime/deployment is unverified. UML and data-flow figures are under `docs/diagrams/`.

## Computational colour methodology

L1 is the local CIE tabulated D65 SPD, not a 6500 K light source. L2 and L3 are parameterized three-Gaussian-band phosphor-LED approximations fitted for 4000 K and 3000 K Planckian-locus chromaticity. They are not measured store spectra. Data use the 380–780 nm common computation grid at 1 nm and the CIE 1931 2° observer. XYZ is integrated as (k\sum S(\lambda)R(\lambda)\bar{x},\bar{y},\bar{z}\Delta\lambda), with perfect-diffuser (Y=100). Smooth bounded reflectance is reconstructed from sRGB-derived D65 XYZ because sRGB does not identify a unique spectrum.

Virtual print uses absorbance (A=-\ln(R)), density gain 1.06, a blue absorbance term of 0.018 centred at 455 nm (45 nm sigma), substrate factor 0.96 and reflectance bounds [0.005,0.995]. These values are model assumptions. Same-illuminant CIELAB is compared with CIEDE2000 (k_L=k_C=k_H=1), tested against included Sharma et al. reference pairs. The CSV retains signed ΔL*, raw ΔC*, adjusted ΔC′/ΔH′, xy, Bradford diagnostic, reconstruction error and virtual-print provenance. Chromaticity/wavelength/purity are geometric descriptors.

## Trigger, inventory, statistics and sustainability

Per-class error probability is (p_0+p_{max}/(1+\exp[-(\Delta E-m)/s])), with (p_0=.01,p_{max}=.39,m=8,s=3); the confusion weighting is adjacent .70 and nonadjacent .15. This is an illustrative synthetic observer, not human-participant data. Trigger simulations use 10,000 trials per label/illuminant.

Inventory arrivals are Poisson(80/day), 50% red donation candidates, 30 days, capacities 10/25/50 units/day and 500 seeded replicates. Discount recovery is Bernoulli(.55). Perfect recognition is a counterfactual; simulated errors use the stated confusion model. This is not Nigam's model. The supplied Nigam copy is included, but its capacity and sustainability inputs do not provide a sufficiently sourced, independently reproducible match to this implementation. Sustainability is an alternative model: saved units × 0.8 kg/unit × illustrative factor 1.5/2.5/3.5 kg CO₂e/kg; it is not an LCA or observed impact.

Four-colour intervals describe this fixed set only. Trigger Wilson intervals quantify Monte Carlo draws from assumed probabilities; inventory intervals are seeded replicate percentiles. The logit coefficients are fitted to assumption-generated trials, not empirical human data. Do not claim empirical predictive validity, infer population effects, or manufacture significance.

## Results to use and where to verify

Use `FINAL_RESULTS_AND_LIMITATIONS.md` for selected numeric findings and provenance. Primary row-level files are `results/colour_measurements.csv`, `delta_e_summary.csv`, `chromaticity_data.csv`, `trigger_rates.csv`, `trigger_simulation.csv`, `trigger_logistic_model.csv`, `donation_simulation.csv`, `statistical_summary.csv`, and `sustainability_analysis.csv`. Use source figures from `results/figures/` and Blender/UI images from their organized asset folders. Every table/figure must reference its source artifact and computation.

## Literature review context and limitation

The supplied guide and Nigam bibliography identify the assigned works. Their verified records and comparison are in `LITERATURE_REVIEW_NOTES.md`. Two PDFs are not in the local archive (Pilarski and Li), although their final works and open-access full-text records are verified online. Wadhawan's included file is the 2024 preprint; the final article appeared in 2025. The supplied Nigam copy lacks venue/DOI/date metadata and contains internally inconsistent reference/result details; treat those as claims in the copy, not independently validated literature facts. The ToC images depict an unrelated medical-imaging project; use only their broad chapter sequence. See `IMPLEMENTATION_SCOPE_NOTE.md` and `TOC_STRUCTURE_MAPPING.md`.

## Testing and academic integrity

The Phase 4 verification includes Python pytest, frontend build and unit tests, and Playwright against the live FastAPI/React application. Playwright exercised the six sections, GLB/render previews, actual colour comparison and simulation requests, CSV/evidence download, viewport checks, WebGL fallback, and a completed Blender 12-case render job. Logs are included. Docker, cloud deployment and physical validation are unverified/not conducted. Clearly distinguish sourced reference data, calculated colour results, simulated decisions/inventory, and absent physical/participant evidence.
