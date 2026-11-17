# HANDOFF_MANIFEST

Generated: 2026-11-15

## Archive inventory

- Archive: `Q3_COMPLETE_IEEE_RESEARCH_HANDOFF.zip`
- Archive size (bytes): `000094628284`
- Files: 308 (includes this manifest)
- Folders: 68
- File-type counts (manifest excluded):
- `.blend`: 4
- `.conf`: 1
- `.css`: 2
- `.csv`: 30
- `.example`: 2
- `.glb`: 2
- `.html`: 1
- `.json`: 15
- `.md`: 51
- `.pdf`: 4
- `.png`: 98
- `.puml`: 6
- `.py`: 42
- `.sql`: 1
- `.svg`: 11
- `.ts`: 6
- `.tsx`: 13
- `.txt`: 9
- `.yml`: 2
- `[no extension]`: 7

## Major included evidence

- Supplied assignment/rubric, complete guide, two original ToC images, and full Nigam/Jullien/Wadhawan-preprint PDFs. Pilarski and Li have verified public full-text links but their PDF binaries could not be retrieved locally.
- Complete Python scientific engine, FastAPI backend, SQLite schema, Streamlit fallback, React/TypeScript frontend, Blender scripts/assets and test source.
- Both saved Blender projects (`q3_project.blend`, `q3_supermarket.blend`), all 12 controlled measurement renders, six 2560×1440 supermarket production renders, and Blender-exported GLB.
- Actual result CSVs, 11 scientific charts, 6 architecture/UML diagrams, seven live-app Playwright screenshots (six desktop pages at 1440 px and Overview at 390 px), run metadata and executed Phase 4 logs.
- Claude's five report materials plus source-scope/ToC maps, project documentation, source provenance, model assumptions, API documentation and deployment configuration.
- Local CIE D65 and 1931 2° tables and Sharma CIEDE2000 verification pairs, with source citations/checksums and rights notes.

## Latest configuration and outputs

- Central configuration: `05_COMPLETE_SOURCE_CODE/config.json`; initial colours and illuminants unchanged; deterministic seed 20261115.
- Latest pipeline output: `07_RESEARCH_RESULTS/Configuration/run_metadata.json`, generated 2026-11-15.
- Latest run logs: `09_TESTING_AND_API_DOCUMENTATION/Test_Reports/phase4_*`.

## Source items not bundled as local PDFs

- The assignment/rubric, two original ToC photographs, complete execution guide, supplied Nigam copy, Jullien final paper, and Wadhawan 2024 preprint are included. Pilarski and Li full texts have been verified online, but local PDF retrieval failed; the final 2025 Wadhawan PDF is also not included. The exact-title Nigam copy has no independently verified publication record. See `MISSING_INPUTS.md`, `SOURCE_MATERIALS_INDEX.md`, `03_REFERENCE_PAPERS/REFERENCE_SOURCE_REGISTER.md` and literature notes. Team identifiers and the faculty checklist remain prompt transcriptions, not institutional records.
- Standards PDFs were not available and are not bundled. Official URLs, publication metadata, local data license notes and hashes are provided in the colour-science reference documentation.

## Secret and deployment checks

- `.env` and credential/token files are excluded; only `.env.example` is included.
- `node_modules`, build outputs, virtual environments, caches, prior evidence ZIPs and runtime SQLite data are excluded.
- Docker/cloud deployment remains unverified. No physical measurements or human-participant data are included.

## Selected checksums

