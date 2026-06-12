import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    # Kept for consistency with chapters (and required by the WASM
    # build, whose inliner replaces this exact line).
    import delib
    return delib, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Lab 99 — The animation playground

        **Game-style physics, powered by the equations of this course.**

        This page is a *technology test ground*, not a chapter. Every
        demo below is interactive the way a game is interactive — you
        grab, drag, listen, orbit — and every one of them is secretly
        integrating a differential equation from this course, in
        JavaScript, at 60 frames per second, right in your browser.

        | # | Demo | Tech stack | Underlying DE |
        |---|------|-----------|---------------|
        | 1 | Grab the mass | Canvas 2D + Pointer Events, RK4 in JS | $\ddot x = -\omega_0^2 x - 2\gamma\dot x$ — damped oscillator (Ch 6) |
        | 2 | Hear resonance | Web Audio (OscillatorNode + GainNode) | $\ddot x + 2\gamma\dot x + \omega_0^2 x = F_0\cos(\omega t)$; loudness $\propto A(\omega)$ (Ch 7) |
        | 3 | Lorenz butterfly | Three.js + WebGL + OrbitControls | $\dot x = \sigma(y-x),\ \dot y = x(\rho-z)-y,\ \dot z = xy - \beta z$ (Ch 20) |
        | 4 | Flow you can touch | Canvas 2D + RK2 particle advection | $\ddot\theta = -\sin\theta - 0.15\,\dot\theta$ — damped pendulum (Ch 13) |
        | 5 | A tiny game engine | Matter.js rigid-body engine | $m\ddot{\mathbf x} = \mathbf F$ per body + collision constraints (Ch 4) |
        | 6 | Field, GPU-rendered | WebGL2 + GLSL fragment shader (per-pixel) | $\dot x = y,\ \dot y = \mu(1-x^2)\,y - x$ — Van der Pol (Ch 14) |
        | 7 | Smooth bifurcation | D3.js + SVG `d3.transition()` | $\dot x = r x - x^3$ — pitchfork (Ch 10) |
        | 8 | Sync you can hear | Tone.js (PolySynth) + Canvas 2D | $\dot\theta_i = \omega_i + (K/N)\sum_j \sin(\theta_j - \theta_i)$ — Kuramoto (Ch 14) |
        | 9 | Anatomy of a solution | GSAP 3 timeline + SVG | $x(t) = x_h(t) + x_p(t)$, choreographed (Ch 7) |
        | 10 | Drawn vs solved | lottie-web (keyframes) + Canvas 2D (integrated) | $\ddot y = -g$, restitution $e = 0.75$ — Ch 4 parable |
        | 11 | 120,000 particles | WebGPU + WGSL compute shader | Same damped pendulum as #4, RK2 dispatched GPU-side (Ch 13) |

        If a demo earns its keep, it graduates into a real chapter as a
        `delib` widget. If it doesn't, it dies here, cheaply.
        """
    )
    return


# ============================================================================
# Demo 1 — Grab the mass (Canvas 2D, 60 fps, direct manipulation)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 1 · Grab the mass

        A damped spring-mass from Chapter 6 — except this one you can
        **grab**. Drag the red mass sideways and let go (flick it for
        extra velocity). The motion you see is RK4 integrating
        $\ddot x = -\omega_0^2 x - 2\gamma \dot x$ at 120 steps per
        second, redrawn at 60 fps with `requestAnimationFrame`. The
        sliders change the physics live — set damping to zero and
        flick it.

        *Why it matters:* dragging **is** choosing an initial
        condition. Releasing **is** launching the IVP. Nobody needs to
        be told what $x(0)$ and $\dot x(0)$ mean after doing this.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import anywidget as _aw

    class _SpringGrab(_aw.AnyWidget):
        _esm = """
        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <canvas style="width:100%;max-width:680px;border:1px solid #dde4ec;border-radius:8px;background:#fff;touch-action:none;cursor:grab"></canvas>
              <div style="display:flex;gap:18px;margin-top:6px;flex-wrap:wrap">
                <label>stiffness ω₀ <input type="range" min="0.5" max="4" step="0.1" value="2" data-k="w0"> <span data-v="w0">2.0</span></label>
                <label>damping γ <input type="range" min="0" max="1" step="0.02" value="0.15" data-k="g"> <span data-v="g">0.15</span></label>
              </div>
            </div>`;
          var canvas = el.querySelector('canvas');
          var W = 680, H = 300, dpr = window.devicePixelRatio || 1;
          canvas.width = W * dpr; canvas.height = H * dpr;
          var ctx = canvas.getContext('2d');
          ctx.scale(dpr, dpr);

          var w0 = 2.0, g = 0.15;
          var x = 0.9, v = 0;                  // physical units
          var dragging = false, lastPx = 0, lastT = 0, dragV = 0;
          var anchorX = 60, eqX = W * 0.55, scale = 180;  // px per unit
          var hist = [];

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
            // wall
            ctx.fillStyle = '#7c8aa0';
            ctx.fillRect(anchorX - 10, 60, 10, 110);
            // equilibrium tick
            ctx.strokeStyle = '#c9d4e0'; ctx.setLineDash([4, 4]);
            ctx.beginPath(); ctx.moveTo(eqX, 50); ctx.lineTo(eqX, 185); ctx.stroke();
            ctx.setLineDash([]);
            // spring + mass
            ctx.strokeStyle = '#5b7db1'; ctx.lineWidth = 2.5;
            spring(ctx, anchorX, 115, massPx() - 24, 115, 9);
            ctx.fillStyle = dragging ? '#a13648' : '#d1495b';
            ctx.beginPath(); ctx.arc(massPx(), 115, 24, 0, 6.2832); ctx.fill();
            // sparkline x(t)
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

    spring_grab = _SpringGrab()
    return (spring_grab,)


@app.cell(hide_code=True)
def _(mo, spring_grab):
    mo.ui.anywidget(spring_grab)
    return


# ============================================================================
# Demo 2 — Hear resonance (Web Audio API)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 2 · Hear resonance

        Chapter 7's amplitude curve $A(\omega)$ — but rendered as
        **sound**. Press *enable sound*, then sweep the drive
        frequency. The tone's pitch follows $\omega$; its **loudness
        follows the response amplitude** $A(\omega) =
        F_0/\sqrt{(\omega_0^2-\omega^2)^2 + (2\gamma\omega)^2}$. As
        you sweep through the natural frequency the system *sings*
        at you, then fades as you pass it. Tighten the damping and
        the loud zone narrows.

        *Why it matters:* resonance is fundamentally about a peak in
        a response curve, and your ear is a far better peak detector
        than your eye.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import anywidget as _aw

    class _ResonanceAudio(_aw.AnyWidget):
        _esm = """
        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <canvas style="width:100%;max-width:680px;border:1px solid #dde4ec;border-radius:8px;background:#fff"></canvas>
              <div style="display:flex;gap:18px;margin-top:6px;align-items:center;flex-wrap:wrap">
                <button data-b="snd" style="padding:6px 14px;border:1px solid #c7d2e0;border-radius:6px;background:#f3f7fc;cursor:pointer">🔊 enable sound</button>
                <label>drive ω <input type="range" min="0.2" max="4.5" step="0.02" value="1.0" data-k="om"> <span data-v="om">1.00</span></label>
                <label>damping γ <input type="range" min="0.05" max="0.8" step="0.01" value="0.15" data-k="g"> <span data-v="g">0.15</span></label>
              </div>
            </div>`;
          var canvas = el.querySelector('canvas');
          var W = 680, H = 260, dpr = window.devicePixelRatio || 1;
          canvas.width = W * dpr; canvas.height = H * dpr;
          var ctx2d = canvas.getContext('2d'); ctx2d.scale(dpr, dpr);

          var w0 = 2.0, F0 = 1.0;
          var om = 1.0, g = 0.15;
          var audio = null, osc = null, gain = null;

          function A(w) {
            var d1 = w0 * w0 - w * w, d2 = 2 * g * w;
            return F0 / Math.sqrt(d1 * d1 + d2 * d2);
          }
          function Amax() { return A(Math.sqrt(Math.max(0.01, w0*w0 - 2*g*g))); }

          el.querySelector('[data-b="snd"]').addEventListener('click', function () {
            if (audio) {  // toggle off
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
            var wMax = 4.5, aMax = Amax() * 1.1;
            // axes
            ctx2d.strokeStyle = '#c9d4e0';
            ctx2d.beginPath(); ctx2d.moveTo(L, T); ctx2d.lineTo(L, B); ctx2d.lineTo(R, B); ctx2d.stroke();
            // omega0 marker
            var x0px = L + (R - L) * w0 / wMax;
            ctx2d.setLineDash([4, 4]); ctx2d.strokeStyle = '#9aa7b5';
            ctx2d.beginPath(); ctx2d.moveTo(x0px, T); ctx2d.lineTo(x0px, B); ctx2d.stroke();
            ctx2d.setLineDash([]);
            ctx2d.fillStyle = '#8a96a5'; ctx2d.font = '11px sans-serif';
            ctx2d.fillText('ω₀', x0px + 4, T + 12);
            // amplitude curve
            ctx2d.strokeStyle = '#5b7db1'; ctx2d.lineWidth = 2.5;
            ctx2d.beginPath();
            for (var i = 0; i <= 300; i++) {
              var w = wMax * i / 300;
              var px = L + (R - L) * i / 300;
              var py = B - (B - T) * A(w) / aMax;
              if (i === 0) ctx2d.moveTo(px, py); else ctx2d.lineTo(px, py);
            }
            ctx2d.stroke();
            // current marker, sized by loudness
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

    resonance_audio = _ResonanceAudio()
    return (resonance_audio,)


@app.cell(hide_code=True)
def _(mo, resonance_audio):
    mo.ui.anywidget(resonance_audio)
    return


# ============================================================================
# Demo 3 — The Lorenz butterfly (Three.js / WebGL)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 3 · The Lorenz butterfly, in real 3-D

        The Lorenz system — three coupled ODEs, the original chaos
        demo, and the finale of this course (Ch 20). Two trajectories
        start $0.001$ apart; watch them agree, then split forever.
        **Drag to orbit. Scroll to zoom.** This is Three.js driving
        your GPU through WebGL — the same stack as a browser game.

        *Why it matters:* a 3-D attractor on a 2-D screen is nearly
        unreadable as a static plot. Orbiting it with your hand is
        how you actually see the structure.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import anywidget as _aw

    class _Lorenz3D(_aw.AnyWidget):
        _esm = """
        import * as THREE from "https://esm.sh/three@0.160.0";
        import { OrbitControls } from "https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js";

        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <div data-r style="width:100%;max-width:680px;height:420px;border:1px solid #dde4ec;border-radius:8px;overflow:hidden;background:#fff"></div>
              <div style="margin-top:6px"><button data-b style="padding:6px 14px;border:1px solid #c7d2e0;border-radius:6px;background:#f3f7fc;cursor:pointer">↺ restart</button>
              <span style="color:#8a96a5">  drag = orbit · scroll = zoom</span></div>
            </div>`;
          var host = el.querySelector('[data-r]');
          var Wpx = host.clientWidth || 680, Hpx = 420;

          var scene = new THREE.Scene();
          scene.background = new THREE.Color(0xffffff);
          var camera = new THREE.PerspectiveCamera(45, Wpx / Hpx, 0.1, 1000);
          camera.position.set(70, 40, 110);
          var renderer = new THREE.WebGLRenderer({ antialias: true });
          renderer.setSize(Wpx, Hpx);
          renderer.setPixelRatio(window.devicePixelRatio || 1);
          host.appendChild(renderer.domElement);
          var controls = new OrbitControls(camera, renderer.domElement);
          controls.target.set(0, 0, 25);
          controls.enableDamping = true;

          var SIGMA = 10, RHO = 28, BETA = 8 / 3, MAX = 14000;
          function mkLine(color) {
            var geo = new THREE.BufferGeometry();
            geo.setAttribute('position',
              new THREE.BufferAttribute(new Float32Array(MAX * 3), 3));
            geo.setDrawRange(0, 0);
            return new THREE.Line(geo,
              new THREE.LineBasicMaterial({ color: color }));
          }
          var lineA = mkLine(0x5b7db1), lineB = mkLine(0xd1495b);
          scene.add(lineA); scene.add(lineB);

          var sA, sB, nPts;
          function reset() {
            sA = [1, 1, 20]; sB = [1.001, 1, 20]; nPts = 0;
            lineA.geometry.setDrawRange(0, 0);
            lineB.geometry.setDrawRange(0, 0);
          }
          reset();
          el.querySelector('[data-b]').addEventListener('click', reset);

          function deriv(s) {
            return [SIGMA * (s[1] - s[0]),
                    s[0] * (RHO - s[2]) - s[1],
                    s[0] * s[1] - BETA * s[2]];
          }
          function rk4(s, dt) {
            var k1 = deriv(s);
            var k2 = deriv([s[0]+dt/2*k1[0], s[1]+dt/2*k1[1], s[2]+dt/2*k1[2]]);
            var k3 = deriv([s[0]+dt/2*k2[0], s[1]+dt/2*k2[1], s[2]+dt/2*k2[2]]);
            var k4 = deriv([s[0]+dt*k3[0], s[1]+dt*k3[1], s[2]+dt*k3[2]]);
            return [s[0] + dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0]),
                    s[1] + dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1]),
                    s[2] + dt/6*(k1[2]+2*k2[2]+2*k3[2]+k4[2])];
          }
          function push(line, s, i) {
            var arr = line.geometry.attributes.position.array;
            arr[3*i] = s[0]; arr[3*i+1] = s[2] - 25; arr[3*i+2] = s[1];
            line.geometry.attributes.position.needsUpdate = true;
            line.geometry.setDrawRange(0, i + 1);
          }

          var raf, running = true;
          function frame() {
            if (!running) return;
            for (var k = 0; k < 5 && nPts < MAX; k++) {
              sA = rk4(sA, 0.004); sB = rk4(sB, 0.004);
              push(lineA, sA, nPts); push(lineB, sB, nPts); nPts++;
            }
            controls.update();
            renderer.render(scene, camera);
            raf = requestAnimationFrame(frame);
          }
          frame();
          return function () {
            running = false; cancelAnimationFrame(raf);
            renderer.dispose(); controls.dispose();
          };
        }
        export default { render };
        """

    lorenz3d = _Lorenz3D()
    return (lorenz3d,)


@app.cell(hide_code=True)
def _(lorenz3d, mo):
    mo.ui.anywidget(lorenz3d)
    return


# ============================================================================
# Demo 4 — Flow you can touch (Canvas particle advection)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 4 · Flow you can touch

        The damped pendulum's phase plane —
        $\dot\theta = \omega$, $\dot\omega = -\sin\theta - 0.15\,\omega$
        — rendered as a few hundred glowing particles riding the flow.
        **Click or drag anywhere** to inject particles at that state
        and watch where the flow carries them: small angles spiral
        into the bottom rest point; big pushes whirl over the top a
        few times first.

        *Why it matters:* this is the phase-portrait intuition from
        the qualitative-dynamics chapters, but *felt through the
        fingertip* — you choose the initial condition by touching the
        state space itself.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import anywidget as _aw

    class _PendulumFlow(_aw.AnyWidget):
        _esm = """
        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <canvas style="width:100%;max-width:680px;border:1px solid #dde4ec;border-radius:8px;background:#fff;touch-action:none;cursor:crosshair"></canvas>
              <div style="color:#8a96a5;margin-top:4px">θ (angle) horizontal · ω (angular velocity) vertical · click / drag to release pendulums</div>
            </div>`;
          var canvas = el.querySelector('canvas');
          var W = 680, H = 380, dpr = window.devicePixelRatio || 1;
          canvas.width = W * dpr; canvas.height = H * dpr;
          var ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr);

          var TH = Math.PI * 1.6, OM = 3.2;  // view half-ranges
          function toPx(th, om) {
            return [W/2 + th/TH * (W/2 - 10), H/2 - om/OM * (H/2 - 10)];
          }
          function toState(px, py) {
            return [(px - W/2) / (W/2 - 10) * TH, (H/2 - py) / (H/2 - 10) * OM];
          }
          function f(th, om) { return [om, -Math.sin(th) - 0.15 * om]; }

          // static field layer
          var field = document.createElement('canvas');
          field.width = W * dpr; field.height = H * dpr;
          var fx = field.getContext('2d'); fx.scale(dpr, dpr);
          fx.strokeStyle = 'rgba(124,138,160,0.45)'; fx.lineWidth = 1;
          for (var i = 0; i <= 26; i++) for (var j = 0; j <= 14; j++) {
            var th = -TH + 2*TH*i/26, om = -OM + 2*OM*j/14;
            var d = f(th, om), n = Math.hypot(d[0], d[1]) || 1;
            var p = toPx(th, om);
            var ux = d[0]/n * 9, uy = -d[1]/n * 9;
            fx.beginPath(); fx.moveTo(p[0]-ux/2, p[1]-uy/2);
            fx.lineTo(p[0]+ux/2, p[1]+uy/2); fx.stroke();
          }
          // fixed points
          [[-Math.PI,0],[0,0],[Math.PI,0]].forEach(function (s, idx) {
            var p = toPx(s[0], s[1]);
            fx.beginPath(); fx.arc(p[0], p[1], 6, 0, 6.2832);
            if (idx === 1) { fx.fillStyle = '#2a9d8f'; fx.fill(); }
            else { fx.strokeStyle = '#d1495b'; fx.lineWidth = 2.2;
                   fx.fillStyle = '#fff'; fx.fill(); fx.stroke(); }
          });

          var parts = [];
          function spawn(th, om, n) {
            for (var i = 0; i < n; i++)
              parts.push({ th: th + 0.06*(Math.random()-0.5),
                           om: om + 0.06*(Math.random()-0.5),
                           life: 420 + Math.random() * 240 });
            if (parts.length > 900) parts.splice(0, parts.length - 900);
          }
          for (var i = 0; i < 250; i++)
            spawn((Math.random()-0.5)*2*TH, (Math.random()-0.5)*2*OM, 1);

          var pressing = false;
          function pointerState(e) {
            var r = canvas.getBoundingClientRect();
            return toState((e.clientX-r.left)*(W/r.width), (e.clientY-r.top)*(H/r.height));
          }
          canvas.addEventListener('pointerdown', function (e) {
            pressing = true; var s = pointerState(e); spawn(s[0], s[1], 24);
          });
          canvas.addEventListener('pointermove', function (e) {
            if (pressing) { var s = pointerState(e); spawn(s[0], s[1], 6); }
          });
          window.addEventListener('pointerup', function () { pressing = false; });

          // background with first paint
          ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H);
          var raf, running = true;
          function frame() {
            if (!running) return;
            // fade trails
            ctx.fillStyle = 'rgba(255,255,255,0.16)';
            ctx.fillRect(0, 0, W, H);
            ctx.drawImage(field, 0, 0, W, H);

            var dt = 0.025;
            ctx.fillStyle = '#5b7db1';
            for (var i = parts.length - 1; i >= 0; i--) {
              var p = parts[i];
              var k1 = f(p.th, p.om);
              var k2 = f(p.th + dt*k1[0], p.om + dt*k1[1]);
              p.th += dt/2 * (k1[0] + k2[0]);
              p.om += dt/2 * (k1[1] + k2[1]);
              p.life--;
              if (p.life <= 0 || Math.abs(p.om) > OM*1.2) { parts.splice(i, 1); continue; }
              if (p.th > TH) p.th -= 2*TH;       // wrap angle
              if (p.th < -TH) p.th += 2*TH;
              var q = toPx(p.th, p.om);
              ctx.beginPath(); ctx.arc(q[0], q[1], 1.8, 0, 6.2832); ctx.fill();
            }
            while (parts.length < 250)
              spawn((Math.random()-0.5)*2*TH, (Math.random()-0.5)*2*OM, 1);

            raf = requestAnimationFrame(frame);
          }
          frame();
          return function () { running = false; cancelAnimationFrame(raf); };
        }
        export default { render };
        """

    pendulum_flow = _PendulumFlow()
    return (pendulum_flow,)


@app.cell(hide_code=True)
def _(mo, pendulum_flow):
    mo.ui.anywidget(pendulum_flow)
    return


# ============================================================================
# Demo 5 — A tiny game engine (Matter.js)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 5 · A tiny game engine

        An actual rigid-body physics engine — Matter.js, the kind of
        library 2-D browser games are built on. **Drag the boxes and
        balls around, fling them, stack them.** Press *drop more* to
        add bodies.

        *Why it matters:* this is Chapter 4's punchline made
        playable. Under the hood, Matter.js is stepping Newton's
        $m\ddot{\mathbf x} = \mathbf F$ for every body, every frame —
        the same walk-the-field numerical integration you derived,
        plus collision constraints. Every physics game you've ever
        played is a differential-equation solver with a renderer
        attached.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import anywidget as _aw

    class _MatterPlayground(_aw.AnyWidget):
        _esm = """
        import Matter from "https://esm.sh/matter-js@0.19.0";

        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <div data-r style="width:100%;max-width:680px;border:1px solid #dde4ec;border-radius:8px;overflow:hidden"></div>
              <div style="margin-top:6px"><button data-b style="padding:6px 14px;border:1px solid #c7d2e0;border-radius:6px;background:#f3f7fc;cursor:pointer">⬇ drop more</button>
              <span style="color:#8a96a5">  drag bodies with the mouse</span></div>
            </div>`;
          var host = el.querySelector('[data-r]');
          var W = host.clientWidth || 680, H = 400;

          var engine = Matter.Engine.create();
          var render2 = Matter.Render.create({
            element: host, engine: engine,
            options: { width: W, height: H, wireframes: false,
                       background: '#ffffff' },
          });

          var palette = ['#5b7db1', '#d1495b', '#2a9d8f', '#e9a23b', '#7c8aa0'];
          function col() { return palette[Math.floor(Math.random()*palette.length)]; }
          function body(x, y) {
            return Math.random() < 0.5
              ? Matter.Bodies.rectangle(x, y, 30+Math.random()*40, 30+Math.random()*40,
                  { restitution: 0.4, render: { fillStyle: col() } })
              : Matter.Bodies.circle(x, y, 14+Math.random()*16,
                  { restitution: 0.65, render: { fillStyle: col() } });
          }

          var world = engine.world;
          Matter.Composite.add(world, [
            Matter.Bodies.rectangle(W/2, H-10, W, 20, { isStatic: true,
              render: { fillStyle: '#7c8aa0' } }),
            Matter.Bodies.rectangle(10, H/2, 20, H, { isStatic: true,
              render: { fillStyle: '#dde4ec' } }),
            Matter.Bodies.rectangle(W-10, H/2, 20, H, { isStatic: true,
              render: { fillStyle: '#dde4ec' } }),
            Matter.Bodies.rectangle(W*0.32, H*0.62, W*0.4, 14, { isStatic: true,
              angle: 0.32, render: { fillStyle: '#9aa7b5' } }),
            Matter.Bodies.rectangle(W*0.72, H*0.36, W*0.36, 14, { isStatic: true,
              angle: -0.28, render: { fillStyle: '#9aa7b5' } }),
          ]);
          function drop(n) {
            for (var i = 0; i < n; i++)
              Matter.Composite.add(world, body(60+Math.random()*(W-120), -20-Math.random()*120));
          }
          drop(10);
          el.querySelector('[data-b]').addEventListener('click', function () { drop(8); });

          var mouse = Matter.Mouse.create(render2.canvas);
          var mc = Matter.MouseConstraint.create(engine, {
            mouse: mouse, constraint: { stiffness: 0.2,
                                        render: { visible: false } },
          });
          Matter.Composite.add(world, mc);
          render2.mouse = mouse;

          var runner = Matter.Runner.create();
          Matter.Runner.run(runner, engine);
          Matter.Render.run(render2);

          return function () {
            Matter.Render.stop(render2);
            Matter.Runner.stop(runner);
            Matter.Engine.clear(engine);
            render2.canvas.remove();
          };
        }
        export default { render };
        """

    matter_playground = _MatterPlayground()
    return (matter_playground,)


@app.cell(hide_code=True)
def _(matter_playground, mo):
    mo.ui.anywidget(matter_playground)
    return


# ============================================================================
# Demo 6 — Slope field on the GPU (WebGL2 fragment shader)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 6 · The field, rendered by the GPU

        The Van der Pol oscillator's phase plane,
        $\dot x = y,\ \dot y = \mu(1 - x^2)\,y - x$ — but instead of
        drawing a sparse arrow at each grid point, this version
        evaluates $(\dot x, \dot y)$ at **every single pixel** via a
        fragment shader running on your graphics card. Hue tracks
        the direction of the flow; brightness tracks the speed.
        Scrub $\mu$ and the entire field recolors instantly.

        On top, ~300 test particles ride the flow — RK4 in
        JavaScript on the CPU, drawn over the GPU-rendered field
        each frame. At $\mu = 0$ they orbit; ramp $\mu$ up and you
        see them get pulled onto a limit cycle.

        *Why it matters:* a Plotly slope-field is a fixed grid of
        arrows; a shader is *the entire plane*, continuous, at
        millions of samples per second. This is the technique
        scientific-visualization apps use for fluid sim, wind
        fields, and electromagnetic vectors.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import anywidget as _aw

    class _ShaderField(_aw.AnyWidget):
        _esm = r"""
        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <div data-r style="position:relative;width:100%;max-width:680px;height:420px;border:1px solid #dde4ec;border-radius:8px;overflow:hidden;background:#0c1118">
                <canvas data-gl style="position:absolute;inset:0;width:100%;height:100%"></canvas>
                <canvas data-px style="position:absolute;inset:0;width:100%;height:100%"></canvas>
              </div>
              <div style="display:flex;gap:18px;margin-top:6px;flex-wrap:wrap">
                <label>μ (vdP) <input type="range" min="0" max="3.5" step="0.05" value="0.6" data-k="mu"> <span data-v="mu">0.60</span></label>
                <span style="color:#8a96a5">  hue = direction · brightness = speed</span>
              </div>
            </div>`;
          var host = el.querySelector('[data-r]');
          var W = host.clientWidth || 680, H = 420;
          var glC = el.querySelector('[data-gl]'), pxC = el.querySelector('[data-px]');
          var dpr = window.devicePixelRatio || 1;
          [glC, pxC].forEach(function (c) { c.width = W * dpr; c.height = H * dpr; });
          var ctx = pxC.getContext('2d'); ctx.scale(dpr, dpr);
          var gl = glC.getContext('webgl2');
          if (!gl) { ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H);
            ctx.fillStyle = '#333'; ctx.font = '14px sans-serif';
            ctx.fillText('WebGL2 not available — try a recent browser', 20, 30);
            return function () {}; }

          var mu = 0.6;
          var XR = 3.2, YR = 3.2;       // half-ranges

          var vs = `#version 300 es
            in vec2 a_pos;
            out vec2 v_p;
            uniform vec2 u_range;
            void main() {
              v_p = a_pos * u_range;
              gl_Position = vec4(a_pos, 0.0, 1.0);
            }`;
          var fs = `#version 300 es
            precision highp float;
            in vec2 v_p;
            uniform float u_mu;
            out vec4 outColor;
            vec3 hsv2rgb(vec3 c) {
              vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
              vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
              return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
            }
            void main() {
              float fx = v_p.y;
              float fy = u_mu * (1.0 - v_p.x * v_p.x) * v_p.y - v_p.x;
              float mag = length(vec2(fx, fy));
              float ang = atan(fy, fx);
              float hue = ang / 6.283185 + 0.5;
              float bright = 0.18 + 0.72 * (mag / (mag + 1.6));
              outColor = vec4(hsv2rgb(vec3(hue, 0.85, bright)), 1.0);
            }`;
          function shader(type, src) {
            var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
            if (!gl.getShaderParameter(s, gl.COMPILE_STATUS))
              console.error(gl.getShaderInfoLog(s));
            return s;
          }
          var prog = gl.createProgram();
          gl.attachShader(prog, shader(gl.VERTEX_SHADER, vs));
          gl.attachShader(prog, shader(gl.FRAGMENT_SHADER, fs));
          gl.linkProgram(prog); gl.useProgram(prog);
          var quad = new Float32Array([-1,-1, 1,-1, -1,1, -1,1, 1,-1, 1,1]);
          var vbo = gl.createBuffer();
          gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
          gl.bufferData(gl.ARRAY_BUFFER, quad, gl.STATIC_DRAW);
          var loc = gl.getAttribLocation(prog, 'a_pos');
          gl.enableVertexAttribArray(loc);
          gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
          var uMu = gl.getUniformLocation(prog, 'u_mu');
          var uRange = gl.getUniformLocation(prog, 'u_range');
          gl.uniform2f(uRange, XR, YR);
          gl.viewport(0, 0, glC.width, glC.height);

          function renderField() {
            gl.uniform1f(uMu, mu);
            gl.drawArrays(gl.TRIANGLES, 0, 6);
          }

          el.querySelector('input').addEventListener('input', function () {
            mu = parseFloat(this.value);
            el.querySelector('[data-v="mu"]').textContent = mu.toFixed(2);
            renderField();
          });
          renderField();

          // CPU particle layer
          function rhs(x, y) {
            return [y, mu * (1.0 - x * x) * y - x];
          }
          function step(p, dt) {
            var k1 = rhs(p.x, p.y);
            var k2 = rhs(p.x + dt/2 * k1[0], p.y + dt/2 * k1[1]);
            var k3 = rhs(p.x + dt/2 * k2[0], p.y + dt/2 * k2[1]);
            var k4 = rhs(p.x + dt * k3[0], p.y + dt * k3[1]);
            p.x += dt/6 * (k1[0]+2*k2[0]+2*k3[0]+k4[0]);
            p.y += dt/6 * (k1[1]+2*k2[1]+2*k3[1]+k4[1]);
            p.life--;
          }
          var parts = [];
          function spawn() {
            parts.push({ x: (Math.random()-0.5) * 2 * XR,
                         y: (Math.random()-0.5) * 2 * YR,
                         life: 200 + Math.random() * 300 });
          }
          for (var i = 0; i < 320; i++) spawn();
          function toPx(x, y) {
            return [W/2 + x / XR * (W/2), H/2 - y / YR * (H/2)];
          }
          ctx.fillStyle = 'rgba(0,0,0,0)'; ctx.fillRect(0,0,W,H);

          var raf, running = true;
          function frame() {
            if (!running) return;
            ctx.fillStyle = 'rgba(12,17,24,0.18)';
            ctx.fillRect(0, 0, W, H);
            for (var i = parts.length - 1; i >= 0; i--) {
              var p = parts[i];
              step(p, 0.025);
              if (p.life <= 0 || Math.abs(p.x) > XR * 1.1 || Math.abs(p.y) > YR * 1.1) {
                parts.splice(i, 1); spawn(); continue;
              }
              var q = toPx(p.x, p.y);
              ctx.fillStyle = 'rgba(255,255,255,0.85)';
              ctx.beginPath(); ctx.arc(q[0], q[1], 1.4, 0, 6.2832); ctx.fill();
            }
            raf = requestAnimationFrame(frame);
          }
          frame();
          return function () { running = false; cancelAnimationFrame(raf); };
        }
        export default { render };
        """

    shader_field = _ShaderField()
    return (shader_field,)


@app.cell(hide_code=True)
def _(mo, shader_field):
    mo.ui.anywidget(shader_field)
    return


# ============================================================================
# Demo 7 — Smooth bifurcation (D3 SVG transitions)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 7 · The bifurcation, animated by D3

        The pitchfork bifurcation $\dot x = rx - x^3$ — Chapter 10's
        bread and butter. The equilibria are at $x^* = 0$ (always)
        and $x^* = \pm\sqrt{r}$ (only when $r > 0$). Stability: the
        centre point is stable when $r < 0$, unstable when $r > 0$;
        the side points (when they exist) are always stable.

        Drag the $r$ slider. The phase-line dots **smoothly slide**
        into place — that's the signature D3 move, *data-driven
        transitions on SVG*. As $r$ crosses zero, the centre dot
        switches from filled (stable) to open (unstable), and two
        new stable dots **emerge from it** and slide outward. Pull
        $r$ back and they slide home and merge.

        *Why it matters:* D3 is what the New York Times, FiveThirty
        Eight, and the Financial Times use. Plotly redraws on every
        update; D3 *interpolates*, so transitions are smooth and
        narratively legible. The choreography itself communicates
        what's happening — dots emerging from a point *is* the
        bifurcation.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import anywidget as _aw

    class _BifurcationD3(_aw.AnyWidget):
        _esm = r"""
        import * as d3 from "https://esm.sh/d3@7.8.5";

        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <div data-r style="width:100%;max-width:680px;border:1px solid #dde4ec;border-radius:8px;background:#fff"></div>
              <div style="display:flex;gap:18px;margin-top:6px;align-items:center;flex-wrap:wrap">
                <label>r <input type="range" min="-2" max="2" step="0.02" value="-1.0" style="width:280px" data-k="r"> <span data-v="r">−1.00</span></label>
                <span style="color:#8a96a5">  drag to move through the bifurcation</span>
              </div>
            </div>`;
          var host = el.querySelector('[data-r]');
          var W = host.clientWidth || 680, H = 320;
          var svg = d3.select(host).append('svg')
            .attr('width', W).attr('height', H)
            .style('display', 'block');

          var R_MIN = -2, R_MAX = 2;
          var X_MIN = -1.6, X_MAX = 1.6;
          var pad = { l: 50, r: 30, t: 25, b: 40 };
          // Right panel: bifurcation diagram (r horizontal, x* vertical).
          var bw = 280;
          var rScale = d3.scaleLinear().domain([R_MIN, R_MAX])
            .range([W - bw - pad.r, W - pad.r]);
          var xScale = d3.scaleLinear().domain([X_MIN, X_MAX])
            .range([H - pad.b, pad.t]);
          // Left panel: phase line (x* on a horizontal axis).
          var plScale = d3.scaleLinear().domain([X_MIN, X_MAX])
            .range([pad.l, W - bw - pad.r - 30]);
          var plY = H / 2;

          // Axes / labels
          svg.append('g').attr('transform', 'translate(0,' + (H - pad.b) + ')')
            .call(d3.axisBottom(rScale).ticks(5)).attr('color', '#7c8aa0');
          svg.append('g').attr('transform', 'translate(' + (W - bw - pad.r) + ',0)')
            .call(d3.axisLeft(xScale).ticks(5)).attr('color', '#7c8aa0');
          svg.append('text').attr('x', W - bw/2 - pad.r).attr('y', H - 6)
            .attr('fill', '#666').attr('font-size', 11).attr('text-anchor', 'middle')
            .text('parameter r');
          svg.append('text').attr('x', W - bw - pad.r - 28).attr('y', pad.t - 8)
            .attr('fill', '#666').attr('font-size', 11).attr('text-anchor', 'end')
            .text('x*');
          svg.append('text').attr('x', plScale(0)).attr('y', plY - 26)
            .attr('fill', '#666').attr('font-size', 11).attr('text-anchor', 'middle')
            .text('phase line of  ẋ = r x − x³');
          svg.append('line').attr('x1', plScale(X_MIN)).attr('x2', plScale(X_MAX))
            .attr('y1', plY).attr('y2', plY)
            .attr('stroke', '#9aa7b5').attr('stroke-width', 1.2);
          svg.append('text').attr('x', plScale(X_MIN)).attr('y', plY + 22)
            .attr('fill', '#7c8aa0').attr('font-size', 11).text(X_MIN.toFixed(1));
          svg.append('text').attr('x', plScale(X_MAX)).attr('y', plY + 22)
            .attr('fill', '#7c8aa0').attr('font-size', 11).attr('text-anchor', 'end')
            .text(X_MAX.toFixed(1));

          // Static bifurcation curves on the right panel.
          var rs = d3.range(0, 2.001, 0.02);
          var lineUp = d3.line().x(function (r) { return rScale(r); })
            .y(function (r) { return xScale(Math.sqrt(r)); });
          var lineDown = d3.line().x(function (r) { return rScale(r); })
            .y(function (r) { return xScale(-Math.sqrt(r)); });
          svg.append('path').attr('d', lineUp(rs))
            .attr('stroke', '#2a9d8f').attr('stroke-width', 2.5).attr('fill', 'none');
          svg.append('path').attr('d', lineDown(rs))
            .attr('stroke', '#2a9d8f').attr('stroke-width', 2.5).attr('fill', 'none');
          svg.append('line').attr('x1', rScale(R_MIN)).attr('x2', rScale(0))
            .attr('y1', xScale(0)).attr('y2', xScale(0))
            .attr('stroke', '#2a9d8f').attr('stroke-width', 2.5);
          svg.append('line').attr('x1', rScale(0)).attr('x2', rScale(R_MAX))
            .attr('y1', xScale(0)).attr('y2', xScale(0))
            .attr('stroke', '#d1495b').attr('stroke-width', 2).attr('stroke-dasharray', '4,3');

          // Cursor and dot groups.
          var cursor = svg.append('line')
            .attr('stroke', '#9aa7b5').attr('stroke-width', 1.4).attr('stroke-dasharray', '3,3');
          var plDots = svg.append('g');
          var bdDots = svg.append('g');

          function eqs(r) {
            // Always three slots so D3 has stable keys for transitions.
            var center = { id: 'c', x: 0, stable: r < 0, exists: true };
            var plus  = { id: 'p', x: r > 0 ? Math.sqrt(r) : 0,
                          stable: true, exists: r > 0 };
            var minus = { id: 'm', x: r > 0 ? -Math.sqrt(r) : 0,
                          stable: true, exists: r > 0 };
            return [center, plus, minus];
          }

          function update(r, immediate) {
            var data = eqs(r);
            var T = immediate ? 0 : 360;

            // Cursor line on right panel
            cursor.transition().duration(T)
              .attr('x1', rScale(r)).attr('x2', rScale(r))
              .attr('y1', pad.t).attr('y2', H - pad.b);

            // Phase-line dots (left panel)
            var sel = plDots.selectAll('circle').data(data, function (d) { return d.id; });
            sel.enter().append('circle')
              .attr('cx', function (d) { return plScale(d.x); })
              .attr('cy', plY)
              .attr('r', 9)
              .attr('fill', function (d) { return d.stable ? '#2a9d8f' : 'white'; })
              .attr('stroke', function (d) { return d.stable ? '#2a9d8f' : '#d1495b'; })
              .attr('stroke-width', 2.5)
              .attr('opacity', function (d) { return d.exists ? 1 : 0; })
              .merge(sel)
              .transition().duration(T)
              .attr('cx', function (d) { return plScale(d.x); })
              .attr('opacity', function (d) { return d.exists ? 1 : 0; })
              .attr('fill', function (d) { return d.stable ? '#2a9d8f' : 'white'; })
              .attr('stroke', function (d) { return d.stable ? '#2a9d8f' : '#d1495b'; });

            // Bifurcation-diagram dots (right panel, dressed-down)
            var bs = bdDots.selectAll('circle').data(data, function (d) { return d.id; });
            bs.enter().append('circle')
              .attr('cx', rScale(r))
              .attr('cy', function (d) { return xScale(d.x); })
              .attr('r', 5.5)
              .attr('fill', function (d) { return d.stable ? '#2a9d8f' : 'white'; })
              .attr('stroke', function (d) { return d.stable ? '#2a9d8f' : '#d1495b'; })
              .attr('stroke-width', 2)
              .attr('opacity', function (d) { return d.exists ? 1 : 0; })
              .merge(bs)
              .transition().duration(T)
              .attr('cx', rScale(r))
              .attr('cy', function (d) { return xScale(d.x); })
              .attr('opacity', function (d) { return d.exists ? 1 : 0; })
              .attr('fill', function (d) { return d.stable ? '#2a9d8f' : 'white'; })
              .attr('stroke', function (d) { return d.stable ? '#2a9d8f' : '#d1495b'; });
          }
          update(-1.0, true);

          el.querySelector('input').addEventListener('input', function () {
            var r = parseFloat(this.value);
            el.querySelector('[data-v="r"]').textContent =
              (r < 0 ? '−' : '') + Math.abs(r).toFixed(2);
            update(r, false);
          });
          return function () { svg.remove(); };
        }
        export default { render };
        """

    bifurcation_d3 = _BifurcationD3()
    return (bifurcation_d3,)


@app.cell(hide_code=True)
def _(bifurcation_d3, mo):
    mo.ui.anywidget(bifurcation_d3)
    return


# ============================================================================
# Demo 8 — Coupled oscillators that synchronize (Tone.js)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 8 · Synchronization you can hear

        Five Kuramoto phase oscillators on the unit circle:

        $$
        \dot\theta_i \;=\; \omega_i \;+\; \frac{K}{N}\sum_j \sin(\theta_j - \theta_i).
        $$

        Each oscillator has a slightly different natural frequency
        $\omega_i$ — left to themselves they drift apart and never
        agree. **Each one plays a different pentatonic note as it
        passes the top of the circle.** With coupling $K = 0$ the
        notes scatter randomly; turn $K$ up and watch (and listen
        to) the dots **pull each other into a single cluster** —
        the chord turns into a unified rhythm. The big red arrow is
        the **order parameter**, the centroid; its length is how
        synchronized the population is.

        *Why it matters:* this is the central phenomenon in Chapter
        14 territory (coupled oscillators, fireflies, neurons,
        Tacoma Narrows again — different mechanism but the same
        word), and it is *much* clearer through your ears than
        through your eyes. Tone.js is the abstraction over Web
        Audio that makes scheduling musical events painless.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import anywidget as _aw

    class _KuramotoSync(_aw.AnyWidget):
        _esm = r"""
        import * as Tone from "https://esm.sh/tone@14.8.49";

        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <canvas style="width:100%;max-width:680px;border:1px solid #dde4ec;border-radius:8px;background:#fff;display:block"></canvas>
              <div style="display:flex;gap:18px;margin-top:6px;align-items:center;flex-wrap:wrap">
                <button data-b="snd" style="padding:6px 14px;border:1px solid #c7d2e0;border-radius:6px;background:#f3f7fc;cursor:pointer">🔊 enable sound</button>
                <label>coupling K <input type="range" min="0" max="2" step="0.02" value="0" data-k="K"> <span data-v="K">0.00</span></label>
                <button data-b="reset" style="padding:6px 14px;border:1px solid #c7d2e0;border-radius:6px;background:#f3f7fc;cursor:pointer">↺ reseed</button>
              </div>
            </div>`;
          var canvas = el.querySelector('canvas');
          var W = 680, H = 380, dpr = window.devicePixelRatio || 1;
          canvas.width = W * dpr; canvas.height = H * dpr;
          var ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr);

          var N = 5, K = 0;
          var palette = ['#5b7db1', '#d1495b', '#2a9d8f', '#e9a23b', '#7c8aa0'];
          var pentatonic = ['C4', 'D4', 'E4', 'G4', 'A4'];
          var omega, theta, prevSin;
          function reseed() {
            omega = []; theta = []; prevSin = [];
            for (var i = 0; i < N; i++) {
              omega.push(0.85 + 0.3 * i / (N - 1));
              theta.push(Math.random() * 6.2832);
              prevSin.push(Math.sin(theta[i]));
            }
          }
          reseed();

          var synth = null, sndOn = false;
          el.querySelector('[data-b="snd"]').addEventListener('click', async function () {
            if (!sndOn) {
              await Tone.start();
              synth = new Tone.PolySynth(Tone.Synth, {
                oscillator: { type: 'triangle' },
                envelope: { attack: 0.004, decay: 0.18, sustain: 0.0, release: 0.18 },
              }).toDestination();
              synth.volume.value = -10;
              sndOn = true;
              this.textContent = '🔇 mute';
            } else {
              if (synth) synth.dispose();
              synth = null; sndOn = false;
              this.textContent = '🔊 enable sound';
            }
          });
          el.querySelector('[data-b="reset"]').addEventListener('click', reseed);
          el.querySelector('input').addEventListener('input', function () {
            K = parseFloat(this.value);
            el.querySelector('[data-v="K"]').textContent = K.toFixed(2);
          });

          var cx = 220, cy = H / 2, R = 130;
          var lastNote = [0, 0, 0, 0, 0];

          function step(dt) {
            // Standard Kuramoto with mean-field coupling
            var dtheta = new Array(N).fill(0);
            for (var i = 0; i < N; i++) {
              var s = 0;
              for (var j = 0; j < N; j++) s += Math.sin(theta[j] - theta[i]);
              dtheta[i] = omega[i] + (K / N) * s;
            }
            for (var i = 0; i < N; i++) {
              var ps = prevSin[i];
              theta[i] = (theta[i] + dtheta[i] * dt) % (2 * Math.PI);
              if (theta[i] < 0) theta[i] += 2 * Math.PI;
              var ns = Math.sin(theta[i]);
              // Trigger note at top crossing (theta passing through pi/2 upward)
              var now = performance.now();
              if (ps < 1 && Math.cos(theta[i]) > 0 && Math.sin(theta[i]) > 0.98
                  && now - lastNote[i] > 120) {
                if (sndOn && synth) {
                  try { synth.triggerAttackRelease(pentatonic[i], '16n'); } catch (e) {}
                }
                lastNote[i] = now;
              }
              prevSin[i] = ns;
            }
          }

          function order() {
            var sx = 0, sy = 0;
            for (var i = 0; i < N; i++) { sx += Math.cos(theta[i]); sy += Math.sin(theta[i]); }
            return { r: Math.hypot(sx, sy) / N, psi: Math.atan2(sy, sx) };
          }

          function draw() {
            ctx.clearRect(0, 0, W, H);
            // Unit circle
            ctx.strokeStyle = '#c9d4e0'; ctx.lineWidth = 1.4;
            ctx.beginPath(); ctx.arc(cx, cy, R, 0, 6.2832); ctx.stroke();
            // ghost notes at the top
            ctx.fillStyle = '#9aa7b5'; ctx.font = '11px sans-serif';
            ctx.fillText('▴ note triggers when an oscillator passes here', cx - 100, cy - R - 8);
            // Oscillator dots
            for (var i = 0; i < N; i++) {
              var x = cx + R * Math.cos(theta[i] - Math.PI / 2);
              var y = cy - R * Math.sin(theta[i] - Math.PI / 2);
              ctx.fillStyle = palette[i];
              ctx.beginPath(); ctx.arc(x, y, 9, 0, 6.2832); ctx.fill();
            }
            // Order parameter
            var o = order();
            var ox = cx + R * o.r * Math.cos(o.psi - Math.PI / 2);
            var oy = cy - R * o.r * Math.sin(o.psi - Math.PI / 2);
            ctx.strokeStyle = '#d1495b'; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(ox, oy); ctx.stroke();
            ctx.fillStyle = '#d1495b';
            ctx.beginPath(); ctx.arc(ox, oy, 5, 0, 6.2832); ctx.fill();

            // Sidebar text
            ctx.fillStyle = '#333'; ctx.font = '13px sans-serif';
            ctx.fillText('order parameter  r = ' + o.r.toFixed(2),
                         cx + R + 50, cy - 60);
            ctx.font = '11px sans-serif'; ctx.fillStyle = '#7c8aa0';
            ctx.fillText('(1 = fully sync, 0 = scattered)', cx + R + 50, cy - 40);
            // Mini bar
            ctx.fillStyle = '#e3e9f0';
            ctx.fillRect(cx + R + 50, cy - 20, 180, 14);
            ctx.fillStyle = '#d1495b';
            ctx.fillRect(cx + R + 50, cy - 20, 180 * o.r, 14);

            ctx.fillStyle = '#333'; ctx.font = '13px sans-serif';
            ctx.fillText('K = ' + K.toFixed(2), cx + R + 50, cy + 20);
            ctx.font = '11px sans-serif'; ctx.fillStyle = '#7c8aa0';
            ctx.fillText('critical coupling  K_c ≈ 0.06', cx + R + 50, cy + 40);
          }

          var raf, running = true;
          function frame() {
            if (!running) return;
            step(1 / 60);
            draw();
            raf = requestAnimationFrame(frame);
          }
          frame();
          return function () {
            running = false; cancelAnimationFrame(raf);
            if (synth) synth.dispose();
          };
        }
        export default { render };
        """

    kuramoto_sync = _KuramotoSync()
    return (kuramoto_sync,)


@app.cell(hide_code=True)
def _(kuramoto_sync, mo):
    mo.ui.anywidget(kuramoto_sync)
    return


# ============================================================================
# Demo 9 — Anatomy of a solution (GSAP timeline choreography)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 9 · Anatomy of a solution, choreographed

        Chapter 7 says every driven solution is a sum:
        $x(t) = x_h(t) + x_p(t)$ — a transient that dies plus a
        steady state that lives. This demo *performs* that sentence
        as a four-act story, choreographed with **GSAP**, the
        animation library behind most award-winning marketing sites:

        1. the full solution draws itself in,
        2. it **splits** into its two components, which slide apart,
        3. the transient visibly **fades to nothing** while a time
           cursor sweeps,
        4. the steady state slides back up — it alone remains.

        Press ▶, or drag the scrubber to any point in the story.

        *Why it matters:* unlike every other demo here, nothing is
        being integrated during the animation — the curves are
        precomputed, and GSAP choreographs *narrative emphasis*:
        what appears when, what fades, what moves where. That's a
        different tool for a different job: storytelling beats.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import anywidget as _aw

    class _GsapAnatomy(_aw.AnyWidget):
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

          // --- precompute the three curves (RK4; omega0=2, gamma=0.25,
          //     omega=1.2, F0=1, from rest) --------------------------------
          var w0 = 2, g = 0.25, om = 1.2, F0 = 1;
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
          function path(arr, y0, sc) {
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

          var mid = H / 2, sc = 95;
          var fullP  = mkPath(path(xs, mid, sc), '#5b7db1', 3);
          var transP = mkPath(path(hs, mid, sc), '#b5651d', 2.2);
          var stdyP  = mkPath(path(ps, mid, sc), '#2a9d8f', 2.2);
          var fullL  = mkText('x(t) — the full solution', 44, 34, '#5b7db1');
          var transL = mkText('x_h — transient (Ch 6, dies)', 44, 34, '#b5651d');
          var stdyL  = mkText('x_p — steady state (locked to the drive)', 44, 34, '#2a9d8f');
          var cursor = document.createElementNS(NS, 'line');
          cursor.setAttribute('y1', 24); cursor.setAttribute('y2', H - 16);
          cursor.setAttribute('x1', 40); cursor.setAttribute('x2', 40);
          cursor.setAttribute('stroke', '#9aa7b5'); cursor.setAttribute('stroke-width', 1.4);
          cursor.setAttribute('opacity', 0);
          svg.appendChild(cursor);

          // Initial state: components hidden, full curve undrawn.
          var len = fullP.getTotalLength();
          gsap.set(fullP, { strokeDasharray: len, strokeDashoffset: len });
          gsap.set([transP, stdyP], { opacity: 0 });
          gsap.set(fullL, { opacity: 0 });

          var actEl = el.querySelector('[data-v="act"]');
          function act(s) { return function () { actEl.textContent = s; }; }

          var tl = gsap.timeline({ paused: true });
          // Act 1 — draw the full solution
          tl.call(act('act 1 · the full solution'))
            .to(fullP, { strokeDashoffset: 0, duration: 2.2, ease: 'power1.inOut' })
            .to(fullL, { opacity: 1, duration: 0.4 }, '<0.8')
            .to({}, { duration: 0.6 });
          // Act 2 — split into components
          tl.call(act('act 2 · split into x_h + x_p'))
            .to([transP, stdyP], { opacity: 1, duration: 0.5 })
            .to(transP, { y: -105, duration: 1.1, ease: 'power2.inOut' }, '<')
            .to(stdyP,  { y: 105, duration: 1.1, ease: 'power2.inOut' }, '<')
            .to(fullP,  { opacity: 0.22, duration: 0.8 }, '<')
            .to(fullL,  { opacity: 0.25, duration: 0.8 }, '<')
            .to(transL, { opacity: 1, y: -105, duration: 0.6 }, '<0.3')
            .to(stdyL,  { opacity: 1, y: 105, duration: 0.6 }, '<')
            .to({}, { duration: 0.6 });
          // Act 3 — the transient dies as time sweeps
          tl.call(act('act 3 · the transient dies'))
            .to(cursor, { opacity: 1, duration: 0.3 })
            .to(cursor, { attr: { x1: W - 40, x2: W - 40 },
                          duration: 2.6, ease: 'none' })
            .to(transP, { opacity: 0.06, duration: 2.2, ease: 'power1.in' }, '<0.4')
            .to(transL, { opacity: 0.15, duration: 2.2 }, '<')
            .to(cursor, { opacity: 0, duration: 0.3 });
          // Act 4 — the steady state alone remains
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
          tl.eventCallback('onUpdate', function () {
            scrub.value = tl.progress();
          });
          tl.eventCallback('onComplete', function () {
            btn.textContent = '▶ replay';
          });
          scrub.addEventListener('input', function () {
            tl.pause(); btn.textContent = '▶ play the story';
            tl.progress(parseFloat(this.value));
          });

          return function () { tl.kill(); svg.remove(); };
        }
        export default { render };
        """

    gsap_anatomy = _GsapAnatomy()
    return (gsap_anatomy,)


@app.cell(hide_code=True)
def _(gsap_anatomy, mo):
    mo.ui.anywidget(gsap_anatomy)
    return


# ============================================================================
# Demo 10 — Drawn vs solved (Lottie keyframes next to a real integrator)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 10 · Drawn vs solved — spot the imposter

        Two bouncing balls. The **left one is a Lottie animation** —
        the After Effects-style keyframe format that powers most
        animated icons and loading spinners on the modern web. A
        designer (here: a JSON literal written by hand) *chose*
        where the ball is at each keyframe and let the player
        interpolate. The **right one is solved**: the browser is
        integrating $\ddot y = -g$ with a coefficient-of-restitution
        bounce, every frame.

        Watch a few loops and the difference surfaces. The solved
        ball's bounce heights decay *geometrically* — each apex is
        $e^2 = 0.56$ times the previous, because the physics says
        so. The drawn ball's heights are whatever the designer
        picked, and its rhythm subtly fails the physics test
        (real ballistic flight spends *more* time near the apex
        than keyframe easing tends to give it).

        *Why it matters:* Lottie is the right tool for chapter-
        opener art, icons, and decorative motion — and exactly the
        wrong tool for the math itself. This demo is the
        distinction made visible.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import anywidget as _aw

    class _LottieVsSolved(_aw.AnyWidget):
        _esm = r"""
        import lottie from "https://esm.sh/lottie-web@5.12.2";

        function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <div style="display:flex;gap:10px;flex-wrap:wrap">
                <div style="flex:1;min-width:280px">
                  <div data-l style="width:100%;height:300px;border:1px solid #dde4ec;border-radius:8px;background:#fff"></div>
                  <div style="text-align:center;color:#8a96a5;margin-top:4px">drawn — Lottie keyframes</div>
                </div>
                <div style="flex:1;min-width:280px">
                  <canvas data-c style="width:100%;height:300px;border:1px solid #dde4ec;border-radius:8px;background:#fff;display:block"></canvas>
                  <div style="text-align:center;color:#8a96a5;margin-top:4px">solved — ÿ = −g, bounce e = 0.75</div>
                </div>
              </div>
            </div>`;

          // ---- Left: hand-authored Lottie JSON (a designer's bounce) ----
          var anim = lottie.loadAnimation({
            container: el.querySelector('[data-l]'),
            renderer: 'svg', loop: true, autoplay: true,
            animationData: {
              v: '5.7.4', fr: 60, ip: 0, op: 150, w: 340, h: 300,
              nm: 'bounce', ddd: 0, assets: [],
              layers: [
                { ddd: 0, ind: 1, ty: 4, nm: 'ball', sr: 1,
                  ks: {
                    o: { a: 0, k: 100 }, r: { a: 0, k: 0 },
                    p: { a: 1, k: [
                      { t: 0,   s: [170, 50],  o: { x: [0.55], y: [0] }, i: { x: [1],    y: [1] } },
                      { t: 40,  s: [170, 252], o: { x: [0],    y: [0] }, i: { x: [0.45], y: [1] } },
                      { t: 75,  s: [170, 120], o: { x: [0.55], y: [0] }, i: { x: [1],    y: [1] } },
                      { t: 105, s: [170, 252], o: { x: [0],    y: [0] }, i: { x: [0.45], y: [1] } },
                      { t: 130, s: [170, 185], o: { x: [0.55], y: [0] }, i: { x: [1],    y: [1] } },
                      { t: 150, s: [170, 252] }
                    ] },
                    a: { a: 0, k: [0, 0, 0] },
                    s: { a: 1, k: [
                      { t: 36,  s: [100, 100], o: { x: [0.3], y: [0] }, i: { x: [0.7], y: [1] } },
                      { t: 40,  s: [132, 68],  o: { x: [0.3], y: [0] }, i: { x: [0.7], y: [1] } },
                      { t: 46,  s: [100, 100] },
                      { t: 101, s: [100, 100], o: { x: [0.3], y: [0] }, i: { x: [0.7], y: [1] } },
                      { t: 105, s: [124, 78],  o: { x: [0.3], y: [0] }, i: { x: [0.7], y: [1] } },
                      { t: 111, s: [100, 100] }
                    ] }
                  },
                  shapes: [
                    { ty: 'gr', it: [
                      { ty: 'el', p: { a: 0, k: [0, 0] }, s: { a: 0, k: [44, 44] } },
                      { ty: 'fl', c: { a: 0, k: [0.82, 0.286, 0.357, 1] }, o: { a: 0, k: 100 } },
                      { ty: 'tr', p: { a: 0, k: [0, 0] }, a: { a: 0, k: [0, 0] },
                        s: { a: 0, k: [100, 100] }, r: { a: 0, k: 0 }, o: { a: 0, k: 100 } }
                    ] }
                  ],
                  ip: 0, op: 150, st: 0 },
                { ddd: 0, ind: 2, ty: 4, nm: 'ground', sr: 1,
                  ks: { o: { a: 0, k: 100 }, r: { a: 0, k: 0 },
                        p: { a: 0, k: [170, 280, 0] }, a: { a: 0, k: [0, 0, 0] },
                        s: { a: 0, k: [100, 100, 100] } },
                  shapes: [
                    { ty: 'gr', it: [
                      { ty: 'rc', p: { a: 0, k: [0, 0] }, s: { a: 0, k: [300, 10] }, r: { a: 0, k: 3 } },
                      { ty: 'fl', c: { a: 0, k: [0.486, 0.541, 0.627, 1] }, o: { a: 0, k: 100 } },
                      { ty: 'tr', p: { a: 0, k: [0, 0] }, a: { a: 0, k: [0, 0] },
                        s: { a: 0, k: [100, 100] }, r: { a: 0, k: 0 }, o: { a: 0, k: 100 } }
                    ] }
                  ],
                  ip: 0, op: 150, st: 0 }
              ]
            }
          });

          // ---- Right: the integrated bounce ------------------------------
          var canvas = el.querySelector('[data-c]');
          var Wc = 340, Hc = 300, dpr = window.devicePixelRatio || 1;
          canvas.width = Wc * dpr; canvas.height = Hc * dpr;
          var ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr);

          var G = 700, E = 0.75;             // px/s², restitution
          var y = 50, vy = 0;                // px, px/s (y down)
          var floor = 252, r = 22;
          function reset() { y = 50; vy = 0; }

          var raf, running = true, last = performance.now();
          function frame(now) {
            if (!running) return;
            var dt = Math.min(0.033, (now - last) / 1000); last = now;
            vy += G * dt; y += vy * dt;
            if (y > floor) {
              y = floor; vy = -vy * E;
              if (Math.abs(vy) < 28) reset();   // restart the loop
            }
            ctx.clearRect(0, 0, Wc, Hc);
            ctx.fillStyle = '#7c8aa0';
            ctx.fillRect(20, 275, Wc - 40, 10);
            // squash on contact, conserving area — driven by the physics
            var squash = y >= floor - 1 ? Math.min(0.4, Math.abs(vy) / 900) : 0;
            ctx.fillStyle = '#2a9d8f';
            ctx.beginPath();
            ctx.ellipse(Wc / 2, y, r * (1 + squash), r * (1 - squash), 0, 0, 6.2832);
            ctx.fill();
            raf = requestAnimationFrame(frame);
          }
          raf = requestAnimationFrame(frame);

          return function () {
            running = false; cancelAnimationFrame(raf);
            anim.destroy();
          };
        }
        export default { render };
        """

    lottie_vs_solved = _LottieVsSolved()
    return (lottie_vs_solved,)


@app.cell(hide_code=True)
def _(lottie_vs_solved, mo):
    mo.ui.anywidget(lottie_vs_solved)
    return


# ============================================================================
# Demo 11 — 120,000 particles (WebGPU compute shader)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 11 · 120,000 particles, integrated on the GPU

        Demo 4 advected a few hundred particles on the CPU. This is
        the same damped pendulum flow — but **120,000 particles**,
        every one of them stepped by an RK2 integrator that runs *as
        a compute shader on your graphics card*. The CPU's only job
        is to say "go" once per frame; the integration arithmetic —
        a quarter of a million function evaluations per frame —
        happens in parallel across the GPU's cores. This is
        **WebGPU**, the successor to WebGL that exposes
        general-purpose GPU computing to the browser.

        The texture of the flow appears in a way no arrow plot can
        show: dense rivers where trajectories bunch, voids around
        the unstable points, the slow spiral drains at the stable
        equilibria.

        *Requires a WebGPU-capable browser (Chrome/Edge 113+, Safari
        18+). If unsupported you'll see a notice instead.*
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import anywidget as _aw

    class _WebGpuFlow(_aw.AnyWidget):
        _esm = r"""
        async function render({ model, el }) {
          el.innerHTML = `
            <div style="font:13px sans-serif;color:#333">
              <div data-r style="width:100%;max-width:680px;height:420px;border:1px solid #dde4ec;border-radius:8px;overflow:hidden;background:#0c1118;position:relative">
                <canvas style="width:100%;height:100%;display:block"></canvas>
              </div>
              <div style="color:#8a96a5;margin-top:4px">θ horizontal · ω vertical · 120,000 particles, RK2 per-particle in a compute shader</div>
            </div>`;
          var host = el.querySelector('[data-r]');
          var canvas = host.querySelector('canvas');

          function bail(msg) {
            host.innerHTML = '<div style="padding:24px;color:#c9d4e0;font:13px sans-serif">' + msg + '</div>';
            return function () {};
          }
          if (!navigator.gpu) return bail(
            'WebGPU is not available in this browser. Chrome/Edge 113+ or Safari 18+ required — Demo 4 above shows the same flow CPU-side.');
          var adapter = await navigator.gpu.requestAdapter();
          if (!adapter) return bail('No WebGPU adapter found on this device.');
          var device = await adapter.requestDevice();

          var dpr = window.devicePixelRatio || 1;
          var W = (host.clientWidth || 680), H = 420;
          canvas.width = W * dpr; canvas.height = H * dpr;
          var ctx = canvas.getContext('webgpu');
          var format = navigator.gpu.getPreferredCanvasFormat();
          ctx.configure({ device: device, format: format, alphaMode: 'opaque' });

          var N = 120000;
          var XR = 5.2, YR = 3.4;

          // particle buffer: vec4f per particle (x, y, life, seed)
          var init = new Float32Array(N * 4);
          for (var i = 0; i < N; i++) {
            init[4*i]   = (Math.random() - 0.5) * 2 * XR;
            init[4*i+1] = (Math.random() - 0.5) * 2 * YR;
            init[4*i+2] = 100 + Math.random() * 500;
            init[4*i+3] = Math.random() * 1000;
          }
          var partBuf = device.createBuffer({
            size: init.byteLength,
            usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
          });
          device.queue.writeBuffer(partBuf, 0, init);
          var uniBuf = device.createBuffer({
            size: 16,
            usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
          });

          var computeWGSL = `
            @group(0) @binding(0) var<storage, read_write> parts: array<vec4f>;
            @group(0) @binding(1) var<uniform> u: vec4f;  // dt, frame, _, _

            fn flow(p: vec2f) -> vec2f {
              return vec2f(p.y, -sin(p.x) - 0.15 * p.y);
            }
            fn hash(n0: u32) -> f32 {
              var n = n0;
              n = n ^ (n >> 16u); n = n * 0x7feb352du;
              n = n ^ (n >> 15u); n = n * 0x846ca68bu;
              n = n ^ (n >> 16u);
              return f32(n) / 4294967295.0;
            }

            @compute @workgroup_size(64)
            fn main(@builtin(global_invocation_id) gid: vec3u) {
              let i = gid.x;
              if (i >= arrayLength(&parts)) { return; }
              var p = parts[i];
              let dt = u.x;
              let k1 = flow(p.xy);
              let k2 = flow(p.xy + dt * k1);
              var pos = p.xy + 0.5 * dt * (k1 + k2);
              var life = p.z - 1.0;
              if (life <= 0.0 || abs(pos.x) > 5.2 || abs(pos.y) > 3.4) {
                let f = u32(u.y);
                let r1 = hash(i * 1664525u + f * 13u + 1u);
                let r2 = hash(i * 22695477u + f * 7u + 5u);
                pos = vec2f((r1 - 0.5) * 10.4, (r2 - 0.5) * 6.8);
                life = 100.0 + 500.0 * hash(i + f * 3u);
              }
              parts[i] = vec4f(pos, life, p.w);
            }`;
          var renderWGSL = `
            @group(0) @binding(0) var<storage, read> parts: array<vec4f>;

            @vertex
            fn vs(@builtin(vertex_index) vi: u32) -> @builtin(position) vec4f {
              let p = parts[vi].xy;
              return vec4f(p.x / 5.2, p.y / 3.4, 0.0, 1.0);
            }
            @fragment
            fn fs() -> @location(0) vec4f {
              return vec4f(0.42, 0.55, 0.75, 1.0);
            }`;

          var computePipe = device.createComputePipeline({
            layout: 'auto',
            compute: { module: device.createShaderModule({ code: computeWGSL }),
                       entryPoint: 'main' },
          });
          var renderPipe = device.createRenderPipeline({
            layout: 'auto',
            vertex: { module: device.createShaderModule({ code: renderWGSL }),
                      entryPoint: 'vs' },
            fragment: { module: device.createShaderModule({ code: renderWGSL }),
                        entryPoint: 'fs',
                        targets: [{ format: format }] },
            primitive: { topology: 'point-list' },
          });
          var computeBind = device.createBindGroup({
            layout: computePipe.getBindGroupLayout(0),
            entries: [
              { binding: 0, resource: { buffer: partBuf } },
              { binding: 1, resource: { buffer: uniBuf } },
            ],
          });
          var renderBind = device.createBindGroup({
            layout: renderPipe.getBindGroupLayout(0),
            entries: [{ binding: 0, resource: { buffer: partBuf } }],
          });

          var frameNo = 0, raf, running = true;
          function frame() {
            if (!running) return;
            frameNo++;
            device.queue.writeBuffer(uniBuf, 0,
              new Float32Array([0.012, frameNo, 0, 0]));

            var enc = device.createCommandEncoder();
            var cp = enc.beginComputePass();
            cp.setPipeline(computePipe);
            cp.setBindGroup(0, computeBind);
            cp.dispatchWorkgroups(Math.ceil(N / 64));
            cp.end();

            var rp = enc.beginRenderPass({
              colorAttachments: [{
                view: ctx.getCurrentTexture().createView(),
                clearValue: { r: 0.047, g: 0.067, b: 0.094, a: 1 },
                loadOp: 'clear', storeOp: 'store',
              }],
            });
            rp.setPipeline(renderPipe);
            rp.setBindGroup(0, renderBind);
            rp.draw(N);
            rp.end();
            device.queue.submit([enc.finish()]);
            raf = requestAnimationFrame(frame);
          }
          frame();
          return function () {
            running = false; cancelAnimationFrame(raf);
            device.destroy();
          };
        }
        export default { render };
        """

    webgpu_flow = _WebGpuFlow()
    return (webgpu_flow,)


@app.cell(hide_code=True)
def _(mo, webgpu_flow):
    mo.ui.anywidget(webgpu_flow)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---
        ## The full bench has now played

        Eleven demos, ten technologies. The only candidate left
        unbuilt is **CodeMirror 6** (embedded code editing inside a
        widget) — skipped deliberately, because marimo already gives
        every chapter cell-level code editing; duplicating it inside
        a widget adds machinery without adding capability.

        Everything on this page runs **client-side** with no Python
        in the loop — where there's motion, the JS integrates the
        ODE itself (except Demo 9 and the left half of Demo 10,
        which are the two *deliberate* exceptions: choreographed
        narrative and designer keyframes, shown precisely to draw
        the contrast with integration). That's the architectural
        lesson: for *feel* (drag, fling, orbit, hear), put the
        integrator in the browser; for *analysis* (convergence
        plots, parameter sweeps, symbolic work), keep Python and
        Plotly. The two coexist in one notebook because each widget
        is just a cell.

        **Graduation criteria** — a demo gets promoted into a real
        chapter as a `delib` widget when (1) the chapter's core idea
        is about *feel* (initial conditions, basins, resonance,
        bifurcation, sync, chaos sensitivity), and (2) the static
        alternative demonstrably fails. Current ranked candidates:

        | Demo | Earns its keep in | Replaces |
        |------|-------------------|----------|
        | 1 · grab the mass | Ch 6 / Ch 7 | "imagine pulling it down…" prose |
        | 2 · hear resonance | Ch 7 | the $A(\omega)$ peak as a visual abstraction |
        | 7 · D3 bifurcation | Ch 10 | static bifurcation diagrams without a slider |
        | 6 · shader slope field | Ch 12 / Ch 13 | sparse arrow grids |
        | 8 · Kuramoto sync | Ch 14 (coupled oscillators) | "they synchronize" stated, never shown |
        | 9 · GSAP anatomy | Ch 7 / Ch 8 | the $x_h + x_p$ split as static stacked plots |
        | 4 · touchable flow | Ch 12 / Ch 13 | a phase plane you can't seed by hand |
        | 11 · WebGPU swarm | Ch 12 / Ch 13 (deluxe) | Demo 6's hybrid, where supported |
        | 3 · Lorenz butterfly | Ch 20 | a static 2-D projection of a 3-D attractor |
        | 10 · drawn vs solved | Ch 4 (epigraph material) | — it's a *parable*, not a tool |
        | 5 · tiny game engine | nowhere — it's the *thesis*, not a chapter | |
        """
    )
    return


if __name__ == "__main__":
    app.run()
