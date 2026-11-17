"""Build and validate the single Claude research handoff archive.

Only project source/evidence allow-listed below is copied. Existing evidence ZIPs,
runtime databases, caches, local environments, and secret files are never nested.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sqlite3
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF"
ARCHIVE = PROJECT / "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF.zip"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ensure_dirs() -> None:
    paths = [
        "01_ASSIGNMENT_AND_FACULTY/Report_Format_Images",
        "02_EXECUTION_GUIDE",
        "03_REFERENCE_PAPERS/Pilarski",
        "03_REFERENCE_PAPERS/Jullien",
        "03_REFERENCE_PAPERS/Li_2023",
        "03_REFERENCE_PAPERS/Wadhawan",
        "03_REFERENCE_PAPERS/Nigam",
        "04_COLOUR_SCIENCE_REFERENCES/data",
        "05_COMPLETE_SOURCE_CODE/blender",
        "05_COMPLETE_SOURCE_CODE/colour_engine",
        "05_COMPLETE_SOURCE_CODE/simulation",
        "05_COMPLETE_SOURCE_CODE/backend",
        "05_COMPLETE_SOURCE_CODE/dashboard",
        "05_COMPLETE_SOURCE_CODE/frontend",
        "05_COMPLETE_SOURCE_CODE/tests",
        "05_COMPLETE_SOURCE_CODE/configuration",
        "05_COMPLETE_SOURCE_CODE/data",
        "05_COMPLETE_SOURCE_CODE/results",
        "05_COMPLETE_SOURCE_CODE/renders",
        "06_BLENDER_VISUALS/Hero_Renders",
        "06_BLENDER_VISUALS/Macro_Renders",
        "06_BLENDER_VISUALS/Shelf_Renders",
        "06_BLENDER_VISUALS/Illuminant_Comparisons",
        "06_BLENDER_VISUALS/Research_Renders",
        "06_BLENDER_VISUALS/Final_Blend",
        "06_BLENDER_VISUALS/GLB_Assets",
        "06_BLENDER_VISUALS/Scene_Evidence",
        "07_RESEARCH_RESULTS/CSV",
        "07_RESEARCH_RESULTS/Statistical_Analysis",
        "07_RESEARCH_RESULTS/Donation_Simulation",
        "07_RESEARCH_RESULTS/Sustainability",
        "07_RESEARCH_RESULTS/Configuration",
        "08_FIGURES_AND_DIAGRAMS/Research_Figures",
        "08_FIGURES_AND_DIAGRAMS/Scientific_Charts",
        "08_FIGURES_AND_DIAGRAMS/UML/source",
        "08_FIGURES_AND_DIAGRAMS/UML/rendered",
        "08_FIGURES_AND_DIAGRAMS/Architecture",
        "08_FIGURES_AND_DIAGRAMS/Dashboard_Screenshots",
        "09_TESTING_AND_API_DOCUMENTATION/Test_Reports",
        "09_TESTING_AND_API_DOCUMENTATION/API_Documentation",
        "09_TESTING_AND_API_DOCUMENTATION/Frontend_Documentation",
        "09_TESTING_AND_API_DOCUMENTATION/Deployment",
        "10_CLAUDE_REPORT_MATERIALS",
        "11_PROJECT_DOCUMENTATION",
    ]
    for item in paths:
        (OUT / item).mkdir(parents=True, exist_ok=True)


def copy_file(source: str | Path, relative: str | Path | None = None, required: bool = True) -> None:
    src = Path(source)
    if not src.is_absolute():
        src = PROJECT / src
    if not src.is_file():
        if required:
            raise FileNotFoundError(f"Required handoff input missing: {src}")
        return
    dest = OUT / (Path(relative) if relative is not None else src.relative_to(PROJECT))
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def copy_tree(source: str | Path, destination: str | Path, patterns: tuple[str, ...] = ()) -> None:
    src = PROJECT / source
    dst = OUT / destination
    if not src.is_dir():
        raise FileNotFoundError(f"Required source directory missing: {src}")
    ignored = shutil.ignore_patterns(
        "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache",
        ".venv", "venv", "node_modules", "dist", "coverage", "test-results",
        "playwright-report", ".vite", ".git", "*.pyc", "*.pyo", "*.blend1",
        ".env", ".env.*", *patterns,
    )
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignored)


def copy_glob(pattern: str, destination: str, required_count: int = 0) -> list[Path]:
    matches = sorted(PROJECT.glob(pattern))
    if len(matches) < required_count:
        raise RuntimeError(f"Expected at least {required_count} files for {pattern}, found {len(matches)}")
    copied = []
    for src in matches:
        if src.is_file():
            copy_file(src, Path(destination) / src.name)
            copied.append(OUT / destination / src.name)
    return copied


def create_schema_sql() -> None:
    source = PROJECT / "backend" / "database.py"
    # Use an isolated in-memory database and the application's actual initializer.
    import os
    os.environ["Q3_DATABASE_PATH"] = ":memory:"
    # The repository module resolves a filesystem path, so create DDL from its
    # actual CREATE statements without connecting to or copying runtime records.
    text = source.read_text(encoding="utf-8")
    start = text.index('db.executescript("""') + len('db.executescript("""')
    end = text.index('""")', start)
    ddl = text[start:end].strip()
    (OUT / "05_COMPLETE_SOURCE_CODE/configuration/sqlite_schema.sql").write_text(
        "-- DDL copied from backend/database.py initialize(); no runtime rows included.\n"
        + ddl + "\n",
        encoding="utf-8",
    )


