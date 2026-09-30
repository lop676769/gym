```python
import streamlit as st
import google.generativeai as genai
import datetime
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Plateau Breaker", page_icon="🏋️‍♂️", layout="wide")

st.title("🏋️‍♂️ Проект: Plateau Breaker (от HTN к Chadlite)")
st.caption("Персональный трекер тренировок, массы, питания, восстановления и кожи")

# Инициализация хранилища сессии
if "workout_history" not in st.session_state:
    st.session_state.workout_history = []

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("👤 Профиль атлета")
    height = st.number_input("Рост (см)", value=182)
    current_weight = st.number_input("Текущий вес (кг)", value=73.0, step=0.1)
    target_weight = st.number_input("Целевой вес (кг)", value=77.0, step=0.5)

    st.divider()
    st.header("🔑 ИИ Интеграция")
    api_key = st.text_input("Gemini API Key", type="password", help="Бесплатный ключ из Google AI Studio")
    st.caption("Каждая открытая вкладка работает независимо для каждого пользователя.")

# --- ВКЛАДКИ ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏋️‍♂️ Запись и Анализ Тренировки",
    "💤 Сон и Восстановление",
    "📊 Калькулятор КБЖУ",
    "📸 Сканер Еды (ИИ)",
    "🤖 ИИ-Консультант"
])

# --- ВКЛАДКА 1: ЗАПИСЬ И АНАЛИЗ ТРЕНИРОВКИ ---
with tab1:
    st.subheader("📝 Запись проведенной тренировки")

    col_t1, col_t2 = st.columns([1, 2])

    with col_t1:
        workout_date = st.date_input("Дата тренировки", datetime.date.today())
        workout_type = st.selectbox("Группа мышц / Тип тренировки", [
            "Грудь + Трицепс / Жим",
            "Спина + Бицепс / Тяга",
            "Ноги + Плечи / Присед",
            "Full Body (Всё тело)",
            "Кор / Пресс / Кардио",
            "Другое"
        ])
        rpe_level = st.select_slider("Уровень сложности / Нагрузка (RPE)", options=[
            "1-4 (Лёгкая / Разминка)",
            "5-6 (Умеренная)",
            "7-8 (Тяжёлая, 1-2 повтора в запасе)",
            "9-10 (Максимальный отказ / Пик)"
        ], value="7-8 (Тяжёлая, 1-2 повтора в запасе)")
        duration = st.number_input("Длительность (минут)", value=60, step=5, min_value=10)

    with col_t2:
        st.markdown("**Упражнения, вес и повторения:**")
        default_text = (
            "1. Жим штанги лёжа: 80кг х 8, 85кг х 6, 85кг х 5\n"
            "2. Жим гантелей под углом 30°: 28кг х 10, 30кг х 8, 30кг х 8\n"
            "3. Брусья с весом: +15кг х 10, +20кг х 8, +20кг х 6\n"
            "4. Разгибания на блоке (трицепс): 35кг х 12, 40кг х 10, 40кг х 10"
        )
        workout_details = st.text_area("Запиши упражнения списком (Упражнение: вес х повторы):", value=default_text, height=180)
        workout_notes = st.text_input("Ощущения / Заметки (например: 'болело плечо', 'был отличный памп')", value="Отличный памп, в жиме шёл тяжело последний подход")

    if st.button("🧠 Записать и проанализировать через ИИ", type="primary"):
        if not api_key:
            st.error("Пожалуйста, введи Gemini API Key в меню слева!")
        else:
            with st.spinner("ИИ анализирует твою тренировку и прогрессию..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.5-flash")

                    prompt = f"""
                    Ты профессиональный тренер по бодибилдингу и пауэрлифтингу.
                    Проанализируй тренировку атлета:
                    - Рост: {height} см, Вес: {current_weight} кг (Цель: {target_weight} кг, набор массы)
                    - Тип тренировки: {workout_type}
                    - Длительность: {duration} мин
                    - Субъективная нагрузка: {rpe_level}
                    - Список упражнений:
                    {workout_details}
                    - Примечания: {workout_notes}

                    Дай структурированный разбор:
                    1. 📈 **Оценка объёма и интенсивности:** Достаточно ли объема для гипертрофии на наборе массы?
                    2. 🎯 **Прогрессия нагрузок (Рекомендации на следующую тренировку):** В каких упражнениях добавить вес или повторы?
                    3. ⚠️ **Риски и ошибки:** Обрати внимание на дисбаланс, объём или перегрузку.
                    4. 🥤 **Восстановление после тренировки:** Что съесть/выпить прямо сейчас для закрытия анаболического окна?
                    Пиши конкретно, подбадривающе и по делу.
                    """

                    response = model.generate_content(prompt)

                    st.markdown("---")
                    st.markdown("### 📊 Результаты разбора тренировки:")
                    st.markdown(response.text)

                    st.session_state.workout_history.append({
                        "Дата": workout_date,
                        "Тип": workout_type,
                        "Нагрузка": rpe_level,
                        "Заметки": workout_notes
                    })
                    st.success("Тренировка успешно сохранена в дневник!")

                except Exception as e:
                    st.error(f"Ошибка обращения к ИИ: {e}")

    if st.session_state.workout_history:
        st.divider()
        st.subheader("📜 История сохранённых тренировок")
        st.dataframe(pd.DataFrame(st.session_state.workout_history))

# --- ВКЛАДКА 2: СОН И ВОССТАНОВЛЕНИЕ ---
with tab2:
    st.subheader("💤 Мониторинг ЦНС и Кожи")
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        sleep_hours = st.number_input("Длительность сна (часов)", min_value=0.0, max_value=16.0, value=8.0, step=0.5)
        recovery_quality = st.select_slider("Готовность к тренировке (ЦНС)", options=[
            "1/5 — Полное истощение (нужен отдых)",
            "2/5 — Слабое (усталость)",
            "3/5 — Нормальное",
            "4/5 — Хорошее",
            "5/5 — Заряд на 100% (Пик)"
        ], value="4/5 — Хорошее")

    with col_s2:
        skin_status = st.select_slider("Состояние кожи лица", options=[
            "Отлично",
            "Нормально",
            "Небольшие воспаления",
            "Обострение (акне/пот)"
        ])
        skin_notes = st.text_input("Уход за кожей (салицилка, умывание и т.д.)")

    st.info(f"Текущий уровень готовности: {recovery_quality}. Сон: {sleep_hours} ч.")

# --- ВКЛАДКА 3: КАЛЬКУЛЯТОР КБЖУ ---
with tab3:
    st.subheader("📊 Расчёт суточной нормы на набор массы")
    bmr = 10 * current_weight + 6.25 * height - 5 * 18 + 5
    tdee = bmr * 1.55
    surplus_calories = int(tdee + 350)

    protein = int(current_weight * 2.0)
    fats = int(current_weight * 1.0)
    carbs = int((surplus_calories - (protein * 4 + fats * 9)) / 4)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Цель калорий", f"{surplus_calories} ккал", "+350 ккал профицит")
    c2.metric("Белки", f"{protein} г", "2.0 г/кг")
    c3.metric("Жиры", f"{fats} г", "1.0 г/кг")
    c4.metric("Углеводы", f"{carbs} г", "Энергия")

# --- ВКЛАДКА 4: СКАНЕР ЕДЫ ---
with tab4:
    st.subheader("📸 Распознавание еды по фото")
    uploaded_file = st.file_uploader("Сделай фото тарелки или загрузи из галереи", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Твой приём пищи", width=350)

        if st.button("🔍 Рассчитать КБЖУ по фото"):
            if not api_key:
                st.error("Сначала введи Gemini API Key в меню слева!")
            else:
                with st.spinner("Gemini анализирует порцию..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-2.5-flash")

                        prompt = """
                        Проанализируй это фото еды.
                        1. Назови блюда/продукты на тарелке и оцени их примерный вес в граммах.
                        2. Оцени калорийность и БЖУ:
                           - Всего калорий (ккал)
                           - Белки (г)
                           - Жиры (г)
                           - Углеводы (г)
                        3. Соотнеси это с рационом спортсмена на наборе массы (182 см, 73 кг).
                        Напиши чётко, структурированно и с итоговыми цифрами.
                        """

                        response = model.generate_content([prompt, image])
                        st.markdown("### 🥗 Результат анализа:")
                        st.write(response.text)

                    except Exception as e:
                        st.error(f"Ошибка при анализе: {e}")

# --- ВКЛАДКА 5: ИИ-ЧАТ ---
with tab5:
    st.subheader("🤖 Чат с тренером Plateau Breaker")
    user_msg = st.text_area("Задай вопрос по тренировкам, технике, восстановлению или питанию:")
    if st.button("Отправить вопрос"):
        if not api_key:
            st.warning("Введи Gemini API Key в левой панели!")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                prompt_text = f"""
                Ты эксперт-тренер и биохакер проекта Plateau Breaker.
                Параметры атлета: Рост {height} см, Вес {current_weight} кг, Цель {target_weight} кг.
                Запрос пользователя: {user_msg}
                Дай практичный, экспертный и точный совет.
                """
                res = model.generate_content(prompt_text)
                st.write(res.text)
            except Exception as e:
                st.error(f"Ошибка обращения к ИИ: {e}")
```


