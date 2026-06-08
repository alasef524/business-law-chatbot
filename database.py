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

    # Clear old weak sample data and insert clean act-wise data
    cursor.execute("DELETE FROM laws")

    sample_laws = [
        (
            "Contract Act, 1872",
            "Section 2(h) and Section 10",
            "Essentials of a valid contract",
            "The law of contract determines the circumstances in which promises made by parties become legally binding. An agreement becomes a contract when it creates a legal obligation. A valid contract requires offer and acceptance, intention to create legal relationship, lawful consideration, competent parties, free and genuine consent, lawful object, agreement not declared void, certainty and possibility of performance, and necessary legal formalities."
        ),
        (
            "Sale of Goods Act, 1930",
            "Sections 4, 5, 7, 9 and 26",
            "Goods, sale, agreement to sell, and essentials of sale",
            "Goods include every kind of movable property except actionable claims and money. Goods may be existing goods, future goods, or contingent goods. Under Section 4, a contract for sale of goods may be a sale or an agreement to sell. In a sale, ownership transfers from seller to buyer. In an agreement to sell, ownership transfers later or after fulfillment of a condition. A contract of sale requires movable goods, price, different buyer and seller, offer and acceptance, and must satisfy the essentials of a valid contract."
        ),
        (
            "Negotiable Instruments Act, 1881",
            "Sections 4, 5, 6 and 13",
            "Negotiable instruments, promissory note, bill of exchange, and cheque",
            "A negotiable instrument is a written document transferable by delivery or order by which a right is created in favour of a person. Under Section 13, negotiable instruments include promissory notes, bills of exchange, and cheques. A promissory note under Section 4 contains an unconditional promise to pay. A bill of exchange under Section 5 contains an unconditional order to pay. A cheque under Section 6 is a bill of exchange drawn on a specified banker and payable on demand."
        ),
        (
            "Partnership Act, 1932",
            "Sections 4, 5, 6 and 69",
            "Partnership, true partnership, registration, and non-registration",
            "Section 4 defines partnership as the relation between persons who have agreed to share the profits of a business carried on by all or any of them acting for all. The essential elements are agreement between two or more persons, sharing of profits of a business, and business carried on by all or any partner acting for all. Section 5 states that partnership arises from contract and not from status. Section 6 says the real relation between the parties must be considered. Registration is not compulsory, but under Section 69 an unregistered firm faces disabilities in filing suits to enforce contractual rights."
        ),
        (
            "Companies Act, 1994",
            "Basic Concept",
            "Company",
            "The Companies Act, 1994 deals with company formation, registration, memorandum of association, articles of association, directors, meetings, shares, company management, and winding up. A company is an incorporated association formed and registered under company law. It may be private or public depending on its structure and restrictions."
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


def search_laws(question, limit=1):
    laws = get_all_laws()
    q = question.lower()

    # Strong direct Act detection
    if "partnership" in q:
        return [law for law in laws if "partnership" in law["act_name"].lower()][:1]

    if "contract" in q:
        return [law for law in laws if "contract" in law["act_name"].lower()][:1]

    if "sale of goods" in q or "sales of goods" in q or "goods" in q or "seller" in q or "buyer" in q:
        return [law for law in laws if "sale of goods" in law["act_name"].lower()][:1]

    if "negotiable" in q or "cheque" in q or "check" in q or "promissory" in q or "bill of exchange" in q:
        return [law for law in laws if "negotiable" in law["act_name"].lower()][:1]

    if "company" in q or "companies" in q or "director" in q or "share" in q or "memorandum" in q or "articles" in q:
        return [law for law in laws if "companies" in law["act_name"].lower()][:1]

    question_words = tokenize(question)

    stop_words = {
        "what", "is", "are", "the", "a", "an", "of", "to", "in", "for",
        "and", "or", "can", "i", "my", "me", "does", "do", "by", "on",
        "with", "from", "under", "according", "explain", "tell", "about",
        "act", "law", "section", "meaning", "define", "definition"
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
