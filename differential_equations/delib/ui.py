"""Standardized marimo UI controls so every chapter feels consistent."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import marimo as mo

__all__ = [
    "param_slider", "param_panel", "run_exercise", "ai_code", "equilibria_report",
    "exercise_inputs", "exercise_ai", "exercise_view", "check_number", "closed_form_report", "solve_steps",
    "derivation", "video",
    "key_field", "key_bridge_widget", "cell_picker_widget", "persist_key",
    "tutor_chat", "tutor_sidebar",
]

_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_DELIB_API = (
    "delib API — call with these POSITIONAL args only; do NOT invent extra keyword "
    "arguments: delib.vector_field_plotly(f, xlim, ylim) with f(x,y); "
    "delib.flow_field(f, xlim, ylim) with f(x,y); delib.solution_surface(f, t_span, "
    "y0_values) with f(t,y); delib.solve_ode(f, t_span, y0) with f(t,y) -> result with "
    ".t and .y. Assign a Plotly figure to `view` to display it."
)


def param_slider(
    label: str,
    start: float,
    stop: float,
    step: float,
    value: float,
):
    """A labelled :func:`marimo.ui.slider` with the value shown inline."""
    return mo.ui.slider(
        start=start,
        stop=stop,
        step=step,
        value=value,
        label=label,
        show_value=True,
    )


def param_panel(specs: Sequence[Mapping]):
    """Build a group of sliders keyed by name.

    ``specs`` is a sequence of dicts like
    ``{"name": "a", "label": "growth a", "start": -2, "stop": 2,
       "step": 0.1, "value": 1.0}``.

    Returns a :func:`marimo.ui.dictionary`; read individual values via
    ``panel.value["a"]`` and display the controls with ``mo.vstack`` over
    ``panel.values()`` (or just render ``panel``).
    """
    sliders = {
        spec["name"]: param_slider(
            spec.get("label", spec["name"]),
            spec["start"],
            spec["stop"],
            spec["step"],
            spec["value"],
        )
        for spec in specs
    }
    return mo.ui.dictionary(sliders)


def run_exercise(code: str, run_pressed: bool, *, check=None, ns_extra: Mapping | None = None):
    """Run a student's code answer and auto-grade it.

    Pair with a ``mo.ui.code_editor`` and a ``mo.ui.run_button`` in the chapter::

        delib.run_exercise(editor.value, run_btn.value, check=my_check)

    Execs ``code`` in the standard namespace (``mo, np, plt, go, delib`` plus any
    ``ns_extra``), renders a ``view`` if the code assigns one, and runs
    ``check(ns) -> (ok: bool, message: str)`` to show a pass/fail callout. The
    student code runs in the visitor's own browser sandbox, so it can only affect
    their session. Returns a marimo object to display.
    """
    if not run_pressed:
        return mo.md("*Write your answer above and press **Run**.*")

    import traceback
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go
    import delib as _delib

    ns = {"mo": mo, "np": np, "plt": plt, "go": go, "delib": _delib}
    if ns_extra:
        ns.update(ns_extra)
    try:
        exec(code, ns)
    except Exception:
        return mo.callout(mo.md(f"```\n{traceback.format_exc()}\n```"), kind="danger")

    out = []
    view = ns.get("view")
    if isinstance(view, matplotlib.axes.Axes):
        view = view.figure
    if view is not None:
        out.append(view)
    if check is not None:
        try:
            ok, msg = check(ns)
        except Exception as exc:
            ok, msg = False, f"checker error: {exc}"
        out.append(mo.callout(mo.md(("✅ " if ok else "❌ ") + msg),
                              kind=("success" if ok else "warn")))
    return mo.vstack(out) if out else mo.md("*(ran with no output)*")


async def ai_code(instruction, current_code, key, *, context="", coach=False,
                  model="claude-haiku-4-5-20251001"):
    """Ask Claude to write or edit a code answer for a single exercise.

    Given the student's plain-language ``instruction`` and their ``current_code``,
    returns the FULL updated program as a string (the python block extracted from
    the reply). On any error or empty key, returns ``current_code`` unchanged so
    the editor is never wiped. BYO key, called client-side.

    With ``coach=True`` (graded exercises), the AI scaffolds and hints but is told
    NOT to fill in the final graded ``answer`` — the student completes that.
    """
    import json
    import re

    if not (key and instruction and instruction.strip()):
        return current_code
    system = (
        "You write and edit Python for a math notebook. Given the student's request "
        "and their current code, reply with the FULL updated program as exactly one "
        "```python fenced block and nothing else. Use only mo, np, plt, go, delib.\n"
        "delib API — call with these POSITIONAL args only; do NOT invent extra keyword "
        "arguments:\n"
        "  delib.vector_field_plotly(f, xlim, ylim)        # f(x, y); xlim/ylim are (lo, hi) -> Plotly fig\n"
        "  delib.flow_field(f, xlim, ylim)                 # f(x, y); animated Plotly fig\n"
        "  delib.solution_surface(f, t_span, y0_values)    # f(t, y); t_span=(t0,t1); y0_values list -> 3D fig\n"
        "  delib.solve_ode(f, t_span, y0)                  # f(t, y) -> result with .t and .y (.y[0] = solution)\n"
        "Assign what the task needs — a number to `answer`, and/or a Plotly figure to "
        "`view`. Do no file or network I/O. " + context
    )
    if coach:
        system += (
            " This is a GRADED exercise: help the student set up and explore the "
            "problem with code and short hint comments, but do NOT compute or fill in "
            "the final graded value — leave the `answer = ...` line for them to finish."
        )
    user = f"Current code:\n```python\n{current_code}\n```\n\nRequest: {instruction}"
    body = json.dumps({
        "model": model, "max_tokens": 800, "system": system,
        "messages": [{"role": "user", "content": user}],
    })
    headers = {
        "content-type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "anthropic-dangerous-direct-browser-access": "true",
    }
    url = "https://api.anthropic.com/v1/messages"
    try:
        from pyodide.http import pyfetch

        resp = await pyfetch(url, method="POST", headers=headers, body=body)
        data = await resp.json()
    except ModuleNotFoundError:
        import urllib.request
        import urllib.error

        req = urllib.request.Request(url, data=body.encode(), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as exc:
            data = json.loads(exc.read().decode())
    except Exception:
        return current_code

    if not (isinstance(data, dict) and data.get("content")):
        return current_code
    full = "".join(b.get("text", "") for b in data["content"])
    m = re.search(r"```(?:python)?\s*\n(.*?)```", full, re.S)
    return m.group(1).strip() if m else (full.strip() or current_code)


def _guard_expr(expr):
    """Raise ValueError if a SymPy expression looks too wild to solve safely
    (huge exponents/numbers, or very deep). dsolve/solve/integrate are called
    only after this passes, so pathological input can't hang the single-threaded
    WASM kernel (e.g. ``...*e^999``)."""
    import sympy as sp

    for p in expr.atoms(sp.Pow):
        e = p.exp
        if getattr(e, "is_Number", False) and abs(float(e)) > 12:
            raise ValueError("that exponent is too large — try a smaller one")
    for n in expr.atoms(sp.Number):
        try:
            big = abs(float(n)) > 1e6
        except (OverflowError, TypeError):
            big = True
        if big:
            raise ValueError("that number is too large")
    if sp.count_ops(expr) > 60:
        raise ValueError("that expression is too complex to solve here")


def equilibria_report(expr_str, *, var="y"):
    """Symbolically find and classify the equilibria of ``d{var}/dt = expr``.

    Parses ``expr_str`` (free symbols like ``a``, ``K`` are allowed), solves
    ``expr = 0`` for ``var``, and reports each equilibrium with ``f'(var)`` (an
    equilibrium is stable where the slope of the rate is negative). Rendered as
    marimo markdown with LaTeX. Uses SymPy in the kernel; lets students edit the
    rate law and watch the formalism re-solve live.
    """
    import sympy as sp

    try:
        y = sp.Symbol(var)
        expr = sp.sympify(expr_str, locals={var: y})
        _guard_expr(expr)
    except Exception as exc:
        return mo.callout(
            mo.md(f"Couldn't read that — try something like `a*y*(1 - y/K)`.\n\n`{exc}`"),
            kind="warn",
        )
    try:
        sols = sp.solve(sp.Eq(expr, 0), y)
    except Exception:
        sols = []
    fprime = sp.diff(expr, y)
    lines = [f"Rate law: $\\dfrac{{d{var}}}{{dt}} = {sp.latex(expr)}$."]
    if sols:
        lines.append(
            "**Equilibria** (where the rate is $0$): "
            + ", ".join(f"${var} = {sp.latex(s)}$" for s in sols) + "."
        )
        lines.append(
            f"Slope of the rate $f'({var}) = {sp.latex(sp.simplify(fprime))}$ — an "
            "equilibrium is **stable** where this is negative:"
        )
        for s in sols:
            d = sp.simplify(fprime.subs(y, s))
            lines.append(f"- at ${var} = {sp.latex(s)}$: &nbsp; $f' = {sp.latex(d)}$")
    else:
        lines.append(f"No equilibrium in ${var}$ for this rate law.")
    return mo.md("\n\n".join(lines))


# --- code-challenge kit -------------------------------------------------------
# A challenge is five tiny cells (state, inputs, AI, view, eval). These helpers
# carry the repeated wiring so each chapter writes ~1 line per cell. UI elements
# must still be created as globals in a cell (marimo reactivity), so the cell
# count stays; the boilerplate does not.

def exercise_inputs(default_code, *, run_label="Run & check"):
    """The four controls for a code challenge: AI box, ✨ button, editor, run.

    Use in one cell (bind to globals): ``ai, gen, code, run =
    delib.exercise_inputs(get_code())`` where ``get_code`` is an ``mo.state`` so
    the AI can refill the editor.
    """
    ai = mo.ui.text(placeholder="✨ ask the tutor to write/edit the code…", full_width=True)
    gen = mo.ui.run_button(label="✨ Write / edit")
    code = mo.ui.code_editor(value=default_code, language="python")
    run = mo.ui.run_button(label=run_label, full_width=True)
    return ai, gen, code, run


async def exercise_ai(gen, ai, code, set_code, key, *, context="", coach=True):
    """Glue for the ✨ button — call in an async cell. Stops until pressed, then
    writes the AI's code into the editor state. ``coach=True`` scaffolds without
    filling in the graded ``answer``."""
    mo.stop(not gen.value)
    set_code(await ai_code(ai.value, code.value, key, context=context, coach=coach))


def exercise_view(prompt, ai, gen, code, run):
    """Lay out a challenge: prompt (optional), then AI box + button, editor, run."""
    items = []
    if prompt is not None:
        items.append(mo.md(prompt) if isinstance(prompt, str) else prompt)
    items += [mo.vstack([ai, gen]), code, run]
    return mo.vstack(items)


def check_number(ns, *, target, tol=1e-6, key="answer", ok="Correct.", hint=""):
    """A ready-made ``run_exercise`` checker: pass when ``ns[key]`` is within
    ``tol`` of ``target``."""
    v = ns.get(key)
    if v is None or v is Ellipsis:
        return False, f"Define `{key}`."
    try:
        good = abs(float(v) - target) < tol
    except Exception:
        return False, f"`{key}` should be a single number."
    return (True, ok) if good else (False, hint or f"You got {v}.")


def closed_form_report(rhs_str, *, func="y", indep="t"):
    """Symbolically solve ``d{func}/d{indep} = rhs`` for its closed form (SymPy
    ``dsolve``), rendered as marimo markdown — the symbol-play beat for chapters
    about solving exactly. Free symbols (e.g. ``k``) are allowed."""
    import sympy as sp

    t = sp.Symbol(indep)
    f = sp.Function(func)
    try:
        rhs = sp.sympify(rhs_str, locals={func: f(t), indep: t})
        _guard_expr(rhs)
        sol = sp.dsolve(sp.Eq(f(t).diff(t), rhs), f(t))
        return mo.md(
            f"The equation $\\dfrac{{d{func}}}{{d{indep}}} = {sp.latex(rhs)}$ solves to\n\n"
            f"$$ {sp.latex(sol)} $$\n\n"
            "where the constant is pinned down by the starting value."
        )
    except Exception as exc:
        return mo.callout(mo.md(f"Couldn't solve that one symbolically.\n\n`{exc}`"), kind="warn")


def derivation(steps, *, autoplay_ms=1500, title=None):
    """An in-browser ANIMATED derivation for the *teaching* (not an exercise).

    ``steps`` is a list of LaTeX strings, or ``(latex, caption)`` pairs. Returns a
    small player (anywidget): one equation at a time with Prev / Play / Next,
    cross-fading between steps — a serverless, guided take on Manim-style algebra.
    Emphasise a moving term inside the LaTeX with ``\\textcolor{...}{...}``. For a
    true Manim morph on a hero derivation, render offline and embed with
    :func:`video`.
    """
    import json
    import anywidget
    import traitlets

    norm = []
    for s in steps:
        if isinstance(s, (list, tuple)):
            norm.append({"tex": s[0], "note": s[1] if len(s) > 1 else ""})
        else:
            norm.append({"tex": s, "note": ""})

    _steps_json = json.dumps(norm)
    _ms = int(autoplay_ms)
    _title = title or ""

    class _Derivation(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) {
          var steps = []; try { steps = JSON.parse(model.get('steps')); } catch(e){}
          var ms = model.get('ms') || 1500;
          var ttl = model.get('title') || '';
          var i = 0, timer = null;
          var root = el.getRootNode();
          try { if (root.querySelector && !root.querySelector('link[data-mlkd]')) { var l=document.createElement('link'); l.rel='stylesheet'; l.href='https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css'; l.setAttribute('data-mlkd','1'); (root.head||root).appendChild(l); } } catch(e){}
          el.style.cssText='border:1px solid #e4e9f0;border-radius:10px;padding:14px 16px;background:#fff';
          var bs='padding:6px 12px;border:1px solid #c7d2e0;border-radius:8px;background:#f3f7fc;cursor:pointer;font:13px sans-serif;color:#2c3e50';
          el.innerHTML =
            (ttl?('<div style="font-weight:600;color:#2c3e50;margin-bottom:8px">'+ttl+'</div>'):'')+
            '<div class="ml-eq" style="min-height:52px;display:flex;align-items:center;justify-content:center;transition:opacity .22s"></div>'+
            '<div class="ml-note" style="text-align:center;color:#56636f;font:13px sans-serif;min-height:18px;margin-top:6px"></div>'+
            '<div style="display:flex;gap:8px;align-items:center;justify-content:center;margin-top:10px">'+
              '<button class="ml-prev" style="'+bs+'">\\u2039 Prev</button>'+
              '<button class="ml-play" style="'+bs+'">\\u25B6 Play</button>'+
              '<button class="ml-next" style="'+bs+'">Next \\u203A</button>'+
              '<span class="ml-ind" style="color:#7c8aa0;font:12px sans-serif;margin-left:6px"></span>'+
            '</div>';
          var eqEl=el.querySelector('.ml-eq'), noteEl=el.querySelector('.ml-note'), indEl=el.querySelector('.ml-ind'), playBtn=el.querySelector('.ml-play');
          function paint(){
            var s = steps[i] || {tex:'', note:''};
            try { eqEl.innerHTML = window.katex ? window.katex.renderToString(s.tex, {displayMode:true, throwOnError:false}) : s.tex; } catch(e){ eqEl.textContent = s.tex; }
            noteEl.textContent = s.note || '';
            indEl.textContent = (i+1)+' / '+steps.length;
            eqEl.style.opacity = 1;
          }
          function show(k){ i = Math.max(0, Math.min(steps.length-1, k)); eqEl.style.opacity=0; setTimeout(paint, 170); }
          function stop(){ if(timer){ clearInterval(timer); timer=null; playBtn.textContent='\\u25B6 Play'; } }
          function play(){ if(timer){ stop(); return; } playBtn.textContent='\\u275A\\u275A Pause'; if(i>=steps.length-1) show(0); timer=setInterval(function(){ if(i>=steps.length-1){ stop(); } else { show(i+1); } }, ms); }
          el.querySelector('.ml-prev').addEventListener('click', function(){ stop(); show(i-1); });
          el.querySelector('.ml-next').addEventListener('click', function(){ stop(); show(i+1); });
          playBtn.addEventListener('click', play);
          show(0);
        }
        export default { render };
        """
        steps = traitlets.Unicode(_steps_json).tag(sync=True)
        ms = traitlets.Int(_ms).tag(sync=True)
        title = traitlets.Unicode(_title).tag(sync=True)

    return mo.ui.anywidget(_Derivation())


