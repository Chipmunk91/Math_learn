---
title: Math Learn — WIP Preview
emoji: 🎢
colorFrom: indigo
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# Math Learn — fast WIP chapter preview

This Hugging Face Space serves the **in-progress** chapter of the
[Math Learn](https://chipmunk91.github.io/Math_learn/) differential-equations
course on a **real Python kernel** (`marimo run`), so it loads in **under a
second**. The public site runs every chapter in the browser via WebAssembly
(Pyodide), which is wonderful for "no install, runs anywhere" but takes ~50s to
boot — too slow for tight authoring iteration. This Space is the fast loop for
the chapter currently being written.

- **Read-only app mode.** You can interact with the rendered chapter; you
  can't run arbitrary code on the server.
- **The finished chapters** live on the WASM site:
  <https://chipmunk91.github.io/Math_learn/>

See `DEPLOY.md` (in the project repo under `deploy/hf-space/`) for how this is
built and how to refresh it.
