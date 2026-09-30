import datetime
import google.generativeai as genai
import pandas as pd
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Plateau Breaker", page_icon="🏋️‍♂️", layout="wide"
)

st.title("🏋️‍♂️ Проект: Plateau Breaker (от HTN к Chadlite)")
st.caption("Персональный трекер массы, силовых, питания и ухода за кожей")

if "food_log" not in st.session_state:
  st.session_state.food_log = []

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

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Калькулятор",
    "📸 Сканер Еды (ИИ)",
    "📅 Дневник и Таблица",
    "🤖 ИИ-Консультант",
])

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
            model = genai.GenerativeModel("gemini-1.5-flash")

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

with tab3:
  st.subheader("Ввод данных за день")
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

  skin_status = st.select_slider(
      "Состояние кожи",
      options=[
          "Отлично",
          "Нормально",
          "Есть воспаления",
          "Сильное обострение (после зала)",
      ],
  )
  notes = st.text_input("Заметки (уход, салицилка, самочувствие)")

  if st.button("Сохранить запись за день"):
    st.success("Данные зафиксированы!")

with tab4:
  st.subheader("Консультант Plateau Breaker")
  user_msg = st.text_area("Задай вопрос по тренировкам, коже или питанию:")
  if st.button("Отправить"):
    if not api_key:
      st.warning("Введи Gemini API Key в левой панели!")
    else:
      genai.configure(api_key=api_key)
      model = genai.GenerativeModel("gemini-1.5-flash")
      res = model.generate_content(
          f"Ты тренер проекта Plateau Breaker. Ответь пользователю (Рост 182,"
          f" вес 73 кг, цель 77 кг, жим 105 кг). Вопрос: {user_msg}"
      )
      st.write(res.text)
