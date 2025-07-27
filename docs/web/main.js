const API = "https://voroninsergei-triz-ai-patent-assistant-api.hf.space/formula";

async function generate() {
  const title    = document.getElementById("title").value.trim();
  const known    = document.getElementById("known").value.trim();
  const distinct = document.getElementById("distinct").value.trim();
  const effect   = document.getElementById("effect").value.trim();

  if (!title || !effect) {
    alert("Заполните как минимум «Название» и «Эффект»");
    return;
  }

  const resp = await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, known, distinct, effect }),
  });

  if (!resp.ok) {
    alert(`Ошибка API: ${resp.status}`);
    return;
  }

  const { formula } = await resp.json();
  document.getElementById("formula").textContent = formula;
  document.getElementById("result").classList.remove("hidden");
}

document.getElementById("btn").onclick  = generate;
document.getElementById("copy").onclick = () =>
  navigator.clipboard.writeText(document.getElementById("formula").textContent);
