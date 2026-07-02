async function runPyodideCode(block_id) {
  const block = document.getElementById(block_id);
  const outputEl = block.querySelector(".pyodide-output");
  const depsEl = block.querySelector("script.deps");
  if (outputEl) outputEl.textContent = "";

  if (depsEl) {
    let dependencies = JSON.parse(depsEl.innerHTML);
    await window.pyodide.loadPackage("micropip");
    const micropip = window.pyodide.pyimport("micropip");
    await micropip.install(dependencies.packages);
  }

  window.pyodide.setStdout({
    batched: (msg) => {
      outputEl.textContent += msg + "\n";
    },
  });

  const codeEl = block.querySelector(".pyodide-code") || block.querySelector(".highlight");
  window.pyodide.runPython(codeEl.textContent);
  window.pyodide.setStdout();
}

function setPyodideBlockStatus(block_id, status) {
  const block = document.getElementById(block_id);
  const statusEl = block.querySelector(".pyodide-status");
  statusEl.classList.remove("loading", "success", "error", "idle");
  statusEl.classList.add(status);
}

async function initPyodide() {
  if (!window.pyodide) {
    window.pyodide = await loadPyodide();
  }
}

async function processPyodideBlocks() {
  const pyodide_blocks = Array.from(
    document.getElementsByClassName("pyodide-block")
  );

  for (const block of pyodide_blocks) {
    const outputEl = block.querySelector(".pyodide-output");
    const statusEl = block.querySelector(".pyodide-status");
    const runBtn = block.querySelector(".pyodide-run-button");

    if (outputEl) outputEl.style.display = "block";
    if (statusEl) statusEl.style.display = "flex";

    if (runBtn) {
      setPyodideBlockStatus(block.id, "idle");
    } else {
      setPyodideBlockStatus(block.id, "loading");
      try {
        await runPyodideCode(block.id);
        setPyodideBlockStatus(block.id, "success");
      } catch (err) {
        if (block.dataset.showErrors) {
          const outputEl = block.querySelector(".pyodide-output");
          if (outputEl) outputEl.textContent = "Error: " + (err.message || err);
        }
        console.error(err);
        setPyodideBlockStatus(block.id, "error");
      }
    }

    const editor = block.querySelector(".highlight[contenteditable]");
    if (editor && runBtn) {
      editor.addEventListener("input", () => {
        runBtn.disabled = false;
      });
    }
  }

  document.querySelectorAll(".pyodide-run-button").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const block = btn.closest(".pyodide-block");
      if (!block) return;
      setPyodideBlockStatus(block.id, "loading");
      try {
        await runPyodideCode(block.id);
        setPyodideBlockStatus(block.id, "success");
        btn.disabled = true;
      } catch (err) {
        if (block.dataset.showErrors) {
          const outputEl = block.querySelector(".pyodide-output");
          if (outputEl) outputEl.textContent = "Error: " + (err.message || err);
        }
        console.error(err);
        setPyodideBlockStatus(block.id, "error");
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const enableButton = document.getElementById("pyodide-enable-button");
  if (!enableButton) return;

  enableButton.addEventListener("click", async () => {
    enableButton.textContent = "Loading\u2026";
    enableButton.disabled = true;

    try {
      await initPyodide();
      enableButton.textContent = "\u2713 Enabled";
      enableButton.classList.add("enabled");
      await processPyodideBlocks();
    } catch (err) {
      enableButton.textContent = "Failed to load";
      enableButton.classList.add("error");
      console.error("Pyodide failed to load:", err);
    }
  });
});
