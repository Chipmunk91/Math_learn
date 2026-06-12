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

        | # | Demo | Technology | The equation underneath |
        |---|------|-----------|--------------------------|
        | 1 | Grab the mass | Canvas 2D + pointer capture | $\ddot x = -\omega_0^2 x - 2\gamma\dot x$ (Ch 6) |
        | 2 | Hear resonance | Web Audio API | $A(\omega)$ from Ch 7 |
        | 3 | The Lorenz butterfly | Three.js / WebGL | $\dot x = \sigma(y{-}x),\ \dot y = x(\rho{-}z){-}y,\ \dot z = xy - \beta z$ (Ch 20) |
        | 4 | Flow you can touch | Canvas particle advection | $\ddot\theta = -\sin\theta - 0.15\,\dot\theta$ (Ch 13) |
        | 5 | A tiny game engine | Matter.js rigid bodies | Newton's $m\ddot{\mathbf x} = \mathbf F$, stepped Ch 4-style |

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


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---
        ## What's deliberately *not* here, and what happens next

        Two technologies from the original list didn't make the page:
        **GSAP / Motion One** (timeline animation — superb for
        choreographed UI and narrative transitions, but our motion
        comes from integrating equations, not from keyframes) and
        **Lottie** (designer-authored After Effects animations — needs
        an asset pipeline we don't have yet; the natural fit would be
        decorative chapter-opener art, not the math itself).

        Everything on this page runs **client-side at 60 fps** with no
        Python in the loop — the JS integrates the ODEs itself. That's
        the architectural lesson: for *feel* (drag, fling, orbit,
        hear), put the integrator in the browser; for *analysis*
        (convergence plots, parameter sweeps, symbolic work), keep
        Python and Plotly. The two coexist in one notebook because each
        widget is just a cell.

        **Graduation criteria** — a demo gets promoted into a real
        chapter as a `delib` widget when (1) the chapter's core idea is
        about *feel* (initial conditions, basins, resonance, chaos
        sensitivity), and (2) the static alternative demonstrably
        fails. Current candidates: the grabbable mass → Ch 6/7, the
        audible resonance → Ch 7, the touchable flow → Ch 12/13, the
        butterfly → Ch 20.
        """
    )
    return


if __name__ == "__main__":
    app.run()
