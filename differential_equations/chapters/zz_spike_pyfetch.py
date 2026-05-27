import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go

    import delib
    return delib, go, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Spike — can the kernel talk to Claude? (client-side, BYO-key)

        Throwaway test of the **single make-or-break unknown** for the in-notebook
        playground: *can marimo's WASM kernel call the Anthropic API directly from
        Python?* If a reply renders below, the whole playground design is feasible
        client-side with no server.

        Paste your Anthropic API key, type anything, press **Ask**. Your key stays
        in your browser and is sent only to `api.anthropic.com`.
        """
    )
    return


@app.cell
def _():
    import json

    SPIKE_MODEL = "claude-haiku-4-5-20251001"
    ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

    async def ask_claude(key, prompt):
        body = json.dumps(
            {
                "model": SPIKE_MODEL,
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}],
            }
        )
        headers = {
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "anthropic-dangerous-direct-browser-access": "true",
        }
        try:
            # WASM path: routes through the browser's fetch().
            from pyodide.http import pyfetch

            resp = await pyfetch(
                ANTHROPIC_URL, method="POST", headers=headers, body=body
            )
            data = await resp.json()
        except ModuleNotFoundError:
            # Local path (marimo edit on CPython): plain urllib.
            import urllib.request
            import urllib.error

            req = urllib.request.Request(
                ANTHROPIC_URL, data=body.encode(), headers=headers, method="POST"
            )
            try:
                with urllib.request.urlopen(req) as r:
                    data = json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                data = json.loads(e.read().decode())

        if isinstance(data, dict) and data.get("content"):
            return "".join(b.get("text", "") for b in data["content"])
        return "**API error**\n\n```json\n" + json.dumps(data, indent=2)[:1000] + "\n```"

    return (ask_claude,)


@app.cell(hide_code=True)
def _(mo):
    api_key = mo.ui.text(label="Anthropic API key", kind="password", full_width=True)
    prompt = mo.ui.text_area(
        label="Ask Claude something",
        value="Say hello in exactly five words.",
        full_width=True,
    )
    ask = mo.ui.run_button(label="Ask")
    mo.vstack([api_key, prompt, ask])
    return api_key, ask, prompt


@app.cell
async def _(api_key, ask, ask_claude, mo, prompt):
    mo.stop(not ask.value, mo.md("*Press **Ask** to send.*"))
    mo.stop(not api_key.value, mo.callout("Enter your API key first.", kind="warn"))

    _reply = await ask_claude(api_key.value, prompt.value)
    mo.md(_reply)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---
        ## Step 1 — the `view` harness

        The contract: any code string — typed or AI-generated — runs in a fixed
        namespace (`mo`, `np`, `plt`, `go`, `delib` + helpers) and ends by assigning
        its single renderable to **`view`**. The harness execs it and renders `view`.
        Below it is fed a hardcoded string; if the slope field draws, Step 1 passes.
        """
    )
    return


@app.cell
def _(delib, go, mo, np, plt):
    _helpers = {k: getattr(delib, k) for k in delib.__all__}

    def run_view(code):
        import traceback
        import matplotlib

        ns = {"mo": mo, "np": np, "plt": plt, "go": go, "delib": delib, **_helpers}
        try:
            exec(code, ns)
        except Exception:
            tb = traceback.format_exc()
            return mo.callout(mo.md(f"```\n{tb}\n```"), kind="danger")
        view = ns.get("view")
        if view is None:
            return mo.callout("Code ran but never assigned `view`.", kind="warn")
        if isinstance(view, matplotlib.axes.Axes):
            view = view.figure
        return view

    return (run_view,)


@app.cell(hide_code=True)
def _(run_view):
    _demo_code = (
        "view = delib.slope_field(lambda x, y: np.sin(x) + y, (-3, 3), (-3, 3))"
    )
    run_view(_demo_code)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---
        ## Step 2 — Write mode

        The same `run_view` harness, now fed by a live editor instead of a
        hardcoded string. Edit the code and press **Run**: it execs in the fixed
        namespace and renders `view`. Try changing the equation, or break it on
        purpose to see the error callout.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    code_input = mo.ui.code_editor(
        value="view = delib.slope_field(lambda x, y: np.sin(x) + y, (-3, 3), (-3, 3))",
        language="python",
    )
    run_btn = mo.ui.run_button(label="Run")
    mo.vstack([code_input, run_btn])
    return code_input, run_btn


@app.cell(hide_code=True)
def _(code_input, mo, run_btn, run_view):
    mo.stop(not run_btn.value, mo.md("*Edit the code above and press **Run**.*"))
    run_view(code_input.value)
    return


if __name__ == "__main__":
    app.run()
