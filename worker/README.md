# Tutor proxy (Cloudflare Worker)

A tiny key-holding proxy so the static lesson site can offer an AI tutor
without ever shipping an Anthropic API key. The browser POSTs a conversation
to this Worker; the Worker adds the secret key and forwards it to Anthropic's
Messages API, then returns the reply with CORS headers.

```
browser (GitHub Pages, Pyodide)  ──POST {system, messages}──▶  Worker  ──x-api-key──▶  api.anthropic.com
```

## Deploy

1. Install the CLI and log in:
   ```sh
   npm install -g wrangler
   wrangler login
   ```
2. From this `worker/` directory, store your key as a secret (never committed):
   ```sh
   wrangler secret put ANTHROPIC_API_KEY
   ```
3. Publish:
   ```sh
   wrangler deploy
   ```
   Wrangler prints a URL like `https://math-tutor.<your-subdomain>.workers.dev`.
4. Put that URL in the lesson: set `TUTOR_ENDPOINT` in
   `differential_equations/delib/tutor.py` (or pass `endpoint=` to
   `delib.tutor(...)`), then rebuild the site.
5. Make sure your GitHub Pages origin is in `ALLOWED_ORIGINS` at the top of
   `tutor-proxy.js` (it ships with `https://chipmunk91.github.io`).

Test it without a browser:

```sh
curl -X POST https://math-tutor.<your-subdomain>.workers.dev \
  -H 'Origin: https://chipmunk91.github.io' \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"hello"}]}'
```

## What the Worker enforces

- **CORS allowlist** — only listed origins get a usable response.
- **Model allowlist** — defaults to Claude Haiku (cheap); ignores any other
  model the caller asks for.
- **`max_tokens` cap** (1024) and **conversation trim** (last 24 turns) to bound
  cost per request.

## Cost / abuse note

The URL is public. The origin check stops casual browser misuse, but `Origin`
can be spoofed by a non-browser client, so anyone who finds the URL could spend
your tokens. For a class-sized audience the token caps keep this cheap. If you
expose it widely, add a real gate:

- Cloudflare **Rate Limiting** rules on the route, and/or
- **Turnstile** (a free CAPTCHA): verify the token in the Worker before calling
  Anthropic, and/or
- a shared secret header the page sends (modest protection — still visible in
  client code).
