# Проект системы выявления TRIZ-функций и противоречий

## Цель

Разработать систему на базе GPT‑модели, которая по текстовому описанию изобретения выделяет ключевые слова, определяет подходящие классы Международной патентной классификации (IPC/МПК) и связывает их с типовыми ТРИЗ‑функциями и противоречиями. Такая система помогает найти аналоги, выявить технические проблемы и наметить направление для решения.

## Общая архитектура

1. **Извлечение ключевых слов**.  Модуль принимает свободный текст и с помощью GPT‑модели выделяет наиболее значимые технические термины: объекты, процессы, свойства.  При этом игнорируются общие или банальные высказывания, подобно тому как в другом контексте рекомендуется не фиксировать **временный контекст и общие принципы**【340773968921043†L19-L27】.  Модель должна возвращать конкретные и действенные ключевые слова, которые хорошо характеризуют технологию, аналогично тому, как для памяти оставляют только **специфические и применимые предпочтения**【340773968921043†L63-L69】.

2. **Классификация по МПК/IPC**.  Используя выделенные ключевые слова, GPT или специализированный классификатор предлагает наиболее вероятные классы IPC.  Возможный подход — обучить модель на паре «описание → IPC» или использовать сторонние сервисы для классификации.  Результатом будет несколько кодов IPC с вероятностями.

3. **Сопоставление с TRIZ‑функциями**.  В базе знаний хранится таблица соответствий между классами IPC и типовыми TRIZ‑функциями (например, превращать, передавать, измерять, очищать и т.д.).  Система подбирает функции, наиболее соответствующие выделенным ключевым словам и классам.

4. **Идентификация противоречий**.  TRIZ рассматривает два вида противоречий: технические (улучшение одного параметра ухудшает другой) и физические (объект должен обладать противоположными свойствами).  Система анализирует описание и выделенные ключевые слова, чтобы сформулировать полезные и вредные параметры, затем по стандартной матрице противоречий TRIZ находит соответствующие принципы и рекомендуемые направления.

5. **Вывод отчёта**.  Итоговый отчёт должен содержать:
   - Список ключевых слов и возможных IPC‑классов;
   - Соответствующие TRIZ‑функции;
   - Выявленные противоречия и рекомендации по их преодолению;
   - Ссылки на патентные классы и описание для дальнейшего анализа.

## Применение GPT

GPT‑модель используется на двух этапах:

* **Ключевые слова** – генерируется системный prompt, который просит модель выделить из текста все технические существительные и глаголы, отбрасывая общеупотребительные слова.  Модель должна избегать слишком общих понятий и уделять внимание новым терминам.

* **Предсказание IPC** – на основе ключевых слов GPT предлагает вероятные классы, объясняя выбор.  Эти предложения затем уточняются через поиск по базе патентов или внешние классификаторы.

## Расширение и интеграция

* **Набор данных**: Для надёжного сопоставления необходимо составить таблицу «IPC → TRIZ‑функции» и «функция → типовые противоречия» вручную или с использованием экспертной базы.

* **Обратная связь**: пользователь может корректировать ключевые слова и предложенные классы; система обучается на таких правках.

* **Интеграция с патентными API**: для верификации IPC и поиска аналогов можно подключить API Espacenet, Google Patents или WIPO.

## Ограничения

В текущем прототипе система не содержит реализацию глубокого NLP‑анализа или внешних API.  Часть функций (классификация IPC и матрица противоречий) требует отдельной базы знаний и может быть реализована как сервис, доступный модели.  Тем не менее предложенная архитектура позволяет начать разработку и постепенно расширять функциональность.