def write_input_status() -> None:
    (OUT / "01_ASSIGNMENT_AND_FACULTY/Faculty_Requirements.txt").write_text(
        "FACULTY SOFTWARE-ENGINEERING REQUIREMENTS — PROMPT TRANSCRIPTION\n"
        "This file is a transcription of the project instructions supplied by the team; it is not an original faculty-issued handout.\n\n"
        "1. Explain user mode and kernel mode; explain why no custom kernel component is required when the application executes in user space.\n"
        "2. Apply object-oriented software design meaningfully.\n"
        "3. Produce UML class, object, component, data-flow, sequence and deployment diagrams that reflect the implementation.\n"
        "4. Implement query parameters, APIs and API integration.\n"
        "5. Demonstrate unit, integration, API and system testing, including sandbox and isolated processing.\n"
        "6. Implement routing, pagination and backend robustness.\n"
        "7. Prepare for cloud deployment without claiming deployment unless it is executed.\n\n"
        "Implementation mapping: 10_CLAUDE_REPORT_MATERIALS/FACULTY_REQUIREMENTS_MAPPING.md and the actual sources/diagrams listed there.\n",
        encoding="utf-8",
    )
    (OUT / "01_ASSIGNMENT_AND_FACULTY/Team_Details.md").write_text(
        "# Team details (transcribed from supplied project prompt)\n\n"
        "Institution: Dayananda Sagar Academy of Technology and Management, Bengaluru, India.\n\n"
        "| Student | USN |\n|---|---|\n"
        "| Pallavi Bammanni | 1DT24CS185 |\n"
        "| Preethi S Pujari | 1DT24CS195 |\n"
        "| Sagar R | 1DT24CS232 |\n"
        "| R S Diya | 1DT24CS206 |\n"
        "| Nisha A | 1DT24CS178 |\n\n"
        "This is prompt-sourced text, not a scan or original institutional record.\n",
        encoding="utf-8",
    )
    (OUT / "01_ASSIGNMENT_AND_FACULTY/Original_Source_Status.md").write_text(
        "The supplied assignment PDF, its 30-mark rubric, and two original ToC photographs are included. The PDF's first page contains five six-mark criteria. The ToC images depict an unrelated medical/quantum project; see 10_CLAUDE_REPORT_MATERIALS/TOC_STRUCTURE_MAPPING.md for the generic section mapping and excluded topics.\n",
        encoding="utf-8",
    )
    (OUT / "01_ASSIGNMENT_AND_FACULTY/Report_Format_Images/README.md").write_text(
        "The two original supplied photographs are included unchanged. They describe fingerprint/blood-group and quantum-inspired medical-imaging content from another project. Only the generic chapter sequence is mapped to Q3; see 10_CLAUDE_REPORT_MATERIALS/TOC_STRUCTURE_MAPPING.md.\n",
        encoding="utf-8",
    )
    (OUT / "02_EXECUTION_GUIDE/IMPLEMENTATION_SCOPE_NOTE.md").write_text(
        "The original Q3_Execution_Guide.md is included in full and unchanged. Its physical print/light/camera and human-participant instructions were not executed because the team's direct software-only requirement prohibits them. The project uses virtual print and simulated-observer models; see 10_CLAUDE_REPORT_MATERIALS/IMPLEMENTATION_SCOPE_NOTE.md and 11_PROJECT_DOCUMENTATION/Research_Methodology.md.\n",
        encoding="utf-8",
    )
    paper_notes = {
        "Pilarski": "Exact identity/full text verified: Sebastian Pilarski, Aman Sidhu, Dániel Varró (2025), Simulation 101(3), 267–285, DOI 10.1177/00375497241299054; publisher says CC BY 4.0. Official full text https://liu.diva-portal.org/smash/get/diva2:1928671/FULLTEXT01.pdf. Local host timed out; PDF binary not included. See literature notes.\n",
        "Jullien": "Final published PDF is included. Sami Jullien et al., Transactions on Machine Learning Research (2023), Article 769; official record https://openreview.net/forum?id=KSvr8A62MD. UvA-DARE identifies CC BY.\n",
        "Li_2023": "Exact identity/full text verified: Richard Li, Anthony S. F. Chiu, Rosemary Seva (2023), Cleaner and Responsible Consumption 11, 100150, DOI 10.1016/j.clrc.2023.100150. Full text identifies CC BY-NC-ND 4.0. Publisher record https://www.sciencedirect.com/science/article/pii/S2666784323000517 and author-uploaded source https://www.researchgate.net/publication/375102523_Reducing_carbon_footprint_and_promoting_resource_sustainability_in_the_retail_industry_through_the_prevention_of_dead_stocks. Download endpoint returned HTTP 403; PDF binary not included.\n",
        "Wadhawan": "Included PDF is the 2024 CC BY arXiv:2406.13226v1 preprint. Final publication: Applied Mathematical Modelling 146 (2025), Article 116166, DOI 10.1016/j.apm.2025.116166.\n",
        "Nigam": "Supplied five-page PDF is included verbatim. It identifies authors but no venue, DOI, publication date, or license; independent exact-title publication record was not verified. Treat as course-supplied material; see literature notes for source claims and inconsistencies.\n",
    }
    for folder, text in paper_notes.items():
        (OUT / "03_REFERENCE_PAPERS" / folder / "SOURCE_ACCESS.md").write_text(text, encoding="utf-8")


