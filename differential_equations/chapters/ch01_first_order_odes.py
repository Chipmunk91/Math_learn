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
        # Chapter 1 — First-order ODEs & slope fields

        **See the field, follow the flow.**

        By the end of this chapter you should be able to:

        - Read a **slope field** as a picture of *every* solution to $y' = f(x, y)$ at once.
        - Predict how a solution curve bends just by looking at the field.
        - Explain how the parameters of an equation reshape the whole flow.
        - Connect **equilibria** (where $y' = 0$) to the horizontal stripes in the field.
        - See a single solution emerge in time as it follows the flow from its start point.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Concept

        A first-order ODE $y' = f(x, y)$ doesn't hand you one solution — it hands
        you a *rule for the slope* at every point of the plane. Draw a tiny arrow
        with slope $f(x, y)$ at a grid of points and you get the **slope field**:
        a map of the flow that every solution must follow.

        Our worked equation is the **logistic** model

        $$ y' = a\,y\left(1 - \frac{y}{K}\right), $$

        with growth rate $a$ and carrying capacity $K$. It has two equilibria,
        $y = 0$ and $y = K$, where the slope is zero and the field goes flat.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, np, plt):
    def logistic_grid(a, K):
        """y' = a*y*(1 - y/K), vectorized over a slope-field grid."""
        return lambda x, y: a * y * (1.0 - y / K)

    # A static illustration with fixed parameters, before we make it interactive.
    _f = logistic_grid(1.0, 4.0)
    _ax = delib.slope_field(_f, xlim=(0, 10), ylim=(-1, 6), density=22)
    _ax.axhline(4.0, color="#2a9d8f", lw=1.5, ls="--", label="K = 4 (equilibrium)")
    _ax.axhline(0.0, color="#888", lw=1.0, ls=":", label="y = 0 (equilibrium)")
    _ax.set_title("Slope field of the logistic equation (a = 1, K = 4)")
    _ax.legend(loc="lower right")
    _ax.figure
    return (logistic_grid,)


@app.cell(hide_code=True)
def _(delib, mo):
    controls = delib.param_panel(
        [
            {"name": "a", "label": "growth rate a", "start": -2.0, "stop": 2.0, "step": 0.1, "value": 1.0},
            {"name": "K", "label": "carrying capacity K", "start": 0.5, "stop": 5.0, "step": 0.1, "value": 4.0},
            {"name": "y0", "label": "initial condition y₀", "start": -1.0, "stop": 6.0, "step": 0.1, "value": 0.5},
        ]
    )
    mo.md(
        f"""
        ## Interactive exploration

        Drag the sliders. The slope field redraws and the red solution curve — the
        one passing through $y(0) = y_0$ — bends to follow the new flow in real time.

        {mo.as_html(controls)}
        """
    )
    return (controls,)


@app.cell(hide_code=True)
def _(controls, delib, logistic_grid, np, plt):
    a = controls.value["a"]
    K = controls.value["K"]
    y0 = controls.value["y0"]

    f_grid = logistic_grid(a, K)

    fig_explore, ax_explore = plt.subplots(figsize=(7, 5))
    delib.slope_field(f_grid, xlim=(0, 10), ylim=(-1, 6), density=22, ax=ax_explore)

    # Equilibria flatten the field; show them for reference.
    ax_explore.axhline(K, color="#2a9d8f", lw=1.5, ls="--")
    ax_explore.axhline(0.0, color="#888", lw=1.0, ls=":")

    # Integrate the single solution through y0 and overlay it on the flow.
    sol = delib.solve_ode(lambda t, y: a * y * (1.0 - y / K), (0.0, 10.0), y0)
    delib.overlay_solution(ax_explore, sol.t, sol.y[0], label=f"y(0) = {y0:.1f}")
    ax_explore.set_title(f"a = {a:.1f},  K = {K:.1f},  y₀ = {y0:.1f}")
    fig_explore
    return K, a, f_grid, sol, y0


