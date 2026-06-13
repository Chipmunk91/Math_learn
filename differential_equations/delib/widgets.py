"""Interactive game-style widgets (anywidget) graduated from the Lab.

These are the demos from ``ch99_animation_lab.py`` that earned a place in a
real chapter, refactored into parametrised factory functions so the same
widget can be configured per chapter and so there is a single source of
truth (the Lab calls these too).

Each factory returns an ``mo.ui.anywidget(...)`` ready to render. The
physics constants are passed in as traitlets and read JS-side via
``model.get(...)``; everything else (RK4 integration, drawing, audio,
GSAP timeline) runs client-side at 60 fps with no Python in the loop.

- :func:`spring_grab` — drag a damped spring-mass to set its initial
  condition, flick it to set velocity. Canvas 2D, RK4. (Ch 6.)
- :func:`resonance_audio` — sweep the drive frequency and *hear* the
  steady-state amplitude ``A(omega)``. Web Audio. (Ch 7.)
- :func:`solution_anatomy` — a four-act GSAP choreography of the
  transient + steady-state split ``x = x_h + x_p``. (Ch 7.)
- :func:`feedback_form` — a star + comment box that posts to a Google
  Form (anonymous, lands in a Sheet you own). Replaces the per-chapter
  playground.
"""

from __future__ import annotations

__all__ = ["spring_grab", "resonance_audio", "solution_anatomy",
           "feedback_form"]

# --- Google Form feedback wiring --------------------------------------------
# Fill these four in ONCE after creating the feedback Google Form (see
# AUTHORING.md → "Feedback form setup"). Until GFORM_ACTION is set, the
# widget renders a polite "being set up" placeholder instead of posting
# nowhere, so the site is safe to ship before the form exists.
GFORM_ACTION = ""          # "https://docs.google.com/forms/d/e/<ID>/formResponse"
GFORM_ENTRY_RATING = ""    # "entry.<NNN>"  — the 1–5 rating field
GFORM_ENTRY_COMMENT = ""   # "entry.<NNN>"  — the paragraph/comment field
GFORM_ENTRY_CHAPTER = ""   # "entry.<NNN>"  — the (auto-filled) chapter field
GFORM_VIEW_URL = ""        # optional "…/viewform" for a fallback link


# ---------------------------------------------------------------------------
# 1. Grabbable damped spring-mass (Canvas 2D + RK4)
# ---------------------------------------------------------------------------

