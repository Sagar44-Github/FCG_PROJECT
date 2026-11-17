# Q3 Execution Guide — Blender × Colour Theory × Retail Shelf Labels

**Question (Q3, 30 marks):** What is the perceptual error (ΔE) between a Blender-rendered "expiry warning" colour and the same colour on a physical store shelf label under D65 vs. store LED illumination — and does that error predict missed donation triggers?

**Team 3 (Row 3 of the OE-CCA sheet)** · built for **4 active members working in parallel** · **Blender is mandatory** · prepared 30 Oct 2026

> **How to use this file.** Read §0–§3 together (about 30 minutes). Then each person jumps to their own role in §1.2 and follows the phases in order. Copy the data-sheet templates from §16 into Excel / Google Sheets. All scripts are in the Appendix.
>
> **Honest status of the scripts:** the Python scripts (Appendix C–F) were run end to end on dummy data and work. The two Blender scripts (Appendix A–B) could not be run inside real Blender where this guide was written (only logic-checked), so test them early; if Blender shows an error, send the error text to your teammate or back to Claude.

## Contents
0. At a glance
1. Team and who does what (4 active members)
2. Understand the question
3. Marks map — what earns the 30 marks
4. Phase 0 — Before you start
5. Phase 1 — Literature (five papers)
6. Phase 2 — Experiment design (then freeze it)
7. Phase 3 — Blender (Role A)
8. Phase 4 — Physical measurement (Role B)
9. Phase 5 — Computing ΔE (A + B)
10. Phase 6 — User study (Role C + everyone)
11. Phase 7 — Statistics (Role C)
12. Phase 8 — Impact simulation, SDG and carbon audit (Role D)
13. Phase 9 — Writing the report
14. Phase 10 — Final checks, viva and slides
15. Do and Don't — the master list
16. Data sheets to fill (S1–S9)
17. Troubleshooting
18. Glossary and references
Appendix A–F — scripts

---

## 0. At a glance

### The 10-step path

| # | Step | Who | Done when |
|---|---|---|---|
| 1 | Ask faculty the questions in §4.1 | All | Answers pasted into Sheet S2 |
| 2 | Freeze colours, lights, printer and camera settings (§6) | All | Sheet S2 complete (Day 2) |
| 3 | Read the five papers; fill S1 and the novelty matrix S1b (§5) | D leads, all read abstracts | S1 + S1b complete |
| 4 | Build the Blender scene, Standard colour management, render 12 images (§7) | A | 12 PNGs + Sheet S3 |
| 5 | Build the light box, print labels, take 72 photos (§8) | B | 72 photos + Sheet S4 |
| 6 | Run the ΔE script; build the CIE chromaticity figure (§9) | A + B | `delta_e_summary.csv` + figure F5 |
| 7 | Run the user study, at least 30 participants (§10) | C leads, all help | `trial_data.csv` filled (36 × 24 = 864 rows) |
| 8 | Run the statistics (§11) | C | Printed tables + `fig_error_vs_dE.png` |
| 9 | Impact simulation + SDG / carbon sheet (§12) | D | `fig_sim_sensitivity.png` + Sheet S8 |
| 10 | Write, merge, check against the rubric, rehearse (§13–§14) | All; D assembles | Final PDF + zip |

### Three levels of effort (so you never end up with nothing)

**Level 1 — Minimum (finish this first, no participants needed)**
- Blender scene, Standard colour management, 12 renders, compositor white-balance demo, CIE chromaticity figure with gamut triangle, dominant wavelength and purity.
- Physical labels photographed under 3 lights with a phone, ΔE00 table with confidence intervals.
- The full validation protocol written down (n ≥ 30, tests chosen, success criteria) and a pilot with 3–5 people to prove it works.
- Toy A/B simulation, SDG and carbon table, report.

**Level 2 — Target:** run the full user study (≥ 30 participants), run the logistic model, report the odds ratio with its confidence interval.

**Level 3 — Stretch:** spectrophotometer readings, Geometry-Nodes procedural gamut triangle, Eevee-vs-Cycles check, printer-gamut triangle, a metameric-pair demo, an extra "stress" condition to widen the ΔE range.

> The faculty rubric reads like a **proposal evaluation** ("is it new?", "can it be validated?", "is it implementable?"). If faculty accept a design plus a working Blender prototype, Level 1 can already earn marks in every column; Level 2 makes *rigour* and *applicability* much stronger because you have real data. **Ask which one they expect (§4.1).**

### Deliverables to plan for (confirm exact format with faculty)
1. **Report (PDF)**, journal style (§13).
2. **Blender package:** `.blend`, 12 renders, chromaticity figure, node-tree screenshots.
3. **Data package:** spreadsheets, scripts, raw photos (zip or Drive link).
4. **Slides + viva readiness** if asked (§14).

---

## 1. Team and who does what

### 1.1 Team as listed on the sheet

| # | Name (as on the sheet) | USN (as listed) | Active? (Y/N, fill in) | Role (A–D, fill in) |
|---|---|---|---|---|
| 1 | Pallavi Bammanni | 1DT24CS185 | | |
| 2 | Preethi S Pujari | 1DT24CS195 | | |
| 3 | Sagar R | 1DT24CS232 | | |
| 4 | R S Diya | 1DT24CS206 | | |
| 5 | Nisha A | 1DT24CS178 | | |

> **Two things to check.** (1) The PDF row lists **5 names**, but your team is 6 — ask faculty to confirm the official list so nobody is missing from the submission. (2) The PDF text is jumbled, so names were matched to USNs **by order**; verify each USN against your class list.

### 1.2 Four work-streams (Roles A–D)

| Role | Owns | Main outputs | Writes in the report | Rough effort* |
|---|---|---|---|---|
| **A — Blender Lead** (digital twin) | §7, Blender half of §9 | `.blend`, 12 renders, Sheet S3, CIE diagram, compositor demo, node-tree screenshots | Method–Blender, figures | 15–20 h |
| **B — Measurement Lead** (physical world) | §8, photo half of §9 | Light box, printed labels, 72 photos, Sheet S4, ROI coordinates; the same box is used for the user study | Method–Physical, Limitations | 15–20 h |
| **C — Study & Statistics Lead** | §10, §11 | Protocol, consent, trial sheets, pilot, sessions, cleaned data, stats output | Method–Study, Results–Study | 20–25 h + session time |
| **D — Literature, Sustainability & Report Lead** | §5, §12, §13 | S1, S1b, simulation, SDG/carbon sheet S8, report assembly, references, slides | Abstract, Intro, Related work, SDG, Discussion, Conclusion | 15–20 h |

\*Rough estimates for planning only.

**Pair up so each person has a backup:** A + B cover measurement; C + D cover study and impact.

**What blocks what (critical path):**
- The **colour set** (Sheet S2) is needed by A (renders), B (prints) and C (legend). Freeze it on **Day 2**.
- B's **light box and printed labels** are needed by the user study. B is on the critical path, so start Day 1.
- A's renders and B's photos are both needed by the ΔE script (Day 5–6). The user study does **not** wait for ΔE; ΔE is merged in later during the stats.
- D's reading is independent until writing starts.

### 1.3 14-day parallel plan (squeeze or stretch to your real deadline)

| Day | A — Blender | B — Physical | C — Study & stats | D — Literature & report | Gate |
|---|---|---|---|---|---|
| 1 | Install Blender, save `.blend`, run scene script (calibrate) | Get bulb, grey card, box, matte paper | Read §10; draft consent and instructions | Read Nigam + Li; start S1 | Kick-off + send §4.1 questions |
| 2 | Calibrate light strength; check colour management | Print test labels; test camera settings | Run trial-sheet generator; design legend image | Finish S1 for three papers | **Freeze 1: Sheet S2** |
| 3 | Render the 12 images; fill S3 | Verify lights (warm-up, lux, uniformity); tape position marks | Dry-run of the session script inside the team | Finish S1 + S1b | |
| 4 | Chromaticity figure v1; compositor demo | Photo session 1 (all lights) → S4 | Pilot with 3 outsiders | SDG and carbon table draft; report outline | **Pilot OK?** |
| 5 | Find ROIs; run ΔE script | Photo session 2 (retakes) | Fix the protocol; print the trial sheets | Intro + related-work draft | **Freeze 2: ΔE table** |
| 6 | Sanity-check ΔE; Level-3 extras if time | Recruit participants; write Method–Physical | Sessions start | Set up simulation script | |
| 7–9 | Run sessions (crew roles §10.3) | Run sessions | Run sessions + data entry | Run sessions | **Gate: ≥ 30 complete** |
| 10 | Final figures F1–F6 | Limitations text | Stats + figure | Simulation with measured miss rates; carbon calc | |
| 11–12 | Write A sections | Write B sections | Write C sections | Write D sections; assemble | |
| 13 | Rubric check of figures | Proofread | Proofread | Merge, slides, outside reader | |
| 14 | Export PDF, zip, rehearse | Rehearse | Rehearse | Submit | **Submit** |

### 1.4 If the number of active people changes
- **3 people:** merge D into C (C does stats and simulation); B writes the literature extraction for two papers.
- **5–6 people:** the extra members do *non-critical* work: recruiting participants (each brings 5), proofreading, formatting references, slides. Do **not** put them on the critical path (colour freeze, photos, ΔE script).
- Keep a **contribution log** (Sheet S9: who did what, when). It protects everyone if the faculty asks.

### 1.5 Team rules
- One shared folder (Drive) for photos and sheets; code can live in GitHub, but **keep photos out of the repo** (too large).
- 10-minute stand-up every day (what I finished / what blocks me).
- Never rename or edit raw files after analysis starts; work on copies.
- The person who owns a file is the only one who edits it; others comment.

---

## 2. Understand the question

### 2.1 In plain English
Two questions: **(1)** how different does the warning colour look between what Blender shows and what is printed on the real shelf label — under daylight-like light (D65) and under shop LED light? **(2)** Do bigger colour differences make staff pick the wrong action, including **missing the "donate now" signal**?

### 2.2 Key terms

| Term | Meaning here |
|---|---|
| **ΔE (ΔE00, CIEDE2000)** | One number for how different two colours look, computed in CIELAB. CIEDE2000 corrects CIELAB's unevenness. Rules of thumb (not laws): < 1 barely noticeable, 1–2 noticeable only on close inspection, 2–5 noticeable at a glance, > 5 clearly different. The sheet itself uses **ΔE < 2** as the "reproducible" bar (Q14), so we call **< 2 an acceptable match**. |
| **D65** | CIE standard daylight (about 6504 K); also the white of sRGB and of Blender's default working space. A "6500 K daylight" LED bulb only *approximates* it. |
| **Store LED** | Shop lighting is typically warm-to-neutral white LED (about 3000–4000 K). There is no single standard, so **you must define yours** (colour temperature, CRI, lux) and state it. |
| **White point / illuminant** | The colour of the light, as CIE xy. D65 = (0.3127, 0.3290). |
| **Chromatic adaptation** | The eye partly cancels the light's colour (white paper still looks white under a warm lamp). We imitate it by forcing the grey card to neutral. We report **adapted ΔE (primary)** and **unadapted ΔE (secondary)**. |
| **Metamerism** | Two samples match under one light but not another because their spectra differ. It needs full spectra, so a 3-channel RGB renderer cannot model it. |
| **Chromaticity xy, spectral locus, gamut triangle** | The CIE 1931 diagram, the horseshoe of pure spectral colours, and the triangle spanned by three primaries. sRGB primaries: R (0.64, 0.33), G (0.30, 0.60), B (0.15, 0.06). |
| **Dominant wavelength / purity** | Draw a line from the white point through your colour to the spectral locus. Where it hits is the dominant wavelength; how far along the line your colour sits is the purity (saturation). |
| **Missed donation trigger ("miss")** | A **red / donate-now** label for which the participant chooses any other action. Secondary outcome **"error"** = any wrong action for any colour. |

### 2.3 Research questions and hypotheses (write these into Sheet S2 *before* collecting data)
- **RQ1** — How large is ΔE00 between the Blender-rendered label colour and the physical label colour under **L1 (≈ D65)**, **L2 (store LED, 4000 K)** and **L3 (warm LED, 3000 K)**?
  **H1:** we expect ΔE00 to be larger under store LED than under D65 (spectral mismatch); tested two-sided. Primary contrast L1 vs L2; L3 is a sensitivity check.
- **RQ2** — Does a larger ΔE00 raise the chance of a wrong action, including missing the donate-now signal?
  **H2:** the odds of a wrong action increase with ΔE00 (logistic slope > 0).
