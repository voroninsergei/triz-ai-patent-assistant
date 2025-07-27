async function generate() {
  const title     = document.getElementById("title").value.trim();
  const known     = document.getElementById("known").value.trim();
  const distinct  = document.getElementById("distinct").value.trim();
  const effect    = document.getElementById("effect").value.trim();

  if (!title || !effect) {
    return alert("Поля «Название» и «Эффект» обязательны.");
  }

  const payload = { title, known, distinct, effect };

  // 👉 адрес вашего FastAPI бэкенда на Spaces
  const resp = await fetch(
    "https://voroninsergei-triz-ai-patent-assistant-api.hf.space/formula",
    {
      method : "POST",
      headers: { "Content-Type": "application/json" },
      body   : JSON.stringify(payload)
    }
  );

  if (!resp.ok) {
    return alert("Ошибка " + resp.status);
  }

  const data = await resp.json();        // {formula: "..."}
  document.getElementById("formula").textContent = data.formula;
  document.getElementById("result").classList.remove("hidden");
}

document.getElementById("btn").onclick  = generate;
document.getElementById("copy").onclick = () =>
  navigator.clipboard.writeText(document.getElementById("formula").textContent);
