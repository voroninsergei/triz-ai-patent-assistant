// Base URL of the API.
// NOTE: Hugging Face Spaces serve the application at a domain that
// uses a double hyphen (`--`) between the username and space name.
// For example, a space hosted at `voroninsergei/triz-ai-patent-assistant-api`
// will be reachable at `voroninsergei--triz-ai-patent-assistant-api.hf.space`.
// The extra hyphen is critical; without it the domain does not resolve.
const API_BASE   = "https://voroninsergei--triz-ai-patent-assistant-api.hf.space";
const API_FORMULA = `${API_BASE}/formula`;
const API_ANALYZE = `${API_BASE}/analyze`;
const API_ENHANCE = `${API_BASE}/enhance`;

// Translation strings for UI.  Russian (ru) and English (en)
// Added style_compact and style_detailed keys so that the formula style
// drop-down options are translated correctly when the language changes.
const translations = {
  ru: {
    h1: "TRIZ‑AI Patent Assistant",
    label_title: "Название (объект + функция)",
    label_known: "Известные признаки",
    label_distinct: "Отличительные признаки",
    label_effect: "Эффект (технический результат)",
    label_language: "Язык формулы",
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
    // Formula style labels in Russian
    style_compact: "компактный (без повторений)",
    style_detailed: "подробный (с повторениями)",
    // Field labels for result section
    field_title: "Название",
    field_formula: "Формула",
    // Field labels for analysis section
    field_keywords: "Ключевые слова",
    field_ipc: "IPC‑коды",
    field_triz: "TRIZ‑функции",
    field_contradictions: "Противоречия",
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
    // Formula style labels in English
    style_compact: "compact (no repetition)",
    style_detailed: "detailed (with repetition)",
    // Field labels for result section
    field_title: "Name",
    field_formula: "Formula",
    // Field labels for analysis section
    field_keywords: "Keywords",
    field_ipc: "IPC codes",
    field_triz: "TRIZ functions",
    field_contradictions: "Contradictions",
  },
};

// Mapping of Russian connecting phrases to their bolded Russian
// or English equivalents. Used to replace phrases in generated formulas
// depending on the selected language. For Russian, the phrases are wrapped
// in <b> tags; for English, they are translated and wrapped in <b> tags.
const connectorPhrases = {
  ru: {
    "включающий": "<b>включающий</b>",
    "отличающийся тем, что": "<b>отличающийся тем, что</b>",
    "обеспечивает": "<b>обеспечивает</b>",
  },
  en: {
    "включающий": "<b>including</b>",
    "отличающийся тем, что": "<b>characterized in that</b>",
    "обеспечивает": "<b>provides</b>",
  },
};

// Replace connector phrases in a formula string and return formatted HTML.
function formatFormulaText(text, lang) {
  let result = text || "";
  const dict = connectorPhrases[lang] || connectorPhrases.ru;
  Object.keys(dict).forEach((phrase) => {
    // Use global replacement to replace all occurrences.
    const re = new RegExp(phrase, 'g');
    result = result.replace(re, dict[phrase]);
  });
  return result;
}

// Set all UI text to the appropriate language when the language selector changes.
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
  // Update style option labels so the drop-down values reflect the selected language.
  const styleSelect = document.getElementById("style");
  if (styleSelect && styleSelect.options.length >= 2) {
    styleSelect.options[0].textContent = t.style_compact;
    styleSelect.options[1].textContent = t.style_detailed;
  }

  // Update result section labels (Название, Формула) if result is visible
  const resultPre = document.getElementById("result");
  if (resultPre) {
    const resultStrong = resultPre.querySelectorAll("strong");
    if (resultStrong && resultStrong.length >= 2) {
      resultStrong[0].textContent = t.field_title + ":";
      resultStrong[1].textContent = t.field_formula + ":";
    }
  }

  // Update analysis section labels if they exist
  const analyzePre = document.getElementById("analyze_result");
  if (analyzePre) {
    const analyzeLabels = analyzePre.querySelectorAll("strong");
    if (analyzeLabels && analyzeLabels.length >= 4) {
      analyzeLabels[0].textContent = t.field_keywords + ":";
      analyzeLabels[1].textContent = t.field_ipc + ":";
      analyzeLabels[2].textContent = t.field_triz + ":";
      analyzeLabels[3].textContent = t.field_contradictions + ":";
    }
  }
}

// Re-render language-dependent UI whenever the language select changes.
document.getElementById("language").addEventListener("change", updateLanguageUI);

// Generate a patent formula using the backend API
async function generate() {
  const title    = document.getElementById("title").value.trim();
  const known    = document.getElementById("known").value.trim();
  const distinct = document.getElementById("distinct").value.trim();
  const effect   = document.getElementById("effect").value.trim();
  const style    = document.getElementById("style").value;
  const variants = document.getElementById("variants").value;
  const language = document.getElementById("language").value;
  // Validate required fields
  if (!title || !effect) {
    const t = translations[language] || translations.ru;
    alert(t.error_fill_required || "Заполните как минимум «Название» и «Эффект»");
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
  // Format the returned formulas: replace connector phrases and bold them.
  if (Array.isArray(formula)) {
    const formatted = formula.map((f) => formatFormulaText(f, language));
    formulaEl.innerHTML = formatted.join("<br/><br/>");
  } else {
    formulaEl.innerHTML = formatFormulaText(formula, language);
  }
  document.getElementById("f_title").textContent = title;
  document.getElementById("result").classList.remove("hidden");
}

// Analyze a given invention description using the backend API
async function analyze() {
  const text        = document.getElementById("analyze_text").value.trim();
  const maxKwInput  = document.getElementById("max_keywords").value;
  const max_keywords = maxKwInput ? Number(maxKwInput) : undefined;
  const lang = document.getElementById("language").value;
  if (!text) {
    const t = translations[lang] || translations.ru;
    alert(t.error_enter_description || "Введите описание изобретения для анализа");
    return;
  }
  const payload = { text };
  // Include language hint for English analysis.  The backend can infer Russian automatically,
  // but for English we explicitly pass the language code to ensure IPC/TRIZ detection works.
  if (lang === "en") {
    payload.language = "en";
  }
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
    const t = translations[lang] || translations.ru;
    li.textContent = t.no_contradictions;
    contradictionsList.appendChild(li);
  }
  document.getElementById("analyze_result").classList.remove("hidden");

  // After displaying analysis results, update labels according to the selected language
  // so that section titles like Keywords, IPC codes, etc. are translated correctly.
  updateLanguageUI();
}

// Enhance an existing patent formula using the backend API
async function enhance() {
  const formula = document.getElementById("enhance_formula").value.trim();
  const openai_api_key = document.getElementById("openai_api_key").value.trim();
  const provider = document.getElementById("provider").value;
  const lang = document.getElementById("language").value;
  if (!formula) {
    const t = translations[lang] || translations.ru;
    alert(t.error_enter_formula || "Введите формулу для улучшения");
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

// Attach event listeners for user actions
document.getElementById("btn").onclick = generate;
document.getElementById("analyze_btn").onclick = analyze;
document.getElementById("enhance_btn").onclick = enhance;

// Initialise UI on page load
updateLanguageUI();