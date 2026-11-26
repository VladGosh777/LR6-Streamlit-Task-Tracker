from datetime import date, timedelta
from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tasks.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
STATUSES = ("Заплановано", "У роботі", "Виконано")
PRIORITIES = ("Низький", "Середній", "Високий")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        if connection.execute("SELECT COUNT(*) FROM subjects").fetchone()[0] == 0:
            subjects = [
                ("Алгоритми та структури даних", "Олена Коваль", 6),
                ("Основи програмування", "Ігор Мельник", 8),
                ("Інформаційні технології", "Наталія Бойко", 5),
                ("Комп’ютерні мережі", "Роман Савчук", 5),
                ("Вебтехнології", "Марія Левченко", 6),
            ]
            connection.executemany(
                "INSERT INTO subjects (name, teacher, planned_count) VALUES (?, ?, ?)",
                subjects,
            )
            subject_ids = {
                row["name"]: row["id"]
                for row in connection.execute("SELECT id, name FROM subjects")
            }
            today = date.today()
            tasks = [
                ("Лабораторна № 5: обробка списку", "Основи програмування", -8, "Середній", "Виконано", "Додати перевірку вхідних даних"),
                ("Функції та модулі Python", "Основи програмування", -3, "Низький", "Виконано", "Практичні приклади готові"),
                ("Пошук у бінарному дереві", "Алгоритми та структури даних", 2, "Високий", "У роботі", "Звірити складність алгоритму"),
                ("Лабораторна № 6: трекер завдань", "Інформаційні технології", 1, "Високий", "У роботі", "Підготувати звіт і скриншоти"),
                ("Сортування злиттям", "Алгоритми та структури даних", 5, "Середній", "Заплановано", "Перевірити роботу на різних масивах"),
                ("Налаштування локальної мережі", "Комп’ютерні мережі", 7, "Середній", "Заплановано", "Намалювати схему мережі"),
                ("Модель OSI та протоколи", "Комп’ютерні мережі", -1, "Низький", "Виконано", "Повторити призначення рівнів"),
                ("HTML-форма для реєстрації", "Вебтехнології", 3, "Високий", "У роботі", "Перевірити поля форми"),
                ("CSS-макет сторінки портфоліо", "Вебтехнології", 9, "Середній", "Заплановано", "Додати адаптивне відображення"),
                ("Практична № 4: хмарні сервіси", "Інформаційні технології", 12, "Низький", "Заплановано", "Підготувати короткий огляд"),
            ]
            records = [
                (title, subject_ids[subject], (today + timedelta(days=offset)).isoformat(), priority, status, note)
                for title, subject, offset, priority, status, note in tasks
            ]
            connection.executemany(
                "INSERT INTO tasks (title, subject_id, due_date, priority, status, note) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                records,
            )


def get_subjects():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, teacher, planned_count FROM subjects ORDER BY name"
        ).fetchall()
        return [dict(row) for row in rows]


def get_tasks(subject_id=None, search_text=""):
    query = (
        "SELECT t.id, t.title, t.subject_id, s.name AS subject_name, "
        "s.teacher, t.due_date, t.priority, t.status, t.note "
        "FROM tasks AS t JOIN subjects AS s ON s.id = t.subject_id WHERE 1 = 1"
    )
    parameters = []
    if subject_id is not None:
        query += " AND t.subject_id = ?"
        parameters.append(int(subject_id))
    if search_text.strip():
        query += " AND (LOWER(t.title) LIKE LOWER(?) OR LOWER(t.note) LIKE LOWER(?))"
        pattern = f"%{search_text.strip()}%"
        parameters.extend((pattern, pattern))
    query += " ORDER BY CASE t.status WHEN 'У роботі' THEN 0 WHEN 'Заплановано' THEN 1 ELSE 2 END, t.due_date, t.id"
    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]


def get_subject_summary():
    query = (
        "SELECT s.name AS subject_name, s.planned_count, COUNT(t.id) AS task_count, "
        "SUM(CASE WHEN t.status = 'Виконано' THEN 1 ELSE 0 END) AS completed_count, "
        "SUM(CASE WHEN t.status = 'У роботі' THEN 1 ELSE 0 END) AS active_count "
        "FROM subjects AS s LEFT JOIN tasks AS t ON t.subject_id = s.id "
        "GROUP BY s.id ORDER BY s.name"
    )
    with get_connection() as connection:
        rows = connection.execute(query).fetchall()
        return [dict(row) for row in rows]


def add_task(title, subject_id, due_date, priority, status, note=""):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, subject_id, due_date, priority, status, note) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (title.strip(), int(subject_id), str(due_date), priority, status, note.strip()),
        )
        return cursor.lastrowid


def update_task_status(task_id, status):
    if status not in STATUSES:
        raise ValueError("Вибери статус зі списку.")
    with get_connection() as connection:
        connection.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, int(task_id)))


def delete_task(task_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM tasks WHERE id = ?", (int(task_id),))


def add_subject(name, teacher, planned_count):
    if not name.strip() or not teacher.strip():
        raise ValueError("Вкажи назву предмета та викладача.")
    if int(planned_count) < 1:
        raise ValueError("Кількість робіт має бути більшою за нуль.")
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO subjects (name, teacher, planned_count) VALUES (?, ?, ?)",
            (name.strip(), teacher.strip(), int(planned_count)),
        )


def delete_subject(subject_id):
    with get_connection() as connection:
        task_count = connection.execute(
            "SELECT COUNT(*) FROM tasks WHERE subject_id = ?", (int(subject_id),)
        ).fetchone()[0]
        if task_count:
            raise ValueError("Не можна видалити предмет, поки до нього прив’язані завдання.")
        connection.execute("DELETE FROM subjects WHERE id = ?", (int(subject_id),))
