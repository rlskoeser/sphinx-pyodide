async function runPyodideCode(block_id) {
  const block = document.getElementById(block_id);
  // get other elements  relative to block
  const outputEl = block.querySelector(".pyodide-output");
  const statusEl = block.querySelector(".pyodide-status");
  const depsEl = block.querySelector("script.deps");
  const codeEl = block.querySelector(".pyodide-code");

  if (outputEl) outputEl.textContent = "";
  // statusEl.classList.add("loading");

  if (depsEl) {
    let dependencies  = JSON.parse(depsEl.innerHTML);
    await window.pyodide.loadPackage("micropip");
    const micropip = window.pyodide.pyimport("micropip");
    await micropip.install(dependencies.packages);
  }
  //override stdout handler to append to output element
  window.pyodide.setStdout({
    batched: (msg) =>
      (outputEl.textContent = outputEl.textContent + "\n" + msg),
  });

  // run the code in the code element
  window.pyodide.runPython(`${codeEl.textContent}`);
  // statusEl.classList.replace("loading", "success");
  // reset stdout handler to default
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
    setPyodideBlockStatus(block.id, "loading");
  });

  await initPyodide();

  for (const block of pyodide_blocks) {
    try {
      await runPyodideCode(block.id);
      setPyodideBlockStatus(block.id, "success");
    } catch (err) {
      console.log(err);
      setPyodideBlockStatus(block.id, "error");
    }
  }
});
