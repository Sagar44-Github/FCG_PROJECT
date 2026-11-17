# Spectral sources and model definition

## D65 and observer

The primary source is the CIE's `CIE_std_illum_D65.csv` (CIE 2019 dataset, DOI 10.25039/CIE.DS.hjfjmt59). The file contains the relative spectral power distribution at 1 nm steps from 300 to 830 nm. The CIE 1931 2° standard colorimetric observer is `CIE_xyz_1931_2deg.csv` (CIE 2019 dataset, DOI 10.25039/CIE.DS.xvudnb9b), also at 1 nm steps, over 360–830 nm. Both local CSV files are raw, headerless CIE downloads; `results/run_metadata.json` records checksums. The engine integrates their common 380–780 nm interval at 1 nm intervals. The relative SPD is normalized in each XYZ integration so that a perfect diffuser has Y=100. The source's tabulated D65 is used directly for L1; no 6500 K blackbody or LED substitutes for it.

## LED scenarios

No measured store-lamp spectrum was supplied. L2 and L3 are reproducible, parameterized phosphor-converted LED approximations. Each is the nonnegative weighted sum of three Gaussian bands: blue pump (450 nm centre, 17 nm sigma), broad green/yellow phosphor (555 nm, 72 nm), and red tail (615 nm, 48 nm). An optimizer fits the band weights to the Planckian-locus xy of a Planck radiator at the configured 4000 K or 3000 K target. The result is normalized to 100 at 560 nm. This matching targets chromaticity/CCT only; it does not create a measured LED SPD, specify CRI, or describe a particular shop fixture. The approximated spectra may have different metameric effects from real lamps sharing a CCT.

## Reflectance reconstruction and print response

An sRGB hex triplet is linearized and converted to D65 XYZ using the IEC sRGB matrix. Since three tristimulus values do not determine a unique reflectance spectrum, a bounded least-squares reconstruction selects a smooth metamer over 380–780 nm. It minimizes D65 XYZ mismatch with a second-difference smoothness penalty and weak reflectance prior. `d65_reflectance_reconstruction_error_xyz` makes this reconstruction residual visible in the measurement CSV.

The virtual printed label applies configured synthetic absorbance transfer: reflectance is transformed to absorbance `A=-ln(R)`; effective ink density is multiplied by 1.06; a small blue-band absorbance term is added; and substrate reflectance is set to 0.96. Reflectance is bounded to [0.005, 0.995]. These values are configurable assumptions, not a printer profile, measured paper reflectance, or claim about a real print process. Consequently, the ΔE results describe this modeled transfer only. Source and print spectra are each integrated under the same illumination and converted to CIELAB relative to that illuminant's perfect-diffuser white before CIEDE2000 comparison.

## Colorimetric calculations

The observer is CIE 1931 2°. XYZ integration uses the official tabulated matching functions. Lab conversion uses the illuminant-specific normalized XYZ white. The CIEDE2000 implementation follows Sharma, Wu and Dalal's implementation notes and uses default `kL=kC=kH=1`. The result includes signed ΔL*, adjusted ΔC′ and ΔH′ terms plus unadjusted ΔC*. When comparing across illuminations, a separate Bradford transform adapts both spectra from the scenario white to D65; this adapted metric is supplemental, while the primary within-condition ΔE00 uses the common condition white directly. Chromaticity is x=X/(X+Y+Z), y=Y/(X+Y+Z). Dominant wavelength is the intersection of the ray from the illuminant white through the stimulus with the spectral locus; for purple-line colors, the complementary wavelength is reported. Excitation purity is the ratio of white-to-sample distance to white-to-locus intersection distance.

## Sources

- CIE, [CIE standard illuminant D65 dataset](https://www.cie.co.at/datatable/cie-standard-illuminant-d65), DOI 10.25039/CIE.DS.hjfjmt59.
- CIE, [CIE 1931 colour-matching functions, 2 degree observer](https://www.cie.co.at/datatable/cie-1931-colour-matching-functions-2-degree-observer), DOI 10.25039/CIE.DS.xvudnb9b.
- ISO/CIE 11664-2:2022, [Colorimetry — Part 2: CIE standard illuminants](https://www.iso.org/standard/77215.html).
- G. Sharma, W. Wu and E. N. Dalal, [The CIEDE2000 Color-Difference Formula: Implementation Notes, Supplementary Test Data, and Mathematical Observations](https://www.ece.rochester.edu/~gsharma/ciede2000/ciede2000noteCRNA.pdf), *Color Research & Application*, 30(1), 21–30, 2005, DOI 10.1002/col.20070.
