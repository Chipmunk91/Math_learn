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
        # Sidebar layout — feel the panel version

        The whole playground lives in a **persistent left sidebar** (`mo.sidebar`)
        instead of inline. The API key is defined **once** in the sidebar; the chat
        model just reads its `.value`, so it is shared automatically — no second
        field, no syncing. Switch **Ask / Write** in the sidebar; results render
        here in the main column.

        *(This is the chapter body. Scroll — the sidebar stays put.)*
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
            return mo.callout(mo.md(f"```\n{traceback.format_exc()}\n```"), kind="danger")
        view = ns.get("view")
        if view is None:
            return mo.callout("Code ran but never assigned `view`.", kind="warn")
        if isinstance(view, matplotlib.axes.Axes):
            view = view.figure
        return view

    return (run_view,)


@app.cell(hide_code=True)
def _(mo):
    api_key = mo.ui.text(label="Anthropic key", kind="password", full_width=True)
    mode = mo.ui.radio(["Ask", "Write code"], value="Ask", inline=True)
    code_input = mo.ui.code_editor(
        value="view = delib.slope_field(lambda x, y: np.sin(x) + y, (-3, 3), (-3, 3))",
        language="python",
    )
    run_btn = mo.ui.run_button(label="Run", full_width=True)
    return api_key, code_input, mode, run_btn


@app.cell
def _(api_key):
    import json as _json

    _MODEL = "claude-haiku-4-5-20251001"
    _URL = "https://api.anthropic.com/v1/messages"
    _SYS = (
        "You help a student explore first-order ODEs inside a marimo notebook. "
        "Reply with a SHORT (1-3 sentence) explanation, then exactly ONE ```python "
        "code block. The code must be self-contained and use only these names: mo, "
        "np, plt, go, delib (with helpers slope_field(f, xlim, ylim) -> matplotlib "
        "Axes, phase_portrait, overlay_solution, solve_ode, solve_system). Do NO "
        "file or network I/O. END by assigning the single renderable to a variable "
        "named `view`."
    )

    async def chat_model(messages, config):
        msgs = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role in ("user", "assistant") and m.content
        ]
        body = _json.dumps(
            {"model": _MODEL, "max_tokens": 700, "system": _SYS, "messages": msgs}
        )
        headers = {
            "content-type": "application/json",
            "x-api-key": api_key.value,
            "anthropic-version": "2023-06-01",
            "anthropic-dangerous-direct-browser-access": "true",
        }
        try:
            from pyodide.http import pyfetch

            resp = await pyfetch(_URL, method="POST", headers=headers, body=body)
            data = await resp.json()
        except ModuleNotFoundError:
            import urllib.request
            import urllib.error

            req = urllib.request.Request(
                _URL, data=body.encode(), headers=headers, method="POST"
            )
            try:
                with urllib.request.urlopen(req) as r:
                    data = _json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                data = _json.loads(e.read().decode())

        if isinstance(data, dict) and data.get("content"):
            return "".join(b.get("text", "") for b in data["content"])
        return "**API error**\n\n```json\n" + _json.dumps(data, indent=2)[:800] + "\n```"

    return (chat_model,)


@app.cell
def _(chat_model, mo):
    chatbox = mo.ui.chat(
        chat_model,
        prompts=[
            "show the solution when the rate is negative",
            "draw the slope field for y' = y - x",
        ],
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_key, chatbox, code_input, mo, mode, run_btn):
    _panel = chatbox if mode.value == "Ask" else mo.vstack([code_input, run_btn])
    mo.sidebar(
        [
            mo.md("### Playground"),
            api_key,
            mode,
            mo.md("---"),
            _panel,
        ]
    )
    return


@app.cell(hide_code=True)
def _(chatbox, code_input, mo, mode, run_btn, run_view):
    import re

    if mode.value == "Write code":
        mo.stop(not run_btn.value, mo.md("*Type code in the sidebar and press **Run**.*"))
        _out = run_view(code_input.value)
    else:
        _bot = [m for m in (chatbox.value or []) if m.role == "assistant" and m.content]
        mo.stop(not _bot, mo.md("*Ask in the sidebar to generate a plot.*"))
        _hit = re.search(r"```(?:python)?\s*\n(.*?)```", _bot[-1].content, re.S)
        mo.stop(_hit is None, mo.callout("The reply had no python block.", kind="warn"))
        _out = run_view(_hit.group(1))
    _out
    return


if __name__ == "__main__":
    app.run()
