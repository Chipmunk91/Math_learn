// Cloudflare Worker: a thin, key-holding proxy in front of the Anthropic
// Messages API so the static lesson site can offer an AI tutor without ever
// shipping a key. The API key lives only in the Worker secret ANTHROPIC_API_KEY
// (set with `wrangler secret put ANTHROPIC_API_KEY`), never in the repo or the
// browser.
//
// The Worker locks down what a caller may do: it enforces a CORS origin
// allowlist, forces the model to a cheap allowlisted choice, clamps max_tokens,
// and trims the conversation length. It is still public, so treat the URL as
// rate-limited spend — see worker/README.md for hardening notes.

const ALLOWED_ORIGINS = [
  "https://chipmunk91.github.io",
  // Add "http://localhost:8000" etc. while testing the built site locally.
];

const ALLOWED_MODELS = new Set([
  "claude-haiku-4-5-20251001",
  "claude-sonnet-4-6",
]);
const DEFAULT_MODEL = "claude-haiku-4-5-20251001";

const MAX_TOKENS_CAP = 1024;
const MAX_TURNS = 24;
const MAX_SYSTEM_CHARS = 20000;

function corsHeaders(origin) {
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0] || "*";
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

function json(obj, status, origin) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", ...corsHeaders(origin) },
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }
    if (request.method !== "POST") {
      return json({ error: { message: "Use POST." } }, 405, origin);
    }
    if (ALLOWED_ORIGINS.length && !ALLOWED_ORIGINS.includes(origin)) {
      return json({ error: { message: "Origin not allowed." } }, 403, origin);
    }
    if (!env.ANTHROPIC_API_KEY) {
      return json({ error: { message: "Server is missing ANTHROPIC_API_KEY." } }, 500, origin);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: { message: "Invalid JSON body." } }, 400, origin);
    }

    const incoming = Array.isArray(body.messages) ? body.messages : [];
    const messages = incoming
      .slice(-MAX_TURNS)
      .map((m) => ({
        role: m && m.role === "assistant" ? "assistant" : "user",
        content: String((m && m.content) ?? ""),
      }))
      .filter((m) => m.content.trim().length > 0);

    if (!messages.length) {
      return json({ error: { message: "No messages provided." } }, 400, origin);
    }

    const model = ALLOWED_MODELS.has(body.model) ? body.model : DEFAULT_MODEL;
    const maxTokens = Math.min(Math.max(Number(body.max_tokens) || 800, 1), MAX_TOKENS_CAP);

    const payload = { model, max_tokens: maxTokens, messages };
    if (typeof body.system === "string" && body.system.trim()) {
      payload.system = body.system.slice(0, MAX_SYSTEM_CHARS);
    }

    let upstream;
    try {
      upstream = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": env.ANTHROPIC_API_KEY,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify(payload),
      });
    } catch (err) {
      return json({ error: { message: `Upstream request failed: ${err}` } }, 502, origin);
    }

    // Pass Anthropic's JSON (success or error) straight through, with CORS.
    const text = await upstream.text();
    return new Response(text, {
      status: upstream.status,
      headers: { "content-type": "application/json", ...corsHeaders(origin) },
    });
  },
};