@app.cell(hide_code=True)
def _(K, a, delib, go, mo, np, y0):
    # --- Section 4: time animation -------------------------------------------
    # Trace the solution curve being drawn as t advances, with native play/pause.
    n_frames = 60
    t_request = np.linspace(0.0, 10.0, n_frames)
    sol_anim = delib.solve_ode(lambda t, y: a * y * (1.0 - y / K), (0.0, 10.0), y0, t_eval=t_request)
    # The solver stops early if the solution diverges, so use what it returned
    # rather than assuming all n_frames points exist.
    t_anim = sol_anim.t
    ys = sol_anim.y[0]
    n = len(t_anim)

    finite = ys[np.isfinite(ys)]
    lo = float(min(finite.min(), 0.0)) if finite.size else -1.0
    hi = float(max(finite.max(), K)) if finite.size else K + 1.0
    y_lo, y_hi = lo - 0.5, hi + 0.5

    def _equilibria():
        return [
            go.Scatter(x=[0, 10], y=[K, K], mode="lines",
                       line=dict(color="#2a9d8f", dash="dash"), name="K"),
            go.Scatter(x=[0, 10], y=[0, 0], mode="lines",
                       line=dict(color="#bbb", dash="dot"), name="y = 0"),
            go.Scatter(x=t_anim, y=ys, mode="lines",
                       line=dict(color="#f0c9cf"), name="full solution"),
        ]

    frames_data = [
        {
            "name": f"{t_anim[i]:.1f}",
            "data": _equilibria()
            + [
                go.Scatter(x=t_anim[: i + 1], y=ys[: i + 1], mode="lines",
                           line=dict(color="#d1495b", width=3), name="y(t)"),
                go.Scatter(x=[t_anim[i]], y=[ys[i]], mode="markers",
                           marker=dict(color="#d1495b", size=10), name="now"),
            ],
        }
        for i in range(n)
    ]

    anim_fig = delib.animate_plotly(
        frames_data,
        layout=dict(
            title="The solution being traced as t advances",
            xaxis=dict(title="t", range=[0, 10]),
            yaxis=dict(title="y", range=[y_lo, y_hi]),
            height=480,
            showlegend=False,
        ),
    )
    mo.md("## Time animation\n\nPress **▶ Play** to watch the solution follow the flow from $y_0$.")
    return (anim_fig,)


@app.cell(hide_code=True)
def _(anim_fig):
    anim_fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Try it

        1. Set $a < 0$. Which equilibrium becomes the **attractor** now, and which
           one repels nearby solutions?
        2. Start with $y_0$ *above* $K$. Does the population fall to $K$ or overshoot?
        3. Find a value of $K$ where a solution starting at $y_0 = 0.5$ barely moves
           over the whole window. What does that say about the slope near $y = 0$?
        4. Push $a$ toward $2$. How does the steepness of the climb to $K$ change?
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---
        ## Your turn — the playground

        Open the **Playground** panel on the left (tap the ☰ toggle on mobile) and
        **ask in plain language** — *"show the solution when a is negative."* The
        tutor writes the code straight into the editor; **review it and press Run**
        to see the result below. Prefer to type your own? Just edit the code and
        Run. Bring your own Anthropic key — set it once in the 💬 tutor and it is
        shared here too.
        """
    )
    return


@app.cell
def _():
    # Bridge: runs on the main thread (the kernel is sandboxed in a Web Worker and
    # cannot see sessionStorage or the page config). Reads the shared key slot and
    # the chapter's cell sources, and writes the key back when set here.
    import anywidget
    import traitlets

    class Bridge(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) {
          function readKey(){ try { return sessionStorage.getItem('mathlearn.anthropicKey')||''; } catch(e){ return ''; } }
          function readCells(){ try { var c=(window.TUTOR_CONFIG||{}).cells||[]; return c.map(function(x){return (x.text||'').slice(0,1500);}); } catch(e){ return []; } }
          function push(){ model.set('key', readKey()); model.set('cells', JSON.stringify(readCells())); model.set('ready', true); model.save_changes(); }
          push();
          model.on('change:save_value', function(){ try{ sessionStorage.setItem('mathlearn.anthropicKey', model.get('save_value')); model.set('key', model.get('save_value')); model.save_changes(); }catch(e){} });
          el.style.display='none';
        }
        export default { render };
        """
        key = traitlets.Unicode("").tag(sync=True)
        cells = traitlets.Unicode("[]").tag(sync=True)
        ready = traitlets.Bool(False).tag(sync=True)
        save_value = traitlets.Unicode("").tag(sync=True)

    return (Bridge,)


@app.cell
def _(Bridge, mo):
    bridge = mo.ui.anywidget(Bridge())
    return (bridge,)


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


@app.cell
def _(mo):
    # One shared code string. Ask mode writes the tutor's code here; the editor
    # below reads it. This is the single code path — no separate Ask/Write modes.
    get_code, set_code = mo.state(
        "view = delib.slope_field(lambda x, y: 1.0*y*(1 - y/4.0), (0, 10), (-1, 6))"
    )
    return get_code, set_code


@app.cell
def _(bridge, mo):
    import json as _json

    _cells = []
    try:
        _cells = _json.loads((bridge.value or {}).get("cells", "[]"))
    except Exception:
        _cells = []
    _opts = {"(whole chapter)": ""}
    for _i, _src in enumerate(_cells):
        _flat = " ".join((_src or "").split())
        if _flat:
            _opts[f"Cell {_i + 1}: {_flat[:46]}"] = _src

    api_field = mo.ui.text(label="Anthropic key (optional here)", kind="password", full_width=True)
    cell_pick = mo.ui.dropdown(options=_opts, value="(whole chapter)", label="Ask about", full_width=True)
    return api_field, cell_pick