def spring_grab(omega0: float = 2.0, gamma: float = 0.15):
    """A draggable damped spring-mass: ``x'' = -omega0^2 x - 2 gamma x'``.

    Drag the mass sideways to set its position; flick and release to give
    it a velocity. Two sliders retune the stiffness and damping live. The
    initial slider positions come from ``omega0`` and ``gamma``.
    """
    import marimo as mo
    import anywidget
    import traitlets

    class _SpringGrab(anywidget.AnyWidget):
        _esm = r"""
        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <canvas style="width:100%;max-width:680px;border:1px solid #dde4ec;border-radius:8px;background:#fff;touch-action:none;cursor:grab"></canvas>
              <div style="display:flex;gap:18px;margin-top:6px;flex-wrap:wrap">
                <label>stiffness ω₀ <input type="range" min="0.5" max="4" step="0.1" data-k="w0"> <span data-v="w0"></span></label>
                <label>damping γ <input type="range" min="0" max="1" step="0.02" data-k="g"> <span data-v="g"></span></label>
              </div>
            </div>`;
          var canvas = el.querySelector('canvas');
          var W = 680, H = 300, dpr = window.devicePixelRatio || 1;
          canvas.width = W * dpr; canvas.height = H * dpr;
          var ctx = canvas.getContext('2d');
          ctx.scale(dpr, dpr);

          var w0 = model.get('init_w0'), g = model.get('init_g');
          var x = 0.9, v = 0;                  // physical units
          var dragging = false, lastPx = 0, lastT = 0, dragV = 0;
          var anchorX = 60, eqX = W * 0.55, scale = 180;  // px per unit
          var hist = [];

          // seed slider positions + labels from the factory defaults
          var sw0 = el.querySelector('[data-k="w0"]'); sw0.value = w0;
          el.querySelector('[data-v="w0"]').textContent = w0.toFixed(2);
          var sg = el.querySelector('[data-k="g"]'); sg.value = g;
          el.querySelector('[data-v="g"]').textContent = g.toFixed(2);

          el.querySelectorAll('input').forEach(function (inp) {
            inp.addEventListener('input', function () {
              var val = parseFloat(inp.value);
              if (inp.dataset.k === 'w0') w0 = val; else g = val;
              el.querySelector('[data-v="' + inp.dataset.k + '"]').textContent = val.toFixed(2);
            });
          });

          function massPx() { return eqX + x * scale; }

          canvas.addEventListener('pointerdown', function (e) {
            var r = canvas.getBoundingClientRect();
            var px = (e.clientX - r.left) * (W / r.width);
            if (Math.abs(px - massPx()) < 46) {
              dragging = true; canvas.setPointerCapture(e.pointerId);
              canvas.style.cursor = 'grabbing';
              lastPx = px; lastT = performance.now(); dragV = 0;
            }
          });
          canvas.addEventListener('pointermove', function (e) {
            if (!dragging) return;
            var r = canvas.getBoundingClientRect();
            var px = (e.clientX - r.left) * (W / r.width);
            px = Math.max(anchorX + 40, Math.min(W - 30, px));
            var now = performance.now(), dt = (now - lastT) / 1000;
            if (dt > 0.001) dragV = 0.7 * dragV + 0.3 * ((px - lastPx) / scale) / dt;
            lastPx = px; lastT = now;
            x = (px - eqX) / scale; v = 0;
          });
          function endDrag() {
            if (!dragging) return;
            dragging = false; canvas.style.cursor = 'grab';
            v = Math.max(-6, Math.min(6, dragV));
          }
          canvas.addEventListener('pointerup', endDrag);
          canvas.addEventListener('pointercancel', endDrag);

          function acc(x_, v_) { return -w0 * w0 * x_ - 2 * g * v_; }
          function step(dt) {
            var k1x = v,                 k1v = acc(x, v);
            var k2x = v + dt/2 * k1v,    k2v = acc(x + dt/2 * k1x, v + dt/2 * k1v);
            var k3x = v + dt/2 * k2v,    k3v = acc(x + dt/2 * k2x, v + dt/2 * k2v);
            var k4x = v + dt * k3v,      k4v = acc(x + dt * k3x, v + dt * k3v);
            x += dt/6 * (k1x + 2*k2x + 2*k3x + k4x);
            v += dt/6 * (k1v + 2*k2v + 2*k3v + k4v);
          }

          function spring(ctx, x0, y0, x1, y1, coils) {
            ctx.beginPath(); ctx.moveTo(x0, y0);
            var dx = (x1 - x0) / (coils * 2);
            for (var i = 1; i < coils * 2; i++)
              ctx.lineTo(x0 + dx * i, y0 + (i % 2 === 1 ? -14 : 14));
            ctx.lineTo(x1, y1); ctx.stroke();
          }

          var raf, running = true;
          function frame() {
            if (!running) return;
            if (!dragging) { step(1/120); step(1/120); }
            hist.push(x); if (hist.length > 360) hist.shift();

            ctx.clearRect(0, 0, W, H);
            ctx.fillStyle = '#7c8aa0';
            ctx.fillRect(anchorX - 10, 60, 10, 110);
            ctx.strokeStyle = '#c9d4e0'; ctx.setLineDash([4, 4]);
            ctx.beginPath(); ctx.moveTo(eqX, 50); ctx.lineTo(eqX, 185); ctx.stroke();
            ctx.setLineDash([]);
            ctx.strokeStyle = '#5b7db1'; ctx.lineWidth = 2.5;
            spring(ctx, anchorX, 115, massPx() - 24, 115, 9);
            ctx.fillStyle = dragging ? '#a13648' : '#d1495b';
            ctx.beginPath(); ctx.arc(massPx(), 115, 24, 0, 6.2832); ctx.fill();
            ctx.strokeStyle = '#5b7db1'; ctx.lineWidth = 1.6;
            ctx.beginPath();
            for (var i = 0; i < hist.length; i++) {
              var sx = 30 + (W - 60) * i / 360;
              var sy = 245 - hist[i] * 32;
              if (i === 0) ctx.moveTo(sx, sy); else ctx.lineTo(sx, sy);
            }
            ctx.stroke();
            ctx.strokeStyle = '#e3e9f0';
            ctx.beginPath(); ctx.moveTo(30, 245); ctx.lineTo(W - 30, 245); ctx.stroke();
            ctx.fillStyle = '#8a96a5'; ctx.font = '11px sans-serif';
            ctx.fillText('x(t)', 30, 215);

            raf = requestAnimationFrame(frame);
          }
          frame();
          return function () { running = false; cancelAnimationFrame(raf); };
        }
        export default { render };
        """
        init_w0 = traitlets.Float(2.0).tag(sync=True)
        init_g = traitlets.Float(0.15).tag(sync=True)

    return mo.ui.anywidget(_SpringGrab(init_w0=float(omega0), init_g=float(gamma)))


