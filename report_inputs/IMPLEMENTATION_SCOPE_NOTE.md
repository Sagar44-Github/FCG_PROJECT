# Source-instruction and implementation-scope reconciliation

This note separates source documents from the team's direct implementation constraints. The source files are preserved intact; their instructions are not silently represented as experiments that were performed.

## Binding project constraints

The project instructions given directly by the team require a software-only computational methodology and explicitly prohibit physical labels/lights, camera measurements, instruments, and real human participants. Accordingly, Q3 uses sourced spectral tables, a virtual print-response model, Blender renders, synthetic observer probabilities, and Monte Carlo inventory simulation. Outputs are labeled calculated or simulated. No physical or human-study data are claimed.

## Supplied Q3 execution guide

The original `Q3_Execution_Guide.md` is included unmodified and in full. It contains instructions for printing labels, arranging physical light/camera setups, recruiting at least 30 people, collecting consent/trial responses, and using empirical participant miss rates. Those steps conflict with the software-only requirement and were not carried out. Claude must not write them up as completed methods or report fictional participant results. The computational fallback and actual model assumptions are in `Research_Methodology.md` and the source code.

## Supplied assignment and rubric

`Original_Assignment.pdf` is the supplied `Copy of OE-CCA(30)(d).pdf`; page 1 contains the 30-mark rubric. The Q3 row describes the original question as comparing a Blender-rendered expiry-warning colour with the same colour on a physical store shelf label under D65 versus store LED and asks whether the difference predicts missed donation triggers. The implemented research question is adapted to a virtual printed-label representation, because physical experiments are explicitly prohibited by the team's direct requirement.

The rubric asks for five six-mark areas: (1) methodological novelty against the named literature; (2) applicability to retail failure modes; (3) evaluability through ΔE, user study/A-B RL/statistics; (4) SDG 12.3/13 and auditable carbon/donation/recycling; and (5) feasibility in Blender using Module 3 constructs. The computational project supplies ΔE, simulation/statistics, sustainability sensitivity, and Blender scenes, but it does not have user-study evidence, and its emissions factors are illustrative rather than sourced. The eventual paper must disclose these limits rather than claim the rubric's empirical options were met.

The assignment sheet also includes the wording “Mandatory to use only Blender.” Blender is used for the digital-twin scenes and all analytical/presentation renders, but the requested end-to-end application also uses Python, FastAPI, SQLite, React, and scientific libraries. Do not claim the complete application is Blender-only. If the instructor intended every subsystem to be implemented inside Blender, that requirement conflicts with the separately specified API/backend/frontend stack and needs faculty interpretation; the current implementation follows the team's explicit full-stack software-project requirements while retaining Blender as the graphics/rendering environment.

## Supplied Table of Contents images

Both images are included without alteration. They depict a different project about fingerprint/blood-group prediction and quantum-inspired medical imaging. Their generic chapter organization is useful as report-structure guidance: introduction; literature review; system specification; high- and low-level design; implementation modules; unit/integration/system/acceptance testing; results/analysis; conclusion/future scope. Their topic-specific modules (quantum state preparation, U-Net++, Swin Transformer, PINN, DMD, medical-image texture/classification) are unrelated to Q3 and must not be added or attributed to this project.

See `TOC_STRUCTURE_MAPPING.md` for the Q3 evidence mapped to those generic sections and `FACULTY_REQUIREMENTS_MAPPING.md` for the actual faculty software-engineering checklist.
