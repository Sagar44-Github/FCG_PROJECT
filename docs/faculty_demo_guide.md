# Faculty demonstration guide

## Use the right Blender file

Open `blender/q3_supermarket.blend` for the complete supermarket. The saved file starts in the hero camera view. `blender/q3_project.blend` is the intentionally simple shelf measurement fixture used by the 12-condition analytical render pipeline; it is not the full-store presentation.

## Change lighting in Blender

1. Open the **Scripting** workspace.
2. In the Text Editor's text selector, choose **Q3 Lighting Lab.py** and press **Run Script** once.
3. Return to the hero camera's 3D View and press **N**.
4. Open **Q3 Research**. Click each light preset and observe the scene's area lights and world colour update.
5. Press **F12** after each selection. Each rendered image is saved separately under `blender/renders/supermarket/previews/` as `live_L1_...png`, `live_L2_...png`, or `live_L3_...png`.

The Blender and WebGL light presets deliberately show a visible difference for teaching. They are RGB visual approximations, not calibrated spectral illumination. Explain that the numerical comparison comes from the Python CIE pipeline and its documented D65/LED spectral inputs.

## Demonstrate the research workflow

1. Start the backend and React dashboard using the commands in the README.
2. On **Digital Twin**, orbit and zoom the Blender-derived shelf model. Select the red **Donate now** label.
3. Click each of the three condition cards under **See the light change**. Point out that the main interactive shelf changes its key/fill/ambient lighting and the adjacent cards show the actual Blender RGB renders for the same selected label.
4. Explain the boundary between the RGB demonstration render and the spectral/colour calculations; then open **Colour Laboratory** to show CIE XYZ, CIELAB, chromaticity, and ΔE00 from the Python backend.
5. Open **Donation Simulator**, run a seeded simulation, and show the output as modelled observer/inventory behaviour, not as human-participant data.
6. Use **Results & Exports** to show the generated CSV/PNG evidence and downloads.

The dashboard must have the API running. It does not replace the science pipeline with locally hardcoded results.
