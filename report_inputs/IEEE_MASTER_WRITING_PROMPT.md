# IEEE paper-writing prompt for Claude

You are preparing the complete IEEE-style journal paper for the Q3 software-only computational research project. Use the attached implementation and evidence package as the source of truth. Do not invent missing assignment requirements, bibliographic records, measurements, participant data, or results. First report any missing source files that prevent a defensible claim. The project is not a physical experiment and has no human participants.

## Required deliverables

Produce a complete editable IEEE LaTeX project and compiled PDF in strict IEEE journal format using a two-column layout, IEEE numbered citations, an abstract, Index Terms, complete bibliography and appropriate appendices. Include real figures and tables from the supplied files and correctly sourced mathematical equations. There must be no unfinished sections, empty headings or TODO comments. Return the `.tex`, bibliography, figure assets needed to compile, and final PDF.

## Required paper structure

I. Introduction  
II. Related Work  
III. Problem Formulation and Research Objectives  
IV. System Architecture and Software Design  
V. Computational Methodology  
VI. Donation-Trigger and Retail Impact Modelling  
VII. Implementation and Software Testing  
VIII. Results and Analysis  
IX. Sustainability and SDG Impact  
X. Discussion  
XI. Conclusion and Future Work  
References and appropriate appendices.

Address all five six-mark assessment criteria in the included original assignment/rubric: methodological novelty against the named works; applicability to named retail failure modes; evaluability; sustainability/SDG alignment; Blender feasibility. Also address all software-engineering requirements in `FACULTY_REQUIREMENTS_MAPPING.md`. The physical/user-study evaluation option and a cited carbon-factor audit are not completed; state that clearly rather than claiming full empirical rubric compliance.

## Technical source of truth

Use the exact project question and objectives in `CLAUDE_RESEARCH_BRIEF.md`; methods and equations in `docs/research_methodology.md`; initial values from `config.json`; data source identity and LED/print assumptions from `docs/spectral_sources.md`; all limitations from `FINAL_RESULTS_AND_LIMITATIONS.md`; actual numbers only from the referenced result CSVs; test claims only from retained final logs. Explain that D65 is taken from the tabulated CIE reference SPD and is not approximated by a 6500 K LED. Treat L2/L3 as parameterized LED approximations, the RGB-to-spectrum reconstruction as a selected smooth metamer, and print output as a configurable virtual transfer.

Use CIEDE2000 with (k_L=k_C=k_H=1) and explain the reported ΔL*, raw ΔC*, adjusted ΔC′/ΔH′. The colour values are calculations from sourced CIE tables plus model assumptions, not physical print measurements. Dominant wavelength, excitation purity and xy are computed geometric descriptors.

## Evidence and claims policy

Label every result as sourced, calculated or simulated. Do not present synthetic observer errors as participant results or empirical human classification probabilities. Do not call the alternative inventory simulation Nigam's model or use Nigam's name for its sustainability equation. Do not present scenario CO₂e as realized impact, measured emissions reduction, or a product LCA. Avoid generalizing intervals across the four fixed label colours; do not manufacture statistical significance. State Docker and cloud deployment are unverified unless separate successful execution evidence is supplied.

## Related work integrity

Use the exact identities and evidence status in `LITERATURE_REVIEW_NOTES.md`. Jullien's final text and the Wadhawan preprint are locally included; Pilarski and Li have verified full-text source links but their PDF binaries could not be locally retrieved; the supplied Nigam PDF lacks independent publication metadata and has inconsistencies documented in the notes. Cite from authoritative records. Never describe the supplied Nigam document as independently peer-reviewed without confirmation. The ToC images are for another project: use only the generic report sequence documented in `TOC_STRUCTURE_MAPPING.md`; omit its medical/quantum modules.

## Required completeness checks

- Include all 12 color/illuminant combinations and give special focus to red `#D62828` DONATE NOW.
- Include the actual values and provenance for ΔE00, components, Lab, chromaticity, wavelength/purity, trigger simulation, capacity simulation and sustainability sensitivity.
- Use the genuine Blender supermarket presentation renders, research renders, actual charts, application screenshots and architecture/UML diagrams; captions must state what each image represents.
- Make every numerical table/figure traceable to its CSV, metadata, render or source code.
- Include the React/FastAPI/SQLite architecture, user-space/kernel explanation, routing/query parameters/pagination, security boundary, testing evidence and prepared-but-unverified deployment status.
- End with a clear limitation statement and scientifically appropriate future work, particularly physical spectral/print validation and human observer calibration.
- Reconcile the direct software-only instruction with the original assignment's physical-label wording and “use only Blender” phrase using `IMPLEMENTATION_SCOPE_NOTE.md`; do not conceal the scope change or claim physical validation.
- Do not write as if all five source-paper PDF binaries are inside this package; consult `SOURCE_MATERIALS_INDEX.md` and `MISSING_INPUTS.md`.
