// Base URL of the API.  If deployed on HuggingFace, adjust accordingly.
const API_BASE = "https://voroninsergei-triz-ai-patent-assistant-api.hf.space";
const API_FORMULA = `${API_BASE}/formula`;
const API_ANALYZE = `${API_BASE}/analyze`;
const API_ENHANCE = `${API_BASE}/enhance`;

// Translation strings for UI.  Russian (ru) and English (en)
const translations = {
  ru: {
    h1: "TRIZ‑AI Patent Assistant",
    label_title: "Название (объект + функция)",
    label_known: "Известные признаки",
    label_distinct: "Отличительные признаки",
    label_effect: "Эффект (технический результат)",
    label_language: "Язык формулы (Formula language)",
    label_style: "Стиль формулы",
    label_variants: "Количество вариантов (оставьте пустым для одного варианта)",
    btn_generate: "Сгенерировать формулу",
    header_analyze: "Анализ изобретения",
    label_analyze_text: "Текст описания изобретения",
    label_max_keywords: "Макс. количество ключевых слов",
    btn_analyze: "Анализировать",
    header_enhance: "Улучшение формулы",
    label_enhance_formula: "Формула для улучшения",
    label_api_key: "API‑ключ (опционально, для использования LLM)",
    label_provider: "Провайдер",
    btn_enhance: "Улучшить формулу",
    no_contradictions: "Противоречия не обнаружены",
  },
  en: {
    h1: "TRIZ‑AI Patent Assistant",
    label_title: "Name (object + function)",
    label_known: "Known features",
    label_distinct: "Distinctive features",
    label_effect: "Effect (technical result)",
    label_language: "Formula language",
    label_style: "Formula style",
    label_variants: "Number of variants (leave blank for one variant)",
    btn_generate: "Generate formula",
    header_analyze: "Invention analysis",
    label_analyze_text: "Description text for analysis",
    label_max_keywords: "Max. number of keywords",
    btn_analyze: "Analyze",
    header_enhance: "Enhance formula",
    label_enhance_formula: "Formula for enhancement",
    label_api_key: "API key (optional, for using LLM)",
    label_provider: "Provider",
    btn_enhance: "Enhance formula",
    no_contradictions: "No contradictions found",
  },
};

function updateLanguageUI() {
  const lang = document.getElementById("language").value;
  const t = translations[lang] || translations.ru;
  // Update labels and buttons
  document.querySelector("h1").textContent = t.h1;
  document.getElementById("label_title").childNodes[0].nodeValue = t.label_title + "\n";
  document.getElementById("label_known").childNodes[0].nodeValue = t.label_known + "\n";
  document.getElementById("label_distinct").childNodes[0].nodeValue = t.label_distinct + "\n";
  document.getElementById("label_effect").childNodes[0].nodeValue = t.label_effect + "\n";
  document.getElementById("label_language").childNodes[0].nodeValue = t.label_language + "\n";
  document.getElementById("label_style").childNodes[0].nodeValue = t.label_style + "\n";
  document.getElementById("label_variants").childNodes[0].nodeValue = t.label_variants + "\n";
  document.getElementById("btn").textContent = t.btn_generate;
  document.querySelector("h2:nth-of-type(1)").textContent = t.header_analyze;
  document.getElementById("label_analyze_text").childNodes[0].nodeValue = t.label_analyze_text + "\n";
  document.getElementById("label_max_keywords").childNodes[0].nodeValue = t.label_max_keywords + "\n";
  document.getElementById("analyze_btn").textContent = t.btn_analyze;
  document.querySelector("h2:nth-of-type(2)").textContent = t.header_enhance;
  document.getElementById("label_enhance_formula").childNodes[0].nodeValue = t.label_enhance_formula + "\n";
  document.getElementById("label_api_key").childNodes[0].nodeValue = t.label_api_key + "\n";
  document.getElementById("label_provider").childNodes[0].nodeValue = t.label_provider + "\n";
  document.getElementById("enhance_btn").textContent = t.btn_enhance;
  // Update placeholder texts
  document.getElementById("title").placeholder = lang === "en" ? "Cooling system for an electric car battery" : "Система охлаждения аккумулятора…";
  document.getElementById("known").placeholder = lang === "en" ? "radiator, electric fan" : "радиатор, электрический вентилятор";
  document.getElementById("distinct").placeholder = lang === "en" ? "heat pipes, controller regulating coolant flow…" : "тепловые трубки, контроллер…";
  document.getElementById("effect").placeholder = lang === "en" ? "maintains cell temperature at 20‑35 °C during fast charging" : "поддерживает температуру ячеек 20‑35 °C…";
  document.getElementById("analyze_text").placeholder = lang === "en" ? "Describe the invention for analysis…" : "Опишите изобретение для анализа…";
  document.getElementById("enhance_formula").placeholder = lang === "en" ? "Enter the formula for enhancement…" : "Введите формулу для улучшения…";
  document.getElementById("openai_api_key").placeholder = lang === "en" ? "sk‑…" : "sk‑…";
}

// Update UI on language change
document.getElementById("language").addEventListener("change", updateLanguageUI);

async function generate() {
  const title    = document.getElementById("title").value.trim();
  const known    = document.getElementById("known").value.trim();
  const distinct = document.getElementById("distinct").value.trim();
  const effect   = document.getElementById("effect").value.trim();
  const style    = document.getElementById("style").value;
  const variants = document.getElementById("variants").value;
  const language = document.getElementById("language").value;

  if (!title || !effect) {
    alert("Заполните как минимум «Название» и «Эффект»");
    return;
  }
  // Build request body with optional variants
  const payload = { title, known, distinct, effect, style, language };
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
  if (result.contradictions && result.contradictions.length) {
    (result.contradictions || []).forEach((c) => {
      const li = document.createElement("li");
      li.textContent = c.description || c;
      contradictionsList.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    const lang = document.getElementById("language").value;
    li.textContent = translations[lang].no_contradictions;
    contradictionsList.appendChild(li);
  }
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

// Initialise UI language on page load
updateLanguageUI();
