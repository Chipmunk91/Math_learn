import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import plotly.graph_objects as go
    import sympy as sp

    import delib
    return delib, go, mo, np, sp


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Chapter 8 — Non-homogeneous equations

        **Same machinery, any push.**

        By the end of this chapter you should be able to:

        - Read the canonical second-order non-homogeneous form
          $y'' + p(x)\,y' + q(x)\,y = g(x)$ and split its solution as
          $y = y_h + y_p$ (homogeneous + particular).
        - Use **undetermined coefficients** to find a particular
          solution for the standard forcings (constant, polynomial,
          exponential, sinusoid, and sums of these); know the
          multiply-by-$x$ rescue when the trial form collides with a
          homogeneous solution.
        - Apply **variation of parameters** for any continuous
          forcing $g(x)$ — including ones the guess table can't
          touch — using the Wronskian formula.
        - Use **superposition** to handle a sum of forcings by
          solving each piece separately and adding the results.
        - Recognise the driven RLC circuit as the same equation as
          the driven spring, with $m \leftrightarrow L$,
          $c \leftrightarrow R$, $k \leftrightarrow 1/C$,
          $F \leftrightarrow V$.
        """
    )
    return


# === Section 1 — Hook: the driven RLC circuit =====================================
@app.cell(hide_code=True)
def _(mo):
    # TODO (user): opening animation for the driven RLC hook.
    # Story: a battery / AC source / arbitrary V(t) on an L-R-C loop;
    # charge q(t) on the capacitor obeys L q'' + R q' + (1/C) q = V(t).
    # The shape is identical to the driven spring of Ch 7 -- the bridge
    # the chapter rests on. Animation slot is here; replace this cell
    # (or vstack one below) when the asset is ready.
    mo.md(
        r"""
        ## Driving an RLC circuit

        > **🎬 Opening animation goes here** *(scaffold placeholder —
        > the chapter's hook is the driven RLC circuit, mirroring
        > Ch 7's swing).*

        Ch 7 drove a spring with a single cosine and chased the
        steady state. This chapter generalises in two directions:
        **any forcing** (not just a single sinusoid) and **a
        systematic method** for finding the particular response —
        with **superposition** stitching the answers back together
        when the forcing is a sum.

        The natural setting for "any forcing" is the **driven RLC
        circuit**: an inductor $L$, resistor $R$, and capacitor $C$
        in series, plus a voltage source $V(t)$ that you choose.
        Kirchhoff's voltage law gives

        $$
        L\, \ddot q + R\, \dot q + \frac{1}{C}\, q \;=\; V(t),
        $$

        where $q(t)$ is the charge on the capacitor. The equation
        has the **same shape** as Ch 7's spring — only the names
        change:

        | spring | circuit |
        |---|---|
        | mass $m$ | inductance $L$ |
        | damping $c$ | resistance $R$ |
        | spring stiffness $k$ | reciprocal capacitance $1/C$ |
        | external force $F(t)$ | source voltage $V(t)$ |

        Circuits are a good lab because $V(t)$ can naturally be **anything**:
        a battery (constant), a ramp, a decaying surge, an AC source
        (sinusoid), or — most importantly — a **sum** of these. Ch 7's
        cosine trick answered one of those cases; we need a system.
        """
    )
    return


# === Section 2 — Recall the split + name superposition ============================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## The split, named once and for all

        For any linear second-order non-homogeneous equation

        $$
        y'' + p(x)\, y' + q(x)\, y \;=\; g(x),
        $$

        the general solution is

        $$
        y(x) \;=\; \underbrace{y_h(x)}_{\text{homogeneous}}
        \;+\; \underbrace{y_p(x)}_{\text{particular}},
        $$

        where $y_h$ is *any* solution of the same equation with
        $g \equiv 0$ (Ch 6's territory: characteristic equation, two
        free constants set by initial conditions) and $y_p$ is *any
        one* solution of the full equation. The two free constants
        of $y_h$ are *all* the freedom — $y_p$ is determined by the
        forcing alone.

        > **Why this is allowed.** If $y_p$ solves the full equation
        > and $y_h$ solves the homogeneous one, then by linearity
        > $y_h + y_p$ also solves the full equation. We met exactly
        > this argument in Ch 7. The whole chapter is now about
        > **how to find one $y_p$**.

        ### Superposition: many forcings, one method

        Linearity gives us one more gift. If $g(x) = g_1(x) + g_2(x)$,
        find a particular solution $y_{p,1}$ for $g_1$ alone and a
        particular solution $y_{p,2}$ for $g_2$ alone. Then

        $$
        y_p \;=\; y_{p,1} + y_{p,2}
        $$

        solves the equation with the full $g$. So "a battery plus an
        AC source" splits into a battery problem plus an AC problem,
        each tackled with whichever method is easiest for that piece.
        """
    )
    return


