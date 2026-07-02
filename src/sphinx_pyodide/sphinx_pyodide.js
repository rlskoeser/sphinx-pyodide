async function runPyodideCode(block_id) {
  const block = document.getElementById(block_id);
  const outputEl = block.querySelector(".pyodide-output");
  const depsEl = block.querySelector("script.deps");
  const codeEl = block.querySelector(".pyodide-code");

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

  window.pyodide.runPython(`${codeEl.textContent}`);
  window.pyodide.setStdout();
}

function setPyodideBlockStatus(block_id, status = "loading") {
  const block = document.getElementById(block_id);
  const statusEl = block.querySelector(".pyodide-status");
  if (status == "loading") {
    statusEl.classList.add(status);
  } else {
    statusEl.classList.replace("loading", status);
  }
}

async function initPyodide() {
  if (!window.pyodide) {
    window.pyodide = await loadPyodide();
  }
}

document.addEventListener("DOMContentLoaded", async function () {
  const pyodide_blocks = Array.from(
    document.getElementsByClassName("pyodide-block")
  );
  if (!pyodide_blocks.length) return;

  pyodide_blocks.forEach((block) => {
    const outputEl = block.querySelector(".pyodide-output");
    const statusEl = block.querySelector(".pyodide-status");
    if (outputEl) outputEl.style.display = "block";
    if (statusEl) statusEl.style.display = "block";
    setPyodideBlockStatus(block.id, "loading");
  });

  try {
    await initPyodide();
  } catch (err) {
    const msg = "Pyodide failed to load: " + (err.message || err);
    document.querySelectorAll(".pyodide-output").forEach((el) => {
      el.textContent = msg;
    });
    document.querySelectorAll(".pyodide-status").forEach((el) => {
      el.classList.replace("loading", "error");
    });
    console.error(msg, err);
    return;
  }

  for (const block of pyodide_blocks) {
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
});
