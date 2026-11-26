PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    teacher TEXT NOT NULL,
    planned_count INTEGER NOT NULL CHECK (planned_count > 0)
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject_id INTEGER NOT NULL,
    due_date TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('Низький', 'Середній', 'Високий')),
    status TEXT NOT NULL CHECK (status IN ('Заплановано', 'У роботі', 'Виконано')),
    note TEXT DEFAULT '',
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_tasks_subject ON tasks(subject_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
