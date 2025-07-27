"""
Streamlit web application for the TRIZ analysis system.

This script provides a simple graphical interface built on Streamlit that
allows users to input a textual description of an invention, run the TRIZ
analysis and view the resulting keywords, IPC codes, TRIZ functions and
contradictions.  Users can also download a generated .docx report.

To run this app locally, install ``streamlit`` in your environment and execute:

    streamlit run streamlit_app.py

Note that Streamlit is not installed in the current sandbox, but the code
is provided for future integration.
"""

import io
import streamlit as st  # type: ignore
from triz_system import analyze_invention, export_report
from prompt_enhancer import enhance_formula, export_enhancement_report


# Localisation strings for GUI elements.  Keys correspond to supported
# languages ('ru', 'en').  Each sub‑dictionary contains UI labels and
# messages used throughout the Streamlit app.  If adding new UI text,
# ensure translations for both languages are provided.
UI_TEXT = {
    'ru': {
        'title': 'TRIZ‑анализ изобретения',
        'intro': (
            'Введите описание изобретения ниже. Система выделит ключевые слова, '
            'определит коды МПК, сопоставит функции ТРИЗ и найдёт возможные противоречия.'
        ),
        'description': 'Описание',
        'max_keywords': 'Количество ключевых слов',
        'style': 'Стиль формулы',
        'style_help': "'compact' удаляет дубли и сводит признаки, 'verbose' сохраняет исходные формулировки",
        'variants': 'Количество вариантов формулы',
        'variants_help': "При 2 и более выводятся 'широкая' и 'узкая' формулы",
        'language': 'Язык описания',
        'language_help': 'Определяет язык для лемматизации и построения формулы',
        'analyze': 'Анализировать',
        'error_no_text': 'Пожалуйста, введите описание.',
        'analyzing': 'Анализ...',
        'keywords': 'Ключевые слова',
        'ipc_codes': 'Коды IPC',
        'triz_functions': 'TRIZ‑функции',
        'contradictions': 'Противоречия',
        'download_report': 'Скачать отчёт (.docx)',
        'download': 'Скачать отчёт',
        'improve_formula': 'Улучшить формулу',
        'generating': 'Генерация формулы и улучшение...',
        'generated_formulas': 'Сгенерированные формулы',
        'generated_formula': 'Сгенерированная формула',
        'variant': 'Вариант',
        'improved_title': 'Улучшенное название',
        'suggestions': 'Подсказки по неочевидности',
        'justification': 'Обоснование патентоспособности',
        'download_improved_report': 'Скачать улучшенный отчёт (.docx)',
        'download_improved': 'Скачать улучшенный отчёт',
    },
    'en': {
        'title': 'TRIZ invention analysis',
        'intro': (
            'Enter the invention description below. The system will highlight keywords, '
            'determine IPC codes, map TRIZ functions and find possible contradictions.'
        ),
        'description': 'Description',
        'max_keywords': 'Number of keywords',
        'style': 'Formula style',
        'style_help': "'compact' removes duplicates and merges features, 'verbose' preserves original wording",
        'variants': 'Number of formula variants',
        'variants_help': "When 2 or more, 'wide' and 'narrow' formulas are shown",
        'language': 'Language of description',
        'language_help': 'Determines the language for lemmatisation and formula generation',
        'analyze': 'Analyze',
        'error_no_text': 'Please enter a description.',
        'analyzing': 'Analyzing...',
        'keywords': 'Keywords',
        'ipc_codes': 'IPC codes',
        'triz_functions': 'TRIZ functions',
        'contradictions': 'Contradictions',
        'download_report': 'Download report (.docx)',
        'download': 'Download report',
        'improve_formula': 'Enhance formula',
        'generating': 'Generating formula and enhancing...',
        'generated_formulas': 'Generated formulas',
        'generated_formula': 'Generated formula',
        'variant': 'Variant',
        'improved_title': 'Improved title',
        'suggestions': 'Non‑obviousness tips',
        'justification': 'Patentability justification',
        'download_improved_report': 'Download improved report (.docx)',
        'download_improved': 'Download improved report',
    },
}


