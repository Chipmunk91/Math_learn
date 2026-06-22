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
        grab, drag, orbit — and every one of them is secretly
        integrating a differential equation from this course, in
        JavaScript, at 60 frames per second, right in your browser.
        (It began as a much wider survey of web techniques; the demos
        that showed off a technology without making the math clearer
        have been retired — what remains are the ones that genuinely
        help you *see* the equation.)

        | # | Demo | Tech stack | Underlying DE | Status |
        |---|------|-----------|---------------|--------|
        | 1 | Grab the mass | Canvas 2D + Pointer Events, RK4 in JS | $\ddot x = -\omega_0^2 x - 2\gamma\dot x$ — damped oscillator | ✅ `spring_grab` · Ch 6 |
        | 2 | Lorenz butterfly | Three.js + WebGL + OrbitControls | $\dot x=\sigma(y-x),\ \dot y=x(\rho-z)-y,\ \dot z=xy-\beta z$ | ○ candidate · Ch 20 |
        | 3 | Flow you can touch | Canvas 2D + RK2 particle advection | $\ddot\theta = -\sin\theta - 0.15\,\dot\theta$ — damped pendulum | ○ candidate · Ch 12/13 |
        | 4 | Drawn vs solved | lottie-web + Canvas 2D (integrated) | $\ddot y = -g$, restitution $e = 0.75$ | ○ candidate · Ch 4 |
        | 5 | Rumor through a crowd | Canvas 2D agents + live logistic fit | $\dot y = b\,y(K-y)$ — spatial vs. well-mixed | ✅ `rumor_crowd` · Ch 1 hook |
        | 6 | Cooling coffee | Canvas 2D + steam particles | $T' + kT = kT_r$ — Newton's cooling | ✅ `cooling_coffee` · Ch 2 hook |
        | 7 | The hidden hillside, in 3-D | Three.js surface + contour walk + water-level plane | $M\,dx + N\,dy = 0$ — solutions are contours of $F$ at constant altitude | ○ candidate · Ch 3a |
        | 8 | Road test — same car, different roads | Canvas 2D side-scrolling road + chassis, RK4 in JS | $y'' + 2\gamma y' + \omega_0^2 y = \omega_0^2\,u(t)$ — non-homogeneous; road profile *is* the forcing | ○ candidate · Ch 8 |

        The **Status** column is the single place this page tracks
        graduation: ✅ means the demo has moved into `delib` and now
        powers a real chapter; ○ means it's still a candidate, waiting
        on the chapter that will host it. If a demo earns its keep it
        graduates; if it doesn't, it dies here, cheaply.
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
def _(delib):
    # Demo 1 — uses the graduated delib.spring_grab widget.
    delib.spring_grab()
    return


