# Hugging Face Space (Docker SDK) that serves a WIP chapter on a REAL Python
# kernel via `marimo run`. Because it isn't Pyodide, the page loads in well
# under a second instead of the ~50s the in-browser WASM build needs to boot.
#
# Read-only app mode (`marimo run`), so it's safe to expose publicly: visitors
# can interact with the rendered chapter but cannot run arbitrary code on the
# server (unlike `marimo edit`).
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Which project / branch / chapter to serve. Override these as build args in
# the Space settings when the WIP chapter or branch changes.
ARG REPO_URL=https://github.com/Chipmunk91/Math_learn
ARG REPO_REF=claude/tender-einstein-arCIU
ARG CHAPTER=differential_equations/chapters/ch07_damping_forcing_resonance.py

WORKDIR /app
# Clone the chosen branch (we need the chapter FILE, not just the package) and
# install delib + the chapter's full runtime stack. `pip install .` brings
# delib's declared deps (numpy/scipy/matplotlib/plotly); anywidget and sympy
# are used by the chapters but aren't delib deps, so add them explicitly.
RUN git clone --depth 1 --branch "${REPO_REF}" "${REPO_URL}" . \
    && pip install --no-cache-dir . anywidget sympy

# A writable HOME so marimo can cache without permission errors.
ENV HOME=/app
ENV CHAPTER=${CHAPTER}

# Hugging Face routes external traffic to port 7860.
EXPOSE 7860

# --no-token: public, no login.  --headless: don't try to open a browser.
# --no-check: don't block startup on a static lint of a draft chapter.
CMD marimo run "$CHAPTER" --host 0.0.0.0 --port 7860 --headless --no-token --no-check
