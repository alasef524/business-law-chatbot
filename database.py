import sqlite3
import re
from datetime import datetime

DB_NAME = "business_law_chatbot.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS laws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act_name TEXT NOT NULL,
            section_no TEXT NOT NULL,
            section_title TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            matched_law_id INTEGER,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def seed_sample_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM laws")
    total = cursor.fetchone()["total"]

    if total > 0:
        conn.close()
        return

    sample_laws = [
        (
            "Contract Act, 1872",
            "Section 10",
            "What agreements are contracts",
            "An agreement becomes a contract when it is made by free consent of parties competent to contract, for lawful consideration and lawful object, and is not expressly declared void."
        ),
        (
            "Contract Act, 1872",
            "Section 11",
            "Who are competent to contract",
            "A person is competent to contract if the person is of the age of majority, is of sound mind, and is not disqualified from contracting by law."
        ),
        (
            "Sale of Goods Act, 1930",
            "Section 4",
            "Sale and agreement to sell",
            "A contract of sale of goods is a contract where the seller transfers or agrees to transfer property in goods to the buyer for a price."
        ),
        (
            "Negotiable Instruments Act, 1881",
            "Section 6",
            "Cheque",
            "A cheque is a bill of exchange drawn on a specified banker and payable on demand."
        ),
        (
            "Partnership Act, 1932",
            "Section 4",
            "Definition of partnership",
            "Partnership is the relation between persons who have agreed to share profits of a business carried on by all or any of them acting for all."
        ),
        (
            "Companies Act, 1994",
            "Basic Concept",
            "Company",
            "A company is an incorporated association formed and registered under company law. It may be private or public depending on its structure and restrictions."
        )
    ]

    for law in sample_laws:
        cursor.execute("""
            INSERT INTO laws (act_name, section_no, section_title, content, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            law[0],
            law[1],
            law[2],
            law[3],
            datetime.now().isoformat()
        ))

    conn.commit()
    conn.close()


def add_law(act_name, section_no, section_title, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO laws (act_name, section_no, section_title, content, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        act_name,
        section_no,
        section_title,
        content,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_all_laws():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, act_name, section_no, section_title, content
        FROM laws
        ORDER BY id DESC
    """)

    laws = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return laws


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def search_laws(question, limit=5):
    laws = get_all_laws()
    question_words = tokenize(question)

    stop_words = {
        "what", "is", "are", "the", "a", "an", "of", "to", "in", "for",
        "and", "or", "can", "i", "my", "me", "does", "do", "by", "on",
        "with", "from", "under", "according", "explain", "tell", "about"
    }

    important_words = [
        word for word in question_words
        if word not in stop_words and len(word) > 2
    ]

    scored_laws = []

    for law in laws:
        searchable_text = f"""
        {law['act_name']}
        {law['section_no']}
        {law['section_title']}
        {law['content']}
        """.lower()

        score = 0

        for word in important_words:
            if word in searchable_text:
                score += 1

        if score > 0:
            scored_laws.append((score, law))

    scored_laws.sort(key=lambda item: item[0], reverse=True)

    return [law for score, law in scored_laws[:limit]]


def save_chat(question, answer, matched_law_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_history (question, answer, matched_law_id, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        question,
        answer,
        matched_law_id,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