def copy_reference_sources() -> None:
    """Copy supplied originals and verified/licensed paper PDFs into the handoff."""
    copies = (
        ("reference_materials/assignment/Copy_of_OE-CCA_30_d.pdf", "01_ASSIGNMENT_AND_FACULTY/Original_Assignment.pdf"),
        ("reference_materials/assignment/Q3_Execution_Guide.md", "02_EXECUTION_GUIDE/Q3_Execution_Guide.md"),
        ("reference_materials/report_format_images/toc_image_1.png", "01_ASSIGNMENT_AND_FACULTY/Report_Format_Images/toc_image_1.png"),
        ("reference_materials/report_format_images/toc_image_2.png", "01_ASSIGNMENT_AND_FACULTY/Report_Format_Images/toc_image_2.png"),
        ("reference_materials/papers/Jullien_2023_TMLR.pdf", "03_REFERENCE_PAPERS/Jullien/Jullien_2023_TMLR.pdf"),
        ("reference_materials/papers/Nigam_Assigned_Copy_retail_waste_managment_RL.pdf", "03_REFERENCE_PAPERS/Nigam/Nigam_Assigned_Copy_retail_waste_managment_RL.pdf"),
        ("reference_materials/papers/Wadhawan_Rizvi_2024_arXiv.pdf", "03_REFERENCE_PAPERS/Wadhawan/Wadhawan_Rizvi_2024_arXiv.pdf"),
        ("reference_materials/REFERENCE_SOURCE_REGISTER.md", "03_REFERENCE_PAPERS/REFERENCE_SOURCE_REGISTER.md"),
    )
    for source, destination in copies:
        copy_file(source, destination, required=True)



