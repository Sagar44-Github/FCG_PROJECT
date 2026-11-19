# Blender render and scene evidence

The controlled analytical Cycles scene is generated from `blender/q3_project.blend`. The automated script renders all twelve configured label/illumination combinations at 960×640, eight Cycles samples, denoising enabled, and Standard view transform. The resulting PNGs and 4×3 contact sheet are under `renders/`. `results/blender_run_metadata.json` records the Blender version, render settings, and SHA-256 checksums. `results/blender_scene_inspection.json` exports the render engine, color-management settings, material socket values and node links from the saved `.blend` through Blender Python.

`blender/evidence/scene_overview_render.png` is a true Cycles render and `12_condition_contact_sheet.png` shows all cases. `shader_node_configuration.png` and `color_management_record.png` are diagrams/cards generated from the serialized scene and render metadata; they are not screenshots of Blender UI panels. The requested live UI captures could not be saved in this run because the desktop screenshot target changed focus while the Blender application remained open. The `.blend`, render outputs and scene-derived records remain available for faculty review in Blender.

The visualization uses Blender's RGB Cycles renderer. D65 is represented by neutral RGB white in that scene. The L2/L3 Blackbody node is a CCT visualization aid only. The colorimetric calculations use the separate Python spectral engine and official CIE datasets; do not interpret Blender pixels as spectroradiometric measurements.
## Blender presentation and live lighting controls

Open `blender/q3_supermarket.blend` to view the full retail presentation scene; it is saved in the hero-camera view. The compact `blender/q3_project.blend` file is the controlled shelf measurement fixture used by the 12 research render batch.

The supermarket `.blend` contains the `Q3 Lighting Lab.py` text script. Run it once in Blender's Scripting workspace, then press **N** in the 3D View and open **Q3 Research**. The L1, L2, and L3 controls update the scene's fixture lights and world color. Press **F12** to render the active camera; the script assigns a separate preview filename for each selected condition. The three-condition image plate is at `blender/renders/supermarket/final/05_illuminant_comparison.png`.

The visible RGB presets are intentionally distinct for a demonstration. They are not measured lamp SPDs or calibrated spectral renders. Use the Python colour-science pipeline and its data files for numerical colour analysis.