# === Section 3 — Undetermined coefficients ========================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Method 1 — Undetermined coefficients (the guess table)

        For a small zoo of "nice" forcings $g(x)$, you can write down
        the *shape* of $y_p$ in advance and pin it down with algebra.
        That's exactly what Ch 7 did with $A\cos(\omega t - \varphi)$
        — now generalised and named.

        > **🚧 Placeholder.** The guess table, the worked RLC example
        > (battery + AC source via superposition), and the
        > **multiply-by-$x$ rescue** for the resonance overlap — the
        > general statement of Ch 7's $t\sin(\omega_0 t)$ disaster
        > — go here.

        Rough shape of the table:

        | $g(x)$ form | trial $y_p$ |
        |---|---|
        | polynomial of degree $n$ | polynomial of degree $n$ |
        | $e^{ax}$ | $C e^{ax}$ |
        | $\cos(bx)$ or $\sin(bx)$ | $A\cos(bx) + B\sin(bx)$ |
        | $e^{ax}\cos(bx)$ | $e^{ax}(A\cos(bx) + B\sin(bx))$ |
        | sum of the above | sum of the trials (superposition) |

        **Resonance rule.** If a piece of your trial $y_p$ is already
        a homogeneous solution, multiply that piece by $x$ (or $x^2$
        for a repeated overlap). Ch 7's $\gamma=0,\omega=\omega_0$
        case is the canonical example.
        """
    )
    return


# === Section 4 — Variation of parameters (the Manim hero + worked example) ========
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Method 2 — Variation of parameters

        When $g(x)$ is **not** in the guess table — like $g(x) =
        \sec x$, or a piecewise / table-defined input — undetermined
        coefficients can't help. Variation of parameters works for
        *any* continuous $g$. Trade-off: the guess table is quick;
        VoP always works but costs you two integrals.

        The idea: take the homogeneous basis $y_1, y_2$ (from Ch 6)
        and let the constants $C_1, C_2$ **vary with $x$**. Ask what
        $u_1(x), u_2(x)$ must be for $y_p = u_1 y_1 + u_2 y_2$ to
        solve the full equation. The Manim derives the formula in
        five steps; the headline is the **Wronskian** formula:

        $$
        \boxed{\;
        y_p(x) \;=\; -\, y_1(x)\!\int\! \frac{y_2(x)\, g(x)}{W(x)}\, dx
        \;+\; y_2(x)\!\int\! \frac{y_1(x)\, g(x)}{W(x)}\, dx,
        \qquad
        W \;=\; y_1 y_2' - y_2 y_1'.
        \;}
        $$
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    delib.video(
        "variation_of_parameters.mp4",
        caption="Variation of parameters: five-step derivation of the Wronskian formula",
        fallback="The variation-of-parameters Manim is being rendered "
                 "(see manim/variation_of_parameters.py).",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        > **🚧 Placeholder.** Worked VoP example goes here — pick a
        > $g(x)$ that the guess table genuinely can't touch (e.g.
        > $g = \sec x$, or a tabulated input), show the Wronskian
        > computation, the two integrals, and the resulting $y_p$.
        """
    )
    return


