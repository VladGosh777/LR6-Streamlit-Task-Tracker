from datetime import date

import pandas as pd
import streamlit as st

import db


st.title("Трекер навчальних завдань студента")

subjects = db.get_subjects()
subject_by_name = {subject["name"]: subject["id"] for subject in subjects}
filter_col, search_col = st.columns([1, 2])
with filter_col:
    selected_subject = st.selectbox("Предмет", ["Усі предмети", *subject_by_name])
with search_col:
    search_text = st.text_input("Пошук", placeholder="Назва завдання або примітка")

subject_id = subject_by_name.get(selected_subject)
tasks = db.get_tasks(subject_id=subject_id, search_text=search_text)
done_count = sum(task["status"] == "Виконано" for task in tasks)
active_count = sum(task["status"] == "У роботі" for task in tasks)
planned_count = sum(task["status"] == "Заплановано" for task in tasks)

metric_cols = st.columns(3)
metric_cols[0].metric("Усього завдань", len(tasks))
metric_cols[1].metric("Виконано", done_count)
metric_cols[2].metric("У роботі", active_count)

if tasks:
    table = pd.DataFrame(
        [
            {
                "Завдання": task["title"],
                "Предмет": task["subject_name"],
                "Дедлайн": task["due_date"],
                "Пріоритет": task["priority"],
                "Статус": task["status"],
            }
            for task in tasks
        ]
    )
    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Завдання": st.column_config.TextColumn(width=280),
            "Предмет": st.column_config.TextColumn(width=240),
            "Дедлайн": st.column_config.TextColumn(width=115),
            "Пріоритет": st.column_config.TextColumn(width=110),
            "Статус": st.column_config.TextColumn(width=115),
        },
    )
else:
    st.info("За цими умовами завдань не знайдено.")

st.subheader("Статистика за предметами")
summary = db.get_subject_summary()
chart_data = pd.DataFrame(
    {
        "Усього": [row["task_count"] for row in summary],
        "Виконано": [row["completed_count"] for row in summary],
    },
    index=[
        {
            "Алгоритми та структури даних": "Алгоритми",
            "Інформаційні технології": "ІТ",
            "Комп’ютерні мережі": "Мережі",
            "Основи програмування": "Програмування",
            "Вебтехнології": "Веб",
        }[row["subject_name"]]
        for row in summary
    ],
)
st.bar_chart(chart_data, color=["#4f86c6", "#47a17b"])
summary_table = pd.DataFrame(
    [
        {
            "Предмет": row["subject_name"],
            "Робіт за планом": row["planned_count"],
            "У трекері": row["task_count"],
            "Виконано": row["completed_count"],
        }
        for row in summary
    ]
)
st.dataframe(summary_table, hide_index=True, use_container_width=True)

st.subheader("Оновлення запису")
all_tasks = db.get_tasks()
if all_tasks:
    task_options = {
        f"{task['title']} · {task['subject_name']} · до {task['due_date']}": task
        for task in all_tasks
    }
    selected_label = st.selectbox("Вибери завдання", list(task_options))
    selected_task = task_options[selected_label]
    action_col, button_col = st.columns([2, 1])
    with action_col:
        new_status = st.selectbox(
            "Новий статус",
            db.STATUSES,
            index=db.STATUSES.index(selected_task["status"]),
        )
    with button_col:
        st.write("")
        st.write("")
        if st.button("Зберегти статус", use_container_width=True):
            db.update_task_status(selected_task["id"], new_status)
            st.success("Статус оновлено.")
            st.rerun()
    if st.button("Видалити вибране завдання"):
        db.delete_task(selected_task["id"])
        st.success("Завдання видалено.")
        st.rerun()

overdue_count = sum(
    task["status"] != "Виконано" and task["due_date"] < date.today().isoformat()
    for task in tasks
)
if overdue_count:
    st.warning(f"Прострочених завдань у поточному перегляді: {overdue_count}.")