# ---------------------------------------------------------------------------
# 2. Audible resonance curve (Web Audio API)
# ---------------------------------------------------------------------------

def resonance_audio(omega0: float = 2.0, gamma: float = 0.15, F0: float = 1.0):
    """Sweep the drive frequency and *hear* the steady-state amplitude.

    The oscillator's pitch tracks the drive frequency ``omega``; its
    loudness tracks ``A(omega) = F0 / sqrt((omega0^2 - omega^2)^2 +
    (2 gamma omega)^2)``. Sweep through ``omega0`` and the system sings.
    """
    import marimo as mo
    import anywidget
    import traitlets

    class _ResonanceAudio(anywidget.AnyWidget):
        _esm = r"""
        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <canvas style="width:100%;max-width:680px;border:1px solid #dde4ec;border-radius:8px;background:#fff"></canvas>
              <div style="display:flex;gap:18px;margin-top:6px;align-items:center;flex-wrap:wrap">
                <button data-b="snd" style="padding:6px 14px;border:1px solid #c7d2e0;border-radius:6px;background:#f3f7fc;cursor:pointer">🔊 enable sound</button>
                <label>drive ω <input type="range" step="0.02" data-k="om"> <span data-v="om"></span></label>
                <label>damping γ <input type="range" min="0.05" max="0.8" step="0.01" data-k="g"> <span data-v="g"></span></label>
              </div>
            </div>`;
          var canvas = el.querySelector('canvas');
          var W = 680, H = 260, dpr = window.devicePixelRatio || 1;
          canvas.width = W * dpr; canvas.height = H * dpr;
          var ctx2d = canvas.getContext('2d'); ctx2d.scale(dpr, dpr);

          var w0 = model.get('init_w0'), F0 = model.get('init_F0');
          var g = model.get('init_g');
          var wMax = w0 * 2.25;
          var om = 0.5 * w0;            // start below resonance (quiet)
          var audio = null, osc = null, gain = null;

          // seed sliders + labels
          var sOm = el.querySelector('[data-k="om"]');
          sOm.min = 0.2; sOm.max = wMax.toFixed(2); sOm.value = om;
          el.querySelector('[data-v="om"]').textContent = om.toFixed(2);
          var sG = el.querySelector('[data-k="g"]'); sG.value = g;
          el.querySelector('[data-v="g"]').textContent = g.toFixed(2);

          function A(w) {
            var d1 = w0 * w0 - w * w, d2 = 2 * g * w;
            return F0 / Math.sqrt(d1 * d1 + d2 * d2);
          }
          function Amax() { return A(Math.sqrt(Math.max(0.01, w0*w0 - 2*g*g))); }

          el.querySelector('[data-b="snd"]').addEventListener('click', function () {
            if (audio) {
              osc.stop(); audio.close(); audio = null;
              this.textContent = '🔊 enable sound'; return;
            }
            audio = new (window.AudioContext || window.webkitAudioContext)();
            osc = audio.createOscillator(); gain = audio.createGain();
            osc.type = 'sine';
            osc.connect(gain); gain.connect(audio.destination);
            gain.gain.value = 0; osc.start();
            this.textContent = '🔇 mute';
            update();
          });

          function update() {
            el.querySelector('[data-v="om"]').textContent = om.toFixed(2);
            el.querySelector('[data-v="g"]').textContent = g.toFixed(2);
            if (audio) {
              var t = audio.currentTime;
              osc.frequency.linearRampToValueAtTime(120 + 130 * om, t + 0.05);
              var vol = 0.45 * A(om) / Amax();
              gain.gain.linearRampToValueAtTime(Math.min(0.45, vol), t + 0.05);
            }
            draw();
          }
          el.querySelectorAll('input').forEach(function (inp) {
            inp.addEventListener('input', function () {
              var val = parseFloat(inp.value);
              if (inp.dataset.k === 'om') om = val; else g = val;
              update();
            });
          });

          function draw() {
            ctx2d.clearRect(0, 0, W, H);
            var L = 50, R = W - 20, T = 20, B = H - 35;
            var aMax = Amax() * 1.1;
            ctx2d.strokeStyle = '#c9d4e0';
            ctx2d.beginPath(); ctx2d.moveTo(L, T); ctx2d.lineTo(L, B); ctx2d.lineTo(R, B); ctx2d.stroke();
            var x0px = L + (R - L) * w0 / wMax;
            ctx2d.setLineDash([4, 4]); ctx2d.strokeStyle = '#9aa7b5';
            ctx2d.beginPath(); ctx2d.moveTo(x0px, T); ctx2d.lineTo(x0px, B); ctx2d.stroke();
            ctx2d.setLineDash([]);
            ctx2d.fillStyle = '#8a96a5'; ctx2d.font = '11px sans-serif';
            ctx2d.fillText('ω₀', x0px + 4, T + 12);
            ctx2d.strokeStyle = '#5b7db1'; ctx2d.lineWidth = 2.5;
            ctx2d.beginPath();
            for (var i = 0; i <= 300; i++) {
              var w = wMax * i / 300;
              var px = L + (R - L) * i / 300;
              var py = B - (B - T) * A(w) / aMax;
              if (i === 0) ctx2d.moveTo(px, py); else ctx2d.lineTo(px, py);
            }
            ctx2d.stroke();
            var mr = 6 + 14 * A(om) / Amax();
            var mx = L + (R - L) * om / wMax;
            var my = B - (B - T) * A(om) / aMax;
            ctx2d.fillStyle = audio ? '#d1495b' : '#c9a0a8';
            ctx2d.beginPath(); ctx2d.arc(mx, my, mr, 0, 6.2832); ctx2d.fill();
            ctx2d.fillStyle = '#666'; ctx2d.font = '12px sans-serif';
            ctx2d.fillText('drive frequency ω →', W / 2 - 50, H - 10);
            ctx2d.save(); ctx2d.translate(16, H / 2); ctx2d.rotate(-Math.PI / 2);
            ctx2d.fillText('A(ω)', -16, 0); ctx2d.restore();
          }
          draw();
          return function () { if (audio) { osc.stop(); audio.close(); } };
        }
        export default { render };
        """
        init_w0 = traitlets.Float(2.0).tag(sync=True)
        init_g = traitlets.Float(0.15).tag(sync=True)
        init_F0 = traitlets.Float(1.0).tag(sync=True)

    return mo.ui.anywidget(_ResonanceAudio(
        init_w0=float(omega0), init_g=float(gamma), init_F0=float(F0)))