def copy_project_evidence() -> None:
    # Complete first-party source trees, excluding caches/build outputs/secrets.
    for name in ("colour_engine", "simulation", "backend", "dashboard", "tests"):
        copy_tree(name, f"05_COMPLETE_SOURCE_CODE/{name}")
    copy_tree("frontend", "05_COMPLETE_SOURCE_CODE/frontend")
    copy_tree("blender/scripts", "05_COMPLETE_SOURCE_CODE/blender/scripts")
    copy_tree("blender/assets", "05_COMPLETE_SOURCE_CODE/blender/assets")
    copy_tree("blender/evidence", "06_BLENDER_VISUALS/Scene_Evidence", patterns=("12_condition_contact_sheet.png",))
    # Preserve the runnable repository layout inside COMPLETE_SOURCE_CODE.
    for path in (
        "blender/q3_project.blend", "blender/q3_supermarket.blend", "config.json", ".gitignore",
    ):
        copy_file(path, Path("05_COMPLETE_SOURCE_CODE") / path, required=True)
    create_schema_sql()

    # CIE reference tables and Sharma verification pairs are not duplicated elsewhere.
    for name in ("CIE_std_illum_D65.csv", "CIE_xyz_1931_2deg.csv", "ciede2000_reference_cases.csv"):
        copy_file(Path("data") / name, Path("04_COLOUR_SCIENCE_REFERENCES/data") / name)
        copy_file(Path("data") / name, Path("05_COMPLETE_SOURCE_CODE/data") / name)
    (OUT / "04_COLOUR_SCIENCE_REFERENCES/README.md").write_text(
        "The CIE and Sharma verification datasets are mirrored in `../05_COMPLETE_SOURCE_CODE/data/` so the application runs without path changes. Dataset identity, checksums, citation, and rights notes are in `../11_PROJECT_DOCUMENTATION/reference_provenance.md`. Standards and papers are not silently replaced; source gaps are listed at package root.\n",
        encoding="utf-8",
    )
    (OUT / "05_COMPLETE_SOURCE_CODE/results/README.md").write_text(
        "This is the generated-output directory expected by the source tree. Run `python run_pipeline.py` here to regenerate results. Current verified outputs are organized separately in `../07_RESEARCH_RESULTS/` and figures in `../08_FIGURES_AND_DIAGRAMS/`.\n",
        encoding="utf-8",
    )
    (OUT / "05_COMPLETE_SOURCE_CODE/renders/README.md").write_text(
        "Run the Blender automation documented in the project README to generate controlled-scene PNGs here. The verified 12-condition renders are in `../06_BLENDER_VISUALS/Research_Renders/`.\n",
        encoding="utf-8",
    )
    (OUT / "05_COMPLETE_SOURCE_CODE/configuration/README.md").write_text(
        "The single runtime configuration file is `../config.json`. The SQLite schema only, without test/database rows, is in this directory.\n",
        encoding="utf-8",
    )
    (OUT / "05_COMPLETE_SOURCE_CODE/README.md").write_text(
        "# Runnable project source\n\n"
        "This directory preserves the repository layout required by the included source. Install `requirements.txt`, run `python run_pipeline.py` to regenerate outputs, start FastAPI with `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`, then install/build the React app from `frontend/`. Local CIE data are in `data/`, configuration is `config.json`, and Blender scripts/scenes are in `blender/`. Verified evidence is in sibling folders 06–08.\n",
        encoding="utf-8",
    )
    for path in ("run_pipeline.py", "make_contact_sheet.py", "requirements.txt", "Dockerfile", "docker-compose.yml", ".dockerignore", ".env.example"):
        copy_file(path, Path("05_COMPLETE_SOURCE_CODE") / path)

    # Authoritative measurement renders: exactly the canonical twelve plus contact sheet.
    for color in ("G", "Y", "O", "R"):
        for light in ("L1", "L2", "L3"):
            copy_file(Path("renders") / f"{color}_{light}.png", Path("06_BLENDER_VISUALS/Research_Renders") / f"{color}_{light}.png")
    copy_file("renders/contact_sheet.png", "06_BLENDER_VISUALS/Research_Renders/12_condition_contact_sheet.png")
    final_render_dir = Path("blender/renders/supermarket/final")
    final_names = [
        "01_supermarket_hero.png", "02_shelf_detail.png", "03_donate_now_macro.png",
        "04_colour_status_system.png", "05_illuminant_comparison.png", "06_supermarket_isometric.png",
        "release_metadata.json", "illumination_components.csv", "illumination_component_sensitivity.png",
    ]
    # Keep the six named production images and metadata; include any exact canonical sidecars if present.
    for name in final_names:
        copy_file(final_render_dir / name, Path("06_BLENDER_VISUALS") / (
            "Hero_Renders" if name.startswith("01_") else
            "Shelf_Renders" if name.startswith("02_") else
            "Macro_Renders" if name.startswith("03_") else
            "Illuminant_Comparisons" if name.startswith(("05_", "illumination_")) else
            "Research_Renders" if name == "release_metadata.json" else "Shelf_Renders"
        ) / name, required=name in {
            "01_supermarket_hero.png", "02_shelf_detail.png", "03_donate_now_macro.png",
            "04_colour_status_system.png", "05_illuminant_comparison.png", "06_supermarket_isometric.png",
            "release_metadata.json",
        })
    copy_file("blender/renders/supermarket/supermarket_contact_sheet.png", "06_BLENDER_VISUALS/Research_Renders/supermarket_contact_sheet.png", required=False)
    copy_file("frontend/public/assets/supermarket/verdant_market.glb", "06_BLENDER_VISUALS/GLB_Assets/verdant_market.glb")
    for src, dst in (
        ("blender/q3_project.blend", "06_BLENDER_VISUALS/Final_Blend/q3_project.blend"),
        ("blender/q3_supermarket.blend", "06_BLENDER_VISUALS/Final_Blend/q3_supermarket.blend"),
        ("results/blender_run_metadata.json", "06_BLENDER_VISUALS/Final_Blend/research_render_metadata.json"),
        ("results/blender_scene_inspection.json", "06_BLENDER_VISUALS/Final_Blend/research_scene_inspection.json"),
    ):
        copy_file(src, dst)

    # Data, tables and run/configuration provenance.
    result_csvs = sorted((PROJECT / "results").glob("*.csv"))
    for src in result_csvs:
        if src.name not in {"phase3_backend_tests.txt", "phase3_e2e_tests.txt"}:
            copy_file(src, Path("07_RESEARCH_RESULTS/CSV") / src.name)
    for src in sorted((PROJECT / "results/tables").glob("*.csv")):
        copy_file(src, Path("07_RESEARCH_RESULTS/Statistical_Analysis") / src.name)
    for name in ("delta_e_summary.csv", "statistical_summary.csv", "trigger_logistic_model.csv"):
        copy_file(Path("results") / name, Path("07_RESEARCH_RESULTS/Statistical_Analysis") / name)
    for name in ("trigger_simulation.csv", "trigger_rates.csv", "donation_simulation.csv"):
        copy_file(Path("results") / name, Path("07_RESEARCH_RESULTS/Donation_Simulation") / name)
    copy_file("results/sustainability_analysis.csv", "07_RESEARCH_RESULTS/Sustainability/sustainability_analysis.csv")
    for name in ("config.json", "run_metadata.json", "illumination_spectra.csv", "reflectance_spectra.csv", "illumination_comparisons.csv"):
        copy_file(Path("results") / name if name != "config.json" else Path("config.json"), Path("07_RESEARCH_RESULTS/Configuration") / name)

    # Research plots and architectural evidence; one canonical copy of each image.
    for src in sorted((PROJECT / "results/figures").glob("*.png")):
        copy_file(src, Path("08_FIGURES_AND_DIAGRAMS/Scientific_Charts") / src.name)
    for name in ("class_diagram", "object_diagram"):
        for ext in (".puml",):
            copy_file(Path("docs/diagrams") / f"{name}{ext}", Path("08_FIGURES_AND_DIAGRAMS/UML/source") / f"{name}{ext}")
    for name in ("component_diagram", "sequence_diagram", "deployment_diagram"):
        copy_file(Path("docs/diagrams") / f"{name}.puml", Path("08_FIGURES_AND_DIAGRAMS/Architecture") / f"{name}.puml")
    copy_file("docs/diagrams/data_flow_diagram.puml", "08_FIGURES_AND_DIAGRAMS/Architecture/data_flow_diagram.puml")
    copy_file("docs/render_diagrams.py", "08_FIGURES_AND_DIAGRAMS/Architecture/render_diagrams.py")
    for src in sorted((PROJECT / "docs/diagrams/rendered").glob("*.png")):
        section = "UML/rendered" if src.stem in {"class_diagram", "object_diagram"} else "Architecture"
        copy_file(src, Path("08_FIGURES_AND_DIAGRAMS") / section / src.name)
    for src in sorted((PROJECT / "docs/diagrams/rendered").glob("*.svg")):
        section = "UML/rendered" if src.stem in {"class_diagram", "object_diagram"} else "Architecture"
        copy_file(src, Path("08_FIGURES_AND_DIAGRAMS") / section / src.name)
    (OUT / "08_FIGURES_AND_DIAGRAMS/Architecture/README.md").write_text(
        "# Architecture and workflow figures\n\n"
        "Rendered system component, data-flow, research methodology workflow, API sequence and deployment diagrams are supplied as PNG/SVG with editable PlantUML source where applicable. Deployment is a prepared topology only; Docker/cloud execution is unverified. Diagram sources describe React as primary, Streamlit as fallback, and the API as the calculation/persistence source of truth.\n",
        encoding="utf-8",
    )
    for name in (
        "overview_desktop.png", "digital_twin_desktop.png", "colour_laboratory_desktop.png",
        "donation_simulator_desktop.png", "sustainability_desktop.png", "results_exports_desktop.png",
        "overview_mobile.png",
    ):
        copy_file(Path("results/frontend_screenshots") / name, Path("08_FIGURES_AND_DIAGRAMS/Dashboard_Screenshots") / name)
    (OUT / "08_FIGURES_AND_DIAGRAMS/Research_Figures/README.md").write_text(
        "The research figures are the generated scientific PNGs under ../Scientific_Charts; the six Cycles presentation renders and 12 analytical RGB renders are under 06_BLENDER_VISUALS. No figure is manually redrawn or presented as a physical measurement.\n",
        encoding="utf-8",
    )
    (OUT / "08_FIGURES_AND_DIAGRAMS/Scientific_Charts/FIGURE_INDEX.md").write_text(
        "# Figure provenance\n\n"
        "Every PNG in this folder was generated by `run_pipeline.py` from the supplied configuration, local CIE data and model outputs. Principal inputs: `07_RESEARCH_RESULTS/CSV/colour_measurements.csv`, `chromaticity_data.csv`, `trigger_simulation.csv`, `donation_simulation.csv`, and `sustainability_analysis.csv`. See `11_PROJECT_DOCUMENTATION/Research_Methodology.md` for assumptions. The diagram folder contains architecture/UML figures generated from their matching editable sources.\n",
        encoding="utf-8",
    )

    # Docs organized once across research, faculty and operational paths.
    for name in (
        "architecture.md", "blender_evidence.md", "config_history.md", "model_assumptions.md",
        "research_methodology.md", "reference_provenance.md", "spectral_sources.md",
        "supermarket_visual_pipeline.md", "faculty_demo_guide.md", "viva_preparation.md",
        "reproduction_guide.md", "setup_instructions.md", "execution_instructions.md",
        "implementation_status.md", "deployment_status.md",
    ):
        copy_file(Path("docs") / name, Path("11_PROJECT_DOCUMENTATION") / name)
    copy_file("README.md", "11_PROJECT_DOCUMENTATION/README.md")
    copy_file("docs/api_reference.md", "09_TESTING_AND_API_DOCUMENTATION/API_Documentation/api_reference.md")
    copy_file("docs/openapi.json", "09_TESTING_AND_API_DOCUMENTATION/API_Documentation/openapi.json")
    copy_file("docs/software_testing.md", "09_TESTING_AND_API_DOCUMENTATION/Test_Reports/software_testing.md")
    copy_file("docs/frontend_architecture.md", "09_TESTING_AND_API_DOCUMENTATION/Frontend_Documentation/frontend_architecture.md")
    for name in ("phase4_backend_tests.txt", "phase4_frontend_build.txt", "phase4_frontend_tests.txt", "phase4_e2e_tests.txt", "phase4_pipeline_run.txt", "test_results.txt", "phase3_backend_tests.txt"):
        copy_file(Path("results") / name, Path("09_TESTING_AND_API_DOCUMENTATION/Test_Reports") / name, required=name.startswith("phase4_"))
    for name in ("Dockerfile", "docker-compose.yml", ".env.example", ".dockerignore"):
        copy_file(name, Path("09_TESTING_AND_API_DOCUMENTATION/Deployment") / name)
    copy_file("README.md", "09_TESTING_AND_API_DOCUMENTATION/Deployment/deployment_notes.md")

    # Claude handoff materials include the five requested reports and source-scope maps.
    for name in (
        "CLAUDE_RESEARCH_BRIEF.md", "FINAL_RESULTS_AND_LIMITATIONS.md", "FACULTY_REQUIREMENTS_MAPPING.md",
        "LITERATURE_REVIEW_NOTES.md", "IEEE_MASTER_WRITING_PROMPT.md",
        "IMPLEMENTATION_SCOPE_NOTE.md", "TOC_STRUCTURE_MAPPING.md",
    ):
        copy_file(Path("report_inputs") / name, Path("10_CLAUDE_REPORT_MATERIALS") / name)
    for name in ("MISSING_INPUTS.md", "SOURCE_MATERIALS_INDEX.md"):
        copy_file(Path("report_inputs") / name, name)

    # Include all Blender automation sidecars and camera/light metadata where available.
    for name in ("scene_record.json", "camera_lighting_record.json", "scene_metadata.json"):
        copy_file(Path("results") / name, Path("06_BLENDER_VISUALS/Final_Blend") / name, required=False)

    # Keep the package self-contained and explain the only known unavailable inputs.
    (OUT / "README.md").write_text(
        "# Q3 complete IEEE research handoff\n\n"
        "This single organized package consolidates the verified source tree, computational data, diagrams, rendered assets, test evidence, and Claude writing materials. Start with `10_CLAUDE_REPORT_MATERIALS/IEEE_MASTER_WRITING_PROMPT.md`, then read the research brief and limitations.\n\n"
        "The supplied assignment/rubric, both ToC images, full execution guide and Nigam copy are included, along with final PDFs for Jullien and the Wadhawan preprint. Pilarski and Li have verified public full-text links but their PDF binaries could not be retrieved locally; the 2025 publisher-final Wadhawan PDF is also absent. `MISSING_INPUTS.md`, `SOURCE_MATERIALS_INDEX.md`, and `03_REFERENCE_PAPERS/REFERENCE_SOURCE_REGISTER.md` report exact status. The ToC images are from an unrelated medical/quantum project; only generic structure is mapped.\n\n"
        "Generated values are calculated or simulated software outputs. No physical measurements or human participants were used. Docker/cloud deployment is unverified.\n",
        encoding="utf-8",
    )
    (OUT / "11_PROJECT_DOCUMENTATION/Project_Manifest.md").write_text(
        "# Project manifest and reproduction entry point\n\n"
        "Project parameters: `05_COMPLETE_SOURCE_CODE/configuration/config.json` (seed 20261115). Reproduce Python evidence with `python run_pipeline.py`; source dependencies are in `requirements.txt`. Build/run the React frontend and API using `README.md` or the adjacent setup/execution guides. Blender automation, saved scenes and original generated textures are in `05_COMPLETE_SOURCE_CODE/blender/`; current renders and GLB are in `06_BLENDER_VISUALS/`. Test logs are under `09_TESTING_AND_API_DOCUMENTATION/Test_Reports/`. All calculated/simulated outputs and limitations are described in the Claude materials. Missing source originals are enumerated at package root.\n",
        encoding="utf-8",
    )