def video(src, *, caption=None, width="100%"):
    """Embed a pre-rendered clip (e.g. a Manim derivation) from the site's assets.

    ``src`` is a filename under ``assets/`` (the build copies the repo's ``assets/``
    into ``site/assets/``); chapter pages live one level down, so the path resolves
    as ``../assets/<src>``.
    """
    cap = (f'<figcaption style="text-align:center;color:#56636f;font:13px sans-serif;'
           f'margin-top:6px">{caption}</figcaption>') if caption else ""
    return mo.Html(
        f'<figure style="margin:0">'
        f'<video controls loop muted playsinline preload="metadata" '
        f'style="width:{width};border-radius:8px;border:1px solid #e4e9f0" '
        f'src="../assets/{src}"></video>{cap}</figure>'
    )


def solve_steps(rhs_str, *, func="y", indep="t"):
    """Step-by-step reveal of solving a *separable* ``d{func}/d{indep} = rhs`` —
    the method ``dsolve`` hides. Returns an ``mo.accordion`` (separate variables →
    integrate both sides → solve). Best for autonomous rhs (depends on ``{func}``).
    """
    import sympy as sp

    t = sp.Symbol(indep)
    Y = sp.Symbol(func)
    f = sp.Function(func)
    try:
        rhs = sp.sympify(rhs_str, locals={func: Y, indep: t})
        _guard_expr(rhs)
    except Exception as exc:
        return mo.callout(mo.md(f"Let's keep it tame — try a simpler rate law.\n\n`{exc}`"), kind="warn")

    steps = {}
    steps["1 · The equation"] = mo.md(f"$$ \\frac{{d{func}}}{{d{indep}}} = {sp.latex(rhs)} $$")
    steps["2 · Separate the variables"] = mo.md(
        f"Gather every ${func}$ on the left and ${indep}$ on the right:\n\n"
        f"$$ \\frac{{d{func}}}{{{sp.latex(rhs)}}} = d{indep} $$"
    )
    try:
        lhs = sp.integrate(1 / rhs, Y)
        steps["3 · Integrate both sides"] = mo.md(
            f"$$ {sp.latex(lhs)} = {indep} + C $$"
        )
    except Exception:
        steps["3 · Integrate both sides"] = mo.md("This one's integral has no elementary closed form.")
    try:
        sol = sp.dsolve(sp.Eq(f(t).diff(t), rhs.subs(Y, f(t))), f(t))
        steps[f"4 · Solve for {func}({indep})"] = mo.md(f"$$ {sp.latex(sol)} $$")
    except Exception:
        steps[f"4 · Solve for {func}({indep})"] = mo.md("No explicit closed form for this one.")
    return mo.accordion(steps)