# ---------------------------------------------------------------------------
# 3. Transient + steady-state choreography (GSAP timeline)
# ---------------------------------------------------------------------------

def solution_anatomy(omega0: float = 2.0, gamma: float = 0.25,
                     omega: float = 1.2, F0: float = 1.0):
    """A four-act choreography of ``x(t) = x_h(t) + x_p(t)``.

    The full solution draws in, splits into its transient and steady-state
    components, the transient fades to nothing under a sweeping time
    cursor, and the steady state returns alone. Curves precomputed by RK4
    in JS from the four constants; GSAP choreographs the narrative.
    """
    import marimo as mo
    import anywidget
    import traitlets

    class _SolutionAnatomy(anywidget.AnyWidget):
        _esm = r"""
        import { gsap } from "https://esm.sh/gsap@3.12.5";

        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <div data-r style="width:100%;max-width:680px;border:1px solid #dde4ec;border-radius:8px;background:#fff;overflow:hidden"></div>
              <div style="display:flex;gap:14px;margin-top:6px;align-items:center;flex-wrap:wrap">
                <button data-b style="padding:6px 14px;border:1px solid #c7d2e0;border-radius:6px;background:#f3f7fc;cursor:pointer">▶ play the story</button>
                <input type="range" min="0" max="1" step="0.001" value="0" style="flex:1;min-width:200px" data-k="scrub">
                <span data-v="act" style="color:#7c8aa0;min-width:150px"></span>
              </div>
            </div>`;
          var host = el.querySelector('[data-r]');
          var W = host.clientWidth || 680, H = 380;

          var w0 = model.get('init_w0'), g = model.get('init_g');
          var om = model.get('init_om'), F0 = model.get('init_F0');
          var T = 22, N = 440, dt = T / N;
          var den = Math.sqrt(Math.pow(w0*w0 - om*om, 2) + Math.pow(2*g*om, 2));
          var A = F0 / den, phi = Math.atan2(2*g*om, w0*w0 - om*om);
          var xs = [], hs = [], ps = [];
          var x = 0, v = 0;
          function acc(t, x_, v_) {
            return F0 * Math.cos(om * t) - 2*g*v_ - w0*w0*x_;
          }
          for (var i = 0; i <= N; i++) {
            var t = i * dt;
            var p = A * Math.cos(om * t - phi);
            xs.push(x); ps.push(p); hs.push(x - p);
            var k1x = v,            k1v = acc(t, x, v);
            var k2x = v + dt/2*k1v, k2v = acc(t + dt/2, x + dt/2*k1x, v + dt/2*k1v);
            var k3x = v + dt/2*k2v, k3v = acc(t + dt/2, x + dt/2*k2x, v + dt/2*k2v);
            var k4x = v + dt*k3v,   k4v = acc(t + dt, x + dt*k3x, v + dt*k3v);
            x += dt/6*(k1x + 2*k2x + 2*k3x + k4x);
            v += dt/6*(k1v + 2*k2v + 2*k3v + k4v);
          }
          // scale so the full solution fills the frame nicely
          var peak = 0;
          for (var i = 0; i <= N; i++) peak = Math.max(peak, Math.abs(xs[i]));
          var sc = (H * 0.30) / (peak || 1);
          function path(arr, y0) {
            var d = '';
            for (var i = 0; i <= N; i++) {
              var px = 40 + (W - 80) * i / N;
              var py = y0 - arr[i] * sc;
              d += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + py.toFixed(1);
            }
            return d;
          }

          var NS = 'http://www.w3.org/2000/svg';
          var svg = document.createElementNS(NS, 'svg');
          svg.setAttribute('width', W); svg.setAttribute('height', H);
          host.appendChild(svg);
          function mkPath(d, color, width) {
            var p = document.createElementNS(NS, 'path');
            p.setAttribute('d', d); p.setAttribute('stroke', color);
            p.setAttribute('stroke-width', width); p.setAttribute('fill', 'none');
            svg.appendChild(p); return p;
          }
          function mkText(s, x_, y_, color) {
            var t = document.createElementNS(NS, 'text');
            t.setAttribute('x', x_); t.setAttribute('y', y_);
            t.setAttribute('fill', color); t.setAttribute('font-size', '13');
            t.textContent = s; t.setAttribute('opacity', 0);
            svg.appendChild(t); return t;
          }

          var mid = H / 2;
          var fullP  = mkPath(path(xs, mid), '#5b7db1', 3);
          var transP = mkPath(path(hs, mid), '#b5651d', 2.2);
          var stdyP  = mkPath(path(ps, mid), '#2a9d8f', 2.2);
          var fullL  = mkText('x(t) — the full solution', 44, 34, '#5b7db1');
          var transL = mkText('x_h — transient (Ch 6, dies)', 44, 34, '#b5651d');
          var stdyL  = mkText('x_p — steady state (locked to the drive)', 44, 34, '#2a9d8f');
          var cursor = document.createElementNS(NS, 'line');
          cursor.setAttribute('y1', 24); cursor.setAttribute('y2', H - 16);
          cursor.setAttribute('x1', 40); cursor.setAttribute('x2', 40);
          cursor.setAttribute('stroke', '#9aa7b5'); cursor.setAttribute('stroke-width', 1.4);
          cursor.setAttribute('opacity', 0);
          svg.appendChild(cursor);

          var len = fullP.getTotalLength();
          gsap.set(fullP, { strokeDasharray: len, strokeDashoffset: len });
          gsap.set([transP, stdyP], { opacity: 0 });
          gsap.set(fullL, { opacity: 0 });

          var actEl = el.querySelector('[data-v="act"]');
          function act(s) { return function () { actEl.textContent = s; }; }

          var tl = gsap.timeline({ paused: true });
          tl.call(act('act 1 · the full solution'))
            .to(fullP, { strokeDashoffset: 0, duration: 2.2, ease: 'power1.inOut' })
            .to(fullL, { opacity: 1, duration: 0.4 }, '<0.8')
            .to({}, { duration: 0.6 });
          tl.call(act('act 2 · split into x_h + x_p'))
            .to([transP, stdyP], { opacity: 1, duration: 0.5 })
            .to(transP, { y: -105, duration: 1.1, ease: 'power2.inOut' }, '<')
            .to(stdyP,  { y: 105, duration: 1.1, ease: 'power2.inOut' }, '<')
            .to(fullP,  { opacity: 0.22, duration: 0.8 }, '<')
            .to(fullL,  { opacity: 0.25, duration: 0.8 }, '<')
            .to(transL, { opacity: 1, y: -105, duration: 0.6 }, '<0.3')
            .to(stdyL,  { opacity: 1, y: 105, duration: 0.6 }, '<')
            .to({}, { duration: 0.6 });
          tl.call(act('act 3 · the transient dies'))
            .to(cursor, { opacity: 1, duration: 0.3 })
            .to(cursor, { attr: { x1: W - 40, x2: W - 40 },
                          duration: 2.6, ease: 'none' })
            .to(transP, { opacity: 0.06, duration: 2.2, ease: 'power1.in' }, '<0.4')
            .to(transL, { opacity: 0.15, duration: 2.2 }, '<')
            .to(cursor, { opacity: 0, duration: 0.3 });
          tl.call(act('act 4 · only the steady state remains'))
            .to(stdyP, { y: 0, duration: 1.2, ease: 'power2.inOut' })
            .to(stdyL, { y: 0, duration: 1.2, ease: 'power2.inOut' }, '<')
            .to([fullP, fullL], { opacity: 0, duration: 0.7 }, '<')
            .to(stdyP, { strokeWidth: 3.2, duration: 0.5 }, '<0.5');

          var scrub = el.querySelector('[data-k="scrub"]');
          var btn = el.querySelector('[data-b]');
          btn.addEventListener('click', function () {
            if (tl.progress() >= 1) tl.progress(0);
            if (tl.paused()) { tl.play(); btn.textContent = '⏸ pause'; }
            else { tl.pause(); btn.textContent = '▶ play the story'; }
          });
          tl.eventCallback('onUpdate', function () { scrub.value = tl.progress(); });
          tl.eventCallback('onComplete', function () { btn.textContent = '▶ replay'; });
          scrub.addEventListener('input', function () {
            tl.pause(); btn.textContent = '▶ play the story';
            tl.progress(parseFloat(this.value));
          });

          return function () { tl.kill(); svg.remove(); };
        }
        export default { render };
        """
        init_w0 = traitlets.Float(2.0).tag(sync=True)
        init_g = traitlets.Float(0.25).tag(sync=True)
        init_om = traitlets.Float(1.2).tag(sync=True)
        init_F0 = traitlets.Float(1.0).tag(sync=True)

    return mo.ui.anywidget(_SolutionAnatomy(
        init_w0=float(omega0), init_g=float(gamma),
        init_om=float(omega), init_F0=float(F0)))