- `01_ASSIGNMENT_AND_FACULTY/Original_Assignment.pdf` — SHA-256 `09c7c76625ee1ea5474be4690c4c759f43f05866737cb03eb23bbf4d546a168d`
- `02_EXECUTION_GUIDE/Q3_Execution_Guide.md` — SHA-256 `5c9b54b1d29f752ac6841d078f27ce2abb87fed6d3b71f449f63d7a1c6cbf224`
- `01_ASSIGNMENT_AND_FACULTY/Report_Format_Images/toc_image_1.png` — SHA-256 `eb2094c1e910079d1c26039d5fa521a8f2a5c39091c3b380c94c796d9f59dfbe`
- `01_ASSIGNMENT_AND_FACULTY/Report_Format_Images/toc_image_2.png` — SHA-256 `f6a578538aafafd6c4640a77484756e3e99518870e7d375173a6d7d5be4b2c76`
- `03_REFERENCE_PAPERS/Jullien/Jullien_2023_TMLR.pdf` — SHA-256 `87013014882394566d4bb78421e5536a736a61e72cae4002b91d32c4d88de3e8`
- `03_REFERENCE_PAPERS/Nigam/Nigam_Assigned_Copy_retail_waste_managment_RL.pdf` — SHA-256 `95fe9894cb5edf08e36049f6de6028be0fb01f788a42cd266db6a8892687beaa`
- `03_REFERENCE_PAPERS/Wadhawan/Wadhawan_Rizvi_2024_arXiv.pdf` — SHA-256 `24b2826238ccc217e7053c0b9d2d0bf2ccc30d676358091fdfacc7b9d7703074`
- `05_COMPLETE_SOURCE_CODE/config.json` — SHA-256 `b3e7376a730562170b2f6739ab22bbbf9622f031c33da19e46867528746c5e60`
- `07_RESEARCH_RESULTS/CSV/colour_measurements.csv` — SHA-256 `5064e82eca3c4fd01f1f604dcf93b085a3fa4330bdf4340bf5d6fce38a023f16`
- `07_RESEARCH_RESULTS/CSV/delta_e_summary.csv` — SHA-256 `64833777b9d79a11a3182234823a0f59416d67f5c5821260239040fcb9f4c80a`
- `07_RESEARCH_RESULTS/CSV/chromaticity_data.csv` — SHA-256 `55c94a9e243a34d8704c86745b0fbe75b323f788def98d088a029d610d95770a`
- `07_RESEARCH_RESULTS/Donation_Simulation/trigger_rates.csv` — SHA-256 `e99bacdc54f00481dbb7795a1140a405092dbf9c1c9404aaa91151b215b3f2b5`
- `07_RESEARCH_RESULTS/Donation_Simulation/donation_simulation.csv` — SHA-256 `f7e91ed9b79a5d6196af60219a35e93b75c7a4da4e9a8ad6984dd3e709999ef9`
- `07_RESEARCH_RESULTS/Sustainability/sustainability_analysis.csv` — SHA-256 `249df4616da519e5f12885f1cd24d410383de8ce0f42ddd9f2743c2c5a96ba09`
- `06_BLENDER_VISUALS/Final_Blend/q3_supermarket.blend` — SHA-256 `9dd9f8469f855ca6b970f2fd9485215fe6d119a86d940cca12bd47501c91a712`
- `06_BLENDER_VISUALS/Final_Blend/q3_project.blend` — SHA-256 `7b5cc762cbb850f664e0aa087f0a320d47f1b4d3ffb89d0a473d4c0274532b64`
- `06_BLENDER_VISUALS/GLB_Assets/verdant_market.glb` — SHA-256 `6901462035282f96e320f1d936fea7fc3c672db9942970d593df8dee477d66b6`
- `06_BLENDER_VISUALS/Hero_Renders/01_supermarket_hero.png` — SHA-256 `caa58e62901864b1f54f9e4389ce5308bd4195fec7854aa119aa7d1a8fdfeb3f`
- `06_BLENDER_VISUALS/Macro_Renders/03_donate_now_macro.png` — SHA-256 `7d7fe81f24c7160c8821d557c0fef902a3590cf211a411ef1523eb9ceb4ea27f`
- `10_CLAUDE_REPORT_MATERIALS/CLAUDE_RESEARCH_BRIEF.md` — SHA-256 `6b5a66494dfdecb45db61767313c29ac3eb12374e81aa24d3f6661363a00c660`
- `10_CLAUDE_REPORT_MATERIALS/FINAL_RESULTS_AND_LIMITATIONS.md` — SHA-256 `a1c0f5e11f9fffa0df9ec136dfece2ee2fd012a7b8317dcfae87805c15c5839a`
- `10_CLAUDE_REPORT_MATERIALS/IEEE_MASTER_WRITING_PROMPT.md` — SHA-256 `4dabf6485f13c542cf0ecee6e7e4f449acdaf54b831bde3e76e6f5f5f497d5e4`

External archive SHA-256: `246fa0264c4ee8384abd3124fafd4a2147830834a958addd7d3f958fd752f627`