# === Section 5 — See it: the decomposition slider =================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## See it — the decomposition

        Below is the canonical split $x = x_h + x_p$ made visible.
        $x_h$ carries the **initial conditions** (drag $x_0$, $v_0$
        and only the top panel changes). $x_p$ carries the
        **forcing** (drag the source amplitudes / frequencies and
        only the middle panel changes). The full motion $x(t)$ at
        the bottom is their literal sum — the dotted ghosts behind
        it are the two components.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    fr8_panel = delib.param_panel([
        {"name": "omega0", "label": "natural freq.  ω₀",
         "start": 0.5, "stop": 3.0, "step": 0.1, "value": 1.5},
        {"name": "gamma", "label": "damping  γ",
         "start": 0.05, "stop": 1.0, "step": 0.05, "value": 0.2},
        {"name": "x0", "label": "initial x(0)",
         "start": -2.0, "stop": 2.0, "step": 0.1, "value": 1.0},
        {"name": "v0", "label": "initial ẋ(0)",
         "start": -2.0, "stop": 2.0, "step": 0.1, "value": 0.0},
        {"name": "F0", "label": "drive amplitude  F₀",
         "start": 0.0, "stop": 3.0, "step": 0.1, "value": 1.0},
        {"name": "omega", "label": "drive freq.  ω",
         "start": 0.0, "stop": 3.0, "step": 0.1, "value": 1.5},
    ])
    return (fr8_panel,)


@app.cell(hide_code=True)
def _(delib, fr8_panel, mo, np):
    _v = fr8_panel.value
    _omega0 = float(_v["omega0"])
    _gamma  = float(_v["gamma"])
    _x0     = float(_v["x0"])
    _v0_    = float(_v["v0"])
    _F0     = float(_v["F0"])
    _omega  = float(_v["omega"])

    _fig = delib.forced_response(
        _omega0, _gamma,
        lambda t: _F0 * np.cos(_omega * t),
        ic=(_x0, _v0_), t_end=30.0, n=600,
        title=f"x = x_h + x_p   ω₀={_omega0:.2f}, γ={_gamma:.2f}, "
              f"x₀={_x0:.2f}, ẋ₀={_v0_:.2f},  F₀cos(ωt) with F₀={_F0:.2f}, ω={_omega:.2f}",
        forcing_label="F₀ cos(ω t)",
    )
    mo.vstack([fr8_panel, _fig])
    return


# === Section 6 — Try it (3 graded exercises) ======================================

# --- Challenge 1: pick the right trial form -------------------------------------
@app.cell
def _(mo):
    # TODO: refine prompt + check once Section 3's table is filled in.
    e1_get, e1_set = mo.state(
        "# For  y'' + 4y = 3 e^{2x},  the standard trial form is\n"
        "# y_p = C e^{2x}. Substitute and solve for C.\n"
        "# Hint: 4 C e^{2x} (second derivative) + 4 C e^{2x} = 3 e^{2x},\n"
        "# so 8 C = 3 -> C = 3/8 = 0.375.\n"
        "# Put C in `answer`.\n"
        "answer = ...\n"
    )
    return e1_get, e1_set


@app.cell
def _(delib, e1_get):
    e1_ai, e1_gen, e1_code, e1_run = delib.exercise_inputs(e1_get())
    return e1_ai, e1_code, e1_gen, e1_run


