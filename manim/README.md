# Manim hero derivations (rendered offline)

The site is serverless WASM, and **Manim can't run in the browser**. So for the
few "hero" derivations that deserve true Manim term-morphing, render them on a
machine with Manim + ffmpeg + LaTeX, commit the video, and embed it.

For everyday animated algebra, use the in-browser **`delib.derivation([...])`**
player instead — it's serverless and authorable in the notebook. Reserve Manim
for the cinematic moments.

## Workflow

1. Write a `Scene` here (see `separable.py`).
2. Render at home / in CI:

   ```
   pip install manim            # plus a LaTeX distribution + ffmpeg
   manim render -qh manim/separable.py SeparableCooling
   ```

3. Copy the output into `assets/` (the build copies `assets/` → `site/assets/`):

   ```
   cp media/videos/separable/1080p60/SeparableCooling.mp4 assets/cooling_separable.mp4
   ```

4. Embed it in a chapter's concept beat:

   ```python
   delib.video("cooling_separable.mp4", caption="Solving by separation of variables")
   ```

Keep clips short and light (a few seconds, 1080p or less) — they ship as static
assets to every visitor.