# --- tutor kit ----------------------------------------------------------------
# The BYO-key chat tutor, factored so each chapter wires it in ~6 one-line cells
# instead of duplicating the widget JS. The kernel runs in a Web Worker (no DOM /
# sessionStorage), so the key bridge and cell picker are main-thread anywidgets.

def key_field():
    """The BYO-key input (password); the value stays in the browser only."""
    return mo.ui.text(label="Anthropic key (stays in your browser)", kind="password", full_width=True)


def key_bridge_widget():
    """Hidden main-thread widget that reads/writes the shared sessionStorage key."""
    import anywidget
    import traitlets

    class _KeyBridge(anywidget.AnyWidget):
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

    return mo.ui.anywidget(_KeyBridge())


def cell_picker_widget():
    """Click-to-pick widget: the student clicks any chapter cell and its rendered
    text becomes context for the next tutor question."""
    import anywidget
    import traitlets

    class _CellPicker(anywidget.AnyWidget):
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

    return mo.ui.anywidget(_CellPicker())


def persist_key(api_field, key_bridge):
    """Persist a key typed in ``api_field`` to the shared slot via the bridge."""
    if api_field.value:
        key_bridge.widget.save_value = api_field.value


def tutor_chat(api_field, key_bridge, picker, context, *, prompts=None,
               model="claude-haiku-4-5-20251001"):
    """A BYO-key chat tutor (``mo.ui.chat``) wired to Claude client-side, with the
    chapter ``context`` and any picked-cell text folded into the system prompt."""
    import json

    system = (
        "You are a friendly, concise math tutor inside a marimo notebook. " + context
        + " Explain clearly in plain language and ALWAYS use LaTeX for math — inline "
        "$...$ and display $$...$$ (never write bare expressions). When code helps, you "
        "may include a ```python block using only mo, np, plt, go, delib. " + _DELIB_API
        + " The student can copy code into a practice cell to run it. Keep answers focused."
    )

    async def chat_model(messages, config):
        key = api_field.value or (key_bridge.value or {}).get("key", "")
        sys = system
        picked = (picker.value or {}).get("picked_text", "")
        if picked:
            sys += '\n\nThe student is asking about this cell:\n"""\n' + picked + '\n"""'
        msgs = [{"role": m.role, "content": m.content} for m in messages
                if m.role in ("user", "assistant") and m.content]
        body = json.dumps({"model": model, "max_tokens": 800, "system": sys, "messages": msgs})
        headers = {"content-type": "application/json", "x-api-key": key,
                   "anthropic-version": "2023-06-01",
                   "anthropic-dangerous-direct-browser-access": "true"}
        try:
            from pyodide.http import pyfetch

            resp = await pyfetch(_ANTHROPIC_URL, method="POST", headers=headers, body=body)
            data = await resp.json()
        except ModuleNotFoundError:
            import urllib.request
            import urllib.error

            req = urllib.request.Request(_ANTHROPIC_URL, data=body.encode(), headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req) as r:
                    data = json.loads(r.read().decode())
            except urllib.error.HTTPError as exc:
                data = json.loads(exc.read().decode())
        if not (isinstance(data, dict) and data.get("content")):
            return "**API error**\n\n```json\n" + json.dumps(data, indent=2)[:800] + "\n```"
        return "".join(b.get("text", "") for b in data["content"])

    return mo.ui.chat(chat_model, prompts=prompts or [])


def tutor_sidebar(api_field, key_bridge, picker, chatbox, *, title="Tutor"):
    """Render the tutor as a left sidebar: key field, then (once a key is set) the
    cell picker and chat; otherwise a prompt to add a key."""
    key_ok = bool(api_field.value or (key_bridge.value or {}).get("key"))
    items = [mo.md(f"### {title}"), key_bridge, api_field]
    if key_ok:
        items += [mo.md("key set ✓"), picker, chatbox]
    else:
        items.append(mo.callout(mo.md(
            "**Add your Anthropic API key** above to ask the tutor.\n\nNo key yet? "
            "Create one at [console.anthropic.com/settings/keys]"
            "(https://console.anthropic.com/settings/keys). It is stored only in this "
            "browser and sent only to Anthropic — never to this site."), kind="info"))
    return mo.sidebar(items, width="420px")
