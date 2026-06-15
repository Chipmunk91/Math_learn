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
- :func:`rumor_crowd` — roaming people who pass a rumor on contact;
  the logistic S-curve emerges and is fit live. (Ch 1.)
- :func:`cooling_coffee` — a hot mug cools toward room temperature;
  steam visualises the heat-loss term, candle/milk shift it. (Ch 2.)
- :func:`feedback_form` — a star + comment box that posts to a Google
  Form (anonymous, lands in a Sheet you own). Replaces the per-chapter
  playground.
"""

from __future__ import annotations

__all__ = ["spring_grab", "resonance_audio", "solution_anatomy",
           "rumor_crowd", "cooling_coffee", "feedback_form"]

# --- Google Form feedback wiring --------------------------------------------
# Fill these four in ONCE after creating the feedback Google Form (see
# AUTHORING.md → "Feedback form setup"). Until GFORM_ACTION is set, the
# widget renders a polite "being set up" placeholder instead of posting
# nowhere, so the site is safe to ship before the form exists.
GFORM_ACTION = "https://docs.google.com/forms/d/e/1FAIpQLSf2zkzsTtLGAkbZ6VdiXQqCLYfqPjlPi3ZLIpEs-VLCP_6gHg/formResponse"
GFORM_ENTRY_RATING = "entry.1887182985"    # the 1–5 rating field
GFORM_ENTRY_COMMENT = "entry.1050269236"   # the paragraph/comment field
# OPTIONAL. Leave "" and the chapter name is folded into the comment instead
# (so a 2-field form just works). Set it only for a clean, separate chapter
# column — and use that field's OWN entry ID with NO "=value" suffix.
GFORM_ENTRY_CHAPTER = "entry.1540647133"   # fixed: had a stray "=123" before
GFORM_VIEW_URL = "https://docs.google.com/forms/d/e/1FAIpQLSf2zkzsTtLGAkbZ6VdiXQqCLYfqPjlPi3ZLIpEs-VLCP_6gHg/viewform"


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
# 4. Rumor through a roaming crowd (Canvas 2D agents + live logistic fit)
# ---------------------------------------------------------------------------

def rumor_crowd(known0: int = 3, speed: int = 80):
    """A crowd of people who walk around and pass a rumor on contact.

    Every figure strolls the frame; an unaware (grey) person lights up the
    moment they cross paths with someone who already knows. The graph plots
    the fraction who know (red) against Chapter 1's logistic law fit live
    (blue). The S-curve — slow start, eruption, plateau — emerges from
    individual contacts rather than being assumed; the residual wander and
    the random ignition time are the honest gap between a well-mixed
    first-order model and a crowd that actually lives in space.

    ``known0`` seeds the initial number of knowers (the rumor story's
    "3 people"); ``speed`` is the initial mingle speed, i.e. Chapter 1's
    spreading-rate constant made physical.
    """
    import marimo as mo
    import anywidget
    import traitlets

    class _RumorCrowd(anywidget.AnyWidget):
        _esm = r"""
        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <div style="display:flex;gap:10px;flex-wrap:wrap">
                <div style="flex:1;min-width:300px">
                  <canvas data-crowd style="width:100%;height:330px;border:1px solid #dde4ec;border-radius:8px;display:block;background:#eef2f7;touch-action:none;cursor:crosshair"></canvas>
                  <div style="text-align:center;color:#8a96a5;margin-top:4px">the crowd · click / drag to plant the rumor</div>
                </div>
                <div style="flex:1;min-width:300px">
                  <canvas data-graph style="width:100%;height:330px;border:1px solid #dde4ec;border-radius:8px;display:block;background:#fff"></canvas>
                  <div style="text-align:center;color:#8a96a5;margin-top:4px">fraction who know · red = crowd, blue = logistic law (Ch 1)</div>
                </div>
              </div>
              <div style="display:flex;gap:18px;margin-top:8px;align-items:center;flex-wrap:wrap">
                <label>mingle speed <input type="range" min="20" max="200" step="5" value="80" data-k="v"> <span data-v="v">80</span></label>
                <button data-b="reset" style="padding:6px 14px;border:1px solid #c7d2e0;border-radius:6px;background:#f3f7fc;cursor:pointer">↺ new rumor</button>
                <span data-stat style="color:#7c8aa0"></span>
              </div>
            </div>`;

          var crowd = el.querySelector('[data-crowd]');
          var graph = el.querySelector('[data-graph]');
          var dpr = window.devicePixelRatio || 1;
          function fit(c, h) {
            var w = c.clientWidth || 320;
            c.width = w * dpr; c.height = h * dpr;
            var x = c.getContext('2d'); x.setTransform(dpr, 0, 0, dpr, 0, 0);
            return { ctx: x, W: w, H: h };
          }
          var C = fit(crowd, 330), G = fit(graph, 330);

          // Population scales with floor area to keep the crowd density (and so
          // the pace) about the same on any screen width.
          var N = Math.max(70, Math.min(180, Math.round(0.0012 * C.W * C.H)));
          var RC = 10, RC2 = RC * RC;            // contact radius (px)
          var GS = 6;                            // person glyph scale (px)
          var KNOWN0 = Math.max(1, model.get('init_known') || 3);
          var speed = model.get('init_speed') || 80;   // px/s, from the slider
          var DT = 1 / 45;                       // model seconds per step
          var slider = el.querySelector('input');
          slider.value = speed; el.querySelector('[data-v="v"]').textContent = speed;

          var x = new Float32Array(N), y = new Float32Array(N);
          var th = new Float32Array(N);
          var aware = new Uint8Array(N), flash = new Float32Array(N);
          var yCount = 0, t = 0, aHat = 0, hist = [];

          function recount() { var s = 0; for (var i = 0; i < N; i++) s += aware[i]; yCount = s; }
          function seed() {
            for (var i = 0; i < N; i++) {
              x[i] = Math.random() * C.W; y[i] = Math.random() * C.H;
              th[i] = Math.random() * 6.2832; aware[i] = 0; flash[i] = 0;
            }
            for (var k = 0; k < KNOWN0; k++) { var j = (Math.random()*N)|0; aware[j] = 1; flash[j] = 1; }
            recount(); t = 0; aHat = 0; hist = [];
          }
          seed();   // a few people start out knowing the rumor

          function plantAt(cx, cy) {
            var rad2 = (RC * 2.6) * (RC * 2.6);
            for (var i = 0; i < N; i++) {
              if (!aware[i]) {
                var dx = x[i]-cx, dy = y[i]-cy;
                if (dx*dx + dy*dy < rad2) { aware[i] = 1; flash[i] = 1; }
              }
            }
            recount();
          }
          var pressing = false;
          function evToCanvas(e) {
            var r = crowd.getBoundingClientRect();
            return [(e.clientX-r.left)*(C.W/r.width), (e.clientY-r.top)*(C.H/r.height)];
          }
          crowd.addEventListener('pointerdown', function (e) { pressing = true; var p = evToCanvas(e); plantAt(p[0], p[1]); });
          crowd.addEventListener('pointermove', function (e) { if (pressing) { var p = evToCanvas(e); plantAt(p[0], p[1]); } });
          window.addEventListener('pointerup', function () { pressing = false; });
          el.querySelector('[data-b="reset"]').addEventListener('click', seed);
          slider.addEventListener('input', function () {
            speed = parseInt(this.value, 10);
            el.querySelector('[data-v="v"]').textContent = speed;
          });

          function lerp(a, b, t) { return a + (b - a) * t; }
          function mix(c1, c2, t) {
            return 'rgb(' + Math.round(lerp(c1[0],c2[0],t)) + ',' +
                            Math.round(lerp(c1[1],c2[1],t)) + ',' +
                            Math.round(lerp(c1[2],c2[2],t)) + ')';
          }
          var BG_LIGHT = [238,242,247], BG_DARK = [12,17,24];
          var UN_LIGHT = [150,163,178], UN_DARK = [58,70,84];

          function step() {
            if (yCount >= N) return;   // whole campus knows — settle the scene
            // Everyone strolls: constant speed, a little random turn each step
            // (so directions decorrelate and the crowd mixes), bounce off walls.
            var d = speed * DT;
            for (var i = 0; i < N; i++) {
              th[i] += (Math.random()*2 - 1) * 0.4;
              x[i] += d * Math.cos(th[i]); y[i] += d * Math.sin(th[i]);
              if (x[i] < 0) { x[i] = -x[i]; th[i] = Math.PI - th[i]; }
              else if (x[i] > C.W) { x[i] = 2*C.W - x[i]; th[i] = Math.PI - th[i]; }
              if (y[i] < 0) { y[i] = -y[i]; th[i] = -th[i]; }
              else if (y[i] > C.H) { y[i] = 2*C.H - y[i]; th[i] = -th[i]; }
            }
            // Contagion: an unaware person who is within RC of any knower hears
            // it and lights up. This is the y·(K−y) "a teller meets an ear"
            // rule of Chapter 1, but resolved in space, pair by real pair.
            for (var i = 0; i < N; i++) {
              if (aware[i]) continue;
              for (var j = 0; j < N; j++) {
                if (!aware[j]) continue;
                var dx = x[i]-x[j], dy = y[i]-y[j];
                if (dx*dx + dy*dy < RC2) { aware[i] = 1; flash[i] = 1; yCount++; break; }
              }
            }
            t += DT;
            // Fit Chapter 1's logistic law to the crowd live. For a logistic,
            // d/dt ln(y/(K−y)) is the constant a, so we can read a straight off
            // the run: slope in logit space from the start to now (smoothed).
            if (yCount >= KNOWN0 + 3 && yCount < N && t > 0.3) {
              var p = yCount / N, p0 = KNOWN0 / N;
              var aInst = (Math.log(p/(1-p)) - Math.log(p0/(1-p0))) / t;
              aHat = aHat === 0 ? aInst : (0.92*aHat + 0.08*aInst);
            }
            hist.push([t, yCount / N]);
            if (hist.length > 5000) hist.shift();
          }

          function person(ctx, cx, cy, s, color) {
            // a restroom-pictogram figure: trapezoid body + round head
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.moveTo(cx - s*0.5, cy + s*0.85); ctx.lineTo(cx + s*0.5, cy + s*0.85);
            ctx.lineTo(cx + s*0.28, cy - s*0.1); ctx.lineTo(cx - s*0.28, cy - s*0.1);
            ctx.closePath(); ctx.fill();
            ctx.beginPath(); ctx.arc(cx, cy - s*0.42, s*0.34, 0, 6.2832); ctx.fill();
          }

          function drawCrowd() {
            var f = yCount / N, ease = f*f*(3 - 2*f);   // smoothstep mood
            C.ctx.fillStyle = mix(BG_LIGHT, BG_DARK, ease);
            C.ctx.fillRect(0, 0, C.W, C.H);
            var unColor = mix(UN_LIGHT, UN_DARK, ease);
            for (var i = 0; i < N; i++) {
              if (aware[i]) {
                if (flash[i] > 0.05) {
                  C.ctx.fillStyle = 'rgba(244,184,96,' + (0.4*flash[i]) + ')';
                  C.ctx.beginPath(); C.ctx.arc(x[i], y[i], GS*2.0, 0, 6.2832); C.ctx.fill();
                }
                person(C.ctx, x[i], y[i], GS, '#f4b860');
              } else {
                person(C.ctx, x[i], y[i], GS, unColor);
              }
              if (flash[i] > 0.001) flash[i] *= 0.9;
            }
          }

          function drawGraph() {
            var ctx = G.ctx, W = G.W, H = G.H;
            ctx.clearRect(0, 0, W, H);
            var pad = { l: 34, r: 12, t: 16, b: 24 };
            var x0 = pad.l, x1 = W - pad.r, y0 = H - pad.b, y1 = pad.t;
            ctx.strokeStyle = '#dde4ec'; ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(x0, y1); ctx.lineTo(x0, y0); ctx.lineTo(x1, y0); ctx.stroke();
            ctx.fillStyle = '#7c8aa0'; ctx.font = '10px sans-serif';
            ctx.fillText('1', x0 - 12, y1 + 4); ctx.fillText('0', x0 - 12, y0);
            ctx.fillText('time →', x1 - 36, y0 + 16);
            var tmax = Math.max(4, hist.length ? hist[hist.length-1][0] : 4);
            function X(tt) { return x0 + (tt / tmax) * (x1 - x0); }
            function Y(ff) { return y0 + ff * (y1 - y0); }
            if (aHat > 0) {
              var p0 = KNOWN0 / N, b0 = Math.log(p0/(1-p0));
              ctx.strokeStyle = '#5b7db1'; ctx.lineWidth = 2; ctx.beginPath();
              for (var k = 0; k <= 120; k++) {
                var tt = tmax * k / 120;
                var yf = 1 / (1 + Math.exp(-(aHat*tt + b0)));
                if (k === 0) ctx.moveTo(X(tt), Y(yf)); else ctx.lineTo(X(tt), Y(yf));
              }
              ctx.stroke();
            }
            ctx.strokeStyle = '#d1495b'; ctx.lineWidth = 2; ctx.beginPath();
            for (var i = 0; i < hist.length; i++) {
              var hx = X(hist[i][0]), hy = Y(hist[i][1]);
              if (i === 0) ctx.moveTo(hx, hy); else ctx.lineTo(hx, hy);
            }
            ctx.stroke();
            ctx.fillStyle = '#5b7db1'; ctx.fillRect(x1 - 150, y1 + 2, 14, 3);
            ctx.fillStyle = '#7c8aa0'; ctx.fillText('logistic law', x1 - 132, y1 + 6);
            ctx.fillStyle = '#d1495b'; ctx.fillRect(x1 - 150, y1 + 14, 14, 3);
            ctx.fillStyle = '#7c8aa0'; ctx.fillText('the crowd', x1 - 132, y1 + 18);
          }

          function updateStat() {
            el.querySelector('[data-stat]').textContent =
              yCount + ' / ' + N + ' know  (' + Math.round(100*yCount/N) + '%)';
          }

          var raf, running = true, acc = 0, last = performance.now();
          function frame(now) {
            if (!running) return;
            acc += Math.min(0.05, (now - last) / 1000); last = now;
            while (acc > DT) { step(); acc -= DT; }
            drawCrowd(); drawGraph(); updateStat();
            raf = requestAnimationFrame(frame);
          }
          raf = requestAnimationFrame(frame);
          return function () { running = false; cancelAnimationFrame(raf); };
        }
        export default { render };
        """
        init_known = traitlets.Int(3).tag(sync=True)
        init_speed = traitlets.Int(80).tag(sync=True)

    return mo.ui.anywidget(_RumorCrowd(
        init_known=int(known0), init_speed=int(speed)))


# ---------------------------------------------------------------------------
# 5. Cooling coffee mug (Canvas 2D + steam particles — Newton's cooling)
# ---------------------------------------------------------------------------

def cooling_coffee(T0: float = 90.0, Tr: float = 22.0, k: float = 0.10,
                   warmer_on: bool = False):
    """A hot mug cooling toward room temperature, with optional candle warmer.

    Newton's law of cooling: ``dT/dt = -k (T - Tr) + Q`` where ``Q`` is the
    warmer's heat input (zero when off). Equilibrium is ``Tr + Q/k``,
    capped at 100 deg C (boiling). The mug starts at ``T0``, the room is at
    ``Tr``, the cooling constant is ``k`` (small = well insulated). With
    ``warmer_on=True`` the candle starts lit.

    Visuals: a mug + steam (spawn rate proportional to k*(T - Tr), so the
    visible puffiness IS the heat-loss term), a thermometer, a candle below.
    The graph and the T readout use the deterministic ODE, so the math is
    exact; sprites are honest proxies.
    """
    import marimo as mo
    import anywidget
    import traitlets

    class _CoolingCoffee(anywidget.AnyWidget):
        _esm = r"""
        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <div style="display:flex;gap:10px;flex-wrap:wrap">
                <div style="flex:1;min-width:300px">
                  <canvas data-scene style="width:100%;height:330px;border:1px solid #dde4ec;border-radius:8px;display:block;background:#fbf6ec"></canvas>
                  <div style="text-align:center;color:#8a96a5;margin-top:4px">hot mug in a room · steam = heat leaving · candle adds heat · milk cools fast</div>
                </div>
                <div style="flex:1;min-width:300px">
                  <canvas data-graph style="width:100%;height:330px;border:1px solid #dde4ec;border-radius:8px;display:block;background:#fff"></canvas>
                  <div style="text-align:center;color:#8a96a5;margin-top:4px">T(t) · dashed line = the equilibrium it's chasing</div>
                </div>
              </div>
              <div style="display:flex;gap:18px;margin-top:8px;align-items:center;flex-wrap:wrap">
                <label>room T_r <input type="range" min="0" max="35" step="1" value="22" data-k="Tr"> <span data-v="Tr">22</span>°C</label>
                <label>cooling rate k <input type="range" min="0.02" max="0.4" step="0.005" value="0.1" data-k="k"> <span data-v="k">0.10</span>/s</label>
                <button data-b="warmer" style="padding:6px 14px;border:1px solid #c7d2e0;border-radius:6px;background:#f3f7fc;cursor:pointer">🔥 candle warmer</button>
                <button data-b="milk" style="padding:6px 14px;border:1px solid #c7d2e0;border-radius:6px;background:#f3f7fc;cursor:pointer">🥛 pour milk</button>
                <button data-b="reset" style="padding:6px 14px;border:1px solid #c7d2e0;border-radius:6px;background:#f3f7fc;cursor:pointer">☕ fresh pour</button>
                <span data-stat style="color:#7c8aa0"></span>
              </div>
            </div>`;

          var dpr = window.devicePixelRatio || 1;
          function fit(c, h) {
            var w = c.clientWidth || 320;
            c.width = w * dpr; c.height = h * dpr;
            var x = c.getContext('2d'); x.setTransform(dpr, 0, 0, dpr, 0, 0);
            return { ctx: x, W: w, H: h };
          }
          var SC = fit(el.querySelector('[data-scene]'), 330);
          var GC = fit(el.querySelector('[data-graph]'), 330);

          // State — the deterministic ODE  dT/dt = -k(T - Tr) + Q  drives both
          // the graph and the T readout, so the math you see plotted is exact.
          // Steam and other visuals are honest proxies layered on top.
          var temp = model.get('init_T0');
          var Tr = model.get('init_Tr');
          var k = model.get('init_k');
          var warmerOn = !!model.get('init_warmer'), Q_MAX = 4.0;
          // sync slider DOM to the initial values
          var _tr = el.querySelectorAll('input')[0], _k = el.querySelectorAll('input')[1];
          _tr.value = Tr; el.querySelector('[data-v="Tr"]').textContent = Tr.toFixed(0);
          _k.value  = k;  el.querySelector('[data-v="k"]').textContent  = k.toFixed(2);
          if (warmerOn) el.querySelector('[data-b="warmer"]').style.background = '#ffe2b3';
          var t = 0, hist = [], steams = [], milkDrops = [];
          var steamAcc = 0, flickerPhase = 0;

          // Layout
          var mugW = 90, mugH = 100, handleR = 18;
          var mugCx = SC.W * 0.36;
          var mugX = mugCx - mugW/2;
          var mugY = 145;

          function reset() {
            temp = model.get('init_T0'); t = 0; hist = []; steams = []; milkDrops = [];
          }
          function pourMilk() {
            // weighted average: 25% milk at 5°C
            temp = 0.75 * temp + 0.25 * 5;
            for (var i = 0; i < 6; i++) {
              milkDrops.push({
                x: mugCx + (Math.random()-0.5) * 14,
                y: mugY - 30 - i * 7,
                vy: 200 + Math.random() * 40
              });
            }
          }
          function toggleWarmer() {
            warmerOn = !warmerOn;
            el.querySelector('[data-b="warmer"]').style.background =
              warmerOn ? '#ffe2b3' : '#f3f7fc';
          }
          el.querySelector('[data-b="reset"]').addEventListener('click', reset);
          el.querySelector('[data-b="milk"]').addEventListener('click', pourMilk);
          el.querySelector('[data-b="warmer"]').addEventListener('click', toggleWarmer);
          var sTr = el.querySelectorAll('input')[0], sK = el.querySelectorAll('input')[1];
          sTr.addEventListener('input', function () {
            Tr = parseFloat(this.value);
            el.querySelector('[data-v="Tr"]').textContent = Tr.toFixed(0);
          });
          sK.addEventListener('input', function () {
            k = parseFloat(this.value);
            el.querySelector('[data-v="k"]').textContent = k.toFixed(2);
          });

          function lerp(a,b,t){ return a+(b-a)*t; }
          function rgb3(c1,c2,t) {
            t = Math.max(0, Math.min(1, t));
            return 'rgb(' + Math.round(lerp(c1[0],c2[0],t)) + ',' +
                            Math.round(lerp(c1[1],c2[1],t)) + ',' +
                            Math.round(lerp(c1[2],c2[2],t)) + ')';
          }
          function tempColor(tt) { return rgb3([66,140,210], [210,72,76], tt/100); }

          function drawScene() {
            var ctx = SC.ctx;
            // Room: warm linear gradient
            var grd = ctx.createLinearGradient(0, 0, 0, SC.H);
            grd.addColorStop(0, '#fbf6ec'); grd.addColorStop(1, '#f4eee2');
            ctx.fillStyle = grd; ctx.fillRect(0, 0, SC.W, SC.H);
            // Table line under the mug
            var tableY = mugY + mugH + 38;
            ctx.strokeStyle = '#cdb98f'; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(20, tableY); ctx.lineTo(SC.W - 20, tableY); ctx.stroke();

            // Candle (always rendered, lights up when warmerOn)
            var cdlY = mugY + mugH + 10;
            ctx.fillStyle = '#b48c5e';
            ctx.fillRect(mugCx - 7, cdlY, 14, 22);
            ctx.fillStyle = '#82603c'; ctx.fillRect(mugCx - 7, cdlY, 14, 2);
            ctx.fillStyle = '#2a1e10'; ctx.fillRect(mugCx - 1, cdlY - 4, 2, 4);

            if (warmerOn) {
              var glow = ctx.createRadialGradient(mugCx, cdlY - 4, 4, mugCx, cdlY - 4, 60);
              glow.addColorStop(0, 'rgba(255,178,80,0.55)');
              glow.addColorStop(1, 'rgba(255,178,80,0)');
              ctx.fillStyle = glow;
              ctx.fillRect(mugCx - 62, cdlY - 55, 124, 82);
              var f = 0.85 + 0.15 * Math.sin(flickerPhase);
              var g = 0.85 + 0.15 * Math.sin(flickerPhase * 1.7 + 1);
              ctx.fillStyle = '#ff8b3a';
              ctx.beginPath(); ctx.ellipse(mugCx, cdlY - 8, 5 * f, 12 * g, 0, 0, 6.2832); ctx.fill();
              ctx.fillStyle = '#ffd585';
              ctx.beginPath(); ctx.ellipse(mugCx, cdlY - 9, 2.6 * f, 7 * g, 0, 0, 6.2832); ctx.fill();
            }

            // Mug handle (drawn first so body covers its inner edge)
            ctx.strokeStyle = '#7a6450'; ctx.lineWidth = 9;
            ctx.beginPath();
            ctx.arc(mugX + mugW + 4, mugY + mugH * 0.45, handleR, -Math.PI * 0.55, Math.PI * 0.55);
            ctx.stroke();

            // Mug body (slight trapezoid)
            ctx.fillStyle = '#a48867';
            ctx.beginPath();
            ctx.moveTo(mugX - 2, mugY);
            ctx.lineTo(mugX + mugW + 2, mugY);
            ctx.lineTo(mugX + mugW - 4, mugY + mugH);
            ctx.lineTo(mugX + 4, mugY + mugH);
            ctx.closePath(); ctx.fill();
            ctx.strokeStyle = '#7a6450'; ctx.lineWidth = 2; ctx.stroke();

            // Liquid (coffee — colour fixed; story is in temperature)
            var liqY = mugY + 12, liqB = mugY + mugH - 5;
            var liqLeft = mugX + 4, liqRight = mugX + mugW - 4;
            ctx.fillStyle = '#3a2615';
            ctx.beginPath();
            ctx.moveTo(liqLeft + 1, liqY);
            ctx.lineTo(liqRight - 1, liqY);
            ctx.lineTo(liqRight - 4, liqB);
            ctx.lineTo(liqLeft + 4, liqB);
            ctx.closePath(); ctx.fill();
            ctx.fillStyle = '#4d3220';
            ctx.beginPath();
            ctx.ellipse(mugX + mugW/2, liqY, (mugW - 8) / 2, 4.5, 0, 0, 6.2832);
            ctx.fill();
            ctx.strokeStyle = '#291810'; ctx.lineWidth = 1; ctx.stroke();

            // Milk droplets (falling toward the mug)
            ctx.fillStyle = 'rgba(248,242,228,0.95)';
            for (var i = 0; i < milkDrops.length; i++) {
              var d = milkDrops[i];
              ctx.beginPath(); ctx.arc(d.x, d.y, 3.2, 0, 6.2832); ctx.fill();
            }

            // Steam particles — spawn-rate is proportional to k(T - Tr), so
            // 'lots of steam' literally means 'lots of heat leaving per second'.
            for (var i = 0; i < steams.length; i++) {
              var s = steams[i];
              var a = 0.42 * s.life;
              ctx.fillStyle = 'rgba(220,225,232,' + a.toFixed(3) + ')';
              ctx.beginPath();
              ctx.arc(s.x, s.y, 4 + (1 - s.life) * 7, 0, 6.2832);
              ctx.fill();
            }

            // Thermometer
            var thX = mugX + mugW + 50;
            var thY_top = mugY - 25, thY_bot = mugY + mugH + 5;
            var thH = thY_bot - thY_top;
            ctx.fillStyle = '#fff'; ctx.fillRect(thX - 7, thY_top, 14, thH);
            ctx.strokeStyle = '#b4a890'; ctx.lineWidth = 1.5;
            ctx.strokeRect(thX - 7, thY_top, 14, thH);
            var tShown = Math.max(0, Math.min(100, temp));
            var fillH = (tShown / 100) * thH;
            ctx.fillStyle = tempColor(tShown);
            ctx.fillRect(thX - 5, thY_bot - fillH, 10, fillH);
            ctx.fillStyle = tempColor(tShown);
            ctx.beginPath(); ctx.arc(thX, thY_bot + 10, 10, 0, 6.2832); ctx.fill();
            ctx.strokeStyle = '#b4a890'; ctx.lineWidth = 1.5; ctx.stroke();
            ctx.fillStyle = '#7c8aa0'; ctx.font = '9px sans-serif';
            for (var tv = 0; tv <= 100; tv += 25) {
              var y = thY_bot - (tv/100) * thH;
              ctx.fillRect(thX - 12, y - 0.5, 4, 1);
              ctx.fillText(tv + '°', thX + 10, y + 3);
            }

            // Big T label above the mug
            ctx.fillStyle = '#33485c';
            ctx.font = 'bold 18px sans-serif'; ctx.textAlign = 'center';
            ctx.fillText('T = ' + temp.toFixed(1) + '°C', mugCx, mugY - 18);
            ctx.textAlign = 'left';
            ctx.fillStyle = '#a99072'; ctx.font = '11px sans-serif';
            ctx.fillText('room T_r = ' + Tr.toFixed(0) + '°C', 16, 20);
          }

          function drawGraph() {
            var ctx = GC.ctx, W = GC.W, H = GC.H;
            ctx.clearRect(0, 0, W, H);
            var pad = { l: 44, r: 14, t: 18, b: 28 };
            var x0 = pad.l, x1 = W - pad.r, y0 = H - pad.b, y1 = pad.t;
            ctx.strokeStyle = '#dde4ec'; ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(x0, y1); ctx.lineTo(x0, y0); ctx.lineTo(x1, y0); ctx.stroke();
            ctx.fillStyle = '#7c8aa0'; ctx.font = '10px sans-serif';
            ctx.fillText('100°', x0 - 30, y1 + 4);
            ctx.fillText('0°', x0 - 18, y0);
            ctx.fillText('time (s) →', x1 - 60, y0 + 18);

            var tmax = Math.max(30, hist.length ? hist[hist.length-1][0] : 30);
            function X(tt) { return x0 + (tt/tmax)*(x1-x0); }
            function Y(tt) { return y0 + (tt/100)*(y1-y0); }

            // Equilibrium it's chasing — dashed line in the equilibrium's colour
            var Q = warmerOn ? Q_MAX : 0;
            var Teq = Math.min(100, Tr + Q/k);
            ctx.strokeStyle = tempColor(Teq); ctx.setLineDash([6, 4]); ctx.lineWidth = 1.8;
            ctx.beginPath(); ctx.moveTo(x0, Y(Teq)); ctx.lineTo(x1, Y(Teq)); ctx.stroke();
            ctx.setLineDash([]);
            ctx.fillStyle = '#7c8aa0';
            ctx.fillText('T_eq = ' + Teq.toFixed(0) + '°', x1 - 72, Y(Teq) - 4);

            // Faint room reference line (so you can see the candle's lift)
            ctx.strokeStyle = '#dde4ec'; ctx.setLineDash([3, 3]); ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(x0, Y(Tr)); ctx.lineTo(x1, Y(Tr)); ctx.stroke();
            ctx.setLineDash([]);

            ctx.strokeStyle = '#a13648'; ctx.lineWidth = 2.4; ctx.beginPath();
            for (var i = 0; i < hist.length; i++) {
              var hx = X(hist[i][0]), hy = Y(hist[i][1]);
              if (i === 0) ctx.moveTo(hx, hy); else ctx.lineTo(hx, hy);
            }
            ctx.stroke();
          }

          var raf, running = true, last = performance.now();
          function frame(now) {
            if (!running) return;
            var dt = Math.min(0.05, (now - last) / 1000); last = now;
            flickerPhase += dt * 14;

            // (1) Deterministic ODE — exact, drives both graph and readout.
            var Q = warmerOn ? Q_MAX : 0;
            temp += (-k * (temp - Tr) + Q) * dt;
            if (temp > 100) temp = 100;
            if (temp < -5) temp = -5;
            t += dt; hist.push([t, temp]);
            if (hist.length > 4000) hist.shift();

            // (2) Steam: spawn rate ∝ heat-loss rate k(T - Tr), so the visible
            // 'puffiness' literally is the size of the term -k(T - Tr).
            var rate = Math.max(0, k * (temp - Tr)) * 6;
            steamAcc += rate * dt;
            while (steamAcc >= 1 && steams.length < 140) {
              steamAcc -= 1;
              var sx = mugX + 12 + Math.random() * (mugW - 24);
              steams.push({ x: sx, y: mugY + 6,
                            vx: (Math.random() - 0.5) * 14,
                            vy: -22 - Math.random() * 18, life: 1.0 });
            }
            for (var i = steams.length - 1; i >= 0; i--) {
              var s = steams[i];
              s.vx += (Math.random() - 0.5) * 28 * dt;
              s.x += s.vx * dt; s.y += s.vy * dt;
              s.life -= 0.45 * dt;
              if (s.life <= 0 || s.y < -10) steams.splice(i, 1);
            }

            // (3) Milk drops (fall, then disappear into the mug)
            for (var i = milkDrops.length - 1; i >= 0; i--) {
              var d = milkDrops[i];
              d.y += d.vy * dt;
              if (d.y >= mugY + 12) milkDrops.splice(i, 1);
            }

            drawScene(); drawGraph();
            var Teq = Math.min(100, Tr + (warmerOn ? Q_MAX : 0) / k);
            el.querySelector('[data-stat]').textContent =
              'τ = 1/k = ' + (1/k).toFixed(1) + ' s   ·   T_eq = ' + Teq.toFixed(0) +
              '°C   ·   gap = ' + (temp - Teq).toFixed(1) + '°';
            raf = requestAnimationFrame(frame);
          }
          raf = requestAnimationFrame(frame);
          return function () { running = false; cancelAnimationFrame(raf); };
        }
        export default { render };
        """
        init_T0 = traitlets.Float(90.0).tag(sync=True)
        init_Tr = traitlets.Float(22.0).tag(sync=True)
        init_k = traitlets.Float(0.10).tag(sync=True)
        init_warmer = traitlets.Bool(False).tag(sync=True)

    return mo.ui.anywidget(_CoolingCoffee(
        init_T0=float(T0), init_Tr=float(Tr), init_k=float(k),
        init_warmer=bool(warmer_on)))


# ---------------------------------------------------------------------------
# 6. Feedback (stars + comment) → Google Form
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
            var eChapter = model.get('e_chapter');
            // If a dedicated chapter field is wired, send the chapter there
            // (clean column). If it ISN'T wired, fold the chapter into the
            // comment so it's never lost — this is the foolproof path that
            // needs only a 2-field form (rating + comment).
            var commentToSend = comment;
            if (chapter && !eChapter) {
              commentToSend = 'Chapter: ' + chapter + (comment ? '\n\n' + comment : '');
            }
            var fd = new FormData();
            if (model.get('e_rating') && rating) fd.append(model.get('e_rating'), String(rating));
            if (model.get('e_comment')) fd.append(model.get('e_comment'), commentToSend);
            if (eChapter) fd.append(eChapter, chapter);
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
