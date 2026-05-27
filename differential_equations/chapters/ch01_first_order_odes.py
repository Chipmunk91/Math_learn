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
        Run. Bring your own Anthropic key — enter it in the panel; it stays in your
        browser.
        """
    )
    return


@app.cell
def _():
    # Two main-thread widgets (the kernel is sandboxed in a Web Worker and cannot
    # see sessionStorage or the page DOM). KeyBridge reads/writes the shared key
    # slot; CellPicker lets the student click a chapter cell to ask about it.
    import anywidget
    import traitlets

    class KeyBridge(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) {
          function readKey(){ try { return sessionStorage.getItem('mathlearn.anthropicKey')||''; } catch(e){ return ''; } }
          model.set('key', readKey()); model.set('ready', true); model.save_changes();
          model.on('change:save_value', function(){ try{ sessionStorage.setItem('mathlearn.anthropicKey', model.get('save_value')); model.set('key', model.get('save_value')); model.save_changes(); }catch(e){} });
          el.style.display='none';
        }
        export default { render };
        """
        key = traitlets.Unicode("").tag(sync=True)
        ready = traitlets.Bool(False).tag(sync=True)
        save_value = traitlets.Unicode("").tag(sync=True)

    class CellPicker(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) {
          var overlay, banner, picking=false;
          function selfCell(){ return el.closest ? el.closest('.marimo-cell') : null; }
          function under(t){ var c = (t && t.closest) ? t.closest('.marimo-cell') : null; return (c && c===selfCell()) ? null : c; }
          function cellText(c){
            var a = c.querySelector('.output-area') || c;
            var clone = a.cloneNode(true);
            var mm = clone.querySelectorAll('.katex-mathml'); for (var j=0;j<mm.length;j++) mm[j].remove();
            return (clone.innerText || '').replace(/\\n{3,}/g,'\\n\\n').trim();
          }
          function titleOf(t){
            var lines = t.split('\\n');
            for (var k=0;k<lines.length;k++){ var s=lines[k].trim(); if(s){ return s.replace(/[*_`#$]/g,'').trim().slice(0,40); } }
            return 'selected cell';
          }
          function ensure(){
            if(overlay) return;
            overlay=document.createElement('div');
            overlay.style.cssText='position:fixed;z-index:9998;background:rgba(47,111,176,.18);border:2px solid #2f6fb0;border-radius:6px;pointer-events:none;display:none';
            banner=document.createElement('div');
            banner.style.cssText='position:fixed;z-index:9999;top:10px;left:50%;transform:translateX(-50%);background:#2f6fb0;color:#fff;padding:6px 12px;border-radius:6px;font:13px sans-serif;display:none';
            banner.textContent='Click a cell to ask about it — Esc to cancel';
            document.body.appendChild(overlay); document.body.appendChild(banner);
          }
          function onMove(e){ var c=under(e.target); if(!c){ overlay.style.display='none'; return;} var r=c.getBoundingClientRect(); var o=overlay.style; o.display='block'; o.top=r.top+'px'; o.left=r.left+'px'; o.width=r.width+'px'; o.height=r.height+'px'; }
          function onClick(e){ var c=under(e.target); if(!c) return; e.preventDefault(); e.stopPropagation(); exit(); select(c); }
          function onKey(e){ if(e.key==='Escape') exit(); }
          function enter(){
            // Clear first: one click re-picks, and cancelling leaves nothing selected.
            model.set('picked_text',''); model.set('picked_title',''); model.save_changes(); paint();
            picking=true; ensure(); overlay.style.display='none'; banner.style.display='block';
            document.addEventListener('mousemove',onMove,true); document.addEventListener('click',onClick,true); document.addEventListener('keydown',onKey,true);
          }
          function exit(){ picking=false; if(overlay)overlay.style.display='none'; if(banner)banner.style.display='none'; document.removeEventListener('mousemove',onMove,true); document.removeEventListener('click',onClick,true); document.removeEventListener('keydown',onKey,true); }
          function select(c){ var t=cellText(c); model.set('picked_text', t.slice(0,2000)); model.set('picked_title', titleOf(t)); model.save_changes(); paint(); }
          var btn=document.createElement('button');
          btn.style.cssText='width:100%;padding:8px 10px;border:1px solid #c7d2e0;border-radius:8px;background:#f3f7fc;cursor:pointer;font:13px sans-serif;color:#2c3e50;text-align:left';
          function paint(){ var ti=model.get('picked_title'); btn.textContent = ti ? ('\\u{1F4CC} Asking about: '+ti) : '\\u{1F4CC} Pick a cell to ask about'; }
          btn.addEventListener('click', function(){ enter(); });
          el.appendChild(btn); paint();
        }
        export default { render };
        """
        picked_text = traitlets.Unicode("").tag(sync=True)
        picked_title = traitlets.Unicode("").tag(sync=True)

    return CellPicker, KeyBridge


@app.cell
def _(KeyBridge, mo):
    key_bridge = mo.ui.anywidget(KeyBridge())
    return (key_bridge,)


@app.cell
def _(CellPicker, mo):
    picker = mo.ui.anywidget(CellPicker())
    return (picker,)


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
def _(mo):
    api_field = mo.ui.text(label="Anthropic key (stays in your browser)", kind="password", full_width=True)
    return (api_field,)


@app.cell
def _(get_code, mo):
    # Rebuilt whenever the code state changes, so the tutor's generated code lands
    # here ready to review and Run. Editing it locally is fine — Run uses .value.
    code_input = mo.ui.code_editor(value=get_code(), language="python")
    run_btn = mo.ui.run_button(label="Run", full_width=True)
    return code_input, run_btn


@app.cell
def _(api_field, key_bridge):
    # Persist a key typed here to the shared slot so it auto-loads next visit.
    if api_field.value:
        key_bridge.widget.save_value = api_field.value
    return


@app.cell
def _(api_field, key_bridge, picker, set_code):
    import json as _json
    import re as _re

    _MODEL = "claude-haiku-4-5-20251001"
    _URL = "https://api.anthropic.com/v1/messages"
    _CONTEXT = (
        "This is Chapter 1 of a differential-equations course: first-order ODEs and "
        "slope fields, worked through the logistic equation y' = a*y*(1 - y/K) with "
        "growth rate a and carrying capacity K (equilibria at y=0 and y=K)."
    )
    _SYS = (
        "You are a tutor inside a marimo notebook. " + _CONTEXT + " Answer in TWO "
        "parts. Part 1: a brief plain-language explanation, 2-4 sentences, with NO "
        "code and NO fenced blocks. Part 2: exactly ONE ```python fenced block with "
        "the full self-contained solution and nothing after it. The code may use only "
        "these names: mo, np, plt, go, delib (helpers: slope_field(f, xlim, ylim) -> "
        "matplotlib Axes, phase_portrait, overlay_solution, solve_ode, solve_system). "
        "Do NO file or network I/O. END by assigning the single renderable to `view` "
        "(a matplotlib or plotly figure)."
    )

    async def chat_model(messages, config):
        key = api_field.value or (key_bridge.value or {}).get("key", "")
        system = _SYS
        _picked = (picker.value or {}).get("picked_text", "")
        if _picked:
            system += '\n\nThe student is asking about this cell:\n"""\n' + _picked + '\n"""'
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
        if not (isinstance(data, dict) and data.get("content")):
            return "**API error**\n\n```json\n" + _json.dumps(data, indent=2)[:800] + "\n```"
        full = "".join(b.get("text", "") for b in data["content"])
        # Lift code into the editor; strip ALL fenced blocks from the chat reply so
        # the bubble shows only readable prose (and no Add-to-Notebook button).
        _blocks = _re.findall(r"```(?:python)?\s*\n(.*?)```", full, _re.S)
        if _blocks:
            set_code(_blocks[0].strip())
        explanation = _re.sub(r"```.*?```", "", full, flags=_re.S).strip()
        return explanation or "Code is in the editor below — review it and press **Run**."

    return (chat_model,)


@app.cell
def _(chat_model, mo):
    chatbox = mo.ui.chat(
        chat_model,
        prompts=[
            "explain this chapter in a paragraph",
            "show the solution when the growth rate a is negative",
            "plot the phase line of the logistic equation",
        ],
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, code_input, key_bridge, mo, picker, run_btn):
    _key_ok = bool(api_field.value or (key_bridge.value or {}).get("key"))
    _items = [mo.md("### Playground"), key_bridge, api_field]
    if _key_ok:
        _items += [
            mo.md("key set ✓"),
            picker,
            chatbox,
            mo.md("**Code** — the tutor writes here; review or edit, then Run:"),
            code_input,
            run_btn,
        ]
    else:
        _items.append(
            mo.callout(
                mo.md(
                    "**Add your Anthropic API key** above to ask the tutor.\n\n"
                    "No key yet? Create one at "
                    "[console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys). "
                    "It is stored only in this browser and sent only to Anthropic — "
                    "never to this site."
                ),
                kind="info",
            )
        )
    mo.sidebar(_items, width="420px")
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