def main() -> None:
    """Run the Streamlit app with localisation support."""
    # Select the UI language; default to Russian.  This setting governs
    # the language of the interface and the lemmatisation for formula
    # generation.
    # Place language selector at the top so that subsequent labels are
    # rendered in the chosen language.
    lang = st.sidebar.selectbox('Language / Язык', options=['ru', 'en'], index=0)
    ui = UI_TEXT.get(lang, UI_TEXT['ru'])
    st.title(ui['title'])
    st.write(ui['intro'])
    # Text input
    text = st.text_area(ui['description'], height=300)
    # Controls for analysis and formula generation
    max_keywords = st.slider(ui['max_keywords'], min_value=5, max_value=20, value=10)
    style_option = st.selectbox(
        ui['style'],
        options=['compact', 'verbose'],
        index=0,
        help=ui['style_help'],
    )
    variants_option = st.slider(
        ui['variants'],
        min_value=1,
        max_value=3,
        value=1,
        help=ui['variants_help'],
    )
    language_option = st.selectbox(
        ui['language'],
        options=['ru', 'en'],
        index=0 if lang == 'ru' else 1,
        help=ui['language_help'],
    )
    # Buttons area
    col1, col2 = st.columns(2)
    with col1:
        if st.button(ui['analyze']):
            if not text.strip():
                st.error(ui['error_no_text'])
            else:
                with st.spinner(ui['analyzing']):
                    analysis = analyze_invention(text, max_keywords=max_keywords)
                st.subheader(ui['keywords'])
                st.write(analysis['keywords'])
                st.subheader(ui['ipc_codes'])
                st.write(analysis['ipc_codes'])
                st.subheader(ui['triz_functions'])
                st.write(analysis['triz_functions'])
                st.subheader(ui['contradictions'])
                for c in analysis['contradictions']:
                    # Capitalise type; for English we leave it capitalised as is
                    c_type = c['type'].capitalize()
                    st.write(f"**{c_type}**: {c['description']}")
                # Export button
                if st.button(ui['download_report']):
                    buf = io.BytesIO()
                    export_report(analysis, buf)
                    buf.seek(0)
                    st.download_button(
                        label=ui['download'],
                        data=buf.getvalue(),
                        file_name='triz_report.docx',
                        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    )
    with col2:
        if st.button(ui['improve_formula']):
            if not text.strip():
                st.error(ui['error_no_text'])
            else:
                with st.spinner(ui['generating']):
                    from generate_formula import generate_formula
                    # Generate one or more formulas according to selected options
                    formulas = generate_formula(
                        text,
                        style=style_option,
                        variants=variants_option,
                        language=language_option,
                    )
                    # Display generated formulas
                    if isinstance(formulas, list):
                        st.subheader(ui['generated_formulas'])
                        for i, frm in enumerate(formulas, start=1):
                            st.write(f"**{ui['variant']} {i}:** {frm}")
                        # Choose the first variant for enhancement
                        formula_for_enhancement = formulas[0] if formulas else ''
                    else:
                        st.subheader(ui['generated_formula'])
                        st.write(formulas)
                        formula_for_enhancement = formulas
                    enhancements = enhance_formula(formula_for_enhancement)
                st.subheader(ui['improved_title'])
                st.write(enhancements['title'])
                st.subheader(ui['suggestions'])
                st.write(enhancements['non_obvious_suggestions'].split('\n'))
                st.subheader(ui['justification'])
                st.write(enhancements['justification'].split('\n'))
                # Download improved report
                if st.button(ui['download_improved_report']):
                    buf = io.BytesIO()
                    export_enhancement_report(enhancements, buf)
                    buf.seek(0)
                    st.download_button(
                        label=ui['download_improved'],
                        data=buf.getvalue(),
                        file_name='formula_enhancement.docx',
                        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    )


if __name__ == '__main__':
    main()