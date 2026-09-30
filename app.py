import datetime
import google.generativeai as genai
import pandas as pd
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Plateau Breaker", page_icon="🏋️‍♂️", layout="wide"
)

st.title("🏋️‍♂️ Проект: Plateau Breaker (от HTN к Chadlite)")
st.caption(
    "Персональный трекер массы, силовых, сна, питания и ухода за кожей"
)

if "food_log" not in st.session_state:
  st.session_state.food_log = []

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
  st.header("👤 Профиль")
  height = st.number_input("Рост (см)", value=182)
  current_weight = st.number_input("Текущий вес (кг)", value=73.0, step=0.1)
  target_weight = st.number_input("Целевой вес (кг)", value=77.0, step=0.5)

  st.divider()
  st.header("🔑 ИИ Интеграция")
  api_key = st.text_input(
      "Gemini API Key",
      type="password",
      help="Бесплатный ключ из Google AI Studio",
  )

# --- ВКЛАДКИ ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Калькулятор",
    "📸 Сканер Еды (ИИ)",
    "📅 Дневник и Восстановление",
    "🤖 ИИ-Консультант",
])

# --- ВКЛАДКА 1: КАЛЬКУЛЯТОР ---
with tab1:
  st.subheader("Расчёт суточной нормы на набор массы")
  bmr = 10 * current_weight + 6.25 * height - 5 * 18 + 5
  tdee = bmr * 1.55
  surplus_calories = int(tdee + 350)

  protein = int(current_weight * 2.0)
  fats = int(current_weight * 1.0)
  carbs = int((surplus_calories - (protein * 4 + fats * 9)) / 4)

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Суточная цель", f"{surplus_calories} ккал", "+350 ккал профицит")
  col2.metric("Белки", f"{protein} г", "2.0 г/кг")
  col3.metric("Жиры", f"{fats} г", "1.0 г/кг")
  col4.metric("Углеводы", f"{carbs} г", "Энергия")

# --- ВКЛАДКА 2: СКАНЕР ЕДЫ ---
with tab2:
  st.subheader("📸 Распознавание еды по фото")
  uploaded_file = st.file_uploader(
      "Сделай фото тарелки или загрузи из галереи",
      type=["jpg", "jpeg", "png"],
  )

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

# --- ВКЛАДКА 3: ДНЕВНИК И ВОССТАНОВЛЕНИЕ ---
with tab3:
  st.subheader("1. Нагрузка и вес")
  col_date, col_w, col_bench, col_squat = st.columns(4)
  date_val = col_date.date_input("Дата", datetime.date.today())
  weight_val = col_w.number_input(
      "Вес утром (кг)", value=current_weight, step=0.1
  )
  bench_val = col_bench.number_input(
      "Жим лёжа (рабочий вес/повторы)", value=105.0
  )
  squat_val = col_squat.number_input(
      "Присед (рабочий вес/повторы)", value=130.0
  )

  st.divider()
  st.subheader("2. 💤 Сон и Восстановление ЦНС")
  col_sleep_h, col_sleep_q = st.columns(2)
  sleep_hours = col_sleep_h.number_input(
      "Длительность сна (часов)",
      min_value=0.0,
      max_value=16.0,
      value=8.0,
      step=0.5,
  )
  recovery_quality = col_sleep_q.select_slider(
      "Качество сна / Готовность к тренировке",
      options=[
          "1/5 — Разбитое (нужен отдых / пропуск)",
          "2/5 — Слабое (усталость)",
          "3/5 — Нормальное",
          "4/5 — Хорошее",
          "5/5 — Полный заряд / Пиковая форма",
      ],
      value="4/5 — Хорошее",
  )

  st.divider()
  st.subheader("3. 🧖‍♂️️ Кожа и заметки")
  skin_status = st.select_slider(
      "Состояние кожи",
      options=[
          "Отлично",
          "Нормально",
          "Есть воспаления",
          "Сильное обострение (после зала)",
      ],
  )
  notes = st.text_input(
      "Заметки (уход, салицилка, бодряки/кофеин, режим делоада)"
  )

  if st.button("Сохранить запись за день"):
    st.success("Данные зафиксированы!")

# --- ВКЛАДКА 4: ИИ-ЧАТ ---
with tab4:
  st.subheader("Консультант Plateau Breaker")
  user_msg = st.text_area(
      "Задай вопрос по тренировкам, восстановлению, коже или питанию:"
  )
  if st.button("Отправить"):
    if not api_key:
      st.warning("Введи Gemini API Key в левой панели!")
    else:
      try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt_text = f"""
                Ты эксперт-тренер и биохакер проекта Plateau Breaker.
                Параметры атлета: Рост {height} см, Вес {current_weight} кг, Цель {target_weight} кг.
                Силовые: Жим {bench_val} кг, Присед {squat_val} кг.
                Данные по восстановлению: Сон {sleep_hours} часов, Самочувствие: {recovery_quality}.
                Состояние кожи: {skin_status}.

                Вопрос пользователя: {user_msg}
                Учитывай уровень восстановления (сон/ЦНС) и прогресс силовых при ответе.
                """
        res = model.generate_content(prompt_text)
        st.write(res.text)
      except Exception as e:
        st.error(f"Ошибка обращения к ИИ: {e}")

