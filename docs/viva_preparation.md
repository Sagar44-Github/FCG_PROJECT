# Viva preparation notes

## Research question and scope

The software compares configured digital shelf-label colors with a virtual print-response representation under standard CIE D65 and two explicitly approximate LED spectra. It explores whether a ΔE00-driven synthetic observer model can affect simulated donation decisions and inventory outcomes. It is a computational study only: there are no physical labels, measured lamps, human participants, or store observations.

## Reproducible color pipeline

1. `config.json` provides the four original sRGB colors, D65/L2/L3 definitions and initial model assumptions.
2. The spectral module reads the official CIE D65 spectral table and CIE 1931 2° color-matching functions. Computations use 380–780 nm at 1 nm spacing. L2 and L3 are normalized parameterized phosphor-LED approximations; they are not claimed to match a measured product.
3. The smooth bounded reflectance reconstruction represents the digital target. A configured absorbance-density transfer creates the virtual printed reflectance. No printer or substrate was physically measured.
4. For each reflectance and illuminant, spectral integration produces XYZ, normalized by the illuminant white, and then CIELAB. CIEDE2000 calculates the difference between the digital and synthetic-print Lab values. A Bradford adaptation result is retained as an additional diagnostic.
5. Chromaticity `x=X/(X+Y+Z)` and `y=Y/(X+Y+Z)` are reported. Dominant wavelength is found along the chromaticity geometry relative to the illuminant white; out-of-gamut colors can be reported as complementary wavelength. Excitation purity is the corresponding distance ratio.

The tested CIEDE2000 implementation follows the published formula and is checked against reference pairs. The formula combines lightness, chroma and hue terms with weighting and interaction terms; it is not a simple Euclidean RGB distance. The CSV contains raw ΔL*, raw ΔC*, CIEDE2000-adjusted ΔC′/ΔH′ and the final ΔE00.

## Observer and inventory model

The assumed classification error probability is:

`p(error | ΔE) = p0 + pmax / (1 + exp(-(ΔE - midpoint) / scale))`.

The initial values are `p0=0.01`, `pmax=0.39`, `midpoint=8`, and `scale=3`. Given an error, adjacent and nonadjacent actions receive configurable relative weights. These values are illustrative sensitivity assumptions. They were not estimated from human data. The dashboard lets an operator override them for one simulation request; it records the complete effective parameter set, random seed, and configuration digest.

The inventory scenario samples daily near-expiry arrivals from a Poisson distribution (initial mean 80/day); 50% are red donation-trigger items. It compares perfect recognition and simulated errors, applies daily donation capacities, models 55% recovery of discount candidates, and counts unsaved units as expired stock. The original capacity sweep is 10, 25, and 50 units/day over 30 days with 500 replicates per condition. Seeds are derived deterministically.

## Sustainability model

The alternative estimate is:

`modeled avoided CO₂e = units saved × 0.8 kg/unit × emissions factor (kg CO₂e/kg)`.

The configured central factor remains 2.5. Low/high dashboard scenarios use 1.5 and 3.5 as ±40% sensitivity bounds. These are explicit illustrative model assumptions, not published product-specific footprints. The score is not Nigam's formula, an LCA, or a claim of realized environmental benefit.

## Statistics and interpretation

- ΔE00 summaries and intervals are descriptive over the four configured colors; they are not population estimates.
- Trigger-error Wilson intervals describe Monte Carlo sampling from the assumed observer model.
- Donation intervals are percentiles across seeded simulation replicates.
- The logistic output models generated assumptions and trial draws. Its coefficient or p-value is not evidence of human perceptual response.
- A simulated error rate should not be presented as a forecast for actual staff or shoppers.

## Application and software design

- The React/TypeScript dashboard is the primary client of FastAPI. It requests result data, job status, previews and exports; it contains no independent color or inventory calculation. The Streamlit UI remains available as a fallback client.
- FastAPI uses typed Pydantic requests, validation, REST routes, status resources, query filters, bounded `limit`/`offset`, structured errors and SQLite persistence.
- The science implementation is modular and mostly functional; Pydantic request/response classes provide object-oriented boundary models. SQLite access is isolated in a repository module.
- Blender and the API are user-space processes. Standard filesystem, process, memory, and network access is delegated to the OS kernel. This project needs no kernel driver or privileged device access.
- Blender is launched with a fixed executable and argument array, server-generated job ID path and timeout. Render names and result downloads are allow-listed; arbitrary shell commands and user-selected paths are not accepted.
- Docker Compose prepares separate API and dashboard services, a health check, persistent volumes, an unprivileged API UID, a read-only root filesystem and reduced capabilities. If asked, distinguish this deployment configuration from a successful build/deployment, which requires an available Docker runtime.

## Demonstrable evidence

- Twelve Blender renders and `blender/q3_project.blend`.
- `results/colour_measurements.csv`, `delta_e_summary.csv`, `chromaticity_data.csv` and the 11 result figures.
- `trigger_simulation.csv`, `trigger_rates.csv`, `donation_simulation.csv`, `statistical_summary.csv` and `sustainability_analysis.csv`.
- Run metadata with configuration, CIE data checksums, software versions and deterministic seed.
- Test suite output in `results/test_results.txt`; API definitions in Swagger; six editable/rendered architecture diagrams.

## Likely viva questions

**Why use D65 instead of a 6500 K LED?** D65 is loaded from the recognized reference SPD. CCT alone does not determine the spectral power distribution. Blender's RGB scene is labeled only as a visualization.

**Are the LED spectra real retail spectra?** No. They are documented, parameterized approximations targeting the stated CCT range. The output should be interpreted as sensitivity to the selected modeled SPD.

**How is the print model validated?** It is not validated against a real printer. It is a configurable virtual absorbance transfer and all derived values are labeled synthetic. Physical reflectance data would be needed for empirical validation.

**Does ΔE00 predict actual donation misses?** This software demonstrates a modeled link by making action confusion a function of ΔE00. The curve has no human calibration, so the project cannot establish predictive performance for real people.

**What is the main practical limitation?** The color, LED, virtual-print, observer, inventory, and emissions assumptions need external calibration/data before claims about actual retail performance or sustainability can be made.

**Why keep both React and Streamlit?** React is the primary interface for the interactive 3D demonstration and API-backed research workflows. Streamlit is retained as a fallback. Both call FastAPI, which owns calculations, persistence, validation, exports and job status.