# ---------------------------------------------------------------------------
# 4. Feedback (stars + comment) → Google Form
# ---------------------------------------------------------------------------

def feedback_form(chapter: str = ""):
    """A star-rating + comment box that posts anonymously to a Google Form.

    Reads the form wiring from the module-level ``GFORM_*`` constants. Until
    ``GFORM_ACTION`` is set, it renders a polite "being set up" placeholder
    (so the page is safe to ship before the form exists). ``chapter`` is a
    label auto-attached to each submission so responses are grouped by
    chapter in the linked Sheet.
    """
    import marimo as mo
    import anywidget
    import traitlets

    class _Feedback(anywidget.AnyWidget):
        _esm = r"""
        function render({ model, el }) {
          var action = model.get('action');
          var configured = !!action;
          var chapter = model.get('chapter') || '';

          el.innerHTML = `
            <div style="font:14px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
                        color:#1d2733;border:1px solid #d6dde6;border-left:3px solid #5b7db1;
                        border-radius:.6rem;padding:1rem 1.2rem;max-width:680px;background:#fff">
              <div style="font-weight:600;font-size:1.05rem">Was this chapter helpful?</div>
              <div data-sub style="color:#56636f;font-size:.92rem;margin-top:.15rem">
                Anonymous — a star and an optional note. It goes straight to the author.</div>
              <div data-stars style="margin-top:.7rem;font-size:1.7rem;line-height:1;user-select:none"></div>
              <textarea data-comment rows="3" placeholder="What worked, what was confusing, what you'd change… (optional)"
                style="width:100%;margin-top:.7rem;padding:.55rem .65rem;border:1px solid #d6dde6;
                       border-radius:.45rem;font:inherit;resize:vertical;box-sizing:border-box"></textarea>
              <div style="margin-top:.6rem;display:flex;align-items:center;gap:.8rem;flex-wrap:wrap">
                <button data-send style="padding:.5rem 1.1rem;border:0;border-radius:.45rem;
                  background:#2a5d9c;color:#fff;font:inherit;font-weight:600;cursor:pointer">Send feedback</button>
                <span data-status style="color:#56636f;font-size:.9rem"></span>
              </div>
            </div>`;

          var starsEl = el.querySelector('[data-stars]');
          var commentEl = el.querySelector('[data-comment]');
          var sendEl = el.querySelector('[data-send]');
          var statusEl = el.querySelector('[data-status]');
          var subEl = el.querySelector('[data-sub]');
          var rating = 0;

          // Build five clickable stars.
          var stars = [];
          for (var i = 1; i <= 5; i++) {
            var s = document.createElement('span');
            s.textContent = '☆';                 // ☆
            s.dataset.v = i;
            s.style.cssText = 'cursor:pointer;color:#e9a23b;padding:0 .05rem';
            starsEl.appendChild(s); stars.push(s);
          }
          function paint(n) {
            for (var i = 0; i < 5; i++) stars[i].textContent = (i < n) ? '★' : '☆';
          }
          starsEl.addEventListener('mouseover', function (e) {
            if (e.target.dataset.v) paint(+e.target.dataset.v);
          });
          starsEl.addEventListener('mouseout', function () { paint(rating); });
          starsEl.addEventListener('click', function (e) {
            if (e.target.dataset.v) { rating = +e.target.dataset.v; paint(rating); }
          });

          if (!configured) {
            subEl.textContent = 'Feedback is being set up — check back soon.';
            sendEl.disabled = true;
            sendEl.style.background = '#9aa7b5'; sendEl.style.cursor = 'default';
            return function () {};
          }

          sendEl.addEventListener('click', function () {
            var comment = (commentEl.value || '').trim();
            if (!rating && !comment) {
              statusEl.style.color = '#d1495b';
              statusEl.textContent = 'Pick a star or jot a note first.';
              return;
            }
            var fd = new FormData();
            if (model.get('e_rating') && rating) fd.append(model.get('e_rating'), String(rating));
            if (model.get('e_comment')) fd.append(model.get('e_comment'), comment);
            if (model.get('e_chapter')) fd.append(model.get('e_chapter'), chapter);
            sendEl.disabled = true;
            statusEl.style.color = '#56636f';
            statusEl.textContent = 'Sending…';
            // Google Forms doesn't send CORS headers, so the response is
            // opaque (no-cors) — resolving the fetch is our success signal.
            fetch(action, { method: 'POST', mode: 'no-cors', body: fd })
              .then(function () { thanks(); })
              .catch(function () { thanks(); });   // opaque errors are expected; treat as sent
          });

          function thanks() {
            el.querySelector('div').innerHTML =
              '<div style="font-weight:600;font-size:1.05rem">Thank you</div>' +
              '<div style="color:#56636f;margin-top:.3rem">Your feedback was sent — '
              + 'it genuinely shapes what gets fixed next.</div>'
              + (model.get('view_url')
                  ? ' <div style="margin-top:.5rem;font-size:.9rem">'
                    + '<a href="' + model.get('view_url') + '" target="_blank" rel="noopener">'
                    + 'open the full form</a></div>'
                  : '');
          }
          return function () {};
        }
        export default { render };
        """
        chapter = traitlets.Unicode("").tag(sync=True)
        action = traitlets.Unicode("").tag(sync=True)
        e_rating = traitlets.Unicode("").tag(sync=True)
        e_comment = traitlets.Unicode("").tag(sync=True)
        e_chapter = traitlets.Unicode("").tag(sync=True)
        view_url = traitlets.Unicode("").tag(sync=True)

    return mo.ui.anywidget(_Feedback(
        chapter=chapter,
        action=GFORM_ACTION,
        e_rating=GFORM_ENTRY_RATING,
        e_comment=GFORM_ENTRY_COMMENT,
        e_chapter=GFORM_ENTRY_CHAPTER,
        view_url=GFORM_VIEW_URL,
    ))
