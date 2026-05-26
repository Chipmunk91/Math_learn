/* Math Learn — in-page AI tutor widget (dependency-free).
 *
 * Lives entirely in the browser, outside marimo's runtime. Reads per-chapter
 * config from window.TUTOR_CONFIG (injected by the build), holds the visitor's
 * own Anthropic key in sessionStorage (cleared when the tab closes), and calls
 * api.anthropic.com directly with the documented direct-browser header. The key
 * never touches any server we run, and each visitor pays for their own usage.
 */
(function () {
  "use strict";

  var CFG = window.TUTOR_CONFIG || {};
  var KEY_STORE = "mathlearn.anthropicKey";
  var MODEL_STORE = "mathlearn.model";
  var ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
  var ANTHROPIC_VERSION = "2023-06-01";
  var KEY_CONSOLE = "https://console.anthropic.com/settings/keys";
  var MAX_TOKENS = 800;

  // Own Pyodide sandbox (separate from marimo's runtime) for running tutor code.
  // Loaded lazily on the first Run. Bump PYODIDE_VER if the CDN path 404s.
  var PYODIDE_VER = "0.26.4";
  var PYODIDE_BASE = "https://cdn.jsdelivr.net/pyodide/v" + PYODIDE_VER + "/full/";

  var MODELS = CFG.models || [
    { label: "Claude Haiku 4.5 — fast & cheap", id: "claude-haiku-4-5-20251001" },
    { label: "Claude Sonnet 4.6 — stronger", id: "claude-sonnet-4-6" },
  ];

  var GUIDE =
    "You are a patient, Socratic tutor embedded inside an interactive " +
    "differential-equations lesson. The learner is reading the chapter below " +
    "and experimenting with live sliders and animations.\n\n" +
    "How to help:\n" +
    "- Teach through guidance, not answer dumps. When the learner is stuck, " +
    "give the next hint or a guiding question first; reveal a full solution " +
    "only after they have tried, or if they explicitly ask.\n" +
    "- When they propose an answer, give specific feedback: what is right, " +
    "exactly where any reasoning breaks, and a nudge toward the fix.\n" +
    "- Stay anchored to THIS chapter's equation, parameters, and figures.\n" +
    "- Be concise and encouraging. Use Markdown; write math with $...$.\n" +
    "- When you suggest code, put it in a ```python fenced block; the learner " +
    "gets a Run button that executes it in a sandbox (numpy, scipy, matplotlib " +
    "available) and shows printed output and any matplotlib plot inline. So make " +
    "each snippet fully self-contained and runnable on its own: include imports, " +
    "and end with a plot (plt.show()) or a print so there is visible output.\n" +
    "- If a question is unrelated to the chapter, answer briefly and steer back.";

  var messages = []; // {role, content}
  var scope = "";    // picked-cell content attached to the next question

  // ---- tiny, safe markdown -> html -------------------------------------
  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function mdToHtml(src) {
    var out = esc(src);
    out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
    out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    out = out.replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>");
    var blocks = out.split(/\n{2,}/).map(function (b) {
      var lines = b.split("\n");
      var isList = lines.every(function (l) { return /^\s*([-*]|\d+\.)\s+/.test(l) || l.trim() === ""; }) &&
        lines.some(function (l) { return /^\s*([-*]|\d+\.)\s+/.test(l); });
      if (isList) {
        var items = lines.filter(function (l) { return l.trim(); })
          .map(function (l) { return "<li>" + l.replace(/^\s*([-*]|\d+\.)\s+/, "") + "</li>"; });
        return "<ul>" + items.join("") + "</ul>";
      }
      return "<p>" + b.replace(/\n/g, "<br>") + "</p>";
    });
    return blocks.join("");
  }

  // Render markdown + LaTeX. Math is pulled out before markdown so paragraph
  // wrapping can't split a $$...$$ across tags, then rendered with KaTeX.
  function renderRich(src) {
    var math = [], code = [];
    function stash(tex, display) { math.push({ tex: tex, display: display }); return "@@M" + (math.length - 1) + "@@"; }
    var s = src.replace(/```([\w-]*)\n?([\s\S]*?)```/g, function (_, lang, c) { code.push({ lang: (lang || "").toLowerCase(), text: c.replace(/\n$/, "") }); return "@@C" + (code.length - 1) + "@@"; });
    s = s.replace(/\$\$([\s\S]+?)\$\$/g, function (_, t) { return stash(t, true); });
    s = s.replace(/\\\[([\s\S]+?)\\\]/g, function (_, t) { return stash(t, true); });
    s = s.replace(/\$([^\$\n]+?)\$/g, function (_, t) { return stash(t, false); });
    s = s.replace(/\\\(([\s\S]+?)\\\)/g, function (_, t) { return stash(t, false); });
    var html = mdToHtml(s);
    html = html.replace(/@@M(\d+)@@/g, function (_, i) {
      var m = math[i];
      if (window.katex) {
        try { return window.katex.renderToString(m.tex, { displayMode: m.display, throwOnError: false }); } catch (e) {}
      }
      return "<code>" + esc(m.tex) + "</code>";
    });
    html = html.replace(/@@C(\d+)@@/g, function (_, i) {
      var c = code[i];
      return '<pre class="mt-code" data-lang="' + esc(c.lang) + '"><code>' + esc(c.text) + "</code></pre>";
    });
    return html;
  }

  // ---- DOM scaffold -----------------------------------------------------
  var el = {};
  function build() {
    var fab = document.createElement("button");
    fab.className = "mt-fab";
    fab.title = "Ask the tutor";
    fab.textContent = "💬";

    var panel = document.createElement("div");
    panel.className = "mt-panel";
    panel.innerHTML =
      '<div class="mt-head">' +
      '  <strong>Tutor</strong>' +
      '  <span class="mt-sub" data-mt="sub"></span>' +
      '  <span class="mt-spacer"></span>' +
      '  <button class="mt-iconbtn" data-mt="max" title="Expand">⤢</button>' +
      '  <button class="mt-iconbtn" data-mt="settings" title="API key">⚙</button>' +
      '  <button class="mt-iconbtn" data-mt="close" title="Close">✕</button>' +
      '</div>' +
      '<div class="mt-body" data-mt="body"></div>' +
      '<div class="mt-foot" data-mt="foot"></div>';

    document.body.appendChild(fab);
    document.body.appendChild(panel);

    el.fab = fab;
    el.panel = panel;
    el.sub = panel.querySelector('[data-mt="sub"]');
    el.body = panel.querySelector('[data-mt="body"]');
    el.foot = panel.querySelector('[data-mt="foot"]');

    fab.addEventListener("click", openPanel);
    panel.querySelector('[data-mt="close"]').addEventListener("click", closePanel);
    panel.querySelector('[data-mt="settings"]').addEventListener("click", renderSetup);
    panel.querySelector('[data-mt="max"]').addEventListener("click", toggleMax);
    setupCellAsk();
  }

  function toggleMax() {
    var on = el.panel.classList.toggle("mt-max");
    var b = el.panel.querySelector('[data-mt="max"]');
    if (b) { b.textContent = on ? "⤡" : "⤢"; b.title = on ? "Shrink" : "Expand"; }
  }

  // ---- key storage (session only) --------------------------------------
  function getKey() { try { return sessionStorage.getItem(KEY_STORE) || ""; } catch (e) { return ""; } }
  function setKey(k) { try { sessionStorage.setItem(KEY_STORE, k); } catch (e) {} }
  function clearKey() { try { sessionStorage.removeItem(KEY_STORE); } catch (e) {} }
  function getModel() { try { return sessionStorage.getItem(MODEL_STORE) || MODELS[0].id; } catch (e) { return MODELS[0].id; } }
  function setModel(m) { try { sessionStorage.setItem(MODEL_STORE, m); } catch (e) {} }

  // ---- open / close -----------------------------------------------------
  function openPanel() { showPanel(); }
  function showPanel() {
    el.panel.classList.add("mt-open");
    if (!getKey()) { renderSetup(); } else { renderChat(); }
  }
  function closePanel() { el.panel.classList.remove("mt-open"); }

  // ---- pick a whole cell ------------------------------------------------
  var picking = false;
  function cellText(cell) {
    var area = cell.querySelector(".output-area") || cell;
    var clone = area.cloneNode(true);
    // KaTeX hides a MathML copy of every formula; drop it so math isn't doubled.
    clone.querySelectorAll(".katex-mathml").forEach(function (n) { n.remove(); });
    return (clone.innerText || "").replace(/\n{3,}/g, "\n\n").trim();
  }
  function pickOverlay() {
    if (el.overlay) return;
    el.overlay = document.createElement("div");
    el.overlay.className = "mt-pick-overlay";
    el.banner = document.createElement("div");
    el.banner.className = "mt-pick-banner";
    el.banner.textContent = "Click a cell to add it to the tutor — Esc to cancel";
    document.body.appendChild(el.overlay);
    document.body.appendChild(el.banner);
  }
  function enterPick() {
    picking = true;
    pickOverlay();
    closePanel();
    document.body.classList.add("mt-picking");
    el.overlay.style.display = "none";
    el.banner.style.display = "block";
    document.addEventListener("mousemove", onPickMove, true);
    document.addEventListener("click", onPickClick, true);
    document.addEventListener("keydown", onPickKey, true);
  }
  function exitPick() {
    picking = false;
    document.body.classList.remove("mt-picking");
    if (el.overlay) el.overlay.style.display = "none";
    if (el.banner) el.banner.style.display = "none";
    document.removeEventListener("mousemove", onPickMove, true);
    document.removeEventListener("click", onPickClick, true);
    document.removeEventListener("keydown", onPickKey, true);
  }
  function cellUnder(target) {
    return target && target.closest ? target.closest(".marimo-cell") : null;
  }
  function onPickMove(e) {
    var cell = cellUnder(e.target);
    if (!cell) { el.overlay.style.display = "none"; return; }
    var r = cell.getBoundingClientRect();
    var o = el.overlay.style;
    o.display = "block";
    o.top = r.top + "px"; o.left = r.left + "px";
    o.width = r.width + "px"; o.height = r.height + "px";
  }
  // Prefer the authored source injected at build time (real code for code
  // cells, exact LaTeX for markdown), mapping by the cell's document position.
  function cellSource(cell) {
    if (!CFG.cells || !CFG.cells.length) return "";
    var all = Array.prototype.slice.call(document.querySelectorAll(".marimo-cell"));
    var idx = all.indexOf(cell);
    if (idx < 0 || idx >= CFG.cells.length) return "";
    var c = CFG.cells[idx];
    return c.kind === "code" ? "```python\n" + c.text + "\n```" : c.text;
  }
  function onPickClick(e) {
    var cell = cellUnder(e.target);
    if (!cell) return;
    e.preventDefault();
    e.stopPropagation();
    exitPick();
    pickCellNow(cell);
  }
  function onPickKey(e) {
    if (e.key === "Escape") { exitPick(); showPanel(); }
  }

  // Attach a cell to the next question and jump straight into the chat.
  function pickCellNow(cell) {
    var text = cellSource(cell) || cellText(cell);
    if (text) scope = text;
    showPanel();
    if (el.input) el.input.focus();
  }

  // ---- per-cell hover button (one-click: hover a cell -> "Ask") ---------
  var hoverCell = null;
  function setupCellAsk() {
    el.ask = document.createElement("button");
    el.ask.type = "button";
    el.ask.className = "mt-cell-ask";
    el.ask.innerHTML = "💬 Ask";
    el.ask.title = "Ask the tutor about this cell";
    el.ask.style.display = "none";
    el.ask.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (hoverCell) pickCellNow(hoverCell);
    });
    document.body.appendChild(el.ask);
    document.addEventListener("mousemove", onCellHover, true);
    window.addEventListener("scroll", repositionAsk, true);
  }
  function onCellHover(e) {
    if (picking) { hideAsk(); return; }
    var t = e.target;
    if (el.ask && (t === el.ask || el.ask.contains(t))) return;
    var cell = t && t.closest ? t.closest(".marimo-cell") : null;
    if (!cell) { hideAsk(); return; }
    if (cell === hoverCell && el.ask.style.display !== "none") return;
    hoverCell = cell;
    positionAsk();
  }
  function positionAsk() {
    if (!hoverCell) return;
    var r = hoverCell.getBoundingClientRect();
    var b = el.ask;
    b.style.display = "flex";
    b.style.top = (r.bottom - b.offsetHeight - 8) + "px";
    b.style.left = (r.right - b.offsetWidth - 8) + "px";
  }
  function repositionAsk() {
    if (el.ask && el.ask.style.display !== "none") positionAsk();
  }
  function hideAsk() {
    hoverCell = null;
    if (el.ask) el.ask.style.display = "none";
  }

  // ---- setup view -------------------------------------------------------
  function renderSetup() {
    el.sub.textContent = "";
    el.foot.innerHTML = "";
    var b = el.body;
    b.innerHTML = "";

    var note = document.createElement("p");
    note.className = "mt-hint";
    note.innerHTML =
      "Powered by <strong>your</strong> Anthropic key. It stays in this browser " +
      "tab for the session only, is sent <strong>directly</strong> to Anthropic, " +
      "and never to this site. Get a key at " +
      '<a href="' + KEY_CONSOLE + '" target="_blank" rel="noopener">Anthropic Console</a>.';

    var wrap = document.createElement("div");
    wrap.className = "mt-setup";

    var input = document.createElement("input");
    input.type = "password";
    input.placeholder = "sk-ant-...";
    input.value = getKey();
    input.autocomplete = "off";

    var select = document.createElement("select");
    MODELS.forEach(function (m) {
      var o = document.createElement("option");
      o.value = m.id; o.textContent = m.label;
      if (m.id === getModel()) o.selected = true;
      select.appendChild(o);
    });

    var save = document.createElement("button");
    save.className = "mt-send";
    save.textContent = "Save & start";
    save.addEventListener("click", function () {
      var k = input.value.trim();
      if (!k) { input.focus(); return; }
      setKey(k);
      setModel(select.value);
      renderChat();
    });

    wrap.appendChild(input);
    wrap.appendChild(select);
    wrap.appendChild(save);
    b.appendChild(note);
    b.appendChild(wrap);
    input.focus();
  }

  // ---- chat view --------------------------------------------------------
  function renderChat() {
    el.sub.textContent = CFG.chapter || "";
    renderMessages();
    renderFoot();
  }

  function renderMessages() {
    var b = el.body;
    b.innerHTML = "";
    if (!messages.length) {
      var tip = document.createElement("p");
      tip.className = "mt-hint";
      tip.innerHTML =
        "💡 Ask about the whole chapter, or hover any cell and click its " +
        "<strong>💬 Ask</strong> button to attach that cell to your question.";
      b.appendChild(tip);

      var starters = (CFG.starters || []);
      if (starters.length) {
        var sWrap = document.createElement("div");
        sWrap.className = "mt-starters";
        starters.forEach(function (s) {
          var btn = document.createElement("button");
          btn.className = "mt-starter";
          btn.textContent = s;
          btn.addEventListener("click", function () { send(s); });
          sWrap.appendChild(btn);
        });
        b.appendChild(sWrap);
      }
    }
    messages.forEach(function (m) {
      var row = document.createElement("div");
      row.className = "mt-msg " + (m.role === "user" ? "mt-user" : "mt-bot");
      var bub = document.createElement("div");
      bub.className = "mt-bubble";
      bub.innerHTML = m.role === "user" ? esc(m.content).replace(/\n/g, "<br>") : renderRich(m.content);
      if (m.role !== "user") decorateCode(bub);
      row.appendChild(bub);
      b.appendChild(row);
    });
    b.scrollTop = b.scrollHeight;
  }

  function renderFoot() {
    var f = el.foot;
    f.innerHTML = "";

    var pick = document.createElement("button");
    pick.className = "mt-pickbtn";
    pick.innerHTML = "&#9633; Pick a cell to ask about";
    pick.addEventListener("click", enterPick);

    var keyrow = document.createElement("div");
    keyrow.className = "mt-keyrow";
    keyrow.innerHTML = "<span>key set ✓</span><span class='mt-spacer'></span>";
    var clr = document.createElement("button");
    clr.className = "mt-link";
    clr.textContent = "clear key";
    clr.addEventListener("click", function () { clearKey(); renderSetup(); });
    keyrow.appendChild(clr);

    var chip = document.createElement("div");
    chip.className = "mt-chip";
    el.chip = chip;
    renderScopeChip();

    var row = document.createElement("div");
    row.className = "mt-inputrow";
    var ta = document.createElement("textarea");
    ta.className = "mt-input";
    ta.rows = 1;
    ta.placeholder = scope ? "Ask about the picked cell…" : "Ask about this chapter…";
    el.input = ta;
    var btn = document.createElement("button");
    btn.className = "mt-send";
    btn.textContent = "Send";
    btn.addEventListener("click", function () { send(ta.value); });
    ta.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(ta.value); }
    });

    row.appendChild(ta);
    row.appendChild(btn);
    f.appendChild(pick);
    f.appendChild(keyrow);
    f.appendChild(chip);
    f.appendChild(row);
  }

  function renderScopeChip() {
    if (!el.chip) return;
    if (scope) {
      el.chip.classList.add("mt-show");
      el.chip.innerHTML = "";
      var txt = document.createElement("span");
      txt.className = "mt-chiptext";
      txt.textContent = "Asking about: “" + scope.slice(0, 80) + (scope.length > 80 ? "…" : "") + "”";
      var x = document.createElement("button");
      x.textContent = "✕";
      x.title = "Clear selection";
      x.addEventListener("click", function () { scope = ""; renderScopeChip(); });
      el.chip.appendChild(txt);
      el.chip.appendChild(x);
    } else {
      el.chip.classList.remove("mt-show");
      el.chip.innerHTML = "";
    }
  }

  // ---- code blocks -> run in our own Pyodide sandbox ------------------
  // The tutor never writes into the notebook (marimo's reactive single-
  // definition rule makes that unsafe). Instead, Python snippets get a Run
  // button that executes them in OUR OWN Pyodide instance — completely isolated
  // from marimo's runtime — and renders stdout + any matplotlib figure right
  // here in the chat. Nothing touches the notebook.
  function decorateCode(bubble) {
    var pres = bubble.querySelectorAll("pre.mt-code");
    Array.prototype.forEach.call(pres, function (pre) {
      var codeEl = pre.querySelector("code");
      var text = codeEl ? codeEl.textContent : pre.textContent;
      if (!text || !text.trim()) return;
      var lang = (pre.getAttribute("data-lang") || "").toLowerCase();
      var isPy = (lang === "" || lang === "python" || lang === "py");

      var bar = document.createElement("div");
      bar.className = "mt-codebar";
      var out = document.createElement("div");
      out.className = "mt-run";

      if (isPy) {
        var run = document.createElement("button");
        run.className = "mt-codebtn";
        run.textContent = "▶ Run";
        run.title = "Run this in a sandbox and show the output here.";
        run.addEventListener("click", function () { runInSandbox(text, run, out); });
        bar.appendChild(run);
      }
      var cp = document.createElement("button");
      cp.className = "mt-codebtn";
      cp.textContent = "⧉ Copy";
      cp.addEventListener("click", function () { copyText(text); toast("Copied to clipboard."); });
      bar.appendChild(cp);

      pre.parentNode.insertBefore(bar, pre.nextSibling);
      pre.parentNode.insertBefore(out, bar.nextSibling);
    });
  }

  // ---- Pyodide sandbox --------------------------------------------------
  function loadScript(src) {
    return new Promise(function (res, rej) {
      var s = document.createElement("script");
      s.src = src; s.onload = res; s.onerror = function () { rej(new Error("failed to load " + src)); };
      document.head.appendChild(s);
    });
  }

  var pyodideReady = null;
  function ensurePyodide(onProgress) {
    if (pyodideReady) return pyodideReady;
    pyodideReady = (function () {
      onProgress("Loading Python runtime (first run only)…");
      return loadScript(PYODIDE_BASE + "pyodide.js")
        .then(function () { return window.loadPyodide({ indexURL: PYODIDE_BASE }); })
        .then(function (py) {
          onProgress("Loading numpy + matplotlib…");
          return py.loadPackage(["numpy", "matplotlib"]).then(function () { return py; });
        });
    })();
    return pyodideReady;
  }

  // Run user code, capture stdout/stderr and any matplotlib figures (as PNGs).
  var RUN_HARNESS =
    "import io, sys, base64, json, traceback\n" +
    "def __tutor_run(src):\n" +
    "    out = io.StringIO(); imgs = []; err = None\n" +
    "    try:\n" +
    "        import matplotlib; matplotlib.use('AGG')\n" +
    "    except Exception:\n" +
    "        pass\n" +
    "    _o, _e = sys.stdout, sys.stderr; sys.stdout = sys.stderr = out\n" +
    "    try:\n" +
    "        exec(src, {'__name__': '__main__'})\n" +
    "    except Exception:\n" +
    "        err = traceback.format_exc()\n" +
    "    finally:\n" +
    "        sys.stdout, sys.stderr = _o, _e\n" +
    "    try:\n" +
    "        import matplotlib.pyplot as plt\n" +
    "        for n in plt.get_fignums():\n" +
    "            b = io.BytesIO(); plt.figure(n).savefig(b, format='png', bbox_inches='tight', dpi=110)\n" +
    "            imgs.append(base64.b64encode(b.getvalue()).decode('ascii'))\n" +
    "        plt.close('all')\n" +
    "    except Exception:\n" +
    "        pass\n" +
    "    return json.dumps({'stdout': out.getvalue(), 'error': err, 'images': imgs})\n" +
    "__tutor_run(__tutor_src)\n";

  function runPython(code, onProgress) {
    return ensurePyodide(onProgress).then(function (py) {
      onProgress("Running…");
      return Promise.resolve(py.loadPackagesFromImports(code)).catch(function () {})
        .then(function () {
          py.globals.set("__tutor_src", code);
          return py.runPythonAsync(RUN_HARNESS);
        })
        .then(function (json) { return JSON.parse(json); });
    });
  }

  function runInSandbox(code, btn, out) {
    var orig = btn.textContent;
    btn.disabled = true; btn.textContent = "Running…";
    out.style.display = "block";
    out.innerHTML = '<div class="mt-run-status">Starting…</div>';
    runPython(code, function (msg) { out.innerHTML = '<div class="mt-run-status">' + esc(msg) + "</div>"; })
      .then(function (res) {
        var html = "";
        (res.images || []).forEach(function (b64) {
          html += '<img class="mt-run-img" alt="plot output" src="data:image/png;base64,' + b64 + '" />';
        });
        if (res.stdout && res.stdout.trim()) html += '<pre class="mt-run-out">' + esc(res.stdout) + "</pre>";
        if (res.error) html += '<pre class="mt-run-err">' + esc(res.error) + "</pre>";
        out.innerHTML = html || '<div class="mt-run-status">(ran with no output)</div>';
      })
      .catch(function (e) {
        out.innerHTML = '<pre class="mt-run-err">⚠️ ' + esc(String(e && e.message || e)) + "</pre>";
      })
      .then(function () { btn.disabled = false; btn.textContent = orig; });
  }

  // ---- small utilities --------------------------------------------------
  function copyText(t) {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(t); return; }
    } catch (e) {}
    try {
      var ta = document.createElement("textarea");
      ta.value = t; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      document.execCommand("copy"); document.body.removeChild(ta);
    } catch (e) {}
  }

  var toastTimer = null;
  function toast(msg) {
    var t = el.toast;
    if (!t) { t = document.createElement("div"); t.className = "mt-toast"; document.body.appendChild(t); el.toast = t; }
    t.textContent = msg;
    t.classList.add("mt-toast-show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove("mt-toast-show"); }, 4000);
  }

  // ---- send -------------------------------------------------------------
  function systemPrompt() {
    var s = GUIDE + "\n\n## The chapter the learner is studying\n\n" + (CFG.context || CFG.chapter || "");
    if (scope) {
      s += "\n\n## The learner highlighted this passage; focus your help here\n\n\"" + scope + "\"";
    }
    return s;
  }

  function send(text) {
    text = (text || "").trim();
    if (!text) return;
    var key = getKey();
    if (!key) { renderSetup(); return; }

    messages.push({ role: "user", content: text });
    if (el.input) el.input.value = "";
    renderMessages();

    var typing = document.createElement("div");
    typing.className = "mt-typing";
    typing.textContent = "Tutor is thinking…";
    el.body.appendChild(typing);
    el.body.scrollTop = el.body.scrollHeight;

    var payload = {
      model: getModel(),
      max_tokens: MAX_TOKENS,
      system: systemPrompt(),
      messages: messages.map(function (m) { return { role: m.role, content: m.content }; }),
    };

    fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": key,
        "anthropic-version": ANTHROPIC_VERSION,
        "anthropic-dangerous-direct-browser-access": "true",
      },
      body: JSON.stringify(payload),
    })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        var d = res.d || {};
        if (!res.ok || d.error) {
          var msg = d.error && d.error.message ? d.error.message : "request failed";
          messages.push({ role: "assistant", content: "⚠️ " + msg });
        } else {
          var text2 = (d.content || [])
            .filter(function (b) { return b.type === "text"; })
            .map(function (b) { return b.text; })
            .join("") || "_(empty response)_";
          messages.push({ role: "assistant", content: text2 });
        }
      })
      .catch(function (e) {
        messages.push({ role: "assistant", content: "⚠️ Could not reach Anthropic: " + e + " (a CORS or network issue)." });
      })
      .finally(function () { renderMessages(); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