@app.cell
async def _(api_field, delib, e1_ai, e1_code, e1_gen, e1_set, key_bridge):
    await delib.exercise_ai(
        e1_gen, e1_ai, e1_code, e1_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="The forcing is 3 e^{2x}. Trial: y_p = C e^{2x}. "
                "Then y_p'' = 4 C e^{2x}. Substitute: 4 C e^{2x} + "
                "4 C e^{2x} = 3 e^{2x} -> 8 C = 3 -> C = 0.375. "
                "Put 0.375 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_ai, e1_code, e1_gen, e1_run):
    delib.exercise_view(
        "**1.** For $y'' + 4y = 3\\, e^{2x}$, find the coefficient $C$ "
        "in the particular solution $y_p = C\\, e^{2x}$.",
        e1_ai, e1_gen, e1_code, e1_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_code, e1_run):
    delib.run_exercise(e1_code.value, e1_run.value, check=lambda ns: delib.check_number(
        ns, target=0.375, tol=0.005,
        ok="Right — $y_p'' + 4 y_p = (4C + 4C) e^{2x} = 8C e^{2x} = "
           "3 e^{2x}$, so $C = 3/8 = 0.375$.",
        hint="Differentiate the trial twice, substitute into the LHS, "
             "match the coefficient of $e^{2x}$ on both sides.",
    ))
    return


# --- Challenge 2: superposition --------------------------------------------------
@app.cell
def _(mo):
    e2_get, e2_set = mo.state(
        "# For  y'' - y = 6 + e^{2x},  superposition says split the\n"
        "# forcing: y_p = y_{p,1} + y_{p,2} with\n"
        "#   y_{p,1} solves y'' - y = 6    (constant; try y_{p,1} = A)\n"
        "#   y_{p,2} solves y'' - y = e^{2x}  (try y_{p,2} = B e^{2x})\n"
        "# Compute y_p(0) = A + B.\n"
        "# Put the answer in `answer`.\n"
        "answer = ...\n"
    )
    return e2_get, e2_set


@app.cell
def _(delib, e2_get):
    e2_ai, e2_gen, e2_code, e2_run = delib.exercise_inputs(e2_get())
    return e2_ai, e2_code, e2_gen, e2_run


@app.cell
async def _(api_field, delib, e2_ai, e2_code, e2_gen, e2_set, key_bridge):
    await delib.exercise_ai(
        e2_gen, e2_ai, e2_code, e2_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="Piece 1: y'' - y = 6, try y = A constant. Then "
                "y'' = 0 so -A = 6 -> A = -6. "
                "Piece 2: y'' - y = e^{2x}, try y = B e^{2x}. Then "
                "y'' = 4B e^{2x} so 4B - B = 1 -> B = 1/3. "
                "y_p(0) = -6 + 1/3 = -17/3 ~= -5.6667. "
                "Put -5.6667 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_ai, e2_code, e2_gen, e2_run):
    delib.exercise_view(
        "**2.** Use superposition: for $y'' - y = 6 + e^{2x}$, find "
        "$y_p(0)$.",
        e2_ai, e2_gen, e2_code, e2_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_code, e2_run):
    delib.run_exercise(e2_code.value, e2_run.value, check=lambda ns: delib.check_number(
        ns, target=-17/3, tol=0.01,
        ok="Right — constant piece: $-A = 6 \\Rightarrow A = -6$; "
           "exponential piece: $4B - B = 1 \\Rightarrow B = 1/3$; "
           "$y_p(0) = A + B = -17/3 \\approx -5.667$.",
        hint="Solve each forcing piece separately, then add the two "
             "particular solutions. Evaluate the sum at $x = 0$.",
    ))
    return


# --- Challenge 3: variation of parameters (Wronskian) ----------------------------
@app.cell
def _(mo):
    e3_get, e3_set = mo.state(
        "# For  y'' + y = 0,  a homogeneous basis is\n"
        "#   y_1 = cos(x),  y_2 = sin(x).\n"
        "# Compute the Wronskian W(x) = y_1 y_2' - y_2 y_1'.\n"
        "# (For sin/cos, this should be a constant.)\n"
        "# Put W in `answer`.\n"
        "answer = ...\n"
    )
    return e3_get, e3_set


@app.cell
def _(delib, e3_get):
    e3_ai, e3_gen, e3_code, e3_run = delib.exercise_inputs(e3_get())
    return e3_ai, e3_code, e3_gen, e3_run


@app.cell
async def _(api_field, delib, e3_ai, e3_code, e3_gen, e3_set, key_bridge):
    await delib.exercise_ai(
        e3_gen, e3_ai, e3_code, e3_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="y_1 = cos x, y_2 = sin x. Then y_1' = -sin x, "
                "y_2' = cos x. W = y_1 y_2' - y_2 y_1' = "
                "cos(x) cos(x) - sin(x) (-sin x) = cos^2 + sin^2 = 1. "
                "Put 1 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_ai, e3_code, e3_gen, e3_run):
    delib.exercise_view(
        "**3.** For $y'' + y = g(x)$, the homogeneous basis is "
        "$y_1 = \\cos x$, $y_2 = \\sin x$. Compute the Wronskian "
        "$W = y_1 y_2' - y_2 y_1'$.",
        e3_ai, e3_gen, e3_code, e3_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_code, e3_run):
    delib.run_exercise(e3_code.value, e3_run.value, check=lambda ns: delib.check_number(
        ns, target=1.0, tol=0.001,
        ok="Right — $W = \\cos(x)\\cos(x) - \\sin(x)(-\\sin x) = "
           "\\cos^2 + \\sin^2 = 1$. The Wronskian is identically $1$, "
           "which makes the VoP integrals especially clean for this basis.",
        hint="Plug in $y_1' = -\\sin x$ and $y_2' = \\cos x$, then use "
             "$\\cos^2 + \\sin^2 = 1$.",
    ))
    return


# === Section 7 — Recap & what's next ==============================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---
        ## Recap & what's next

        - **The split.** For a linear non-homogeneous equation,
          $y = y_h + y_p$. The freedom (two constants from initial
          conditions) lives entirely in $y_h$; $y_p$ is determined
          by the forcing.
        - **Superposition.** Sum of forcings → sum of particular
          responses. Solve each piece with whichever method is
          easiest, add at the end.
        - **Undetermined coefficients** — fast, mechanical, works
          for polynomials / exponentials / sinusoids / sums.
          Resonance overlap: multiply by $x$.
        - **Variation of parameters** — slower (two integrals) but
          works for any continuous $g(x)$.
        - **Same equation, many worlds.** Spring, RLC, and many
          other linear oscillators all wear this form; once you
          know the method, you know all of them.

        **Next.** Chapter 9 introduces the **Laplace transform** —
        the natural tool for *switched* and *impulse* inputs (a
        battery flipping on at $t = 1\,\text{s}$, a sudden kick) —
        which UC and VoP handle awkwardly. Laplace turns the ODE
        itself into an algebraic equation in $s$, and the
        characteristic-equation "guessed" exponentials of Ch 6
        reappear as the **poles** of a transfer function.
        """
    )
    return


# --- Tutor (BYO-key chat, from delib) -------------------------------------------
@app.cell
def _(delib):
    key_bridge = delib.key_bridge_widget()
    return (key_bridge,)


@app.cell
def _(delib):
    api_field = delib.key_field()
    return (api_field,)


@app.cell
def _(api_field, delib, key_bridge):
    delib.persist_key(api_field, key_bridge)
    return


@app.cell
def _(delib):
    picker = delib.cell_picker_widget()
    return (picker,)


@app.cell
def _(mo):
    picked_get, picked_set = mo.state({"text": "", "title": ""})
    return picked_get, picked_set


@app.cell
def _(picked_set, picker):
    _val = picker.value or {}
    picked_set({"text": _val.get("picked_text", ""),
                "title": _val.get("picked_title", "")})
    return


@app.cell
def _(api_field, delib, key_bridge, picked_get):
    chatbox = delib.tutor_chat(
        api_field, key_bridge,
        "This is Chapter 8 of a differential-equations course: "
        "non-homogeneous second-order linear equations of the form "
        "y'' + p(x) y' + q(x) y = g(x). The story is built around "
        "the driven RLC circuit, L q'' + R q' + (1/C) q = V(t), "
        "shown as the electrical mirror of Ch 7's driven spring "
        "(m <-> L, c <-> R, k <-> 1/C, F <-> V). Key ideas: the "
        "general solution splits as y = y_h + y_p with y_h handling "
        "initial conditions and y_p set entirely by the forcing; "
        "linearity gives superposition (sum of forcings -> sum of "
        "particulars); undetermined coefficients (guess-and-match) "
        "works for polynomials / exponentials / sinusoids / sums, "
        "with the multiply-by-x rescue when the trial collides with "
        "a homogeneous solution (the Ch 7 gamma=0 resonance case is "
        "the canonical example); variation of parameters handles ANY "
        "continuous g(x) via the Wronskian formula y_p = -y_1 int "
        "(y_2 g / W) dx + y_2 int (y_1 g / W) dx, derived in the "
        "chapter's Manim. Ch 9 next: Laplace transforms for switched / "
        "impulse inputs.",
        prompts=[
            "explain this chapter in a paragraph",
            "when should I use UC vs variation of parameters?",
            "why does the multiply-by-x trick work at resonance?",
        ],
        picked_get=picked_get,
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge, picker):
    delib.tutor_sidebar(api_field, key_bridge, chatbox, picker=picker)
    return


# --- Feedback ------------------------------------------------------------------
@app.cell(hide_code=True)
def _(delib):
    delib.feedback_form("Chapter 8 — Non-homogeneous equations")
    return


if __name__ == "__main__":
    app.run()