def create_manifest(archive_size: int = 0) -> str:
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "HANDOFF_MANIFEST.md")
    folders = sorted(p for p in OUT.rglob("*") if p.is_dir())
    ext_counts = Counter((p.suffix.lower() or "[no extension]") for p in files)
    important = [
        "01_ASSIGNMENT_AND_FACULTY/Original_Assignment.pdf",
        "02_EXECUTION_GUIDE/Q3_Execution_Guide.md",
        "01_ASSIGNMENT_AND_FACULTY/Report_Format_Images/toc_image_1.png",
        "01_ASSIGNMENT_AND_FACULTY/Report_Format_Images/toc_image_2.png",
        "03_REFERENCE_PAPERS/Jullien/Jullien_2023_TMLR.pdf",
        "03_REFERENCE_PAPERS/Nigam/Nigam_Assigned_Copy_retail_waste_managment_RL.pdf",
        "03_REFERENCE_PAPERS/Wadhawan/Wadhawan_Rizvi_2024_arXiv.pdf",
        "05_COMPLETE_SOURCE_CODE/config.json",
        "07_RESEARCH_RESULTS/CSV/colour_measurements.csv",
        "07_RESEARCH_RESULTS/CSV/delta_e_summary.csv",
        "07_RESEARCH_RESULTS/CSV/chromaticity_data.csv",
        "07_RESEARCH_RESULTS/Donation_Simulation/trigger_rates.csv",
        "07_RESEARCH_RESULTS/Donation_Simulation/donation_simulation.csv",
        "07_RESEARCH_RESULTS/Sustainability/sustainability_analysis.csv",
        "06_BLENDER_VISUALS/Final_Blend/q3_supermarket.blend",
        "06_BLENDER_VISUALS/Final_Blend/q3_project.blend",
        "06_BLENDER_VISUALS/GLB_Assets/verdant_market.glb",
        "06_BLENDER_VISUALS/Hero_Renders/01_supermarket_hero.png",
        "06_BLENDER_VISUALS/Macro_Renders/03_donate_now_macro.png",
        "10_CLAUDE_REPORT_MATERIALS/CLAUDE_RESEARCH_BRIEF.md",
        "10_CLAUDE_REPORT_MATERIALS/FINAL_RESULTS_AND_LIMITATIONS.md",
        "10_CLAUDE_REPORT_MATERIALS/IEEE_MASTER_WRITING_PROMPT.md",
    ]
    checks = []
    for rel in important:
        path = OUT / rel
        if path.is_file():
            checks.append(f"- `{rel}` — SHA-256 `{sha256(path)}`")
    ext_lines = "\n".join(f"- `{suffix}`: {count}" for suffix, count in sorted(ext_counts.items()))
    check_lines = "\n".join(checks)
    return f"""# HANDOFF_MANIFEST

Generated: {date.today().isoformat()}

## Archive inventory

- Archive: `Q3_COMPLETE_IEEE_RESEARCH_HANDOFF.zip`
- Archive size (bytes): `{archive_size:012d}`
- Files: {len(files) + 1} (includes this manifest)
- Folders: {len(folders)}
- File-type counts (manifest excluded):
{ext_lines}

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

{check_lines}
"""


