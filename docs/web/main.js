async function generate() {
  const idea = document.getElementById("idea").value.trim();
  if (!idea) return alert("Сначала опишите идею 🙂");

  // 👉 ВАЖНО: путь /api/generate подключите сами
  const resp = await fetch(
    "https://voroninsergei-triz-ai-patent-assistant.hf.space/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: [idea] })
    }
  );

  if (!resp.ok) return alert("Ошибка: " + resp.status);

  const { data } = await resp.json();
  const { formula, title, non_obvious_suggestions, justification } = data[0];

  document.getElementById("formula").textContent   = formula;
  document.getElementById("title").textContent      = title;
  document.getElementById("suggestions").textContent= non_obvious_suggestions;
  document.getElementById("justification").textContent = justification;

  document.getElementById("result").classList.remove("hidden");
}

document.getElementById("btn").onclick  = generate;
document.getElementById("copy").onclick = () =>
  navigator.clipboard.writeText(document.getElementById("formula").textContent);
