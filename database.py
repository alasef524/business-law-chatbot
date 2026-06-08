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

    cursor.execute("DELETE FROM laws")

    sample_laws = [
        (
            "Companies Act, 1994",
            "Basic Concept",
            "Company",
            "The Companies Act, 1994 deals with company formation, registration, memorandum of association, articles of association, directors, meetings, shares, company management, and winding up. A company is an incorporated association formed and registered under company law. It may be private or public depending on its structure and restrictions."
        ),

        (
            "Contract Act, 1872",
            "Section 2(h) and Section 10",
            "Essentials of a valid contract",
            "The law of contract determines the circumstances in which promises made by parties become legally binding. Its purpose is to ensure the realization of reasonable expectations of the parties who enter into a contract. According to Sir William Anson, an agreement becomes a contract when it gives rise to a legal obligation or duty. A valid contract requires offer and acceptance, intention to create legal relationship, lawful consideration, capacity or competency of parties, free and genuine consent, lawful object, agreement not declared void, certainty and possibility of performance, and necessary legal formalities."
        ),
        (
            "Contract Act, 1872",
            "General Principle",
            "Social agreement and legal agreement",
            "An agreement may be a social agreement or a legal agreement. A social agreement does not give rise to contractual obligations and is not enforceable in a Court of law. Only agreements enforceable by law are contracts. For example, if A invites B to dinner and B accepts, it is a social agreement. If a father promises to pay his son pocket allowance and later refuses, the son cannot recover it because it is a domestic agreement and there is no intention to create legal relations."
        ),

        (
            "Sale of Goods Act, 1930",
            "Goods",
            "Meaning and classification of goods",
            "Goods include every kind of movable property except actionable claims and money. Goods can be classified as existing goods, future goods, and contingent goods. Existing goods are already in existence and physically present in some person's possession and ownership. Existing goods may be specific and ascertained, meaning separately identified, or generic and unascertained, meaning indicated by description and not separately identified."
        ),
        (
            "Sale of Goods Act, 1930",
            "Future and Contingent Goods",
            "Future goods and contingent goods",
            "Future goods are goods which will be manufactured, produced, or acquired by the seller after the making of the contract of sale. Example: P agrees to sell Q all mangoes produced in his garden next year. Contingent goods are goods whose acquisition by the seller depends on a contingency which may or may not happen. Example: X agrees to sell Y a ring provided he is able to purchase it from its present owner."
        ),
        (
            "Sale of Goods Act, 1930",
            "Section 4",
            "Sale and agreement to sell",
            "A contract for the sale of goods may be either a sale or an agreement to sell. When ownership in the goods is transferred from the seller to the buyer, the contract is called a sale. When ownership is to transfer at a future time or subject to a condition to be fulfilled later, the contract is called an agreement to sell."
        ),
        (
            "Sale of Goods Act, 1930",
            "Sections 5, 7, 9 and 26",
            "Essentials of contract for sale of goods",
            "A contract for sale of goods requires exchange of movable goods for money. The buyer and seller must be different persons, though a part-owner may sell to another part-owner. Under Section 5(1), a contract of sale is made by offer and acceptance. Under Section 5(2), it may be written, oral, or implied from conduct. Price means money consideration; if no price is fixed, the buyer must pay a reasonable price under Section 9. Under Section 7, a contract for sale of specific goods becomes void if the goods have already perished or become so damaged that they no longer answer the description. Under Section 26, risk usually follows ownership."
        ),

        (
            "Negotiable Instruments Act, 1881",
            "Section 13(1)",
            "Meaning of negotiable instrument",
            "Documents used in commercial transactions and monetary dealings are called negotiable instruments. Negotiable means transferable by delivery, and instrument means a written document by which a right is created in favour of a person. Section 13(1) states that a negotiable instrument means a promissory note, bill of exchange, or cheque payable either to order or to bearer."
        ),
        (
            "Negotiable Instruments Act, 1881",
            "Section 4",
            "Promissory note",
            "A promissory note is an instrument in writing, not being a bank note or currency note, containing an unconditional undertaking signed by the maker to pay a certain sum of money only to, or to the order of, a certain person, or to the bearer of the instrument. The maker is the debtor who signs the instrument, and the payee is the person who receives the money."
        ),
        (
            "Negotiable Instruments Act, 1881",
            "Section 4",
            "Essential elements of promissory note",
            "A promissory note must be in writing, must contain an express promise to pay, the promise must be unconditional, the maker must be certain and definite, it must be signed by the maker, the sum payable must be certain, the money must be payable to a definite person or according to that person's order, and payment must be in legal tender money."
        ),
        (
            "Negotiable Instruments Act, 1881",
            "Section 5",
            "Bill of exchange",
            "A bill of exchange is an instrument in writing containing an unconditional order, signed by the maker, directing a certain person to pay a certain sum of money only to, or to the order of, a certain person or to the bearer of the instrument. The maker is called the drawer, the person directed to pay is the drawee, and the person receiving money is the payee. After acceptance, the drawee becomes the acceptor."
        ),
        (
            "Negotiable Instruments Act, 1881",
            "Section 6",
            "Cheque",
            "A cheque is a bill of exchange drawn upon a specified banker and payable on demand. It may be payable to bearer or to order, but it must be payable on demand. The banker must pay it when presented during usual office hours if the cheque is validly drawn and the drawer has sufficient funds. A cheque must be dated. A future-dated cheque is called a post-dated cheque. A stale cheque is usually considered too old after six months in India and Bangladesh."
        ),

        (
            "Partnership Act, 1932",
            "Section 4",
            "Definition and essential elements of partnership",
            "Section 4 defines partnership as the relation between persons who have agreed to share the profits of a business carried on by all or any of them acting for all. The essential elements are: agreement between two or more persons, agreement to share profits of a business, and business carried on by all or any partner acting for all."
        ),
        (
            "Partnership Act, 1932",
            "Section 5",
            "Partnership arises from contract, not status",
            "Partnership can arise only from an agreement, express or implied, between two or more persons. Where there is no agreement, there is no partnership. Section 5 states that the relation of partnership arises from contract and not from status."
        ),
        (
            "Partnership Act, 1932",
            "Section 6",
            "Tests of true partnership",
            "Section 6 states that to determine whether a group of persons is a firm or whether a person is a partner, regard must be given to the real relation between the parties as shown by all relevant facts taken together. Sharing of profits is important but not conclusive. A creditor, employee, worker, widow, or children of a deceased partner may receive a share of profits without becoming partners."
        ),
        (
            "Partnership Act, 1932",
            "Companies Act Section 11 reference",
            "Partnership forbidden by law",
            "Section 11 of the Companies Act, 1994 prohibits formation of a partnership for banking business with more than ten persons and for any other purpose with more than twenty persons. If business is to be carried on with more persons, a company must be formed. An agreement to form a partnership for carrying on a trade prohibited by law is void."
        ),
        (
            "Partnership Act, 1932",
            "Registration of Firms",
            "Registration of partnership firm",
            "Registration of a partnership is not compulsory, but an unregistered firm suffers from certain disabilities. Registration may be done by sending or delivering a prescribed statement with fee to the Registrar of Firms. The statement includes firm name, principal place of business, other places of business, date when each partner joined, full names and permanent addresses of partners, and duration of the firm."
        ),
        (
            "Partnership Act, 1932",
            "Section 69",
            "Consequences of non-registration",
            "Under Section 69, a partner of an unregistered firm cannot file a suit against the firm or any partner to enforce a right arising from contract or the Partnership Act. No suit can be filed on behalf of an unregistered firm against a third party to enforce contractual rights. An unregistered firm also cannot claim set-off in a suit. Exceptions include suits for dissolution and accounts, realization of properties of a dissolved firm, actions by Official Assignee or Receiver, areas where registration provisions do not apply, and certain small claims."
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
        ORDER BY act_name ASC, id ASC
    """)

    laws = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return laws


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def detect_act(question):
    q = question.lower()

    if "partnership" in q or "partner" in q or "firm" in q:
        return "Partnership Act, 1932"

    if "contract" in q or "agreement" in q or "valid contract" in q or "free consent" in q or "consideration" in q:
        return "Contract Act, 1872"

    if "sale of goods" in q or "sales of goods" in q or "goods" in q or "seller" in q or "buyer" in q or "warranty" in q or "condition" in q:
        return "Sale of Goods Act, 1930"

    if "negotiable" in q or "cheque" in q or "check" in q or "promissory" in q or "bill of exchange" in q or "drawer" in q or "drawee" in q:
        return "Negotiable Instruments Act, 1881"

    if "company" in q or "companies" in q or "director" in q or "share" in q or "memorandum" in q or "articles" in q:
        return "Companies Act, 1994"

    return None


def search_laws(question, limit=3):
    laws = get_all_laws()
    detected_act = detect_act(question)

    if detected_act:
        laws = [law for law in laws if law["act_name"] == detected_act]

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

    if scored_laws:
        return [law for score, law in scored_laws[:limit]]

    if detected_act:
        return laws[:limit]

    return []


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
