# Computational methodology and equations

## Study boundary

This project is a reproducible software study. Blender renders are RGB visual evidence; the numerical colour measurements come from the Python spectral engine. There were no physical labels, measured lamps, physical printers, store observations, or human participants. Consequently, calculated values describe the defined digital/virtual-print model and simulated outcomes describe stated assumptions only.

## Configuration and inputs

The project-wide parameter source is [`config.json`](../config.json): G/Fresh `#2E9E4F`, Y/Watch `#F5B700`, O/Discount now `#F07C1E`, and R/Donate now `#D62828`; L1 is the tabulated CIE D65 distribution; L2 and L3 are parameterized LED approximations targeting 4000 K and 3000 K. The computational interval is 380–780 nm in 1 nm steps, using the CIE 1931 2° color-matching functions. Local CIE source files and metadata are in `data/` and `docs/spectral_sources.md`.

## Spectral colour and virtual print

For an sRGB channel (c_s\in[0,1]), the IEC sRGB decoding is

\[
c=\begin{cases}c_s/12.92,&c_s\le 0.04045,\\((c_s+0.055)/1.055)^{2.4},&c_s>0.04045.\end{cases}
\]

The linear target is converted to D65 XYZ and a smooth bounded reflectance metamer is reconstructed by constrained least squares with a second-difference smoothness term. This is necessary because three RGB/tristimulus values do not uniquely specify a spectrum. The reconstruction residual is saved per colour.

For reflectance (R(\lambda)), illuminant spectral power (S(\lambda)), and CIE matching functions \(\bar{x},\bar{y},\bar{z}\),

\[
X=k\sum_\lambda S(\lambda)R(\lambda)\bar{x}(\lambda)\Delta\lambda,\quad
Y=k\sum_\lambda S(\lambda)R(\lambda)\bar{y}(\lambda)\Delta\lambda,\quad
Z=k\sum_\lambda S(\lambda)R(\lambda)\bar{z}(\lambda)\Delta\lambda,
\]

where `k` normalizes the perfect diffuser to `Y=100`. The implementation returns XYZ relative to that scale, so a perfect diffuser has `Y=1` in the output CSV. D65 is the official tabulated SPD, not a 6500 K LED or blackbody. L2/L3 are sums of three Gaussian bands (450/17 nm, 555/72 nm, 615/48 nm centre/sigma); the nonnegative weights are fitted to Planckian-locus chromaticity for the configured CCT and the SPD is normalized to 100 at 560 nm. CCT matching does not imply a measured lamp spectrum, CRI, or a particular store fixture.

The virtual print model computes (A(\lambda)=-\ln(R(\lambda))), applies configured density gain 1.06, adds a Gaussian blue absorbance bias of amplitude 0.018 centred at 455 nm with 45 nm sigma, applies the 0.96 substrate factor, and clips reflectance to [0.005, 0.995]. These are synthetic transfer assumptions, not printer or substrate measurements.

XYZ is converted to CIELAB using the perfect-diffuser white under the same illuminant. Within-condition digital-versus-virtual-print CIEDE2000 uses `kL=kC=kH=1`. Reported signed components include `ΔL*=L*print−L*digital`, raw `ΔC*=C*print−C*digital`, and Sharma-style adjusted `ΔC′`, `ΔH′`. The implementation is checked against the included Sharma et al. reference pairs. The current `colour_measurements.csv` stores native digital and virtual-print X, Y and Z, Lab, component terms, and supplementary Bradford-adapted XYZ. Bradford adaptation to D65 does not replace the primary same-illuminant comparison.

Chromaticity is (x=X/(X+Y+Z)), (y=Y/(X+Y+Z)). Dominant wavelength is the intersection of a ray from the illuminant white through the sample with the spectral locus; purple-line cases use complementary wavelength. Excitation purity is the sample-to-white distance divided by white-to-locus-intersection distance. These are geometric descriptors, not independent perceptual observations.

## Observer and donation-trigger model

For each configured label, the model uses its calculated (\Delta E_{00}) in the assumed logistic-shaped error curve:

\[
p_e(\Delta E)=p_0+\frac{p_{max}}{1+\exp[-(\Delta E-m)/s]},
\]

with configured (p_0=0.01), (p_{max}=0.39), (m=8), and (s=3). Given an error, adjacent actions have relative weight 0.70 and nonadjacent actions 0.15, normalized across available alternatives. This chosen curve is not fitted to human responses. The 10,000-trial rows and confusion matrices are pseudorandom draws from this assumed model with deterministic seeds.

## Near-expiry inventory and capacity simulation

Each day has a Poisson arrival count with mean 80. Half of arrivals are configured as red donate-now items; the remainder are split evenly among the other actions. The simulation covers 30 days, with 500 replicates and donation capacities of 10, 25, or 50 units per day. A daily capacity is allocated from the recognized donation queue; overflow can be sent for discount recovery with probability 0.55. Other unsaved items expire. Perfect-recognition runs form a counterfactual baseline. Seed derivation is deterministic and recorded with each output.

This is an explicitly alternative inventory-flow model; the assigned Nigam source and its parameterization were not available in the workspace, so the implementation does not claim to reproduce Nigam's Near-Expiry method. Prices, product-specific shelf life, routing, food-safety eligibility, store operations, and cold-chain effects are outside the model.

## Sustainability sensitivity

For each simulation replicate, the illustrative calculation is

\[
\text{modeled avoided CO₂e}=\text{units saved}\times0.8\;\mathrm{kg/unit}\times f,
\]

where (f\in\{1.5,2.5,3.5\}\;\mathrm{kg\ CO₂e/kg}). The factor values are configurable sensitivity assumptions, not source-measured product factors. Outputs are potential modeled scenario values, not realized impact, product LCAs, or Nigam's score.

## Statistical summaries

The four fixed label colours are the entire comparison set, so the reported (t)-intervals and paired illumination differences are descriptive over (n=4), not population inference. Wilson intervals on trigger trial proportions characterize Monte Carlo sampling under the assumed observer. Donation intervals are empirical 2.5th/97.5th percentiles across seeded replicates. The statsmodels logit regresses assumption-generated trial outcomes on (\Delta E_{00}); it is a software diagnostic, not an empirical human-response model. No empirical significance is claimed.

## Provenance classes

- **Sourced:** local CIE D65 and CIE 1931 2° tables; published CIEDE2000 reference pairs and the cited standards/publications.
- **Calculated:** XYZ, CIELAB, CIEDE2000, chromaticity, wavelength/purity, aggregate statistics, and generated figures from the configured model.
- **Simulated:** action errors, confusion counts, near-expiry unit flows, capacities, and sustainability scenarios.
- **Not measured:** printers, labels, retail luminaires, people, donations, waste, food emissions, or environmental outcomes.

See [`model_assumptions.md`](model_assumptions.md), [`spectral_sources.md`](spectral_sources.md), the result CSVs, and `results/run_metadata.json` for operational parameter and software provenance.
