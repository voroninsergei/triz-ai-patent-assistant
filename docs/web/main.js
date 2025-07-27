<script>
/*  URL вашего Space после сборки  */
const API = "https://voroninsergei-triz-ai-patent-assistant-api.hf.space/formula";

/*  отправляем данные на BE и выводим результат  */
async function generate() {
  // читаем поля формы
  const title        = document.getElementById("title").value.trim();
  const known        = document.getElementById("known").value.trim();
  const distinctive  = document.getElementById("distinctive").value.trim();
  const effect       = document.getElementById("effect").value.trim();

  if (!title || !effect)
    return alert("Заполните как минимум Название и Эффект 🙂");

  // POST‑запрос к FastAPI
  const resp = await fetch(API, {
    method : "POST",
    headers: { "Content-Type": "application/json" },
    body   : JSON.stringify({           // → Idea(BaseModel) в app.py
      title, known, distinctive, effect
    })
  });

  if (!resp.ok)
    return alert("Ошибка: " + resp.status);

  const data = await resp.json();

  // выводим результат
  document.getElementById("formula").textContent       = data.formula;
  document.getElementById("result").classList.remove("hidden");
}

// привязки кнопок
document.getElementById("btn").onclick  = generate;
document.getElementById("copy").onclick = () =>
  navigator.clipboard.writeText(document.getElementById("formula").textContent);
</script>
