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
def _(delib, go, mo, np):
    # Beat 1 — the real-world observation that motivates the whole chapter.
    _t = np.linspace(0, 14, 80)
    _sol = delib.solve_ode(lambda t, y: 0.9 * y * (1 - y / 1000.0), (0.0, 14.0), 3.0, t_eval=_t)
    _fig = go.Figure(go.Scatter(x=_sol.t, y=_sol.y[0], mode="lines",
                                line=dict(color="#2f6fb0", width=3),
                                hoverinfo="skip", showlegend=False))
    _fig.update_layout(
        template="plotly_white",
        title=dict(text="One rumor on a 1,000-person campus", x=0.02),
        xaxis=dict(title="day"), yaxis=dict(title="people who've heard it"),
        height=320, margin=dict(l=60, r=20, t=46, b=42),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    mo.vstack([
        mo.md(
            r"""
            ## A story about change

            Most of the math you've met so far describes where things *are* — a point,
            a length, a value. **Differential equations** capture something subtler and
            far more powerful: how things *change*. They rarely hand you the answer
            outright. Instead they hand you a **rule for the rate of change** at each
            instant, and let the whole story unfold from it. Populations, epidemics,
            cooling coffee, orbiting planets, the charge on your phone — all of them are
            stories told by differential equations.

            The quickest way to *feel* that is with a story. So here's one.

            Monday morning, **3 people** on a 1,000-person campus know a juicy rumor. By
            Friday, *everyone* does. If you plot how many have heard it each day, you
            don't get a straight line — you get this lazy **S**: a slow start, an
            explosive middle, and a gentle leveling-off.

            Why that exact shape? Because spreading takes **two** people: one who knows
            and one who doesn't. On Monday there are only a handful of tellers, so it
            creeps. By midweek there are plenty of tellers *and* plenty of fresh ears,
            so it erupts. By Friday almost everyone has heard it, so there's hardly
            anyone left to tell — and it flattens. All the drama lives in the middle.
            """
        ),
        _fig,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Bridge — name the concept the story just illustrated.
    mo.md(
        r"""
        ## What the story is really saying

        Notice we never wrote a formula for "how many know it on day 7." We described
        something more *local*: how fast the number is changing **right now**, in terms
        of how many already know. That is exactly what a **differential equation** is —
        a rule of the form

        $$ \frac{dy}{dt} = f(t, y), $$

        which reads *"tell me where you are, and I'll tell you how fast you're moving."*
        The equation is called **first-order** because the rule uses only the current
        value $y$ (and possibly the time $t$) — no acceleration, no higher rates of
        change. That's all a solver needs: give it the rule plus a starting point and it
        can trace the entire curve, one small step at a time. The S-shape above is
        simply what you get when you **follow the rate** day by day.

        So the rest of this chapter is three moves: **(1)** turn the rumor story into
        such a rate-rule, **(2)** read what the rule tells us *before* solving it, and
        **(3)** watch the family of solutions it implies.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 2 — build the model from the story.
    mo.md(
        r"""
        ## Turning the story into an equation

        Let $y(t)$ be how many people have heard the rumor by day $t$, out of a campus
        of $K$ people. We don't know $y(t)$ yet — that's the whole point. But we *can*
        describe its **rate of change** straight from the mechanism of gossip.

        A fresh telling happens only when a **knower** runs into a **non-knower**. There
        are $y$ knowers and $K - y$ people who haven't heard yet, so the number of
        possible "telling" encounters — and therefore the rate at which new people learn
        the rumor — is proportional to their product:

        $$ \frac{dy}{dt} = b\,y\,(K - y). $$

        It reads more cleanly if we factor out the capacity and write the very same rule
        as

        $$ \frac{dy}{dt} = a\,y\left(1 - \frac{y}{K}\right), \qquad a = bK, $$

        the famous **logistic equation**. Hear it as two voices in tension. The factor
        $y$ is the **engine**: more knowers means more spreading, which is why a rumor
        with no one to start it never moves. The factor $(1 - y/K)$ is the **brake**: as
        $y$ climbs toward the whole campus $K$, the pool of fresh ears shrinks toward
        zero and the brake clamps down. Their tug-of-war — engine winning early, brake
        winning late — is *exactly* the S-curve we observed.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3 — play with the symbols (live SymPy below).
    mo.md(
        r"""
        ## Play with the symbols

        Here's the quiet superpower of writing the rule down: we can mine it for
        insight *before drawing or solving anything*. The most revealing question is —
        where does the spread **stop**? It stops wherever the rate is zero, $dy/dt = 0$.
        The $y$-values that satisfy that are the **equilibria**: populations that, once
        reached, never change.

        For our rumor, $a\,y(1 - y/K) = 0$ has two answers — $y = 0$ (nobody knows) and
        $y = K$ (everybody does) — and they behave oppositely. One is a **stable**
        resting point that nearby solutions are pulled *toward*; the other is
        **unstable**, with solutions pushed *away*. The tell is the slope of the rate,
        $f'(y)$: negative means stable, positive means unstable.

        Don't take that on faith — **change the rate law below and watch the equilibria
        and their stability re-solve symbolically**, live. Try `a*y` (spreading with no
        ceiling), or stack a second brake with `a*y*(1 - y/K)*(2 - y/K)` and see a third
        equilibrium appear.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    eq_input = mo.ui.text(value="a*y*(1 - y/K)", full_width=True, label="dy/dt =")
    eq_input
    return (eq_input,)


@app.cell(hide_code=True)
def _(delib, eq_input):
    delib.equilibria_report(eq_input.value)
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 4 — bridge into the visuals.
    mo.md(
        r"""
        ## See the whole flow at once — the slope field

        Solving the equation from one starting point gives one curve. But the rule
        $dy/dt = f(t, y)$ does something more generous: it assigns a slope to **every**
        point $(t, y)$ in the plane. So at each point we can draw a tiny arrow pointing
        the way a solution passing through there would head — and doing that across a
        grid gives the **slope field**, a picture of *every* possible spread-story at
        once, without solving a thing.

        Read it like a current in water: drop a cork anywhere and it drifts along the
        arrows. The equilibria you just found by hand reappear here as flat, horizontal
        lanes — $y = 0$ (nobody knows) and $y = K$ (everybody does) — where the arrows
        lie perfectly level because the rate is zero. Everywhere between them the arrows
        tilt upward, carrying solutions from the empty rumor toward the full campus.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    def logistic_grid(a, K):
        """y' = a*y*(1 - y/K), vectorized over a slope-field grid."""
        return lambda x, y: a * y * (1.0 - y / K)

    # A static illustration with fixed parameters, before we make it interactive.
    _fig = delib.vector_field_plotly(
        logistic_grid(1.0, 4.0), (0, 10), (-1, 6), density=18,
        title="Vector field of the logistic equation (a = 1, K = 4)",
    )
    _fig.add_hline(y=4.0, line=dict(color="#2a9d8f", dash="dash", width=1.5),
                   annotation_text="K = 4", annotation_position="top right")
    _fig.add_hline(y=0.0, line=dict(color="#9aa7b5", dash="dot", width=1),
                   annotation_text="y = 0", annotation_position="bottom right")
    _fig
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
def _(controls, delib, go, logistic_grid):
    a = controls.value["a"]
    K = controls.value["K"]
    y0 = controls.value["y0"]

    f_grid = logistic_grid(a, K)

    fig_explore = delib.vector_field_plotly(
        f_grid, (0, 10), (-1, 6), density=18,
        title=f"a = {a:.1f},  K = {K:.1f},  y₀ = {y0:.1f}",
    )
    # Equilibria flatten the field; show them for reference.
    fig_explore.add_hline(y=K, line=dict(color="#2a9d8f", dash="dash", width=1.5))
    fig_explore.add_hline(y=0.0, line=dict(color="#9aa7b5", dash="dot", width=1))

    # Integrate the single solution through y0 and overlay it on the flow.
    sol = delib.solve_ode(lambda t, y: a * y * (1.0 - y / K), (0.0, 10.0), y0)
    fig_explore.add_trace(go.Scatter(
        x=sol.t, y=sol.y[0], mode="lines",
        line=dict(color="#d1495b", width=3), hoverinfo="skip", showlegend=False,
    ))
    fig_explore.add_trace(go.Scatter(
        x=[sol.t[0]], y=[sol.y[0][0]], mode="markers",
        marker=dict(color="#d1495b", size=9), hoverinfo="skip", showlegend=False,
    ))
    fig_explore
    return K, a, f_grid, sol, y0


@app.cell(hide_code=True)
def _(K, a, delib, go, mo):
    # The dynamical view: the field is fixed (static arrows); particles ride along
    # it. Reshape the field with the a / K sliders above and re-watch.
    _eq = [
        go.Scatter(x=[0, 10], y=[K, K], mode="lines",
                   line=dict(color="#2a9d8f", dash="dash", width=1.5),
                   hoverinfo="skip", showlegend=False),
        go.Scatter(x=[0, 10], y=[0, 0], mode="lines",
                   line=dict(color="#9aa7b5", dash="dot", width=1),
                   hoverinfo="skip", showlegend=False),
    ]
    anim_fig = delib.flow_field(
        lambda x, y: a * y * (1.0 - y / K), (0, 10), (-1, 6),
        extra_lines=_eq,
        title=f"Particles riding the field  (a = {a:.1f},  K = {K:.1f})",
    )
    mo.md(
        "## Watch particles ride the field\n\nThe arrows are the field — fixed for "
        "these parameters. Press **▶ Play** and watch particles flow *along* them, "
        "all bending toward $y = K$ and peeling off $y = 0$. Then drag the **$a$ / $K$ "
        "sliders above** to reshape the field and play again."
    )
    return (anim_fig,)


@app.cell(hide_code=True)
def _(anim_fig):
    anim_fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Try it — in code

        Each task below is a little code ground. Type and run your own answer, or ask
        the tutor (the ✨ box) to write or edit the code for you — then **Run & check**
        to see the output and whether it's right.
        """
    )
    return


# --- Challenge 1: the stable equilibrium when a < 0 -----------------------------
@app.cell
def _(mo):
    c1_get, c1_set = mo.state(
        "a, K = -1.0, 4.0\n"
        "# With a < 0, which equilibrium do solutions move toward?\n"
        "# Assign that equilibrium's y-value to `answer`.\n"
        "answer = ...\n"
    )
    return c1_get, c1_set


@app.cell
def _(c1_get, mo):
    c1_ai = mo.ui.text(placeholder="✨ ask the tutor to write/edit the code…", full_width=True)
    c1_gen = mo.ui.run_button(label="✨ Write / edit")
    c1_code = mo.ui.code_editor(value=c1_get(), language="python")
    c1_run = mo.ui.run_button(label="Run & check", full_width=True)
    return c1_ai, c1_code, c1_gen, c1_run


@app.cell
async def _(api_field, c1_ai, c1_code, c1_gen, c1_set, delib, key_bridge, mo):
    mo.stop(not c1_gen.value)
    _key = api_field.value or (key_bridge.value or {}).get("key", "")
    c1_set(await delib.ai_code(
        c1_ai.value, c1_code.value, _key, coach=True,
        context="Logistic y'=a*y*(1-y/K). The task: which equilibrium is stable when a<0; put its y-value in `answer`.",
    ))
    return


@app.cell(hide_code=True)
def _(c1_ai, c1_code, c1_gen, c1_run, mo):
    mo.vstack([
        mo.md("**1.** With $a<0$, which equilibrium becomes the **attractor**? "
              "Assign its $y$-value to `answer`."),
        mo.vstack([c1_ai, c1_gen]),
        c1_code,
        c1_run,
    ])
    return


@app.cell(hide_code=True)
def _(c1_code, c1_run, delib):
    def _c1_check(ns):
        a = ns.get("answer")
        if a is None or a is Ellipsis:
            return False, "Assign the attracting equilibrium's $y$-value to `answer`."
        try:
            ok = abs(float(a)) < 1e-9
        except Exception:
            return False, "`answer` should be a single number."
        if ok:
            return True, "Right — for $a<0$, $y=0$ is the attractor (and $y=K$ repels)."
        return False, f"You got {a}. With $a<0$ the flow points toward $y=0$."

    delib.run_exercise(c1_code.value, c1_run.value, check=_c1_check)
    return


# --- Challenge 2: a solution starting above K ----------------------------------
@app.cell
def _(mo):
    c2_get, c2_set = mo.state(
        "a, K, y0 = 1.0, 4.0, 6.0   # start ABOVE the carrying capacity\n"
        "# Integrate to t = 10 and store the final value y(10) in `answer`.\n"
        "answer = ...\n"
    )
    return c2_get, c2_set


@app.cell
def _(c2_get, mo):
    c2_ai = mo.ui.text(placeholder="✨ ask the tutor to write/edit the code…", full_width=True)
    c2_gen = mo.ui.run_button(label="✨ Write / edit")
    c2_code = mo.ui.code_editor(value=c2_get(), language="python")
    c2_run = mo.ui.run_button(label="Run & check", full_width=True)
    return c2_ai, c2_code, c2_gen, c2_run


@app.cell
async def _(api_field, c2_ai, c2_code, c2_gen, c2_set, delib, key_bridge, mo):
    mo.stop(not c2_gen.value)
    _key = api_field.value or (key_bridge.value or {}).get("key", "")
    c2_set(await delib.ai_code(
        c2_ai.value, c2_code.value, _key, coach=True,
        context="Logistic y'=a*y*(1-y/K), a=1, K=4, y0=6 (above K). Task: integrate to t=10 and put y(10) in `answer` (use delib.solve_ode).",
    ))
    return


@app.cell(hide_code=True)
def _(c2_ai, c2_code, c2_gen, c2_run, mo):
    mo.vstack([
        mo.md("**2.** Start **above** the capacity ($y_0=6$, $a=1$, $K=4$). Integrate "
              "to $t=10$ and put the final value $y(10)$ in `answer`. Does it fall to "
              "$K$ or overshoot?"),
        mo.vstack([c2_ai, c2_gen]),
        c2_code,
        c2_run,
    ])
    return


@app.cell(hide_code=True)
def _(c2_code, c2_run, delib):
    def _c2_check(ns):
        a = ns.get("answer")
        if a is None or a is Ellipsis:
            return False, "Assign $y(10)$ to `answer` — try `delib.solve_ode`."
        try:
            ok = abs(float(a) - 4.0) < 0.1
        except Exception:
            return False, "`answer` should be a single number."
        if ok:
            return True, "Right — it settles onto $K=4$ from above, no overshoot."
        return False, f"You got {a}. Integrate $y'=a y(1-y/K)$ from $y_0=6$; it approaches $4$."

    delib.run_exercise(c2_code.value, c2_run.value, check=_c2_check)
    return


# --- Challenge 3: where the growth is steepest ---------------------------------
@app.cell
def _(mo):
    c3_get, c3_set = mo.state(
        "a, K = 1.0, 4.0\n"
        "# The growth rate y' = a*y*(1 - y/K) is largest at one value of y.\n"
        "# Find that y (the steepest point) and store it in `answer`.\n"
        "answer = ...\n"
    )
    return c3_get, c3_set


@app.cell
def _(c3_get, mo):
    c3_ai = mo.ui.text(placeholder="✨ ask the tutor to write/edit the code…", full_width=True)
    c3_gen = mo.ui.run_button(label="✨ Write / edit")
    c3_code = mo.ui.code_editor(value=c3_get(), language="python")
    c3_run = mo.ui.run_button(label="Run & check", full_width=True)
    return c3_ai, c3_code, c3_gen, c3_run


@app.cell
async def _(api_field, c3_ai, c3_code, c3_gen, c3_set, delib, key_bridge, mo):
    mo.stop(not c3_gen.value)
    _key = api_field.value or (key_bridge.value or {}).get("key", "")
    c3_set(await delib.ai_code(
        c3_ai.value, c3_code.value, _key, coach=True,
        context="Logistic y'=a*y*(1-y/K), a=1, K=4. Task: find the y that maximizes the growth rate y'; put it in `answer`.",
    ))
    return


@app.cell(hide_code=True)
def _(c3_ai, c3_code, c3_gen, c3_run, mo):
    mo.vstack([
        mo.md("**3.** The growth rate $y'=a\\,y(1-y/K)$ is **steepest** at one value of "
              "$y$. Find it (for $a=1$, $K=4$) and put it in `answer`."),
        mo.vstack([c3_ai, c3_gen]),
        c3_code,
        c3_run,
    ])
    return


@app.cell(hide_code=True)
def _(c3_code, c3_run, delib):
    def _c3_check(ns):
        a = ns.get("answer")
        if a is None or a is Ellipsis:
            return False, "Assign the $y$ of steepest growth to `answer`."
        try:
            ok = abs(float(a) - 2.0) < 0.05
        except Exception:
            return False, "`answer` should be a single number."
        if ok:
            return True, "Yes — growth peaks at $y=K/2=2$, halfway to capacity."
        return False, f"You got {a}. Maximize $a y(1-y/K)$ over $y$; the peak is at $y=K/2$."

    delib.run_exercise(c3_code.value, c3_run.value, check=_c3_check)
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
def _(mo):
    api_field = mo.ui.text(label="Anthropic key (stays in your browser)", kind="password", full_width=True)
    return (api_field,)


@app.cell
def _(api_field, key_bridge):
    # Persist a key typed here to the shared slot so it auto-loads next visit.
    if api_field.value:
        key_bridge.widget.save_value = api_field.value
    return


@app.cell
def _(api_field, key_bridge, picker):
    import json as _json

    _MODEL = "claude-haiku-4-5-20251001"
    _URL = "https://api.anthropic.com/v1/messages"
    _CONTEXT = (
        "This is Chapter 1 of a differential-equations course: first-order ODEs and "
        "slope fields, worked through the logistic equation y' = a*y*(1 - y/K) with "
        "growth rate a and carrying capacity K (equilibria at y=0 and y=K)."
    )
    _SYS = (
        "You are a friendly, concise math tutor inside a marimo notebook. " + _CONTEXT
        + " Explain clearly in plain language and ALWAYS use LaTeX for math — inline "
        "$...$ and display $$...$$ (never write bare expressions like y'=ay). When code "
        "helps, you may include a ```python block using only mo, np, plt, go, delib. "
        "delib API — call with these POSITIONAL args only; do NOT invent extra keyword "
        "arguments: delib.vector_field_plotly(f, xlim, ylim) with f(x,y); "
        "delib.flow_field(f, xlim, ylim) with f(x,y); delib.solution_surface(f, t_span, "
        "y0_values) with f(t,y); delib.solve_ode(f, t_span, y0) with f(t,y) -> result "
        "with .t and .y. Assign a Plotly figure to `view` to display it. The student "
        "can copy code into a practice cell to run it. Keep answers focused."
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
        body = _json.dumps({"model": _MODEL, "max_tokens": 800, "system": system, "messages": msgs})
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
        return "".join(b.get("text", "") for b in data["content"])

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
def _(api_field, chatbox, key_bridge, mo, picker):
    _key_ok = bool(api_field.value or (key_bridge.value or {}).get("key"))
    _items = [mo.md("### Tutor"), key_bridge, api_field]
    if _key_ok:
        _items += [mo.md("key set ✓"), picker, chatbox]
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
def _(mo):
    mo.md(
        r"""
        ---
        ## Playground — free exploration

        No task, no grading. Type any Python, or ask the tutor (✨) to write it, then
        **Run** to see the result. Build whatever you're curious about.
        """
    )
    return


@app.cell
def _(mo):
    pg_get, pg_set = mo.state(
        "view = delib.vector_field_plotly(lambda x, y: 1.0*y*(1 - y/4.0), (0, 10), (-1, 6))\n"
    )
    return pg_get, pg_set


@app.cell
def _(mo, pg_get):
    pg_ai = mo.ui.text(placeholder="✨ ask the tutor to write/edit the code…", full_width=True)
    pg_gen = mo.ui.run_button(label="✨ Write / edit")
    pg_code = mo.ui.code_editor(value=pg_get(), language="python")
    pg_run = mo.ui.run_button(label="Run", full_width=True)
    return pg_ai, pg_code, pg_gen, pg_run


@app.cell
async def _(api_field, delib, key_bridge, mo, pg_ai, pg_code, pg_gen, pg_set):
    mo.stop(not pg_gen.value)
    _key = api_field.value or (key_bridge.value or {}).get("key", "")
    pg_set(await delib.ai_code(
        pg_ai.value, pg_code.value, _key,
        context="Open sandbox for chapter 1 (first-order ODEs, logistic). Write complete, runnable code; assign a Plotly figure to `view`.",
    ))
    return


@app.cell(hide_code=True)
def _(mo, pg_ai, pg_code, pg_gen, pg_run):
    mo.vstack([
        mo.vstack([pg_ai, pg_gen]),
        pg_code,
        pg_run,
    ])
    return


@app.cell(hide_code=True)
def _(delib, pg_code, pg_run):
    # No check -> run_exercise just renders the view (open sandbox).
    delib.run_exercise(pg_code.value, pg_run.value)
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
