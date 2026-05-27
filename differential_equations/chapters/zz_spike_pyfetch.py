import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    import delib
    return delib, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Spike — can the kernel talk to Claude? (client-side, BYO-key)

        Throwaway test of the **single make-or-break unknown** for the in-notebook
        playground: *can marimo's WASM kernel call the Anthropic API directly from
        Python?* If a reply renders below, the whole playground design is feasible
        client-side with no server.

        Paste your Anthropic API key, type anything, press **Ask**. Your key stays
        in your browser and is sent only to `api.anthropic.com`.
        """
    )
    return


@app.cell
def _():
    import json

    SPIKE_MODEL = "claude-haiku-4-5-20251001"
    ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

    async def ask_claude(key, prompt):
        body = json.dumps(
            {
                "model": SPIKE_MODEL,
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}],
            }
        )
        headers = {
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "anthropic-dangerous-direct-browser-access": "true",
        }
        try:
            # WASM path: routes through the browser's fetch().
            from pyodide.http import pyfetch

            resp = await pyfetch(
                ANTHROPIC_URL, method="POST", headers=headers, body=body
            )
            data = await resp.json()
        except ModuleNotFoundError:
            # Local path (marimo edit on CPython): plain urllib.
            import urllib.request
            import urllib.error

            req = urllib.request.Request(
                ANTHROPIC_URL, data=body.encode(), headers=headers, method="POST"
            )
            try:
                with urllib.request.urlopen(req) as r:
                    data = json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                data = json.loads(e.read().decode())

        if isinstance(data, dict) and data.get("content"):
            return "".join(b.get("text", "") for b in data["content"])
        return "**API error**\n\n```json\n" + json.dumps(data, indent=2)[:1000] + "\n```"

    return (ask_claude,)


@app.cell(hide_code=True)
def _(mo):
    api_key = mo.ui.text(label="Anthropic API key", kind="password", full_width=True)
    prompt = mo.ui.text_area(
        label="Ask Claude something",
        value="Say hello in exactly five words.",
        full_width=True,
    )
    ask = mo.ui.run_button(label="Ask")
    mo.vstack([api_key, prompt, ask])
    return api_key, ask, prompt


@app.cell
async def _(api_key, ask, ask_claude, mo, prompt):
    mo.stop(not ask.value, mo.md("*Press **Ask** to send.*"))
    mo.stop(not api_key.value, mo.callout("Enter your API key first.", kind="warn"))

    _reply = await ask_claude(api_key.value, prompt.value)
    mo.md(_reply)
    return


if __name__ == "__main__":
    app.run()