@app.cell
def _(get_code, mo):
    # Rebuilt whenever the code state changes, so the tutor's generated code lands
    # here ready to review and Run. Editing it locally is fine — Run uses .value.
    code_input = mo.ui.code_editor(value=get_code(), language="python")
    run_btn = mo.ui.run_button(label="Run", full_width=True)
    return code_input, run_btn


@app.cell
def _(api_field, bridge):
    # Persist a key typed here back to the shared slot (so the tutor sees it too).
    if api_field.value:
        bridge.widget.save_value = api_field.value
    return


@app.cell
def _(api_field, bridge, cell_pick):
    import json as _json

    _MODEL = "claude-haiku-4-5-20251001"
    _URL = "https://api.anthropic.com/v1/messages"
    _CONTEXT = (
        "This is Chapter 1 of a differential-equations course: first-order ODEs and "
        "slope fields, worked through the logistic equation y' = a*y*(1 - y/K) with "
        "growth rate a and carrying capacity K (equilibria at y=0 and y=K)."
    )
    _SYS = (
        "You help a student in a marimo notebook. " + _CONTEXT + " Reply with a SHORT "
        "(1-3 sentence) explanation, then exactly ONE ```python code block. The code "
        "must be self-contained and use only these names: mo, np, plt, go, delib (with "
        "helpers slope_field(f, xlim, ylim) -> matplotlib Axes, phase_portrait, "
        "overlay_solution, solve_ode, solve_system). Do NO file or network I/O. END by "
        "assigning the single renderable to a variable named `view`."
    )

    async def chat_model(messages, config):
        key = api_field.value or (bridge.value or {}).get("key", "")
        system = _SYS
        if cell_pick.value:
            system += '\n\nThe student is asking about this cell:\n"""\n' + cell_pick.value + '\n"""'
        msgs = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role in ("user", "assistant") and m.content
        ]
        body = _json.dumps({"model": _MODEL, "max_tokens": 700, "system": system, "messages": msgs})
        headers = {
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "anthropic-dangerous-direct-browser-access": "true",
        }
        from pyodide.http import pyfetch

        resp = await pyfetch(_URL, method="POST", headers=headers, body=body)
        data = await resp.json()
        if isinstance(data, dict) and data.get("content"):
            return "".join(b.get("text", "") for b in data["content"])
        return "**API error**\n\n```json\n" + _json.dumps(data, indent=2)[:800] + "\n```"

    return (chat_model,)


@app.cell
def _(chat_model, mo, set_code):
    import re

    def _on_message(messages):
        # When the tutor replies, lift its python block into the shared code state
        # so it appears in the editor for review + Run. This is the only insertion
        # path — no marimo "Add to Notebook".
        _bot = [m for m in messages if m.role == "assistant" and m.content]
        if not _bot:
            return
        _hit = re.search(r"```(?:python)?\s*\n(.*?)```", _bot[-1].content, re.S)
        if _hit:
            set_code(_hit.group(1).strip())

    chatbox = mo.ui.chat(
        chat_model,
        on_message=_on_message,
        prompts=[
            "explain this chapter in a paragraph",
            "show the solution when the growth rate a is negative",
            "plot the phase line of the logistic equation",
        ],
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, bridge, cell_pick, chatbox, code_input, mo, run_btn):
    _key_ok = bool(api_field.value or (bridge.value or {}).get("key"))
    _status = mo.md(
        "key loaded from the tutor ✓" if _key_ok else "⚠️ set your Anthropic key in the 💬 tutor (or below)"
    )
    _items = [mo.md("### Playground"), bridge, cell_pick, _status]
    if not _key_ok:
        _items.append(api_field)
    _items += [
        chatbox,
        mo.md("**Code** — the tutor writes here; review or edit, then Run:"),
        code_input,
        run_btn,
    ]
    mo.sidebar(_items)
    return


@app.cell(hide_code=True)
def _(code_input, mo, run_btn, run_view):
    mo.stop(not run_btn.value, mo.md("*Ask in the panel, then press **Run** to render the code.*"))
    run_view(code_input.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Recap & what's next

        A slope field turns an equation into a flow you can *see*; a solution curve is
        just a path that stays tangent to it everywhere.

        **Next:** *Separable & linear first-order* — instead of only reading the field,
        we'll solve these equations in closed form and check the formula against the
        very flow we drew here. *(No code from this chapter is required to start it.)*
        """
    )
    return


if __name__ == "__main__":
    app.run()
