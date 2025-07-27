async function generate() {
  const title       = document.getElementById("title").value.trim();
  const known       = document.getElementById("known").value.trim();
  const distinctive = document.getElementById("distinctive").value.trim();
  const effect      = document.getElementById("effect").value.trim();

  if (!title || !known || !distinctive || !effect) {
    return alert("Заполните все четыре поля 🙏");
  }

  const payload = {
    data: [title, known, distinctive, effect]   // порядок важен ↴
  };

  const resp = await fetch(
    "https://voroninsergei-triz-ai-patent-assistant-api.hf.space/run",
    {
      method : "POST",
      headers: { "Content-Type": "application/json" },
      body   : JSON.stringify(payload)
    }
  );

  if (!resp.ok) return alert("Ошибка: " + resp.status);

  const { data } = await resp.json();          // HF Spaces возвращают {data:[…]}
  const { formula } = data[0];                 // ваша API отдаёт объект с ключом formula

  document.getElementById("formula").textContent = formula;
  document.getElementById("result").classList.remove("hidden");
  document.getElementById("copy"  ).classList.remove("hidden");
}

document.getElementById("btn").onclick  = generate;
document.getElementById("copy").onclick = () =>
  navigator.clipboard.writeText(document.getElementById("formula").textContent);