# ============================================================================
# Demo 2 — The Lorenz butterfly (Three.js / WebGL)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 2 · The Lorenz butterfly, in real 3-D

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
# Demo 3 — Flow you can touch (Canvas particle advection)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 3 · Flow you can touch

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
# Demo 4 — Drawn vs solved (Lottie keyframes next to a real integrator)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 4 · Drawn vs solved — spot the imposter

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
# Demo 5 — A rumor through a crowd (Canvas 2D; agent sim vs. live logistic ODE)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 5 · A rumor through a crowd

        Chapter 1 turns a rumor on a campus into the **logistic
        equation** $\dot y = b\,y\,(K - y)$ — knowers $y$ times fresh
        ears $(K - y)$, because spreading takes a *pair*. Here that
        happens for real, one person at a time.

        Every figure is someone walking around. Three start knowing
        (amber); everyone else (grey) is still in the dark. **Click or
        drag across the crowd to plant the rumor** wherever you like —
        that's choosing the initial condition. Whenever a knower bumps
        into someone who hasn't heard, the rumor jumps and they light
        up, and with each telling the room **darkens into the mood of
        the thing everyone now knows**.

        The graph tracks the fraction who know (red), with **Chapter
        1's logistic law fit to the crowd in real time** (blue). That
        S-shape — slow start, middle eruption, plateau — *emerges*;
        nobody imposed it. It's just the bookkeeping of $y \times
        (K - y)$ encounters playing out on the floor in front of you.

        *Why it matters — honestly:* **mingle speed is Chapter 1's rate
        constant $b$ made physical** — faster walking means more bumps
        per minute, a steeper climb, a quicker campus-wide rumor. The
        blue law keeps up because we fit it live, and it tracks the
        crowd to within a few percent. What it *can't* fully capture is
        that a real crowd lives in space, not in a well-mixed jar: the
        rumor travels as a *front*, so the red curve wanders a little
        off the ideal and **ignites at a different moment every run** —
        when only three people know, sheer chance decides how fast it
        catches. That wander is the honest gap between a tidy
        first-order model and a messy world.

        *(With a nod to Nicky Case's "We Become What We Behold" — the
        same darkening crowd, repurposed for contagion.)*
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Demo 12 — uses the graduated delib.rumor_crowd widget (also the
    # opening hook of Chapter 1).
    delib.rumor_crowd()
    return


# ============================================================================
# Demo 6 — A cup of cooling coffee (Canvas 2D + steam particles;
#           Newton's cooling, the chapter's own equation)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 6 · A cup of cooling coffee

        Chapter 2 introduces **Newton's law of cooling** and notes
        that the same equation is *both* separable and linear:

        $$ \frac{dT}{dt} = -k\,(T - T_r). $$

        A hot mug sitting in a cooler room is the chapter's whole
        story made physical. The mug starts at $90^\circ$C, the room
        is at $T_r$ — drag $T_r$ and the coffee chases the new room
        temperature. Drag $k$ to change the insulation (a thick
        ceramic mug = small $k$; a thin paper cup = big $k$); the
        coffee chases faster or slower, with time constant
        $\tau = 1/k$.

        The **steam wisps aren't decoration** — they're a visual
        proxy for the rate of heat leaving. The bigger the gap
        $(T - T_r)$, the more steam you see; as the coffee approaches
        room temperature, the steam dies. That visible rate *is*
        $-k(T - T_r)$ at work.

        Two extra controls cover the equation's other modes:

        - **🔥 candle warmer** — a heat source under the mug adds
          energy at a fixed rate $Q$. Turn it on and the equilibrium
          shifts up to $T_r + Q/k$. With good insulation it can keep
          the coffee at any temperature you like, up to boiling
          (capped at $100^\circ$C).
        - **🥛 pour milk** — adds 25 % cold milk at $5^\circ$C; the
          temperature *jumps down* instantly by weighted average.
          After the jump, the same exponential approach picks up
          from the new starting point.

        *Why a coffee mug and not a tank?* Because heat in a stirred
        mug is **genuinely well mixed** — you don't see hot spots in
        coffee — so the scalar $T(t)$ tells the whole story honestly,
        with no spatial structure to fake.

        *Why it matters:* "approach an equilibrium set by the outside
        world, exponentially" is the shape of every linear first-order
        story. The same equation governs a charging capacitor, a drug
        clearing your bloodstream, or a thermostat reaching set-point.
        Learn the mug and you've met all of them.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Demo 13 — uses the graduated delib.cooling_coffee widget (also the
    # opening hook of Chapter 2).
    delib.cooling_coffee()
    return

# ============================================================================
# Demo 7 — The hidden hillside in 3-D (Three.js surface + contour walk)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 7 · The hidden hillside, in 3-D

        Chapter 3a's secret: an **exact** equation $M\,dx + N\,dy = 0$
        is the *flatness condition of a hidden landscape* $F(x, y)$.
        With $M = F_x$ and $N = F_y$, the equation reads
        $dF = F_x\,dx + F_y\,dy = 0$ — "don't change altitude." Its
        solutions are the **contour lines** $F = C$.

        Here is that landscape as an actual hill you can orbit.
        **Drag to rotate, scroll to zoom, and click anywhere on the
        hill** to send a hiker walking — always at the *same
        altitude*. A translucent **water plane** sits at the hiker's
        height: notice the hiker never leaves it. The path it traces
        is a contour — a solution of the equation.

        The little arrow is the steepest-uphill direction
        $(M, N) = \nabla F$. Watch it stay **perpendicular to the
        path** at every step — which is exactly what
        $M\,dx + N\,dy = 0$ says: move so that the step $(dx, dy)$ has
        zero overlap with the uphill direction, and your altitude
        can't change. The faint curve on the ground is the same
        contour seen from above — the 2-D contour map the chapter
        draws.

        *Why it matters:* "staying at the same altitude" is invisible
        on a flat 2-D map — there it's just a number you have to
        trust. In 3-D you watch the hiker glide along the waterline
        and never rise or fall. That *is* what makes a contour a
        solution of an exact equation.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Demo 7 — uses the graduated delib.hillside_3d widget (same source
    # of truth as Chapter 3a's intro).
    delib.hillside_3d()
    return


# ============================================================================
# Demo 8 — Road test: a car on any road profile (Canvas 2D + RK4 in JS)
# ============================================================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 8 · Road test — same car, different roads

        Chapter 8 is about the non-homogeneous equation
        $y'' + 2\gamma y' + \omega_0^2 y = g(t)$ — the **same** system
        from Chapter 7, but now the right-hand side $g(t)$ can be
        **anything**, not just a single cosine. The chapter's point
        is that the *shape* you put on the right changes the response
        you get.

        Here that's made literal. A car rolls at constant speed over
        a road. **The road's vertical profile *is* the forcing
        $g(t)$** — its shape is what the system is being told. The
        car's chassis bobs up and down — **that bobbing is the
        solution $y(t)$**. Pick a road, watch the response.

        - **Flat road** → no forcing → after any initial bounce, the
          chassis settles. This is the homogeneous part $y_h$ alone.
        - **One bump** → an impulse-like push → the chassis bounces
          once, then the bounce decays.
        - **Wavy road** → sinusoidal forcing → the chassis tracks
          the rhythm. Try the wavelength that matches the car's
          natural bounce — *resonance*, made physical.
        - **Stairs** → a sequence of step changes → each step kicks
          a new bounce that superposes on what's already there.
          Superposition, visible.

        The chart underneath shows it in one picture: the **road**
        $u(t)$ in amber (the forcing, up to a scale $\omega_0^2$),
        the **chassis height** $y(t)$ in cyan (the solution). One
        function in, another function out — and the road shape *is*
        the input shape.

        The car has two real knobs: **stiffness** (how taut the
        spring is — sets the natural bounce frequency $\omega_0$)
        and **damping** (how much the shocks absorb each bounce —
        sets $\gamma$). No L, no R, no C — just a car you can drive.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Demo 15 — uses the graduated delib.road_test widget (same source
    # of truth as Chapter 8's opening animation).
    delib.road_test()
    return



@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---
        ## What survived the cull

        This page started as a wide technology survey — Web Audio,
        Matter.js, GLSL shaders, D3, Tone.js, GSAP, WebGPU, and more —
        to see *how far the browser can reach* for teaching dynamics.
        That survey was worth doing. But a demo only earns a place
        here if it clears one bar: **it has to make the idea more
        intuitive, not just more impressive.** Several of the
        flashier experiments didn't — they showed off a technology
        without making the mathematics clearer — so they've been
        retired. What's left are the eight that genuinely help you
        *see* the equation.

        Everything that remains runs **client-side** with no Python
        in the loop — where there's motion, the JS integrates the
        ODE itself (the one deliberate exception is the *drawn vs
        solved* demo, whose left half is hand-keyframed precisely to
        contrast with a real integrator). That's the architectural
        lesson worth keeping: for *feel* (drag, fling, orbit), put
        the integrator in the browser; for *analysis* (convergence
        plots, parameter sweeps, symbolic work), keep Python and
        Plotly. The two coexist in one notebook because each widget
        is just a cell.

        **Graduation** — a demo gets promoted into a real chapter as
        a `delib` widget when its idea is about *feel* and the static
        alternative demonstrably fails; the **Status** column up top
        is the single source of truth. Four of the survivors have
        graduated and now power chapters: `spring_grab` (Ch 6),
        `rumor_crowd` (Ch 1), `cooling_coffee` (Ch 2), and
        `road_test` (Ch 8). The rest are candidates waiting on the
        chapters that will host them — the 3-D hillside, for
        instance, is queued for Chapter 3a.
        """
    )
    return


if __name__ == "__main__":
    app.run()
