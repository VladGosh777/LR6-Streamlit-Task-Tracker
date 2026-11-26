import streamlit as st


st.title("Про автора та проєкт")
st.subheader("Відомості про автора")
st.write("**Студент:** Павлюк Владислав")
st.write("**Група:** П-31")
st.write("**Навчальний заклад:** Гусятинський фаховий коледж ТНТУ ім. І. Пулюя")
st.write("**Дисципліна:** Інформаційні технології")

st.subheader("Призначення застосунку")
st.write(
    "Трекер допомагає записувати лабораторні й практичні роботи, стежити за дедлайнами "
    "та бачити, які завдання ще потребують уваги."
)

st.subheader("Структура бази даних")
left, arrow, right = st.columns([2, 1, 2])
with left:
    st.info("**subjects**\n\nНазва предмета, викладач і запланована кількість робіт")
with arrow:
    st.markdown("<div style='text-align:center;padding-top:26px;font-size:28px'>1 → ∞</div>", unsafe_allow_html=True)
with right:
    st.info("**tasks**\n\nНазва завдання, дедлайн, пріоритет, статус і примітка")

st.caption("Кожне завдання зберігає subject_id, що пов’язує його з відповідним предметом.")
