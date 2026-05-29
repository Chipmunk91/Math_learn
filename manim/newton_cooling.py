"""Newton's law of cooling — full 4-operation solution, all manual.

ODE:  dT/dt = -k (T - T_r)  ->  T = T_r + A e^{-k t}

Every operation is per-atom (no TransformMatchingShapes): each glyph that
survives a step keeps the same mobject reference, so its path is deterministic
and the motion is one continuous, transparent transform — not a fade. Teal marks
the symbols being actively manipulated.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/newton_cooling.py SceneNewtonCoolingFull
    cp media/videos/newton_cooling/1080p60/SceneNewtonCoolingFull.mp4 \\
       assets/newton_cooling.mp4

Then it appears in ch02 via delib.video("newton_cooling.mp4").
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import *  # noqa: F403,E402
from derivation_kit import vinc, glyph, HIGHLIGHT  # noqa: E402


class SceneNewtonCoolingFull(Scene):
    def construct(self):
        # ---- registry: each leaf glyph is its own persistent mobject ----
        dT = glyph("dT")
        dt = glyph("dt", color=HIGHLIGHT)   # migrates in op 1; morphs to t in op 2
        eq = glyph("=")
        negk = glyph("-k")                  # rides into the exponent in op 3
        lp = glyph("(")
        Tv = glyph("T", color=HIGHLIGHT)
        mns = glyph("-", color=HIGHLIGHT)   # transmutes to + in op 4
        Tr = glyph("T_r", color=HIGHLIGHT)
        rp = glyph(")")
        bar = vinc(dT, dt)

        # ---- initial layout:  dT/dt = -k ( T - T_r ) ----
        bar.move_to(LEFT * 3.4)
        dT.next_to(bar, UP, buff=0.1)
        dt.next_to(bar, DOWN, buff=0.1)
        eq.next_to(bar, RIGHT, buff=0.5)
        negk.next_to(eq, RIGHT, buff=0.3)
        lp.next_to(negk, RIGHT, buff=0.12)
        Tv.next_to(lp, RIGHT, buff=0.08)
        mns.next_to(Tv, RIGHT, buff=0.15)
        Tr.next_to(mns, RIGHT, buff=0.15)
        rp.next_to(Tr, RIGHT, buff=0.08)
        self.play(Write(VGroup(dT, bar, dt, eq, negk, lp, Tv, mns, Tr, rp)))
        self.wait(0.5)

        # 1. SEPARATE:  dT/dt = -k(T - T_r)  ->  dT/(T - T_r) = -k dt
        new_bar = vinc(dT, VGroup(Tv, mns, Tr)).move_to(bar.get_center())
        Tv_t, mns_t, Tr_t = Tv.copy(), mns.copy(), Tr.copy()
        VGroup(Tv_t, mns_t, Tr_t).arrange(RIGHT, buff=0.15).next_to(new_bar, DOWN, buff=0.1)
        dT_t = dT.copy().next_to(new_bar, UP, buff=0.1)
        dt_t = dt.copy().next_to(negk, RIGHT, buff=0.22)
        self.play(
            Transform(bar, new_bar),
            Transform(dT, dT_t),
            Transform(dt, dt_t, path_arc=-PI / 2),
            Transform(Tv, Tv_t, path_arc=PI / 2),
            Transform(mns, mns_t, path_arc=PI / 2),
            Transform(Tr, Tr_t, path_arc=PI / 2),
            FadeOut(lp), FadeOut(rp),
            run_time=1.8,
        )
        self.wait(0.8)

        # 2a. INTEGRATE: integral signs emerge on both sides
        intL = MathTex(r"\int").scale(1.7).set_color(GREY_B)
        intR = MathTex(r"\int").scale(1.7).set_color(GREY_B)
        intL.next_to(VGroup(dT, bar, Tv, mns, Tr), LEFT, buff=0.15)
        intR.next_to(eq, RIGHT, buff=0.3)
        self.play(
            VGroup(negk, dt).animate.shift(RIGHT * 0.75),
            FadeIn(intL, shift=RIGHT * 0.2),
            FadeIn(intR, shift=RIGHT * 0.2),
            run_time=1.0,
        )
        self.wait(0.4)

        # 2b. evaluate: dT, bar, dt vanish; ln|..| on LHS; t and +C on RHS
        ln_t = MathTex(r"\ln").scale(1.3)
        absL = MathTex("|").scale(1.5)
        absR = MathTex("|").scale(1.5)
        Tv_e, mns_e, Tr_e = Tv.copy(), mns.copy(), Tr.copy()
        VGroup(ln_t, absL, Tv_e, mns_e, Tr_e, absR).arrange(RIGHT, buff=0.1).next_to(eq, LEFT, buff=0.4)
        negk_e = negk.copy().next_to(eq, RIGHT, buff=0.3)
        t_e = MathTex("t").scale(1.3).set_color(HIGHLIGHT).next_to(negk_e, RIGHT, buff=0.2)
        plus_e = MathTex("+").scale(1.3).next_to(t_e, RIGHT, buff=0.2)
        C_e = MathTex("C").scale(1.3).next_to(plus_e, RIGHT, buff=0.2)
        self.play(
            Transform(intL, ln_t),
            FadeOut(dT), FadeOut(bar),
            FadeIn(absL), FadeIn(absR),
            Transform(Tv, Tv_e),
            Transform(mns, mns_e),
            Transform(Tr, Tr_e),
            FadeOut(intR),
            Transform(negk, negk_e),
            Transform(dt, t_e),
            FadeIn(plus_e), FadeIn(C_e),
            run_time=1.8,
        )
        ln_ref = intL
        t_sym = dt
        self.wait(0.8)

        # 3. EXPONENTIATE: ln|T - T_r| = -kt + C  ->  T - T_r = A e^{-kt}
        Tv_x, mns_x, Tr_x = Tv.copy(), mns.copy(), Tr.copy()
        VGroup(Tv_x, mns_x, Tr_x).arrange(RIGHT, buff=0.15).next_to(eq, LEFT, buff=0.4)
        A_sym = MathTex("A").scale(1.3).next_to(eq, RIGHT, buff=0.3)
        e_sym = MathTex("e").scale(1.3).next_to(A_sym, RIGHT, buff=0.1)
        negk_exp = negk.copy().scale(0.7)
        t_exp = t_sym.copy().scale(0.7)
        exp_anchor = e_sym.get_corner(UR) + UP * 0.18 + RIGHT * 0.02
        negk_exp.move_to(exp_anchor)
        t_exp.next_to(negk_exp, RIGHT, buff=0.04)
        self.play(
            FadeOut(ln_ref), FadeOut(absL), FadeOut(absR),
            FadeOut(plus_e), FadeOut(C_e),
            Transform(Tv, Tv_x),
            Transform(mns, mns_x),
            Transform(Tr, Tr_x),
            FadeIn(A_sym, shift=LEFT * 0.15),
            FadeIn(e_sym, shift=LEFT * 0.15),
            Transform(negk, negk_exp),
            Transform(t_sym, t_exp, path_arc=-PI / 3),
            run_time=1.8,
        )
        self.wait(0.8)

        # 4. ISOLATE T: T - T_r = A e^{-kt}  ->  T = T_r + A e^{-kt}
        Tr_iso = Tr.copy().next_to(eq, RIGHT, buff=0.3)
        plus_iso = MathTex("+").scale(1.3).next_to(Tr_iso, RIGHT, buff=0.2)
        A_iso = A_sym.copy().next_to(plus_iso, RIGHT, buff=0.2)
        e_iso = e_sym.copy().next_to(A_iso, RIGHT, buff=0.1)
        exp_anchor2 = e_iso.get_corner(UR) + UP * 0.18 + RIGHT * 0.02
        negk_iso = negk.copy().move_to(exp_anchor2)
        t_iso = t_sym.copy().next_to(negk_iso, RIGHT, buff=0.04)
        self.play(
            Transform(mns, plus_iso, path_arc=-PI / 2),
            Transform(Tr, Tr_iso, path_arc=-PI / 2),
            Transform(A_sym, A_iso),
            Transform(e_sym, e_iso),
            Transform(negk, negk_iso),
            Transform(t_sym, t_iso),
            run_time=1.8,
        )
        self.wait(1.5)
        # Final:  T = T_r + A e^{-k t}
