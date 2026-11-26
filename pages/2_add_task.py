from datetime import date

import streamlit as st

import db


st.title("Додати навчальне завдання")
st.caption("Заповни основні дані, щоб додати роботу до списку")

subjects = db.get_subjects()
if subjects:
    subject_names = [subject["name"] for subject in subjects]
    subject_by_name = {subject["name"]: subject["id"] for subject in subjects}
    with st.form("add_task_form", clear_on_submit=False):
        title = st.text_input("Назва завдання")
        first_col, second_col = st.columns(2)
        with first_col:
            subject_name = st.selectbox("Предмет", subject_names)
            priority = st.selectbox("Пріоритет", db.PRIORITIES, index=1)
        with second_col:
            deadline = st.date_input("Дедлайн", value=date.today())
            status = st.selectbox("Статус", db.STATUSES, index=0)
        note = st.text_area("Примітка", placeholder="Що потрібно врахувати")
        submitted = st.form_submit_button("Додати завдання", type="primary")
    if submitted:
        if not title.strip():
            st.error("Введи назву завдання.")
        else:
            db.add_task(
                title,
                subject_by_name[subject_name],
                deadline,
                priority,
                status,
                note,
            )
            st.success("Завдання додано до списку.")

st.divider()
st.subheader("Додати предмет")
with st.form("add_subject_form", clear_on_submit=True):
    subject_name = st.text_input("Назва предмета")
    teacher = st.text_input("Викладач")
    planned_count = st.number_input("Робіт за семестр", min_value=1, max_value=30, value=5)
    add_subject = st.form_submit_button("Зберегти предмет")
if add_subject:
    try:
        db.add_subject(subject_name, teacher, planned_count)
        st.success("Предмет додано.")
        st.rerun()
    except ValueError as error:
        st.error(str(error))
    except Exception:
        st.error("Такий предмет уже є у списку.")
