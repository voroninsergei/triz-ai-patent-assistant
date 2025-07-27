// Base URL of the API.  If deployed on HuggingFace, adjust accordingly.
const API_BASE = "https://voroninsergei-triz-ai-patent-assistant-api.hf.space";
const API_FORMULA = `${API_BASE}/formula`;
const API_ANALYZE = `${API_BASE}/analyze`;
const API_ENHANCE = `${API_BASE}/enhance`;

async function generate() {
  const title    = document.getElementById("title").value.trim();
  const known    = document.getElementById("known").value.trim();
  const distinct = document.getElementById("distinct").value.trim();
  const effect   = document.getElementById("effect").value.trim();
  const style    = document.getElementById("style").value;
  const variants = document.getElementById("variants").value;

  if (!title || !effect) {
    alert("Заполните как минимум «Название» и «Эффект»");
    return;
  }
  // Build request body with optional variants
  const payload = { title, known, distinct, effect, style };
  if (variants) payload.variants = Number(variants);

  const resp = await fetch(API_FORMULA, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    alert(`Ошибка API: ${resp.status}`);
    return;
  }

  const data = await resp.json();
  const formula = data.formula;
  const formulaEl = document.getElementById("formula");
  // If multiple variants returned, join them with line breaks
  if (Array.isArray(formula)) {
    formulaEl.textContent = formula.join("\n\n");
  } else {
    formulaEl.textContent = formula;
  }
  document.getElementById("f_title").textContent = title;
  document.getElementById("result").classList.remove("hidden");
}

async function analyze() {
  const text        = document.getElementById("analyze_text").value.trim();
  const maxKwInput  = document.getElementById("max_keywords").value;
  const max_keywords = maxKwInput ? Number(maxKwInput) : undefined;
  if (!text) {
    alert("Введите описание изобретения для анализа");
    return;
  }
  const payload = { text };
  if (max_keywords) payload.max_keywords = max_keywords;
  const resp = await fetch(API_ANALYZE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    alert(`Ошибка API анализа: ${resp.status}`);
    return;
  }
  const result = await resp.json();
  document.getElementById("keywords").textContent = (result.keywords || []).join(", ");
  document.getElementById("ipc_codes").textContent = (result.ipc_codes || []).join(", ");
  document.getElementById("triz_functions").textContent = (result.triz_functions || []).join(", ");
  const contradictionsList = document.getElementById("contradictions");
  contradictionsList.innerHTML = "";
  (result.contradictions || []).forEach((c) => {
    const li = document.createElement("li");
    li.textContent = c.description || c;
    contradictionsList.appendChild(li);
  });
  document.getElementById("analyze_result").classList.remove("hidden");
}

async function enhance() {
  const formula = document.getElementById("enhance_formula").value.trim();
  const openai_api_key = document.getElementById("openai_api_key").value.trim();
  const provider = document.getElementById("provider").value;
  if (!formula) {
    alert("Введите формулу для улучшения");
    return;
  }
  const payload = { formula, provider };
  if (openai_api_key) payload.openai_api_key = openai_api_key;
  const resp = await fetch(API_ENHANCE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    alert(`Ошибка API улучшения: ${resp.status}`);
    return;
  }
  const result = await resp.json();
  document.getElementById("enhance_title").textContent = result.title || "";
  document.getElementById("non_obvious").textContent = result.non_obvious_suggestions || result.non_obvious || "";
  document.getElementById("justification").textContent = result.justification || "";
  document.getElementById("enhance_result").classList.remove("hidden");
}

// Attach event listeners
document.getElementById("btn").onclick = generate;
document.getElementById("analyze_btn").onclick = analyze;
document.getElementById("enhance_btn").onclick = enhance;
