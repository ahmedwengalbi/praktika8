# quest_master/core/database.py
import sqlite3
from typing import Dict


def create_connection() -> sqlite3.Connection:
    conn = sqlite3.connect("quests.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            difficulty TEXT CHECK(difficulty IN ('Легкий','Средний','Сложный','Эпический')),
            reward INTEGER,
            description TEXT,
            deadline TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quest_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quest_id INTEGER,
            title TEXT,
            difficulty TEXT,
            reward INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quest_id) REFERENCES quests(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quest_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quest_id INTEGER,
            x REAL,
            y REAL,
            type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quest_id) REFERENCES quests(id)
        )
        """
    )
    conn.commit()
    return conn


def save_quest(quest_id: int, data: Dict[str, str | int]):
    conn = create_connection()
    cursor = conn.cursor()
    if quest_id is None:
        cursor.execute(
            "INSERT INTO quests (title, difficulty, reward, description, deadline) VALUES (?, ?, ?, ?, ?)",
            (data["title"], data["difficulty"], data["reward"], data["description"], data["deadline"]),
        )
        quest_id = cursor.lastrowid
    else:
        cursor.execute(
            "UPDATE quests SET title=?, difficulty=?, reward=?, description=?, deadline=? WHERE id=?",
            (data["title"], data["difficulty"], data["reward"], data["description"], data["deadline"], quest_id),
        )

    cursor.execute(
        "INSERT INTO quest_versions (quest_id, title, difficulty, reward, description) VALUES (?, ?, ?, ?, ?)",
        (quest_id, data["title"], data["difficulty"], data["reward"], data["description"]),
    )
    conn.commit()
    conn.close()
    return quest_id