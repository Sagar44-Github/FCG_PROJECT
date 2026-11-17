# Build instructions

## Requirements

- Python 3.11 or compatible, with NumPy and Matplotlib for the manuscript inventory chart and Pillow for the Blender camera plate. The CSV-to-LaTeX table generator uses only the Python standard library.
- Tectonic 0.17.0, or a TeX Live/MiKTeX installation with IEEEtran and BibTeX.
- Poppler pdftoppm and pdfinfo for the visual inspection workflow.

The final PDF in this directory was compiled with Tectonic 0.17.0 using IEEEtran journal mode. Tectonic downloads TeX packages on first use; subsequent builds use its local cache.

## Reproduce the result tables and manuscript

From this directory:

    python scripts/generate_tables.py
    python scripts/generate_paper_figure_overrides.py
    python scripts/compose_camera_plate.py
    tectonic -k --keep-logs main.tex

The table and figure generators read the copied final result CSVs in data/results/CSV. The camera-plate script composes the six included Blender camera renders. The main source uses IEEEtran with a two-column journal layout and references.bib. If using a conventional TeX installation, run pdflatex, bibtex, and pdflatex twice to resolve references and citations.

## Render pages for visual review

    pdftoppm -png -r 150 main.pdf qa/page
    pdfinfo main.pdf

The PNGs produced by the review step are temporary. Inspect each page for figure/table overflow, unreadable labels, orphan headings, and citation/bibliography errors. The manuscript assets are already organized in figures/, data/, and tables/.
