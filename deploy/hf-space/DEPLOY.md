# Deploying the fast WIP preview to Hugging Face Spaces

The public site builds every chapter to WebAssembly (Pyodide), which boots in
~50s in the browser. That's fine for readers but painful while *writing* a
chapter. This Space runs the WIP chapter on a real Python kernel via
`marimo run`, so it loads in **under a second**. Polished chapters stay on the
free WASM GitHub Pages site; only the draft chapter lives here.

`marimo run` is **read-only app mode** — safe to expose publicly (visitors
can't execute code on the server).

## One-time setup

1. Create a Space: <https://huggingface.co/new-space>
   - **SDK: Docker** (blank template), name it e.g. `math-learn-wip`.
2. Add the two files from this folder to the Space repo:
   - `Dockerfile`
   - `README.md`  (its YAML front-matter configures the Space)

   Either upload them in the web UI, or:
   ```bash
   git clone https://huggingface.co/spaces/<you>/math-learn-wip
   cd math-learn-wip
   cp /path/to/Math_learn/deploy/hf-space/{Dockerfile,README.md} .
   git add . && git commit -m "marimo WIP preview" && git push
   ```
3. The Space builds (~2–4 min: clone + pip install), then the chapter is live
   at `https://huggingface.co/spaces/<you>/math-learn-wip`. Loads in <1s.

## Pointing the landing page at the preview

Once you have the Space URL, the Draft card/chip on the landing page can link
straight to the fast preview instead of the slow WASM page. Set an env var in
the GitHub Pages build (JSON mapping slug → URL):

```
WIP_PREVIEW_URLS={"ch07_damping_forcing_resonance":"https://<you>-math-learn-wip.hf.space"}
```

(no code change needed — `build_wasm_site.py` reads it). Leave it unset and the
Draft card just links to the local WASM page as before.

## Refreshing after you edit the chapter

The Dockerfile clones the branch at **build** time, so to pull your latest
commits: Space → **Settings → Factory rebuild** (~2–4 min). Loads stay <1s
afterward. (For a faster refresh loop you could switch the entrypoint to
`git pull` on container start; ask and I'll wire that.)

## Changing which chapter / branch is served

Edit the build args at the top of the `Dockerfile` (or set them as Space build
variables):

- `REPO_REF` — the branch (default `claude/tender-einstein-arCIU`; change to
  `main` after merge).
- `CHAPTER` — path to the `.py` chapter to serve.

## If the GitHub repo is private

Add a Space **secret** `GH_TOKEN` (a GitHub PAT with `repo` read), and change
the clone line in the `Dockerfile` to:

```dockerfile
RUN git clone --depth 1 --branch "${REPO_REF}" \
    "https://x-access-token:${GH_TOKEN}@github.com/Chipmunk91/Math_learn" . \
    && pip install --no-cache-dir . anywidget sympy
```

(reference the secret with `--mount=type=secret` or a build arg per HF's docs).

## Notes / caveats

- **Cold start.** Free Spaces sleep after ~15 min idle and take ~30s to wake;
  they're instant while you're actively using them.
- **Manim videos** (`delib.video(...)`) may show their fallback note here, since
  the pre-rendered mp4s aren't wired into this minimal server. Cosmetic only.
- **One chapter per Space.** To preview several WIP chapters at once, create one
  Space each (different `CHAPTER` build arg), or ask and I'll add a multi-route
  entrypoint.
