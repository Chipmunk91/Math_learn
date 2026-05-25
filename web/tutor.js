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
    "- If a question is unrelated to the chapter, answer briefly and steer back.";

  var messages = []; // {role, content}
  var scope = "";    // highlighted passage, if any

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
  }

  // ---- key storage (session only) --------------------------------------
  function getKey() { try { return sessionStorage.getItem(KEY_STORE) || ""; } catch (e) { return ""; } }
  function setKey(k) { try { sessionStorage.setItem(KEY_STORE, k); } catch (e) {} }
  function clearKey() { try { sessionStorage.removeItem(KEY_STORE); } catch (e) {} }
  function getModel() { try { return sessionStorage.getItem(MODEL_STORE) || MODELS[0].id; } catch (e) { return MODELS[0].id; } }
  function setModel(m) { try { sessionStorage.setItem(MODEL_STORE, m); } catch (e) {} }

  // ---- open / close + selection capture --------------------------------
  function openPanel() {
    var sel = "";
    try { sel = String(window.getSelection ? window.getSelection() : "").trim(); } catch (e) {}
    if (sel) scope = sel;
    el.panel.classList.add("mt-open");
    if (!getKey()) { renderSetup(); } else { renderChat(); }
  }
  function closePanel() { el.panel.classList.remove("mt-open"); }

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
      bub.innerHTML = m.role === "user" ? esc(m.content).replace(/\n/g, "<br>") : mdToHtml(m.content);
      row.appendChild(bub);
      b.appendChild(row);
    });
    b.scrollTop = b.scrollHeight;
  }

  function renderFoot() {
    var f = el.foot;
    f.innerHTML = "";

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
    ta.placeholder = "Ask about this chapter…";
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
