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
        # Bridge spike — reach main-thread `sessionStorage` from the worker kernel

        The diagnostics proved the kernel runs in a Web Worker: only `fetch` is
        reachable, never `sessionStorage`/`document`. This spike tests the fix — an
        **anywidget** whose JS runs on the **main thread**, reads the shared key
        slot (`mathlearn.anthropicKey`, same one the JS tutor uses), and syncs it
        back to Python. If this works, #1 (shared key) and #2 (cell picker) are
        both unblocked; they ride the same bridge.

        **How to test:** set a key in the tutor sidebar first (so the slot is
        populated), then reload this page and read the panel below.
        """
    )
    return


@app.cell
def _():
    import anywidget
    import traitlets

    class StorageBridge(anywidget.AnyWidget):
        # Runs on the MAIN THREAD (frontend), so it can touch sessionStorage.
        _esm = """
        function render({ model, el }) {
          function read() {
            try { return window.sessionStorage.getItem('mathlearn.anthropicKey') || ''; }
            catch (e) { return ''; }
          }
          model.set('key', read());
          model.set('ready', true);
          model.save_changes();
          // Python sets `save_value` -> we persist it back to the shared slot.
          model.on('change:save_value', () => {
            try {
              window.sessionStorage.setItem('mathlearn.anthropicKey', model.get('save_value'));
              model.set('key', model.get('save_value'));
              model.save_changes();
            } catch (e) {}
          });
          el.style.cssText = 'font:12px monospace;color:#7c8aa0';
          el.textContent = 'storage bridge active (main thread)';
        }
        export default { render };
        """
        key = traitlets.Unicode("").tag(sync=True)
        ready = traitlets.Bool(False).tag(sync=True)
        save_value = traitlets.Unicode("").tag(sync=True)

    return (StorageBridge,)


@app.cell
def _(StorageBridge, mo):
    bridge = mo.ui.anywidget(StorageBridge())
    bridge
    return (bridge,)


@app.cell(hide_code=True)
def _(bridge, mo):
    _v = bridge.value or {}
    _key = _v.get("key", "")
    _masked = (
        "(empty)" if not _key else (_key[:4] + "…" + _key[-4:] if len(_key) > 8 else "set")
    )
    mo.md(
        f"""
        **Bridge readout**

        - `ready`: `{_v.get("ready")}`
        - key read from sessionStorage: `{_masked}`
        - length: `{len(_key)}`

        If `ready` is `true`, the main-thread bridge is alive. If the key also
        shows (after you set one in the tutor), the read path works — #1/#2 are
        unblocked.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    set_key = mo.ui.text(label="Write-back test — type a key", kind="password", full_width=True)
    save = mo.ui.run_button(label="Save to sessionStorage")
    mo.vstack([set_key, save])
    return save, set_key


@app.cell
def _(bridge, mo, save, set_key):
    mo.stop(not save.value, mo.md("*Type a value and press Save to test write-back.*"))
    bridge.widget.save_value = set_key.value
    mo.md(
        "Saved to the shared slot. Reload — the readout above should show it, and "
        "the tutor sidebar should pick up the same key."
    )
    return


if __name__ == "__main__":
    app.run()