- **RQ3** — How much would the observed miss rate reduce a near-expiry outcome in a simple A/B simulation? (descriptive)

### 2.4 The key idea (your novelty and your honest limitation in one paragraph)
Cycles and Eevee are **RGB renderers**: light and surface colours are three numbers each. If you white-balance a render against its grey card, the label colour comes out equal to the label's RGB albedo **whatever the light's colour temperature**. A physical label under a real LED does not behave like that, because real reflectance curves and LED spectra have shape. So the ΔE you measure is **the part of real-world appearance that an RGB digital twin cannot predict.** (This holds for standard Cycles builds; check your Blender version's release notes, and if your version has spectral rendering, say so and adapt.)

### 2.5 Variables and controls

| Item | Levels / setting | How it is controlled |
|---|---|---|
| IV1 — light | L1 6500 K, L2 4000 K, L3 3000 K | same lamp position, lux within ±20 %, 10-min warm-up, room dark |
| IV2 — colour | G, Y, O, R | frozen hex values |
| DV1 — ΔE00 | Blender vs physical | CIEDE2000; 3 label copies × 2 shots |
| DV2 — error / miss | participant's chosen action | counterbalanced light blocks, randomised colour order |
| Confounds | printer drift, paper, camera auto-modes, screen colour shift, adaptation time, colour-vision difficulty, order effects, stray room light | one printer/paper; manual camera; screen in sRGB mode with night-shift/True Tone off; 30 s adaptation; self-report; rotating block order; room lights off |

---

## 3. Marks map — what earns the 30 marks

*(This is the rubric "sheet": five columns, 6 marks each, exactly as in the PDF. The faculty fills the marks; you fill the **evidence**.)*

| Criterion | What the grader asks (from the sheet) | What you must show | Where in the report | Evidence file | Owner |
|---|---|---|---|---|---|
| **1. Methodological novelty (6)** | Is the colour-theory / Blender method new vs. Pilarski, Jullien, Li, Wadhawan, Nigam? | A novelty matrix proving none of the five measures the digital-vs-physical label colour gap under different illuminants, plus one clear gap sentence | Intro, Related work, Table T1 | S1, S1b | D |
| **2. Applicability to retail failure modes (6)** | Does it solve a named failure (Near-Expiry, Low Stock, High Demand, Overstocked, Expired)? | Name **Near-Expiry** (which becomes **Expired** if missed); draw the failure chain; tie to Nigam's reported Near-Expiry failure (donation-capacity bottleneck, sustainability score < 0.9) | Intro, Discussion | S1 (Nigam row), failure-chain figure, simulation | D + C |
| **3. Rigour / evaluability (6)** | Can it be validated (ΔE, user study, A/B RL, statistical test)? | ΔE00 table with CIs; user study n ≥ 30; logistic model; A/B simulation; hypotheses written beforehand; limitations | Method, Results | S5, S7, stats output | C + A + B |
| **4. Sustainability & SDG alignment (6)** | SDG 12.3, SDG 13, carbon auditability, donation / recycling | Failure chain → waste → emissions; mapping to SDG 12.3 and 13; an auditable carbon calculation with a cited factor; donation-capacity discussion | Section 6 | S8, simulation | D |
| **5. Execution feasibility in Blender (6)** | Implementable in Eevee / Cycles / Geometry Nodes / compositor with Module 3 constructs? | Screenshots of scene, Blackbody→Emission node tree, compositor white-balance, colour-management panel; a list of **Module 3 constructs used** (CIE xy diagram, spectral locus, dominant wavelength / purity, gamut triangle, XYZ primaries, metamerism); the `.blend` file | Method–Blender | S3, screenshots, `.blend` | A |

**Gap sentences you can adapt (fill the brackets only after reading the papers):**
- *Novelty:* "Pilarski, Jullien, Li, Wadhawan and Nigam address [what you verified], but none checks whether the colour a digital twin shows matches the colour printed on the shelf label under real store lighting. We measure that gap (ΔE00) and test whether it predicts missed donation actions."
- *Applicability:* "A near-expiry batch whose label is misread is not donated or discounted in time and becomes expired stock, the loss that Nigam's Near-Expiry scenario already struggles with (donation capacity, sustainability score below 0.9)."
- *Rigour:* "We report ΔE00 (CIEDE2000) with 95 % confidence intervals from [n] replicates and test whether ΔE00 predicts wrong actions with logistic regression clustered by participant ([n] participants)."
- *SDG:* "Each unit saved from expiry avoids [x] kg of food waste and [y] kg CO₂e (source: [cite]), contributing to SDG 12.3 and SDG 13."
- *Blender:* "The study uses Cycles with the Standard view transform, a Blackbody-driven emissive panel as the lamp, a compositor white-balance, and procedurally generated chromaticity geometry."

---

## 4. Phase 0 — Before you start

### 4.1 Questions to send faculty (one message, Day 1; paste the answers into Sheet S2)
1. What is the **submission format and length** (report, PPT, demo, viva) and the **deadline**?
2. Do you expect an **executed experiment** (real measurements and participants) or a **feasibility design with a working Blender prototype**?
3. The sheet lists **5 names** for our row but our team has 6. What is the official list?
4. Is it acceptable to run a short, **anonymous, voluntary** study with classmates?
5. Which **Blender version** is expected, and is a **colorimeter / spectrophotometer** available in college?
6. Is there a policy on **disclosing AI assistance**? (If yes, follow it.)
7. Is there any extra form or "sheet" we must fill besides the report? (The PDF you have is the rubric sheet; faculty fill the marks.)

### 4.2 Tools

| Tool | Who | Note |
|---|---|---|
| Blender (same version for everyone; note it in Help ▸ About) | A (everyone installs) | Blender 5.x has extra colour options (working space, HDR); leave them at default for this study |
| Python 3.10+ and the libraries below | A, C, D | Analysis scripts |
| Excel or Google Sheets | All | Sheets S1–S9 |
| Image viewer with pixel read-out (Paint, GIMP) | A, B | Finding ROI coordinates |
| Phone with manual camera (iPhone: a manual-camera app) | B | Fixed settings, §8.5 |
| Lux-meter app on a second phone | B | Approximate only; use for *equality* between lights |

```bash
pip install numpy pandas scipy scikit-image statsmodels matplotlib pillow colour-science   # all analysis libraries in one go
python q3_colour_pipeline.py --roi-check data/phone_photos/R_L2_c1_s1.jpg physical        # draws ROI boxes so you can verify placement
python q3_colour_pipeline.py                                                              # ΔE00 tables + chromaticity data
python q3_make_trial_sheets.py                                                            # builds data/trial_data.csv for the study
python q3_stats.py                                                                        # statistics once the study data is entered
python q3_donation_sim.py                                                                 # toy A/B simulation
```

### 4.3 Folder structure (create it on Day 1; everyone uses the same one)

```
q3-project/
├─ q3_project.blend               # save the Blender file HERE (project root)
├─ q3_colour_pipeline.py          # Appendix C
├─ q3_make_trial_sheets.py        # Appendix D
├─ q3_stats.py                    # Appendix E
├─ q3_donation_sim.py             # Appendix F
├─ data/
│  ├─ blender_renders/            # R_L1.png ... (12 files)
│  ├─ phone_photos/               # R_L1_c1_s1.jpg ... (72 files)
│  └─ trial_data.csv              # user-study responses
├─ results/                       # created automatically by the scripts
├─ report/                        # drafts, figures, final PDF
└─ sheets/                        # exports of Sheets S1–S9
```

### 4.4 Naming conventions (the scripts depend on them)
- Colour IDs: single letters **G, Y, O, R**. Light IDs: **L1, L2, L3**.
- Renders: `R_L2.png` (colour_light). Photos: `R_L2_c1_s1.jpg` (colour_light_**c**opy_**s**hot).
- Participants: `P01`…`P36`. Never rename a file after analysis has started.

---

## 5. Phase 1 — Literature (Role D leads; ~1.5 days)

### 5.1 How to read
Everyone reads the abstract, introduction and conclusion of all five papers (20 min each) so anyone can answer in the viva. D reads in depth, in this order: **Nigam** (the Near-Expiry scenario is your anchor) → **Li** → **Jullien** → **Pilarski** → **Wadhawan**.

Pointers: *Jullien* is probably "A Simulation Environment and Reinforcement Learning Method for Waste Reduction" (Jullien et al., arXiv 2205.15455, the RetaiL environment built on real grocery data). **Check that it is the paper your faculty means.** Nigam's paper could not be located online while preparing this guide, so use the copy your faculty gave; for the others, search the first author + "perishable" / "retail inventory" + "reinforcement learning" and confirm with faculty.

### 5.2 What the PDF already tells you (starter notes, from the other questions in the sheet)

| Paper | What the sheet says about it |
|---|---|
| Pilarski | Notes stability issues (Q2) |
| Jullien | Injects Gaussian forecast noise (Q5) |
| Li et al. (2023) | Existing ABC / FSN / VED methods fail to flag near-expiry stock in time; dashboards overload managers with tabular KPIs (Q1, Q8) |
| Wadhawan | The sheet gives no detail — read it |
| Nigam | Near-Expiry scenario failed (donation-capacity bottleneck, sustainability score < 0.9); Low-Stock 0 % pass; High-Demand 9.1 % pass; fixed restock rule Si < 0.8·Di; naive moving-average forecast (Eq. 2); discount tiers 25 / 50 / 75 %; five categories A–E; 2D bar chart (Fig. 3); cloud-native deployment with REST APIs and dashboards |

### 5.3 What to extract from Nigam (fill Sheet S1)
1. How the **Near-Expiry scenario** is defined (stock, shelf life, demand).
2. The **actions** the agent can take (discount tiers, donate, restock) and the **donation capacity**.
3. The exact **formula for the sustainability score** and the pass threshold (0.9).
4. How "pass" is defined per scenario.
5. Whether there is any **visual / dashboard** element and how it shows state (Fig. 3).
6. Whether **code or data** are public.
7. The **limitations** section: what the authors say is unsolved.
8. **Page and figure numbers** to cite.

### 5.4 How to fill the novelty matrix (Sheet S1b)
For each feature mark ✔ / ✘ / ? **only after searching the full text** for: "colour", "color", "ΔE", "illuminant", "LED", "label", "Blender", "visual". Never write ✘ for something you did not check. This matrix becomes **Table T1** and is your evidence for rubric column 1.

---

## 6. Phase 2 — Experiment design (then **freeze** it)

### 6.1 Colour set (default; change only on Day 1–2)

| ID | Meaning on the shelf | Suggested sRGB hex | Why |
|---|---|---|---|
| **G** | Fresh — no action | `#2E9E4F` | Control, clearly different hue |
| **Y** | Watch (tier 1, amber) | `#F5B700` | Neighbour of orange |
| **O** | Discount now (tier 2, orange) | `#F07C1E` | Neighbour of both amber and red |
| **R** | **Donate now — the expiry-warning colour** | `#D62828` | The colour the question is about |

Keep **4–6 colours with hue neighbours** (amber / orange / red): confusions happen between neighbours, and without a spread of ΔE values you cannot test whether ΔE predicts errors. After reading Nigam, replace the action meanings with his exact states.

### 6.2 Lights

| ID | Role | Spec | Note |
|---|---|---|---|
| **L1** | "D65-approximating" daylight | 6500 K LED, CRI as high as you can get (≥ 80) | Not true D65: always say "approximating" |
| **L2** | **Store LED — neutral (primary "store LED")** | about 4000 K | Typical shop |
| **L3** | Store LED — warm (sensitivity check) | about 3000 K | |

All lights: same lamp position, about 500 lux at the label (equal across lights within ±20 %), 10-minute warm-up, room lights and windows off. **Best:** one 3-mode or tunable-white bulb, so the lamp never moves.

### 6.3 Conditions and counts
4 colours × 3 lights = **12 conditions**. Digital: 12 renders. Physical: × 3 label copies × 2 shots = **72 photos**. User study: × 2 repeats = **24 trials per participant**.

### 6.4 Label design and printing
- Card **8 cm × 5 cm**, solid colour patch, identical neutral text on every label (for example "Milk 500 ml", **no expiry date**, which would give a non-colour cue).
- **Matte** paper; **one printer** for everything; **3 copies** per colour; an **18 % grey card** of the same size sits beside the label.
- Print at **100 % scale** (no "fit to page"), highest quality, sRGB / application-managed colour, **no auto-enhance or "vivid" modes**. Record printer model, paper and settings in Sheet S2.
- Let inkjet prints dry at least a few hours, ideally 24 h, before measuring.
- Write colour ID and copy number (c1–c3) on the back.

### 6.5 Freeze point 1 (Day 2)
Fill Sheet S2 completely (colours, lights, bulb CCT/CRI, lux, printer/paper/settings, phone and camera settings, Blender version/engine/settings, hypotheses, tests). **After this: no changes** unless the whole team agrees and logs why. Changing settings mid-study is the fastest way to invalidate your data.

---

## 7. Phase 3 — Blender (Role A)

### 7.1 The idea: the digital twin mirrors the physical box

```
        [ lamp panel 0.5 × 0.5 m, 0.40 m above, facing down ]
                  ▼  light colour = Blackbody node (6500 / 4000 / 3000 K)
      [ LABEL ]   [ GREY CARD 18 % ]      ← on a neutral grey "shelf"
              ╲         ╱
        camera at 45° (0, −0.35, 0.35 m), looking at the middle
```
Label **and** grey card are in the same frame, exactly as in the phone photos, so both pipelines can be normalised the same way (§9).

### 7.2 Script route (recommended)
1. Install Blender; note the exact version. Everyone uses the same version.
2. **File ▸ New ▸ General**, then **File ▸ Save As…** into the **project root** (`q3_project.blend`).
3. **Scripting** workspace ▸ **New** ▸ paste **Appendix A** ▸ **Run Script** (Alt + P).
4. **Calibration:** with `CALIBRATE = True` it renders `data/_calibration_white.png`. Open it (Image Editor ▸ Image ▸ Open) and read the **left patch** with the Sample tool. Aim for **about 235–245** in each channel, R ≈ G ≈ B within about 3. Too dark or too bright → change `LIGHT_STRENGTH`, run again.
5. Set `CALIBRATE = False`, run again → **12 PNGs** in `data/blender_renders/`.
6. Log every render in **Sheet S3**.
7. Check the ROI boxes (§9.2, `--roi-check … digital`).
8. Take the screenshots in §7.5.

### 7.3 Manual route (so you can explain every setting in the viva)
- **Render Properties:** Engine **Cycles**; Samples **128**; Denoise **off**.
- **Color Management:** Display Device **sRGB**; View Transform **Standard**; Look **None**; Exposure **0**; Gamma **1**. (In Blender 5.x also leave *Working Space* at its default, Linear Rec.709, and do not use HDR display.)
- **World:** black colour, strength 0 (the lamp must be the only light).
- **Objects (metres):** shelf plane (grey 0.18), label plane, grey-card plane (albedo 0.18), each with a **Diffuse BSDF** (not Principled, which adds stray specular). Lamp = plane with an **Emission** shader whose colour comes from a **Blackbody** node (Temperature 6500 / 4000 / 3000), rotated to face down.
- **Camera:** 50 mm at (0, −0.35, 0.35) m, rotation X = 45°.
- **Output:** PNG, RGB, 8-bit, 1280 × 720. Render with **F12** (a *final* render, never the viewport), then Image ▸ Save As.
- Enter label colours with the **Hex** field (it is sRGB); grey albedo with the **RGB** sliders (linear) = 0.18.

### 7.4 Why these settings (viva-ready)

| Setting | Why |
|---|---|
| **Standard** view transform | No tone mapping or desaturation, so output equals the sRGB form of the scene colour and can be compared with the hex value. AgX and Filmic compress and desaturate bright colours, which would break the comparison |
| Cycles, denoise off | Physically based light transport; the denoiser can smear or shift flat colours |
| Diffuse BSDF | Matte paper-like surface |
| Grey card in frame | Allows the same white-balance / exposure normalisation as in the photos |
| Blackbody emissive panel | Light colour set in kelvin, like a bulb's CCT |
| Black world | No stray ambient colour |

### 7.5 Figures and records from the Blender phase
- **F1** scene screenshot (3D view + camera view) · **F2** lamp node tree (Blackbody → Emission) · **F3** Color Management panel · **F4** 4 × 3 contact sheet of the 12 renders · **F5** CIE xy diagram (§7.7) · **F6** compositor node tree (§7.6).
- **Sheet S3**: one row per render. **Sanity check:** the pipeline prints ΔE00 between each render and its target hex; it should be **below about 1**.

### 7.6 Compositor white-balance demo (cheap, and strong for rubric column 5)
1. **Compositing** workspace; enable **Use Nodes** (in Blender 5.x click **New** to create a compositing node group).
2. **Render Layers → Mix (blend: Divide)**; its second input is an **RGB** node set to the grey card's linear RGB (columns `grey_lin_r/g/b` in `results/measurements.csv`).
3. Add a second **Mix (Multiply)** with **RGB 0.18, 0.18, 0.18**, then connect to **Composite** / **Viewer**.
4. Render. The grey card becomes neutral and the label colour should match its target hex. Screenshot the node tree (**F6**).

### 7.7 CIE chromaticity diagram in Blender (Module 3 constructs)
1. Run the ΔE pipeline first (§9) so `results/locus.csv` and `results/measurements.csv` exist.
2. In the same `.blend`, run **Appendix B** → `results/fig_cie_xy.png`.
3. How to read it: target colours sit inside the **sRGB gamut triangle**; each coloured **path** shows how the physical label's chromaticity drifts as the light changes (unadapted); the **grey path** shows the lamp's white point moving away from D65 toward the orange corner.
4. Put **dominant wavelength and purity** (columns `dom_wl_nm`, `purity`) into **Table T3**.
5. Add axis labels (x, y) and a legend in your report editor.

### 7.8 Stretch items (Level 3)
- **Geometry Nodes gamut triangle:** new Geometry Nodes group on an empty mesh; inputs = three Vector sockets (R, G, B primaries as xy); three **Curve Line** nodes → **Join Geometry** → **Curve to Mesh** with a small **Curve Circle** profile. Edit the primaries and the triangle updates (Module 3, Fig. 8 style).
- **Printer gamut:** print pure R, G, B patches, photograph them with the same pipeline and draw the printer's triangle next to sRGB's; it explains part of the baseline ΔE.
- **Eevee vs Cycles:** render the same 12 conditions in Eevee and compute ΔE between engines. Eevee treats emissive meshes differently, so use an Area light with the same Blackbody colour; if it does not light the scene, skip it.
- **Metameric pair demo:** two samples (for example printed red and red marker ink) that match under L1 but not under L2.

---

## 8. Phase 4 — Physical measurement (Role B)

### 8.1 Shopping / borrowing list
- **One 3-mode (cool / neutral / warm) LED bulb or a tunable-white bulb** (check the pack for colour temperature and CRI). Fallback: three separate bulbs.
- Lamp holder and cable (check whether your bulb base is B22 or E27).
- **18 % grey card** (photographic, matte), one for the team.
- Cardboard or foam-board box about 40 × 40 × 40 cm, **matte white or neutral grey inside**, plus black cloth for the opening.
- **Matte paper** (see §15 on bright-white paper), access to **one** printer.
- Phone with **manual camera mode**, tripod or fixed stand, remote or timer.
- Free **lux-meter** app on a second phone.
- Masking tape, ruler, scissors.
- *Optional:* a colorimeter or spectrophotometer if a department or friend has one.

### 8.2 Build the light box
- Lamp hangs at the top centre, **35–40 cm** above the base.
- Base is neutral and matte. Mark with tape: **label on the left, grey card on the right**, about 12 cm centre to centre (mirror positions under the lamp so both get equal light).
- The phone sits at a front opening about **35–45 cm** from the cards at roughly **45°**, locked in place (mark the tripod feet).
- Cover every opening so no room light enters. **Test:** lamp off, the inside should be almost dark.

### 8.3 Labels
Print and prepare them exactly as in §6.4 (100 % scale, no enhancement, matte, one printer, 3 copies per colour, dry ≥ 24 h, back-labelled).

### 8.4 Verify the lights (before the photo session and before every study day)
1. Warm up **10 minutes** after every mode change.
2. **Lux:** measure at the label position; keep the three lights within **±20 %** and write the numbers in Sheet S4.
3. **Uniformity test:** photograph the grey card at the label position and at the grey-card position; the mean brightness should differ by less than about **3 %**.
4. **No spill:** lamp off, room closed, the box should be dark.

### 8.5 Camera settings (manual; never change them between lights)
- **ISO fixed** (100–200). **White balance fixed manually** (for example 5000 K) and **never changed**; the software normalisation does the adapting.
- Shutter chosen so the grey card is mid-tone and nothing is clipped; keep that shutter for the whole light block.
- Focus locked. **No HDR, no beauty / AI scene modes, no flash, no digital zoom.** Use a 2–10 s timer.
- Save high-quality JPEG (RAW + JPEG if possible).
- **iPhone:** photos may carry a Display P3 profile; the script converts any embedded profile to sRGB. **Android:** use the natural / sRGB colour mode.

### 8.6 Photo protocol (about 25 min per light)
1. Switch to the light, wait 10 min the first time, set the shutter, take a test and check nothing is clipped.
2. For each colour **G, Y, O, R** and each label copy **c1–c3**: put the label at the left mark and the grey card at the right mark; take **2 shots** (s1, s2) without touching anything (just re-press the timer).
3. **Rename immediately** to `R_L2_c1_s1.jpg` (colour_light_copy_shot).
4. Fill **Sheet S4** as you go.
5. **Drift check:** at the end of each light block, re-shoot the very first label; its ΔE00 against the first shot should be **below 1**. If not, redo the block.

Total: 4 colours × 3 copies × 2 shots × 3 lights = **72 photos**.

### 8.7 Optional: spectrophotometer (Level 3)
Measure each label's reflectance curve. You can then compute Lab under true D65 and under a reference LED spectrum instead of relying on a bulb and a phone (CIE 15:2018 publishes reference LED spectra). Report both and compare with the phone result.

---

## 9. Phase 5 — Computing ΔE (A + B)

### 9.1 What the script does

```
Blender PNG (label + grey card)          Phone JPG (label + grey card)
   │ read sRGB → linear                     │ read sRGB (convert embedded profile) → linear
   │ average inside the ROI boxes           │ average inside the ROI boxes
   ▼                                        ▼
 normalise to the grey card (18 %)       normalise to the grey card (18 %)
 ├─ ADAPTED   (grey card forced neutral) ├─ ADAPTED
 └─ UNADAPTED (exposure only)            └─ UNADAPTED
   ▼                                        ▼
   └──────────── CIELAB (D65, 2°) ──────────┘
                      ▼
 ΔE00, ΔL*, ΔC*, ΔH*  +  xy, dominant wavelength, purity
```

### 9.2 Step by step
1. Put the 12 PNGs in `data/blender_renders/` and the 72 JPGs in `data/phone_photos/`.
2. Open `q3_colour_pipeline.py`: check `COLOURS` (same hex as Sheet S2) and **`ROI_PHYSICAL`** (the default numbers are placeholders).
3. Find coordinates: open one photo in Paint / GIMP, hover over two opposite corners **well inside** each patch and note the pixel positions. Then check:
   `python q3_colour_pipeline.py --roi-check data/phone_photos/R_L2_c1_s1.jpg physical` → open `results/roi_check.png`; both magenta boxes must sit fully inside their patches. Repeat for one photo of each light.
4. Same for the renders: `--roi-check data/blender_renders/R_L1.png digital` (the default digital ROIs fit the layout built by Appendix A).
5. Run `python q3_colour_pipeline.py`.
6. Read the output: the **sanity check** (digital vs target, should be below about 1.5), the **summary table**, and the number of **flagged** measurements.
7. Copy `results/delta_e_summary.csv` into **Sheet S5**.

### 9.3 How to read the results
- **ΔE00 bands** (rules of thumb): < 1 indistinguishable for most viewers · 1–2 noticeable only on close inspection · 2–5 noticeable at a glance · > 5 clearly different. **Your acceptance line is ΔE00 < 2.**
- **Why is it large?** Use the components. **ΔL\*** positive = physical lighter than digital. **ΔC\*** negative = physical duller (printed colours are often less saturated than screen colours). **|ΔH\*|** = hue shift; this is what makes neighbours (orange vs red) get confused.

| Pattern | Likely cause | What to write |
|---|---|---|
| ΔE00 small (< 2) under all lights | Print + camera pipeline reproduce the digital colour; light effect small | "Colour fidelity is not the bottleneck in this setup"; use a stress condition (cheap paper or another print mode) to widen the range |
| ΔE00 similar under all lights but large (> 3) | Gamut / print / camera error, not the light | Discuss printer gamut and camera rendering |
| ΔE00 grows from L1 to L3 | Spectral (metameric) effects of the LED and camera | Discuss metamerism and the RGB-renderer limitation (§2.4) |
| Large scatter between copies | Print variability, glare or a bad ROI | Check flags; improve the procedure; report the scatter |

**Report whatever you get.** A small ΔE is a valid finding; never tune colours to make ΔE look small.

### 9.4 Quality gates (all must pass before you freeze the ΔE table: **Freeze 2**)
- Digital render vs target hex: **ΔE00 < 1.5** for every render.
- SD across the two shots of the same label: **< 0.5**; SD across label copies: **< 1.0**.
- **Flagged = 0**, or each flag explained (clipping, glare, bad ROI) and the photo retaken.
- Drift check from §8.6: **< 1**.

### 9.5 Dominant wavelength and purity (Table T3)
`results/measurements.csv` holds `dom_wl_nm` and `purity` (relative to D65). Tabulate them for target, digital and physical-by-light. A shift of the dominant wavelength under L2 / L3 is a concrete, Module 3-style way to describe the colour drift.

---

## 10. Phase 6 — User study (Role C leads; everyone helps)

### 10.1 Design in one paragraph
Within-subjects. Every participant sees **4 colours × 3 lights × 2 repeats = 24 trials**, in **3 light blocks**. The block order rotates through all **6 permutations** of L1/L2/L3 and colour order is randomised inside each block. Target **36 participants** (4 active members × 9 each = 6 per block order); the faculty benchmark is **n ≥ 30**.

### 10.2 Setup checklist
- Room dark; the box lamp is the **only** light on the label.
- **Legend on a laptop** (sRGB mode, fixed brightness about 50–60 %, **night-shift / True Tone / auto-brightness OFF**): four squares in exactly the target hex values with the actions "Green — Fresh — no action", "Amber — Watch", "Orange — Discount now", "Red — Donate now". Export the squares from Blender (flat emission, Standard view) so the legend is the *digital* colour.
- Participant sits 50–60 cm from the box opening.
- **Adaptation:** 30 s in each new light before its trials.
- Each trial: the label is in view for **5 s**; the participant names the action (A fresh / B watch / C discount / D donate); no changing answers.
- Warm the bulb 10 min at the start of each day; check lux; record the block order in the sheet.

### 10.3 Session crew (4 people, rotate roles)
| Role | Job |
|---|---|
| Facilitator | Reads the script, swaps labels, runs the 5-second timer |
| Recorder | Enters responses A–D into the sheet |
| Recruiter | Brings the next participant, handles consent and demographics |
| Floater | Resets the box, checks lamp mode and lux, prepares the next sheet |

### 10.4 Trial sheet
`python q3_make_trial_sheets.py` → `data/trial_data.csv` (864 rows). Upload it to Sheets; each participant is a block of 24 rows; the Recorder fills the `response` column.

### 10.5 Session script (about 8 minutes)
> "Thanks for helping. This is a short, anonymous colour task for a college project. You can stop at any time. We record only a participant number, your answers, and whether you have any colour-vision difficulty (self-reported). Do you agree to take part?" *(wait for yes)*
> "Imagine you work in a shop checking shelf labels. The laptop shows what each colour means: green is fresh, amber is watch, orange is discount, red is donate now. I'll show a label for a few seconds; tell me which action it means. Some will be hard, so just give your best guess. The light will change a few times; we'll pause for 30 seconds each time."

**Demographics (Sheet S6):** age band (18–20 / 21–25 / 26+), colour-vision self-report (no known difficulty / yes / unsure).

### 10.6 Pilot (Day 4)
Three outsiders. Check timing, wording, legend clarity and adaptation. Fix problems. **Pilot data never goes into the main dataset** (use IDs PILOT1–PILOT3).

### 10.7 Running it
- 9 participants per member, over about 3 days, **maximum 6 per day** (fatigue).
- **No coaching** and do not reveal the hypothesis.
- Enter data **the same day**.

### 10.8 Exclusions (always documented in Sheet S6, never silent)
Participants who report **colour-vision difficulty** go into a separate appendix analysis; **incomplete sessions** (fewer than 20 trials) and sessions where the lamp or room light failed are excluded with the reason written down.

### 10.9 Fallback if physical sessions are impossible
**Screen-photo mode:** show 12 representative photos (one per condition) on a laptop (sRGB, fixed brightness, dark room) in a Google Form with randomised order. Say clearly that screen viewing replaces real viewing and adaptation to the photographed light is lost; treat it as a weaker, Level-1.5 result.

### 10.10 Ethics and courtesy
Voluntary, anonymous, no personal data, no pressure, thank everyone, and make sure faculty are fine with it (§4.1).

---

## 11. Phase 7 — Statistics (Role C)

### 11.1 What to run and how to report it (`q3_stats.py`)

| Question | Test | How to report |
|---|---|---|
| **H1** — does ΔE00 differ between lights? | Two-way ANOVA (colour × light) on replicate ΔE00; **paired Wilcoxon on label-copy means with Holm correction (the main test)** | "Mean ΔE00 was X under L1 and Y under L2 (difference Z, 95 % CI …, Holm-adjusted p = …)" |
| Do miss rates differ between lights (red labels)? | Friedman test on per-participant miss rate; post-hoc Wilcoxon with Holm | "Miss rate rose from … % to … % (Friedman χ² = …, p = …)" |
| **H2** — does ΔE00 predict wrong actions? | Logistic regression `error ~ ΔE00`, standard errors clustered by participant | "Each +1 ΔE00 multiplied the odds of a wrong action by OR (95 % CI …, p = …)" |
| Effect sizes | Mean differences with 95 % CI; odds ratio | Always give the number, not just "significant" |
| Sample size | n ≥ 30 (faculty benchmark); within-subjects design cuts variance; G\*Power is a free option for a formal calculation | State assumptions |

### 11.2 Common mistakes
- Changing tests after seeing results (p-hacking). The table above is your plan; it is written in Sheet S2 **before** the study.
- Forgetting that ΔE00 varies **by condition**, not by trial: the model has only 12 distinct ΔE values, so say it is a **condition-level predictor**.
- Ignoring multiple comparisons (use Holm).
- Claiming causation. The design shows that ΔE predicts errors; it does not isolate every other difference between conditions.

### 11.3 If results are boring
All ΔE00 < 2 and almost no errors is **a valid result**: "colour fidelity was not a limiting factor in this setup". Report the descriptive tables, say the model could not detect an effect, and (if time) add a **stress condition** (different paper or print mode) to widen the ΔE range. Never drop trials or colours to manufacture a result.

---

## 12. Phase 8 — Impact simulation, SDG and carbon audit (Role D)

### 12.1 The failure chain (draw it as figure F0)
**Label colour misread → donation / discount not triggered → near-expiry stock becomes expired → food waste (SDG 12.3) + production and landfill emissions (SDG 13).**
This is how a small colour error connects to a *named retail failure* (Near-Expiry → Expired) and to sustainability.

### 12.2 The toy A/B simulation (`q3_donation_sim.py`)
- **A** = labels always read correctly (miss rate 0). **B** = labels read with the miss rate you measured for the red labels under each light.
- Step by step: (1) after reading Nigam, replace `PARAMS` with his Near-Expiry scenario values and replace the placeholder score with **his sustainability-score formula**; (2) copy your **red-label miss rates** from `q3_stats.py` into `MISS`; (3) run it; (4) report the table and `fig_sim_sensitivity.png`.
- **Say clearly that it is illustrative.** It is not Nigam's environment. If his code is public, the stronger version is to inject *perception noise* (the agent misses a near-expiry flag with your measured probability), in the same spirit as Jullien injecting forecast noise.
- In the toy model, colour errors cost more when donation capacity is plentiful and less when capacity is the binding limit. That is a property of the toy assumptions; re-check it with Nigam's parameters before you claim it.

### 12.3 SDG mapping (Table in report section 6)

| Goal | Link to your work | Metric | Evidence |
|---|---|---|---|
| **SDG 12.3** (halve per-capita food waste at retail and consumer level by 2030; cut food losses along supply chains) | Reliable early detection of near-expiry stock means more units donated or discounted instead of expiring | Units (kg) diverted from expiry per period; waste rate | Simulation + measured miss rates |
| **SDG 13** (climate action) | Avoided food waste avoids production emissions and landfill methane | kg CO₂e avoided, one cited emission factor | Sheet S8 |
| **Donation / recycling** | Donation is the preferred route; Nigam's failure was a **donation-capacity bottleneck** | Units donated; sensitivity to capacity | Simulation sensitivity plot |

### 12.4 Carbon auditability (Sheet S8)
Formula: **avoided CO₂e (kg) = units saved × mass per unit (kg) × emission factor (kg CO₂e per kg of food)**.
- Pick **one** emission-factor source (for example FAO, WRAP, or a peer-reviewed footprint database); record the **exact value, year and link**. Never use a number you only half-remember; look it up and cite it.
- Show a **low / high** range, not a single value.
- "Auditable" means a reader can recompute your number from the sheet alone: inputs, units, source links, assumptions and the formula all visible.

### 12.5 Don't
No unsourced numbers. No claim that the simulation reproduces Nigam. No double counting (a unit donated *and* sold).

---

## 13. Phase 9 — Writing the report

### 13.1 Outline and word targets (assumes about 4,000 words; scale to the faculty limit)

| Section | Words | Owner |
|---|---|---|
| Title, abstract (150–200 words), keywords | 200 | D |
| 1 Introduction (problem, failure chain, gap, RQs, contributions) | 450 | D |
| 2 Related work (five papers + colour-science basics; **Table T1**) | 500 | D |
| 3 Method: 3.1–3.2 Blender (A) · 3.3 physical set-up (B) · 3.4 user study and 3.5 statistics (C) · 3.6 simulation (D) | 1,000 | A, B, C, D |
| 4 Results: ΔE tables and chromaticity figure (A/B) · study results (C) · simulation (D) | 900 | A, B, C, D |
| 5 Discussion (interpretation, metamerism, limitations, threats to validity) | 500 | D, all review |
| 6 Sustainability and SDG alignment | 300 | D |
| 7 Conclusion and future work | 200 | D |
| References + appendix (settings, sheets, scripts, contribution log) | — | D |

### 13.2 Rubric call-outs
Under each relevant section add one short, bold-labelled paragraph: **"Rubric 1 — Novelty"**, **"Rubric 2 — Applicability (Near-Expiry)"**, **"Rubric 3 — Rigour"**, **"Rubric 4 — Sustainability"**, **"Rubric 5 — Blender feasibility"**. The grader should find each criterion in seconds.

### 13.3 Figures and tables
- **Figures:** F0 failure chain · F1 scene · F2 lamp node tree · F3 colour-management panel · F4 render contact sheet · F5 CIE xy diagram · F6 compositor tree · F7 error vs ΔE00 · F8 simulation sensitivity.
- **Tables:** T1 novelty matrix · T2 frozen design · T3 ΔE00 summary (mean ± 95 % CI) with dominant wavelength · T4 error and miss rates · T5 logistic result · T6 simulation + SDG / carbon table.

### 13.4 Writing rules
- Every claim needs a number or a citation. Define every symbol at first use.
- Past tense for what you did; keep **results** and **interpretation** separate.
- Paraphrase sources and cite them; never paste text or numbers you did not check.
- ΔE to two decimals; always give n and units.
- Follow your college's rule on disclosing AI assistance.

### 13.5 Limitations to state openly
Phone camera is not a spectrophotometer · a 6500 K LED is not D65 · an RGB renderer cannot model metamerism · small colour set · one printer and paper · student participants · the legend screen is not colour-calibrated · the simulation is a toy, not Nigam's environment.

---

## 14. Phase 10 — Final checks, viva and slides

### 14.1 Final checklist
- [ ] Each of the 5 rubric columns has its own clearly marked place in the report.
- [ ] Every figure has a caption and every number in the text matches a table.
- [ ] Scripts, raw photos, renders and sheets are in the zip / Drive link.
- [ ] The `.blend` opens on another laptop (relative paths) and the version is noted.
- [ ] Names and USNs are correct; the contribution log (S9) is filled.
- [ ] References are formatted and every citation in the text appears in the list.
- [ ] Someone outside the team read the report for clarity.
- [ ] The file is named and exported as faculty asked.

### 14.2 Likely viva questions

| Question | Short answer |
|---|---|
| Why CIEDE2000, not ΔE76? | It corrects CIELAB's unevenness (blues, neutrals, chroma and hue weighting) and is the current CIE-recommended formula (ISO/CIE 11664-6). |
| Why the Standard view transform? | Filmic / AgX tone-map and desaturate bright colours; Standard gives output comparable to the hex value. |
| Why can't Blender show metamerism? | Cycles is an RGB renderer; metamerism needs full spectra (light × reflectance). That gap is exactly what we measure. |
| Is a 6500 K bulb D65? | No. D65 is a defined spectrum; a daylight LED only approximates it. Stated as a limitation. |
| Why adapt with a grey card? | Viewers adapt to the light; scaling to a neutral reference imitates that. We also report the unadapted result. |
| How do you know ΔE predicts misses? | Logistic regression clustered by participant, odds ratio per +1 ΔE00. Limitation: condition-level predictor, so it is predictive evidence, not proof of cause. |
| Why n ≥ 30? | Faculty benchmark for within-subjects work; the repeated-measures design reduces variance. |
| What if ΔE < 2 everywhere? | Then colour fidelity is not the bottleneck in this setup, which is a valid and useful finding; a stress condition widens the range. |
| How does it relate to Nigam's Near-Expiry failure? | Nigam's failure was a donation-capacity bottleneck; colour misreads add an avoidable perception-side loss, and the simulation shows how the two interact. |
| Which SDGs? | 12.3 (food waste) and 13 (climate), with an auditable carbon formula and a cited emission factor. |
| Which Module 3 constructs did you use? | CIE xy diagram, spectral locus, dominant wavelength and purity, gamut triangle, XYZ primaries, metamerism. |
| Why Blender, not just Python? | Course requirement; Blender gives physically based lighting, a node-based pipeline (compositor) and procedural geometry for the gamut visuals. |

### 14.3 Slides (about 9; each member presents a part)
1 Title and question · 2 Problem and failure chain · 3 Gap and novelty (T1) · 4 Method: the digital twin · 5 Blender pipeline (F1–F3, F6) · 6 ΔE results (T3, F5) · 7 User study and prediction (T4, F7) · 8 Impact and SDG (F8, carbon table) · 9 Limitations and conclusion.

---

## 15. Do and Don't — the master list

### DO
1. **Freeze** colours, lights, camera, printer and Blender settings before the main run, and write them in Sheet S2.
2. Use **CIEDE2000** for every ΔE and report ΔL\*, ΔC\*, ΔH\* too.
3. Use **final renders (F12) in Cycles with the Standard view transform** for every measurement.
4. Keep the **grey card and the label in the same frame**, same lamp, same photo.
5. Keep raw files untouched; analyse copies; log every file in a sheet.
6. Record Blender version, printer / paper / settings, phone model and camera settings, bulb colour temperature / CRI, and lux.
7. **Pilot first** (3 people) before running 36.
8. Write hypotheses and tests **before** collecting data, and report **all** results, including non-significant ones.
9. State limitations honestly (§13.5).
10. Counterbalance light order and randomise trial order.
11. Cite a source for every number you did not measure (emission factors, thresholds).
12. Give each rubric column its own heading in the report.
13. Hold a daily 10-minute stand-up and keep the contribution log.
14. Check your college's policy on AI-assistance disclosure.

### DON'T
1. **Don't use Filmic, AgX or any "Look"** for measurements: they change saturation and brightness.
2. Don't measure from the 3D viewport or from screenshots; use F12 renders.
3. Don't use phone **auto mode, auto white balance, HDR, beauty filters or night mode**.
4. Don't photograph a screen and treat it as data.
5. Don't print with auto-enhance or "vivid"; don't change printer settings mid-study.
6. Don't use glossy paper. Don't use bright-white copier paper as your reference: optical brighteners react to UV in daylight bulbs but not in LEDs, so it changes between lights. Use the grey card.
7. Don't leave room lights or window light on during the experiment (mixed illuminants).
8. **Don't fabricate, "clean" or selectively drop data, and don't tune colours until ΔE looks small.** Small or negative results are valid.
9. Don't call a 6500 K bulb "D65" without saying it is an approximation.
10. Don't mix Eevee and Cycles in the main dataset.
11. Don't reveal the hypothesis to participants or coach them mid-trial.
12. Don't collect personal identifiers; use P01–P36.
13. Don't claim causation from a condition-level predictor.
14. Don't copy text or numbers from papers; paraphrase and cite.
15. Don't leave writing to the last day, and don't change the method after seeing results without logging why.
16. Don't reuse one person's ROI coordinates if the camera or box moved; re-measure.
17. Don't rename files after analysis; the scripts depend on the naming convention.

---

## 16. Data sheets to fill (copy each table into its own Excel / Google Sheets tab)

*(Rows marked EXAMPLE only show the format; delete them.)*

### S1 — Paper extraction (Role D)

| Paper | Year / venue | Problem | Method | Retail scenarios | Near-Expiry handling | Colour / visual used? | Blender / 3D? | Physical shelf validation? | ΔE / illuminant considered? | Donation / sustainability metric | Limitations | Page / figure to cite |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EXAMPLE: Nigam | | | | | | | | | | | | |

### S1b — Novelty matrix (becomes Table T1)

| Feature | Pilarski | Jullien | Li | Wadhawan | Nigam | **This project** |
|---|---|---|---|---|---|---|
| Uses colour theory (CIE, HSV, …) | ? | ? | ? | ? | ? | ✔ |
| Uses Blender / 3D rendering | ? | ? | ? | ? | ? | ✔ |
| Measures ΔE or any colour difference | ? | ? | ? | ? | ? | ✔ |
| Considers the illuminant (D65 / LED) | ? | ? | ? | ? | ? | ✔ |
| Validates on physical shelf labels | ? | ? | ? | ? | ? | ✔ |
| Links a visual signal to a near-expiry / donation action | ? | ? | ? | ? | ? | ✔ |
| Human study (staff or participants) | ? | ? | ? | ? | ? | ✔ |
| RL / policy evaluation | ? | ? | ? | ? | ? | simulation only |

*(Replace "?" with ✔ / ✘ only after checking the full text; add the page number in a note.)*

### S2 — Frozen design (fill by Day 2; hypotheses and tests too)

| Field | Value |
|---|---|
| Colours (ID = hex) | G = 2E9E4F · Y = F5B700 · O = F07C1E · R = D62828 |
| Lights (ID, bulb model, CCT, CRI, lux at label) | L1 / L2 / L3 = … |
| Printer, paper, print settings | |
| Phone model, camera app, ISO, white balance, shutter per light | |
| Blender version, engine, samples, view transform, light strength, resolution | |
| ROI coordinates (digital and physical) | |
| Hypotheses H1, H2 and planned tests (§2.3, §11.1) | |
| Faculty answers (§4.1) | |
| Frozen on (date) and approved by | |

### S3 — Blender render log (Role A)

| File | Colour | Light (K) | Engine | Samples | View transform | Light strength | Sanity ΔE vs target | Notes |
|---|---|---|---|---|---|---|---|---|
| EXAMPLE: R_L2.png | R | L2 (4000) | Cycles | 128 | Standard | 2.6 | 0.10 | |

### S4 — Physical photo log (Role B)

| File | Colour | Light | Label copy | Shot | Time | Lux | Shutter | ISO | WB | Notes (glare, shift, retake) |
|---|---|---|---|---|---|---|---|---|---|---|
| EXAMPLE: R_L2_c1_s1.jpg | R | L2 | 1 | 1 | 15:20 | 480 | 1/60 | 100 | 5000 K | |

### S5 — ΔE results (paste from `results/delta_e_summary.csv`)

| Colour | Light | n | Mean ΔE00 | SD | 95 % CI | Verdict (< 2 acceptable) | Notes |
|---|---|---|---|---|---|---|---|
| EXAMPLE: R | L2 | 6 | 1.41 | 0.32 | 0.34 | acceptable | |

Full per-photo values are in `results/delta_e.csv` (columns `dE00_adapt`, `dE00_unadapt`, `dE00_vs_target`, `dL`, `dC`, `dH`, `flag`).

### S6 — Participant log (Role C)

| Participant | Date | Session leader | Block order | Colour-vision self-report | Age band | Consent (Y) | Included? | Exclusion reason / notes |
|---|---|---|---|---|---|---|---|---|
| EXAMPLE: P01 | 04 Nov | (name) | L1-L2-L3 | no known difficulty | 21–25 | Y | Y | |

### S7 — Trial data (`data/trial_data.csv`, made by the generator)

| Column | Meaning |
|---|---|
| `pid` | Participant ID (P01–P36) |
| `block_order` | Light order for this participant, for example L1-L2-L3 |
| `trial` | 1–24 |
| `light` | L1 / L2 / L3 |
| `true_colour` | G / Y / O / R (what was shown) |
| `response` | **You fill this:** A fresh · B watch · C discount · D donate |
| `rt_s`, `notes` | Optional |

### S8 — Carbon and SDG audit (Role D)

| Item | Value | Unit | Source (link / page) | Assumption | Formula or cell |
|---|---|---|---|---|---|
| Units saved per period | | units | simulation | | |
| Mass per unit | | kg | | | |
| Emission factor (low / high) | | kg CO₂e per kg | | | |
| **Avoided CO₂e** | | kg CO₂e | | | units × mass × factor |

### S9 — Contribution log

| Date | Person | Task | Hours | File(s) |
|---|---|---|---|---|
| EXAMPLE: 30 Oct | (name) | Built Blender scene | 3 | q3_project.blend |

---

## 17. Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| Render is black | Lamp faces away or strength too low | Check the lamp points down (rotation X = 180°); raise `LIGHT_STRENGTH` |
| Render is blown out (255) | Strength too high | Lower `LIGHT_STRENGTH`; the amber label is the brightest |
| Digital ΔE vs target is high (> 1.5) | View transform not Standard, ROI on an edge, clipping, denoiser on, world not black | Re-check §7.3 and `--roi-check … digital` |
| Script says "ROI lies outside the image" | ROI numbers do not fit this resolution | Re-measure coordinates for this photo size |
| Many photos flagged | Glare, clipping or wrong ROI | Move the lamp or label slightly, reduce exposure, re-do ROI |
| Photo ΔE00 is huge | Auto WB or HDR on, grey card not neutral, glare, iPhone profile | Re-shoot in manual mode; check the grey card; keep the same settings |
| ΔE00 looks identical for all lights | Adaptation removes most of the light effect | Valid result; also report the unadapted ΔE; consider a stress condition |
| "Skipped (name does not follow the convention)" | Wrong filename | Rename to `R_L2_c1_s1.jpg` / `R_L2.png` |
| `colour-science` import error | Library not installed | `pip install colour-science` (only dominant wavelength / locus need it) |
| Logistic model fails | Almost no errors, or ΔE does not vary | Report descriptive rates; say no effect could be detected |
| Friedman test error | No variation in miss rates | Report descriptive miss rates only |
| Different results on two laptops | Different Blender or library versions | Note versions; use the same Blender version |
| Blender script error | API difference in your version | Copy the error text to your teammate or to Claude |

---

## 18. Glossary and references

### Glossary
**CCT** correlated colour temperature (K) · **CRI** colour-rendering index (how faithfully a light shows colours) · **lux** illuminance · **ROI** region of interest (the box of pixels you average) · **CIELAB (L\*, a\*, b\*)** perceptual colour space used for ΔE · **CVD** colour-vision difficulty · **Within-subjects** every participant sees every condition · **Counterbalancing** rotating condition order across participants · **Holm correction** a way to adjust p-values for several tests · **Odds ratio** factor by which the odds of an event change per unit of the predictor · **Clustered standard errors** standard errors that account for repeated trials per participant.

### References (verify each one before citing, and add the five assigned papers from the copies faculty provided)
1. Sharma, G., Wu, W., & Dalal, E. N. (2005). The CIEDE2000 color-difference formula: Implementation notes, supplementary test data, and mathematical observations. *Color Research & Application*, 30(1), 21–30.
2. Luo, M. R., Cui, G., & Rigg, B. (2001). The development of the CIE 2000 colour-difference formula: CIEDE2000. *Color Research & Application*, 26(5), 340–350.
3. CIE 15:2018. *Colorimetry*, 4th edition.
4. ISO/CIE 11664-6:2014. *Colorimetry — Part 6: CIEDE2000 colour-difference formula.*
5. IEC 61966-2-1:1999. *Default RGB colour space — sRGB.*
6. Fairchild, M. D. *Color Appearance Models* (3rd ed.). Wiley, 2013.
7. United Nations. *Sustainable Development Goals*, Goal 12 (target 12.3) and Goal 13 — https://sdgs.un.org/goals
8. Blender Manual, "Color Management" — https://docs.blender.org/manual/en/latest/render/color_management.html
9. Jullien, S., et al. *A Simulation Environment and Reinforcement Learning Method for Waste Reduction*, arXiv:2205.15455 (confirm this is the Jullien paper on your sheet).
10. Pilarski; Li et al. (2023); Wadhawan; Nigam — cite from the copies provided by faculty.

---

## Appendix — scripts

Save each script in the project root (Appendix A–B are pasted into Blender instead). Python scripts C–F were run on dummy data to check they work; A–B were only logic-checked outside Blender.

### Appendix A — Blender scene — digital twin and the 12 renders (`q3_blender_scene.py`)

Run inside **Blender** (Scripting workspace). Save the `.blend` in the project root first. See §7.2.

```python
"""
q3_blender_scene.py - Blender digital twin: label + 18% grey card under ONE lamp whose colour temperature is set by a Blackbody node.
HOW TO RUN: Blender > Scripting workspace > New > paste this file > Run Script (Alt+P).
FIRST save the .blend inside your PROJECT ROOT (File > Save As); renders go to  data/blender_renders/  next to it.
Run 1: CALIBRATE = True  -> one white test render (data/_calibration_white.png). Adjust LIGHT_STRENGTH until the label reads ~235-245.
Run 2: CALIBRATE = False -> the 12 real renders  <colour>_<light>.png
"""
import math
import os
import bpy

# =============================== EDIT THIS BLOCK ===============================
COLOURS = {"G": "2E9E4F", "Y": "F5B700", "O": "F07C1E", "R": "D62828"}   # sRGB hex (same as Sheet S2)
LIGHTS = {"L1": 6500, "L2": 4000, "L3": 3000}                          # Blackbody temperature in Kelvin
LIGHT_STRENGTH = 2.6      # starting guess - CALIBRATE it
GREY_ALBEDO = 0.18        # linear reflectance of the grey card
CALIBRATE = True
SAMPLES = 128
# ===============================================================================


def hex_to_linear_rgba(h):
    """sRGB hex -> scene-linear RGBA (Blender colour sockets expect linear values)"""
    lin = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        lin.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (lin[0], lin[1], lin[2], 1.0)


def new_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    return mat, mat.node_tree


def diffuse_material(name, rgba):
    mat, nt = new_material(name)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfDiffuse")            # matte paper; avoids the stray specular of Principled BSDF
    bsdf.inputs["Color"].default_value = rgba
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat, bsdf


def lamp_material(name, kelvin, strength):
    mat, nt = new_material(name)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    blackbody = nt.nodes.new("ShaderNodeBlackbody")          # colour temperature in K, like a bulb's CCT
    blackbody.inputs["Temperature"].default_value = kelvin
    emit.inputs["Strength"].default_value = strength
    nt.links.new(blackbody.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat, blackbody


def make_plane(name, width, height, location, rotation=(0.0, 0.0, 0.0), material=None):
    verts = [(-width / 2, -height / 2, 0), (width / 2, -height / 2, 0), (width / 2, height / 2, 0), (-width / 2, height / 2, 0)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.scene.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def build_scene():
    scene = bpy.context.scene
    for obj in list(bpy.data.objects):                       # start from an empty scene
        bpy.data.objects.remove(obj, do_unlink=True)

    # --- colour management: NO tone mapping, otherwise the colours are not comparable to the hex values ---
    scene.display_settings.display_device = "sRGB"
    scene.view_settings.view_transform = "Standard"
    try:
        scene.view_settings.look = "None"
    except TypeError:
        pass
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0

    # --- render settings ---
    scene.render.engine = "CYCLES"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = False                       # the denoiser can shift flat colours slightly
    scene.cycles.use_adaptive_sampling = False
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1280, 720, 100
    scene.render.film_transparent = False
    img = scene.render.image_settings
    img.file_format, img.color_mode, img.color_depth = "PNG", "RGB", "8"

    # --- black world: the lamp must be the ONLY light ---
    world = bpy.data.worlds.new("BlackWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        bg.inputs["Strength"].default_value = 0.0
    scene.world = world

    # --- objects (metres): shelf, label, grey card, lamp panel, camera ---
    shelf_mat, _ = diffuse_material("ShelfBase", (0.18, 0.18, 0.18, 1.0))
    make_plane("Shelf", 0.50, 0.35, (0.0, 0.0, 0.0), material=shelf_mat)
    label_mat, label_bsdf = diffuse_material("Label", hex_to_linear_rgba("FFFFFF"))
    make_plane("Label", 0.08, 0.05, (-0.06, 0.0, 0.001), material=label_mat)
    grey_mat, _ = diffuse_material("GreyCard", (GREY_ALBEDO, GREY_ALBEDO, GREY_ALBEDO, 1.0))
    make_plane("GreyCard", 0.08, 0.05, (0.06, 0.0, 0.001), material=grey_mat)
    lamp_mat, blackbody = lamp_material("Lamp", 6500, LIGHT_STRENGTH)
    make_plane("LampPanel", 0.50, 0.50, (0.0, 0.0, 0.40), rotation=(math.pi, 0.0, 0.0), material=lamp_mat)   # faces down

    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("Cam", cam_data)
    cam.location = (0.0, -0.35, 0.35)
    cam.rotation_euler = (math.radians(45), 0.0, 0.0)        # looks at the middle between label and grey card
    scene.collection.objects.link(cam)
    scene.camera = cam
    return scene, label_bsdf, blackbody


def render_to(scene, path):
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)                  # same as F12 + save: this is a FINAL render, not the viewport


def main():
    if not bpy.data.filepath:
        raise RuntimeError("Save the .blend file inside your project root first (File > Save As), then run the script again.")
    root = os.path.dirname(bpy.data.filepath)
    out_dir = os.path.join(root, "data", "blender_renders")
    os.makedirs(out_dir, exist_ok=True)
    scene, label_bsdf, blackbody = build_scene()

    if CALIBRATE:
        blackbody.inputs["Temperature"].default_value = LIGHTS["L1"]
        label_bsdf.inputs["Color"].default_value = hex_to_linear_rgba("FFFFFF")
        render_to(scene, os.path.join(root, "data", "_calibration_white.png"))
        print("Calibration render saved to data/_calibration_white.png. Sample the LEFT patch: aim for ~235-245 per channel "
              "(R, G, B within ~3 of each other). Change LIGHT_STRENGTH, re-run, then set CALIBRATE = False.")
        return

    for light_id, kelvin in LIGHTS.items():
        blackbody.inputs["Temperature"].default_value = kelvin
        for colour_id, hex_value in COLOURS.items():
            label_bsdf.inputs["Color"].default_value = hex_to_linear_rgba(hex_value)
            render_to(scene, os.path.join(out_dir, f"{colour_id}_{light_id}.png"))
    print(f"Done: {len(LIGHTS) * len(COLOURS)} renders in {out_dir}")


main()
```

### Appendix B — Blender CIE 1931 chromaticity diagram (`q3_blender_chromaticity.py`)

Run inside **Blender** after the ΔE pipeline has produced `results/locus.csv` and `results/measurements.csv`. See §7.7.

```python
"""
q3_blender_chromaticity.py - CIE 1931 xy chromaticity diagram built in Blender from YOUR results (Module 3 constructs).
Needs (written by q3_colour_pipeline.py):  results/locus.csv  and  results/measurements.csv
HOW TO RUN: save this .blend in the PROJECT ROOT, Scripting workspace > New > paste > Run Script.
Draws: spectral locus + purple line, sRGB gamut triangle, D65 white point, and for every colour a path
target -> physical label under L1 -> L2 -> L3 (UNADAPTED chromaticity, so the shift caused by the light is visible),
plus the path of the grey card (= the lamp's white point as the camera saw it). Output: results/fig_cie_xy.png
"""
import csv
import os
from collections import defaultdict
import bpy

S = 10.0                                                         # 1 xy unit = 10 Blender units
COLOURS = {"G": "2E9E4F", "Y": "F5B700", "O": "F07C1E", "R": "D62828"}
LIGHTS = ["L1", "L2", "L3"]
D65 = (0.3127, 0.3290)
SRGB_TRIANGLE = [(0.64, 0.33), (0.30, 0.60), (0.15, 0.06)]
M = ((0.4124564, 0.3575761, 0.1804375), (0.2126729, 0.7151522, 0.0721750), (0.0193339, 0.1191920, 0.9503041))
BLACK, GREY = (0, 0, 0, 1), (0.35, 0.35, 0.35, 1)


def hex_to_linear_rgba(h):
    lin = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        lin.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (lin[0], lin[1], lin[2], 1.0)


def hex_to_xy(h):
    lin = hex_to_linear_rgba(h)[:3]
    X, Y, Z = [sum(M[r][c] * lin[c] for c in range(3)) for r in range(3)]
    return (X / (X + Y + Z), Y / (X + Y + Z))


def flat_material(name, rgba):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")                  # emission strength 1 shows exactly the colour you give it
    emit.inputs["Color"].default_value = rgba
    emit.inputs["Strength"].default_value = 1.0
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def poly_curve(name, pts, rgba, depth=0.02, cyclic=False):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = depth
    spline = cu.splines.new("POLY")
    spline.points.add(len(pts) - 1)
    for p, (x, y) in zip(spline.points, pts):
        p.co = (x * S, y * S, 0.0, 1.0)
    spline.use_cyclic_u = cyclic
    cu.materials.append(flat_material(name + "_mat", rgba))
    obj = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def dot(name, xy, rgba, radius=0.07):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=(xy[0] * S, xy[1] * S, 0.05))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(flat_material(name + "_mat", rgba))
    return obj


def text(body, xy, size=0.28, rgba=BLACK):
    cu = bpy.data.curves.new("txt_" + body, "FONT")
    cu.body = body
    cu.size = size
    cu.materials.append(flat_material("txt_mat_" + body, rgba))
    obj = bpy.data.objects.new("txt_" + body, cu)
    obj.location = (xy[0] * S + 0.12, xy[1] * S + 0.12, 0.06)
    bpy.context.scene.collection.objects.link(obj)


def read_locus(res):
    with open(os.path.join(res, "locus.csv")) as f:
        return [(float(r["wavelength"]), float(r["x"]), float(r["y"])) for r in csv.DictReader(f)]


def read_means(res):
    """mean UNADAPTED xy of the physical label and of the grey card for every (colour, light)"""
    acc = defaultdict(list)
    with open(os.path.join(res, "measurements.csv")) as f:
        for r in csv.DictReader(f):
            if r["source"] == "physical":
                acc[(r["colour"], r["light"])].append([float(r["x_ex"]), float(r["y_ex"]), float(r["gx"]), float(r["gy"])])
    return {k: [sum(v[i] for v in vals) / len(vals) for i in range(4)] for k, vals in acc.items()}


def main():
    if not bpy.data.filepath:
        raise RuntimeError("Save the .blend in your project root first.")
    res = os.path.join(os.path.dirname(bpy.data.filepath), "results")
    locus, means = read_locus(res), read_means(res)
    scene = bpy.context.scene
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # spectral locus (closing the curve draws the purple line) and the sRGB gamut triangle
    poly_curve("SpectralLocus", [(x, y) for _, x, y in locus], BLACK, cyclic=True)
    for wl, x, y in locus:
        if int(wl) in (460, 480, 500, 520, 540, 560, 580, 600, 620, 700):
            text(str(int(wl)), (x, y), size=0.22, rgba=GREY)
    poly_curve("sRGB_gamut", SRGB_TRIANGLE, GREY, depth=0.015, cyclic=True)
    dot("D65", D65, (1, 1, 1, 1), radius=0.09)
    poly_curve("D65_ring", [(D65[0] + 0.012 * c, D65[1] + 0.012 * s) for c, s in
                            ((1, 0), (0.7, 0.7), (0, 1), (-0.7, 0.7), (-1, 0), (-0.7, -0.7), (0, -1), (0.7, -0.7))], BLACK, depth=0.01, cyclic=True)
    text("D65", D65, size=0.25)

    # grey card path = lamp white point as seen by the camera
    grey_path = [D65] + [(means[("R", l)][2], means[("R", l)][3]) for l in LIGHTS if ("R", l) in means]
    poly_curve("lamp_white_path", grey_path, GREY, depth=0.012)
    for l, p in zip(LIGHTS, grey_path[1:]):
        dot("lamp_" + l, p, GREY, radius=0.05)
        text(l, p, size=0.22, rgba=GREY)

    # one path per colour: intended sRGB colour -> physical label under L1, L2, L3
    for cid, hexv in COLOURS.items():
        rgba = hex_to_linear_rgba(hexv)
        pts = [hex_to_xy(hexv)] + [(means[(cid, l)][0], means[(cid, l)][1]) for l in LIGHTS if (cid, l) in means]
        poly_curve("path_" + cid, pts, rgba, depth=0.018)
        dot("target_" + cid, pts[0], rgba, radius=0.11)
        text(cid, pts[0], size=0.3)
        for i, p in enumerate(pts[1:], start=1):
            dot(f"phys_{cid}_{i}", p, rgba, radius=0.05)

    # camera, world, render
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 9.5
    cam = bpy.data.objects.new("Cam", cam_data)
    cam.location = (4.0, 4.1, 10.0)
    scene.collection.objects.link(cam)
    scene.camera = cam
    world = bpy.data.worlds.new("WhiteWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (1, 1, 1, 1)
        bg.inputs["Strength"].default_value = 1.0
    scene.world = world
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.view_settings.view_transform = "Standard"
    scene.render.resolution_x = scene.render.resolution_y = 1400
    scene.render.filepath = os.path.join(res, "fig_cie_xy.png")
    bpy.ops.render.render(write_still=True)
    print("saved", scene.render.filepath, "- add axis labels (x, y) and a legend in your report editor")


main()
```

### Appendix C — ΔE00 pipeline (renders vs phone photos) (`q3_colour_pipeline.py`)

Run from the project root: `python q3_colour_pipeline.py` (and `--roi-check FILE digital|physical`). See §9.

```python
"""
q3_colour_pipeline.py
ΔE00 between Blender renders (digital) and phone photos of the printed labels (physical).

Project folder layout (run the script from the project root):
  data/blender_renders/R_L1.png          one render per colour x light   ->  <colour>_<light>.png
  data/phone_photos/R_L1_c1_s1.jpg       <colour>_<light>_c<label copy>_s<shot>.jpg
  results/                               created automatically

Usage:
  python q3_colour_pipeline.py                                    # full analysis
  python q3_colour_pipeline.py --roi-check FILE digital|physical  # draw the ROI boxes on one image to verify them
"""
import argparse, glob, io, os, re
import numpy as np
import pandas as pd
from PIL import Image, ImageCms, ImageDraw
from scipy import stats
from skimage import color

try:
    import colour          # colour-science: only used for dominant wavelength, purity and the spectral locus
except ImportError:
    colour = None

# =========================== 1) EDIT THIS BLOCK ===========================
COLOURS = {"G": "2E9E4F", "Y": "F5B700", "O": "F07C1E", "R": "D62828"}   # target sRGB hex (frozen in Sheet S2)
# ROI = (x0, y0, x1, y1) in pixels, drawn well INSIDE each patch (no edges, shadows or glare).
# Check them with --roi-check. The digital ROIs fit the layout built by q3_blender_scene.py (1280x720 render).
ROI_DIGITAL = {"label": (340, 325, 510, 395), "grey": (770, 325, 940, 395)}
ROI_PHYSICAL = {"label": (1000, 1100, 1300, 1400), "grey": (2400, 1100, 2700, 1400)}   # MUST be re-measured for your photos
GREY_TARGET = 0.18       # nominal reflectance of the grey card (linear); both pipelines are normalised to it
# ==========================================================================

D65_XY = np.array([0.3127, 0.3290])
M_RGB2XYZ = np.array([[0.4124564, 0.3575761, 0.1804375],     # linear sRGB -> CIE XYZ (D65)
                      [0.2126729, 0.7151522, 0.0721750],
                      [0.0193339, 0.1191920, 0.9503041]])
LUMA = M_RGB2XYZ[1]                                          # relative-luminance weights (the Y row)
DIG_RE = re.compile(r"^(?P<c>[A-Za-z0-9]+)_(?P<l>L\d+)$")
PHY_RE = re.compile(r"^(?P<c>[A-Za-z0-9]+)_(?P<l>L\d+)_c(?P<copy>\d+)_s(?P<shot>\d+)$")


# ----------------------------- colour maths -------------------------------
def srgb_to_linear(c):
    c = np.asarray(c, dtype=float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(v):
    v = np.clip(np.asarray(v, dtype=float), 0.0, 1.0)
    return np.where(v <= 0.0031308, 12.92 * v, 1.055 * v ** (1 / 2.4) - 0.055)


def hex_to_srgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float) / 255.0


def lab_of_linear(lin):
    """linear-sRGB triplet -> CIELAB (D65, 2-degree observer). No clipping, so values above 1 stay exact."""
    xyz = (M_RGB2XYZ @ np.asarray(lin, dtype=float)).reshape(1, 1, 3)
    return color.xyz2lab(xyz, illuminant="D65", observer="2").reshape(3)


def xy_of_linear(lin):
    X, Y, Z = M_RGB2XYZ @ np.asarray(lin, dtype=float)
    s = X + Y + Z
    return np.array([X / s, Y / s])


def de2000(lab1, lab2):
    return float(color.deltaE_ciede2000(np.asarray(lab1).reshape(1, 1, 3), np.asarray(lab2).reshape(1, 1, 3)).squeeze())


def de_parts(ref, test):
    """ΔL*, ΔC*ab and |ΔH*ab| of test relative to ref (use them to explain WHY a ΔE00 is large)"""
    dL = test[0] - ref[0]
    dC = np.hypot(test[1], test[2]) - np.hypot(ref[1], ref[2])
    dH = np.sqrt(max((test[1] - ref[1]) ** 2 + (test[2] - ref[2]) ** 2 - dC ** 2, 0.0))
    return float(dL), float(dC), float(dH)


def dominant_wl_purity(xy):
    """dominant wavelength (nm) and excitation purity of a colour, relative to the D65 white point"""
    if colour is None:
        return np.nan, np.nan
    try:
        return float(colour.dominant_wavelength(xy, D65_XY)[0]), float(colour.excitation_purity(xy, D65_XY))
    except Exception:
        return np.nan, np.nan


# ------------------------------ image input -------------------------------
def load_srgb(path):
    """Image -> float sRGB array in [0,1]. An embedded ICC profile (e.g. iPhone Display P3) is converted to sRGB."""
    im = Image.open(path)
    icc = im.info.get("icc_profile")
    im = im.convert("RGB")
    if icc:
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            im = ImageCms.profileToProfile(im, src, ImageCms.createProfile("sRGB"), outputMode="RGB")
        except Exception as exc:
            print(f"  ! ICC conversion failed for {os.path.basename(path)} ({exc}); assuming sRGB")
    return np.asarray(im, dtype=float) / 255.0


def roi_stats(img, roi):
    x0, y0, x1, y1 = roi
    h, w = img.shape[:2]
    if not (0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h):
        raise ValueError(f"ROI {roi} lies outside the {w}x{h} image - re-measure it with --roi-check")
    patch = img[y0:y1, x0:x1].reshape(-1, 3)
    lin = srgb_to_linear(patch)
    y = lin @ LUMA
    cv = float(y.std() / max(y.mean(), 1e-9))            # patch non-uniformity (edges / glare / shadow raise it)
    sat = float((patch >= 0.995).any(axis=1).mean())     # fraction of pixels at (or next to) 255
    return lin.mean(axis=0), cv, sat


def analyse_image(path, rois):
    img = load_srgb(path)
    lab_lin, cv_l, sat_l = roi_stats(img, rois["label"])
    grey_lin, cv_g, sat_g = roi_stats(img, rois["grey"])
    adapted = lab_lin * (GREY_TARGET / grey_lin)                      # grey card forced neutral: light colour AND exposure removed
    exposed = lab_lin * (GREY_TARGET / float(grey_lin @ LUMA))        # exposure only: the light's colour stays in the numbers
    over_range = bool(adapted.max() > 1.02)    # a label cannot reflect more than ~100% of the light: glare, overexposure or ROI on a highlight
    lab_ad, lab_ex = lab_of_linear(adapted), lab_of_linear(exposed)
    xy_ad, xy_ex, gxy = xy_of_linear(adapted), xy_of_linear(exposed), xy_of_linear(grey_lin)
    wl, pur = dominant_wl_purity(xy_ad)
    return dict(L_ad=lab_ad[0], a_ad=lab_ad[1], b_ad=lab_ad[2], L_ex=lab_ex[0], a_ex=lab_ex[1], b_ex=lab_ex[2],
                x_ad=xy_ad[0], y_ad=xy_ad[1], x_ex=xy_ex[0], y_ex=xy_ex[1], gx=gxy[0], gy=gxy[1],
                dom_wl_nm=wl, purity=pur, grey_lin_r=grey_lin[0], grey_lin_g=grey_lin[1], grey_lin_b=grey_lin[2],
                roi_cv_label=cv_l, roi_cv_grey=cv_g,
                saturated_frac=max(sat_l, sat_g), over_range=over_range)


def collect(folder, patterns, regex, rois, source):
    files = sorted({f for p in patterns for f in glob.glob(os.path.join(folder, p))})
    rows = []
    for f in files:
        name = os.path.basename(f)
        m = regex.match(os.path.splitext(name)[0])
        if not m or m.group("c") not in COLOURS:
            print(f"  skipped (name does not follow the convention or colour id unknown): {name}")
            continue
        g = m.groupdict()
        rec = dict(source=source, colour=g["c"], light=g["l"], label_copy=int(g.get("copy") or 0),
                   shot=int(g.get("shot") or 0), file=name)
        rec.update(analyse_image(f, rois))
        rows.append(rec)
    print(f"{source}: {len(rows)} images analysed from {folder}")
    return rows


# ------------------------------ helpers/outputs ----------------------------
def roi_check(path, rois):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    for name, (x0, y0, x1, y1) in rois.items():
        d.rectangle((x0, y0, x1, y1), outline=(255, 0, 255), width=max(2, im.width // 400))
        d.text((x0, max(0, y0 - 14)), name, fill=(255, 0, 255))
    out = "results/roi_check.png"
    im.save(out)
    print(f"saved {out}  - open it: both magenta boxes must sit fully inside their patches")


def export_locus(path="results/locus.csv", step=5):
    """CIE 1931 spectral locus (380-700 nm) for the Blender chromaticity diagram"""
    if colour is None:
        print("colour-science not installed: skipping locus.csv (pip install colour-science)")
        return
    cmfs = colour.MSDS_CMFS["CIE 1931 2 Degree Standard Observer"]
    wl = np.asarray(cmfs.wavelengths, dtype=float)
    xy = colour.XYZ_to_xy(np.asarray(cmfs.values))
    keep = (wl >= 380) & (wl <= 700) & (np.mod(wl - 380, step) == 0)
    pd.DataFrame({"wavelength": wl[keep], "x": xy[keep, 0], "y": xy[keep, 1]}).to_csv(path, index=False)


def ci95(x):
    x = np.asarray(x, dtype=float)
    return float(stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 else np.nan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roi-check", nargs=2, metavar=("FILE", "digital|physical"))
    args = ap.parse_args()
    os.makedirs("results", exist_ok=True)
    if args.roi_check:
        roi_check(args.roi_check[0], ROI_DIGITAL if args.roi_check[1] == "digital" else ROI_PHYSICAL)
        return

    export_locus()
    rows = collect("data/blender_renders", ["*.png"], DIG_RE, ROI_DIGITAL, "digital")
    rows += collect("data/phone_photos", ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG", "*.png"], PHY_RE, ROI_PHYSICAL, "physical")
    meas = pd.DataFrame(rows)
    meas.to_csv("results/measurements.csv", index=False)

    target_lab = {c: color.rgb2lab(hex_to_srgb(h).reshape(1, 1, 3)).reshape(3) for c, h in COLOURS.items()}
    dig = meas[meas.source == "digital"].drop_duplicates(["colour", "light"]).set_index(["colour", "light"])

    # SANITY CHECK 1: a correct Blender setup reproduces the target colour, so this should be ~0 (below 1)
    print("\nSanity check - digital render vs target hex (should be ~0):")
    for (c, l), d in dig.iterrows():
        e = de2000(target_lab[c], d[["L_ad", "a_ad", "b_ad"]].to_numpy(float))
        print(f"  {c}_{l}: dE00 = {e:.2f}" + ("   <-- CHECK view transform / ROI / clipping" if e > 1.5 else ""))

    out = []
    for _, r in meas[meas.source == "physical"].iterrows():
        if (r.colour, r.light) not in dig.index:
            print(f"  ! no Blender render for {r.colour}_{r.light}; skipped {r.file}")
            continue
        d = dig.loc[(r.colour, r.light)]
        lab_p_ad, lab_d_ad = r[["L_ad", "a_ad", "b_ad"]].to_numpy(float), d[["L_ad", "a_ad", "b_ad"]].to_numpy(float)
        lab_p_ex, lab_d_ex = r[["L_ex", "a_ex", "b_ex"]].to_numpy(float), d[["L_ex", "a_ex", "b_ex"]].to_numpy(float)
        dL, dC, dH = de_parts(lab_d_ad, lab_p_ad)
        bad = r.over_range or r.saturated_frac > 0.01 or r.roi_cv_label > 0.10 or r.roi_cv_grey > 0.10
        out.append(dict(colour=r.colour, light=r.light, label_copy=r["label_copy"], shot=r["shot"], file=r.file,
                        dE00_adapt=de2000(lab_d_ad, lab_p_ad),        # PRIMARY: both sides adapted to their own grey card
                        dE00_unadapt=de2000(lab_d_ex, lab_p_ex),      # secondary: light colour left in
                        dE00_vs_target=de2000(target_lab[r.colour], lab_p_ad),   # physical label vs the intended sRGB colour
                        dL=dL, dC=dC, dH=dH, dom_wl_phys=r.dom_wl_nm, dom_wl_dig=d.dom_wl_nm,
                        flag="CHECK (clipping/glare/ROI)" if bad else ""))
    de = pd.DataFrame(out)
    de.to_csv("results/delta_e.csv", index=False)

    summ = (de.groupby(["colour", "light"])["dE00_adapt"]
              .agg(n="count", mean="mean", sd="std", ci95=ci95).reset_index())
    summ["verdict"] = np.where(summ["mean"] < 2, "<2 acceptable", ">=2 noticeable")
    summ.to_csv("results/delta_e_summary.csv", index=False)
    pd.set_option("display.width", 140)
    print("\nΔE00 (primary metric) by colour x light:\n", summ.round(2).to_string(index=False))
    print("\nΔE00 by light (all colours):\n", de.groupby("light")["dE00_adapt"].agg(["count", "mean", "std"]).round(2))
    print(f"\nFlagged measurements: {int((de.flag != '').sum())} (see 'flag' column in results/delta_e.csv)")
    print("Written: results/measurements.csv, delta_e.csv, delta_e_summary.csv, locus.csv")


if __name__ == "__main__":
    main()
```

### Appendix D — Trial-sheet generator for the user study (`q3_make_trial_sheets.py`)

Run once: `python q3_make_trial_sheets.py`. See §10.4.

```python
"""
q3_make_trial_sheets.py - builds data/trial_data.csv for the user study (counterbalanced, randomised).
Each participant: 3 light blocks (order rotates through all 6 permutations, 6 participants per order) x 4 colours x 2 repeats = 24 trials.
Fill the empty 'response' column during the sessions: A = fresh/no action, B = watch, C = discount, D = donate now.
"""
import csv, itertools, os, random

N_PARTICIPANTS = 36                 # >= 30 (faculty benchmark); 4 active members x 9 each = 6 per block order
COLOURS = ["G", "Y", "O", "R"]
LIGHTS = ["L1", "L2", "L3"]
REPEATS = 2
random.seed(42)                     # same seed = same sheet for everybody on the team

orders = list(itertools.permutations(LIGHTS))            # 6 block orders -> counterbalancing
rows = []
for i in range(N_PARTICIPANTS):
    pid, order, t = f"P{i + 1:02d}", orders[i % len(orders)], 1
    for light in order:
        block = COLOURS * REPEATS
        random.shuffle(block)                            # random colour order inside each block
        for colour in block:
            rows.append(dict(pid=pid, block_order="-".join(order), trial=t, light=light,
                             true_colour=colour, response="", rt_s="", notes=""))
            t += 1

os.makedirs("data", exist_ok=True)
with open("data/trial_data.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"wrote data/trial_data.csv with {len(rows)} rows ({N_PARTICIPANTS} participants x {len(rows) // N_PARTICIPANTS} trials)")
```

### Appendix E — Statistics (`q3_stats.py`)

Run after the study data is entered: `python q3_stats.py`. See §11.

```python
"""
q3_stats.py - statistics for Q3.
Inputs : results/delta_e.csv  (from q3_colour_pipeline.py)   and   data/trial_data.csv (user study, 'response' filled in)
Outputs: tables printed to the screen + results/fig_error_vs_dE.png
Run    : python q3_stats.py
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests

TRUE_ACTION = {"G": "A", "Y": "B", "O": "C", "R": "D"}      # A none, B watch, C discount, D donate now
PAIRS = [("L1", "L2"), ("L1", "L3"), ("L2", "L3")]

de = pd.read_csv("results/delta_e.csv")
tr = pd.read_csv("data/trial_data.csv").dropna(subset=["response"])

# ---------------------------------------------------------------------------------------------
print("\n=== H1: does the colour error ΔE00 depend on the light? (physical label vs Blender) ===")
model = smf.ols("dE00_adapt ~ C(colour) * C(light)", data=de).fit()
print(sm.stats.anova_lm(model, typ=2).round(4))
cell = de.groupby(["colour", "label_copy", "light"])["dE00_adapt"].mean().unstack("light")     # one row per printed label copy
rows = []
for a, b in PAIRS:
    try:
        p = float(stats.wilcoxon(cell[a], cell[b]).pvalue)
    except ValueError:                                         # all differences are zero
        p = 1.0
    rows.append(dict(contrast=f"{b} - {a}", mean_diff=(cell[b] - cell[a]).mean(), p_raw=p))
post = pd.DataFrame(rows)
post["p_holm"] = multipletests(post["p_raw"], method="holm")[1]
print("\nPaired Wilcoxon on label-copy means (Holm-corrected):\n", post.round(4).to_string(index=False))

# ---------------------------------------------------------------------------------------------
print("\n=== User study: errors and missed donation triggers ===")
tr["true_action"] = tr["true_colour"].map(TRUE_ACTION)
tr["error"] = (tr["response"] != tr["true_action"]).astype(int)                           # any wrong action
tr["miss_donation"] = ((tr["true_colour"] == "R") & (tr["response"] != "D")).astype(int)  # red label, no donation
print(f"participants: {tr.pid.nunique()}   trials: {len(tr)}")
print("\nError rate by true colour x light:\n", tr.groupby(["true_colour", "light"])["error"].mean().unstack().round(3))
red = tr[tr.true_colour == "R"]
print("\nMissed-donation rate (red labels only):\n", red.groupby("light")["miss_donation"].agg(n="count", miss_rate="mean").round(3))

piv = red.groupby(["pid", "light"])["miss_donation"].mean().unstack("light").dropna()
try:
    fr = stats.friedmanchisquare(piv["L1"], piv["L2"], piv["L3"])
    print(f"\nFriedman test (per-participant miss rate, L1 vs L2 vs L3): chi2 = {fr.statistic:.2f}, p = {fr.pvalue:.4f}")
except Exception as exc:
    print("\nFriedman test not possible (probably no variation / too few misses):", exc)

# ---------------------------------------------------------------------------------------------
print("\n=== H2: does ΔE00 predict errors? (logistic regression, standard errors clustered by participant) ===")
cond = de.groupby(["colour", "light"])["dE00_adapt"].mean().rename("dE").reset_index()
d = tr.merge(cond, left_on=["true_colour", "light"], right_on=["colour", "light"], how="left").dropna(subset=["dE"])
d["pid_code"] = pd.factorize(d["pid"])[0]
fit = None
try:
    fit = smf.logit("error ~ dE", data=d).fit(disp=0, cov_type="cluster", cov_kwds={"groups": d["pid_code"]})
    lo, hi = np.exp(fit.conf_int().loc["dE"])
    print(f"odds ratio per +1 ΔE00 = {np.exp(fit.params['dE']):.2f}  (95% CI {lo:.2f} to {hi:.2f}),  p = {fit.pvalues['dE']:.4f}")
    print("Report it as: 'each 1-unit increase in ΔE00 multiplied the odds of a wrong action by <OR>'.")
except Exception as exc:
    print("Logistic model failed (often: almost no errors, or ΔE00 does not vary between conditions):", exc)
    print("-> report the descriptive error rates above and say that the study could not detect an effect.")

obs = d.groupby(["true_colour", "light"]).agg(dE=("dE", "first"), err=("error", "mean"), n=("error", "size")).reset_index()
fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(obs.dE, obs.err, s=obs.n / 1.5, alpha=0.7, label="observed (colour x light)")
if fit is not None:
    xs = np.linspace(0, max(obs.dE.max() * 1.15, 1.0), 100)
    ax.plot(xs, 1 / (1 + np.exp(-(fit.params["Intercept"] + fit.params["dE"] * xs))), label="logistic fit")
ax.set_xlabel("ΔE00 (physical label vs Blender render)")
ax.set_ylabel("share of wrong actions")
ax.legend()
fig.savefig("results/fig_error_vs_dE.png", dpi=200, bbox_inches="tight")
print("\nsaved results/fig_error_vs_dE.png")
```

### Appendix F — Toy A/B donation simulation (`q3_donation_sim.py`)

Edit `PARAMS` and `MISS`, then run `python q3_donation_sim.py`. See §12.

```python
"""
q3_donation_sim.py - TOY A/B simulation: what do misread shelf-label colours do to a near-expiry outcome?
ILLUSTRATIVE ONLY. Replace the PARAMS and the score definition with Nigam's Near-Expiry scenario after you have read the paper.
A = labels always read correctly (miss rate 0)      B = labels read with the miss rate measured in YOUR user study
Run: python q3_donation_sim.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PARAMS = dict(days=90, mean_near_expiry_per_day=20, donation_capacity_per_day=12,
              p_sell_if_discounted=0.50, p_sell_if_unflagged=0.15)           # EXAMPLE values - replace
MISS = {"L1": 0.03, "L2": 0.08, "L3": 0.15}       # EXAMPLE miss rates - copy yours from q3_stats.py (red-label table)


def simulate(miss_rate, n_runs=5000, seed=7, **p):
    rng = np.random.default_rng(seed)
    near = rng.poisson(p["mean_near_expiry_per_day"], size=(n_runs, p["days"]))   # units reaching near-expiry each day
    flagged = rng.binomial(near, 1 - miss_rate)                                    # units whose label was read correctly
    donated = np.minimum(flagged, p["donation_capacity_per_day"])                  # donation capacity is the bottleneck
    sold_disc = rng.binomial(flagged - donated, p["p_sell_if_discounted"])         # flagged but not donated: discount sale
    sold_unfl = rng.binomial(near - flagged, p["p_sell_if_unflagged"])             # missed labels: only luck saves them
    saved = donated + sold_disc + sold_unfl
    return saved.sum(axis=1) / near.sum(axis=1)                                    # PLACEHOLDER 'sustainability score'


def summarise(name, s):
    lo, hi = np.percentile(s, [2.5, 97.5])
    print(f"{name:<28} score = {s.mean():.3f}   (95% of runs between {lo:.3f} and {hi:.3f})")


base = simulate(0.0, **PARAMS)
summarise("A: perfect label reading", base)
for light, m in MISS.items():
    s = simulate(m, **PARAMS)
    summarise(f"B: {light} (miss rate {m:.0%})", s)
    print(f"{'':<28} loss vs A = {base.mean() - s.mean():.3f} of near-expiry units "
          f"(~{(base.mean() - s.mean()) * PARAMS['mean_near_expiry_per_day'] * PARAMS['days']:.0f} units per {PARAMS['days']} days)")

# sensitivity: the colour error matters most when donation capacity is NOT the binding limit
grid = np.linspace(0, 0.4, 9)
fig, ax = plt.subplots(figsize=(6, 4))
for cap in (6, 12, 24):
    p = dict(PARAMS, donation_capacity_per_day=cap)
    ax.plot(grid, [simulate(m, n_runs=1500, **p).mean() for m in grid], marker="o", label=f"donation capacity {cap}/day")
ax.set_xlabel("miss rate of donate-now labels")
ax.set_ylabel("share of near-expiry units saved (placeholder score)")
ax.legend()
fig.savefig("results/fig_sim_sensitivity.png", dpi=200, bbox_inches="tight")
print("\nsaved results/fig_sim_sensitivity.png")
```