def write_zip() -> int:
    # The manifest uses STORE and fixed-width archive-size digits. Its byte length
    # remains constant while the archive is rebuilt with the final size recorded.
    manifest = OUT / "HANDOFF_MANIFEST.md"
    manifest.write_text(create_manifest(0), encoding="utf-8")
    for _ in range(4):
        with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for path in sorted(OUT.rglob("*")):
                if not path.is_file():
                    continue
                arcname = path.relative_to(PROJECT).as_posix()
                if path == manifest:
                    info = zipfile.ZipInfo(arcname)
                    info.compress_type = zipfile.ZIP_STORED
                    info.external_attr = 0o644 << 16
                    zf.writestr(info, path.read_bytes())
                else:
                    zf.write(path, arcname)
        actual = ARCHIVE.stat().st_size
        expected = create_manifest(actual)
        if manifest.read_text(encoding="utf-8") == expected:
            break
        manifest.write_text(expected, encoding="utf-8")
    else:
        raise RuntimeError("Archive manifest size did not converge")
    # Final archive is tested and key paths/counts are checked from its central directory.
    with zipfile.ZipFile(ARCHIVE) as zf:
        bad = zf.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC failure in {bad}")
        names = set(zf.namelist())
        source_integrity = {
            "01_ASSIGNMENT_AND_FACULTY/Original_Assignment.pdf": "reference_materials/assignment/Copy_of_OE-CCA_30_d.pdf",
            "02_EXECUTION_GUIDE/Q3_Execution_Guide.md": "reference_materials/assignment/Q3_Execution_Guide.md",
            "01_ASSIGNMENT_AND_FACULTY/Report_Format_Images/toc_image_1.png": "reference_materials/report_format_images/toc_image_1.png",
            "01_ASSIGNMENT_AND_FACULTY/Report_Format_Images/toc_image_2.png": "reference_materials/report_format_images/toc_image_2.png",
            "03_REFERENCE_PAPERS/Jullien/Jullien_2023_TMLR.pdf": "reference_materials/papers/Jullien_2023_TMLR.pdf",
            "03_REFERENCE_PAPERS/Nigam/Nigam_Assigned_Copy_retail_waste_managment_RL.pdf": "reference_materials/papers/Nigam_Assigned_Copy_retail_waste_managment_RL.pdf",
            "03_REFERENCE_PAPERS/Wadhawan/Wadhawan_Rizvi_2024_arXiv.pdf": "reference_materials/papers/Wadhawan_Rizvi_2024_arXiv.pdf",
        }
        for archive_rel, source_rel in source_integrity.items():
            archive_name = f"Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/{archive_rel}"
            if archive_name not in names:
                raise RuntimeError(f"Required original source missing from archive: {archive_rel}")
            packaged_sha = hashlib.sha256(zf.read(archive_name)).hexdigest()
            if packaged_sha != sha256(PROJECT / source_rel):
                raise RuntimeError(f"Original source changed while packaging: {archive_rel}")
        required = [
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/README.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/MISSING_INPUTS.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/SOURCE_MATERIALS_INDEX.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/HANDOFF_MANIFEST.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/01_ASSIGNMENT_AND_FACULTY/Original_Assignment.pdf",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/01_ASSIGNMENT_AND_FACULTY/Report_Format_Images/toc_image_1.png",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/01_ASSIGNMENT_AND_FACULTY/Report_Format_Images/toc_image_2.png",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/02_EXECUTION_GUIDE/Q3_Execution_Guide.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/03_REFERENCE_PAPERS/Jullien/Jullien_2023_TMLR.pdf",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/03_REFERENCE_PAPERS/Nigam/Nigam_Assigned_Copy_retail_waste_managment_RL.pdf",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/03_REFERENCE_PAPERS/Wadhawan/Wadhawan_Rizvi_2024_arXiv.pdf",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/03_REFERENCE_PAPERS/REFERENCE_SOURCE_REGISTER.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/06_BLENDER_VISUALS/Final_Blend/q3_supermarket.blend",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/06_BLENDER_VISUALS/GLB_Assets/verdant_market.glb",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/07_RESEARCH_RESULTS/CSV/colour_measurements.csv",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/08_FIGURES_AND_DIAGRAMS/Dashboard_Screenshots/overview_mobile.png",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/10_CLAUDE_REPORT_MATERIALS/CLAUDE_RESEARCH_BRIEF.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/10_CLAUDE_REPORT_MATERIALS/FINAL_RESULTS_AND_LIMITATIONS.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/05_COMPLETE_SOURCE_CODE/config.json",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/05_COMPLETE_SOURCE_CODE/data/CIE_std_illum_D65.csv",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/05_COMPLETE_SOURCE_CODE/run_pipeline.py",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/05_COMPLETE_SOURCE_CODE/frontend/package-lock.json",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/05_COMPLETE_SOURCE_CODE/backend/main.py",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/05_COMPLETE_SOURCE_CODE/tests/test_colour_science.py",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/09_TESTING_AND_API_DOCUMENTATION/API_Documentation/openapi.json",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/10_CLAUDE_REPORT_MATERIALS/FACULTY_REQUIREMENTS_MAPPING.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/10_CLAUDE_REPORT_MATERIALS/LITERATURE_REVIEW_NOTES.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/10_CLAUDE_REPORT_MATERIALS/IEEE_MASTER_WRITING_PROMPT.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/10_CLAUDE_REPORT_MATERIALS/IMPLEMENTATION_SCOPE_NOTE.md",
            "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/10_CLAUDE_REPORT_MATERIALS/TOC_STRUCTURE_MAPPING.md",
        ]
        missing = [name for name in required if name not in names]
        if missing:
            raise RuntimeError("Required archive entries missing: " + ", ".join(missing))
        forbidden = [name for name in names if any(token in name.lower() for token in ("node_modules/", ".venv/", "__pycache__/", ".pytest_cache/")) or name.lower().endswith((".env", ".blend1", ".pyc"))]
        if forbidden:
            raise RuntimeError("Forbidden cache/secret/backup entry found: " + ", ".join(forbidden[:10]))
        secret_name_fragments = ("credentials.json", "id_rsa", "id_ed25519", ".pem", ".p12", ".pfx", "secrets.")
        secret_names = [name for name in names if any(fragment in name.lower() for fragment in secret_name_fragments)]
        if secret_names:
            raise RuntimeError("Potential credential/private-key file included: " + ", ".join(secret_names[:10]))
        token_patterns = [
            re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
            re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{25,}\b"),
            re.compile(rb"\bsk-[A-Za-z0-9]{24,}\b"),
            re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
        ]
        text_suffixes = {".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".ini", ".env", ".example"}
        for name in names:
            suffix = Path(name).suffix.lower()
            if suffix not in text_suffixes:
                continue
            payload = zf.read(name)
            if any(pattern.search(payload) for pattern in token_patterns):
                raise RuntimeError(f"Potential embedded credential/token detected in {name}")
        # Exactly the six final UI screenshots and one mobile screenshot are mandatory.
        desktop = [name for name in names if "/Dashboard_Screenshots/" in name and name.endswith("_desktop.png")]
        if len(desktop) != 6:
            raise RuntimeError(f"Expected 6 desktop screenshots, found {len(desktop)}")
        if "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/08_FIGURES_AND_DIAGRAMS/Dashboard_Screenshots/overview_mobile.png" not in names:
            raise RuntimeError("Mobile screenshot missing")
        renders = [name for name in names if "/Research_Renders/" in name and name.rsplit("/",1)[-1].endswith(".png") and name.rsplit("/",1)[-1][0] in "GORY"]
        if len(renders) < 12:
            raise RuntimeError(f"Expected 12 scientific render files, found {len(renders)}")
        required_six = {
            "01_supermarket_hero.png", "02_shelf_detail.png", "03_donate_now_macro.png",
            "04_colour_status_system.png", "05_illuminant_comparison.png", "06_supermarket_isometric.png",
        }
        included_supermarket = {Path(name).name for name in names if "/06_BLENDER_VISUALS/" in name and Path(name).name.endswith(".png")}
        if not required_six.issubset(included_supermarket):
            raise RuntimeError("One or more final supermarket renders are missing")
        csv_name = "Q3_COMPLETE_IEEE_RESEARCH_HANDOFF/07_RESEARCH_RESULTS/CSV/colour_measurements.csv"
        csv_text = zf.read(csv_name).decode("utf-8-sig").splitlines()
        if len(csv_text) != 13 or not all(f"{prefix}_{axis}" in csv_text[0] for prefix in ("digital", "print") for axis in ("X", "Y", "Z")):
            raise RuntimeError("Colour measurement CSV must contain 12 rows and native XYZ columns")
    return ARCHIVE.stat().st_size


def main() -> None:
    # Generated output targets are constrained to the project directory.
    if OUT.resolve().parent != PROJECT.resolve() or ARCHIVE.resolve().parent != PROJECT.resolve():
        raise RuntimeError("Refusing to create handoff outside the project root")
    if OUT.exists():
        shutil.rmtree(OUT)
    if ARCHIVE.exists():
        ARCHIVE.unlink()
    ensure_dirs()
    write_input_status()
    copy_reference_sources()
    copy_project_evidence()

    # Write both indexes at package root after the source-status folder exists.
    copy_file("report_inputs/MISSING_INPUTS.md", "MISSING_INPUTS.md")
    copy_file("report_inputs/SOURCE_MATERIALS_INDEX.md", "SOURCE_MATERIALS_INDEX.md")

    # Verify the six production images and seven browser screenshots before packaging.
    production = sorted((OUT / "06_BLENDER_VISUALS").rglob("0*.png"))
    expected_prod_names = {
        "01_supermarket_hero.png", "02_shelf_detail.png", "03_donate_now_macro.png",
        "04_colour_status_system.png", "05_illuminant_comparison.png", "06_supermarket_isometric.png",
    }
    if {p.name for p in production} != expected_prod_names:
        raise RuntimeError(f"Production render set mismatch: {[p.name for p in production]}")
    for path in production:
        with Image.open(path) as image:
            if image.size != (2560, 1440):
                raise RuntimeError(f"Unexpected production render size for {path}: {image.size}")
    shots = list((OUT / "08_FIGURES_AND_DIAGRAMS/Dashboard_Screenshots").glob("*.png"))
    if len(shots) != 7:
        raise RuntimeError(f"Expected 7 browser screenshots, found {len(shots)}")
    for path in shots:
        with Image.open(path) as image:
            expected_width = 390 if path.name == "overview_mobile.png" else 1440
            if image.width != expected_width:
                raise RuntimeError(f"Unexpected screenshot width for {path}: {image.width}")

    size = write_zip()
    # External manifest includes the archive digest, unavailable inside the ZIP itself.
    external_manifest = PROJECT / "HANDOFF_MANIFEST.md"
    shutil.copy2(OUT / "HANDOFF_MANIFEST.md", external_manifest)
    with external_manifest.open("a", encoding="utf-8") as stream:
        stream.write(f"\nExternal archive SHA-256: `{sha256(ARCHIVE)}`\n")
    with zipfile.ZipFile(ARCHIVE) as zf:
        count = len([name for name in zf.namelist() if not name.endswith("/")])
        print(json.dumps({"archive": str(ARCHIVE), "size_bytes": size, "files": count,
                          "folders": sum(1 for p in OUT.rglob("*") if p.is_dir()),
                          "sha256": sha256(ARCHIVE)}, indent=2))


if __name__ == "__main__":
    main()
