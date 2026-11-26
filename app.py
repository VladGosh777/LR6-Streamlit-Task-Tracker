import streamlit as st

import db


st.set_page_config(
    page_title="Трекер навчальних завдань",
    page_icon="📚",
    layout="wide",
)

db.init_db()

st.sidebar.title("Навчальний план")
st.sidebar.caption("П-31 Павлюк Владислав")

pages = [
    st.Page("pages/1_overview.py", title="Перегляд завдань", default=True),
    st.Page("pages/2_add_task.py", title="Додати запис"),
    st.Page("pages/3_about.py", title="Про автора"),
]

page = st.navigation(pages)
page.run()
