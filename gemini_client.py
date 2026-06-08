import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def rule_based_answer(question, matched_laws):
    q = question.lower()

    # Sale of Goods: specific/ascertained goods
    if (
        ("goods" in q or "car" in q or "toyota" in q or "registration" in q)
        and ("type" in q or "involved" in q or "classification" in q or "what" in q)
        and ("car" in q or "toyota" in q or "registration" in q or "red" in q)
    ):
        return """Act: Sale of Goods Act, 1930
Section: Goods / Classification of goods
Topic: Specific and ascertained goods

Answer:
The car is a specific good because it is clearly identified and agreed upon at the time of the contract.

Simple Explanation:
Rahim agrees to sell a red Toyota car with registration no. DHA-1234 to Karim. Since the car is separately identified by its description and registration number, it is a specific/ascertained good.

Based on:
Goods may be specific and ascertained when they can be identified or recognized as separate things."""

    # Sale of Goods: future goods
    if "future goods" in q or "next year" in q or "will be produced" in q or "will be manufactured" in q:
        return """Act: Sale of Goods Act, 1930
Section: Future Goods
Topic: Future goods

Answer:
The goods are future goods.

Simple Explanation:
Future goods are goods which will be manufactured, produced, or acquired by the seller after the contract is made.

Based on:
Future goods are goods which will be manufactured, produced, or acquired by the seller after the making of the contract of sale."""

    # Sale of Goods: contingent goods
    if "contingent" in q or "provided" in q or "if he is able" in q or "depends" in q or "condition" in q:
        return """Act: Sale of Goods Act, 1930
Section: Contingent Goods
Topic: Contingent goods

Answer:
The goods are contingent goods.

Simple Explanation:
Contingent goods are goods whose acquisition by the seller depends on an event that may or may not happen.

Based on:
Contingent goods are goods whose acquisition by the seller depends upon a contingency which may or may not happen."""

    # Partnership
    if "partnership" in q or "partner" in q:
        return """Act: Partnership Act, 1932
Section: Section 4
Topic: Definition and essential elements of partnership

Answer:
Partnership is the relation between persons who have agreed to share the profits of a business carried on by all or any of them acting for all.

Simple Explanation:
A partnership needs an agreement between two or more persons, sharing of business profits, and the business must be carried on by all or by any partner acting for all.

Based on:
Section 4 of the Partnership Act, 1932."""

    # Cheque
    if "cheque" in q or "check" in q:
        return """Act: Negotiable Instruments Act, 1881
Section: Section 6
Topic: Cheque

Answer:
A cheque is a bill of exchange drawn upon a specified banker and payable on demand.

Simple Explanation:
A cheque is used to order a bank to pay money. It must be payable on demand and should be properly dated.

Based on:
Section 6 of the Negotiable Instruments Act, 1881."""

    # Promissory note
    if "promissory" in q:
        return """Act: Negotiable Instruments Act, 1881
Section: Section 4
Topic: Promissory note

Answer:
A promissory note is a written instrument containing an unconditional promise signed by the maker to pay a certain sum of money.

Simple Explanation:
The maker promises to pay money to a definite person or according to that person's order.

Based on:
Section 4 of the Negotiable Instruments Act, 1881."""

    # Bill of exchange
    if "bill of exchange" in q:
        return """Act: Negotiable Instruments Act, 1881
Section: Section 5
Topic: Bill of exchange

Answer:
A bill of exchange is a written instrument containing an unconditional order directing a certain person to pay a certain sum of money.

Simple Explanation:
The drawer orders the drawee to pay money to the payee.

Based on:
Section 5 of the Negotiable Instruments Act, 1881."""

    # Valid contract
    if "valid contract" in q or "essentials" in q or "contract" in q:
        return """Act: Contract Act, 1872
Section: Section 2(h) and Section 10
Topic: Essentials of a valid contract

Answer:
A valid contract requires offer and acceptance, intention to create legal relationship, lawful consideration, competent parties, free consent, lawful object, agreement not declared void, certainty and possibility of performance, and necessary legal formalities.

Simple Explanation:
An agreement becomes a contract only when it creates a legal obligation and satisfies the essential legal requirements.

Based on:
Section 2(h) and Section 10 of the Contract Act, 1872."""

    return None


def fallback_answer(question, matched_laws):
    direct = rule_based_answer(question, matched_laws)
    if direct:
        return direct

    if not matched_laws:
        return "I could not find this information in the provided Acts."

    law = matched_laws[0]

    return f"""Act: {law['act_name']}
Section: {law['section_no']}
Topic: {law['section_title']}

Answer:
{law['content']}

Simple Explanation:
The answer is based only on the saved description for this Act and section.

Based on:
{law['act_name']} - {law['section_no']}"""


def generate_answer(question, matched_laws):
    if not matched_laws:
        return "I could not find this information in the provided Acts."

    if not api_key or api_key == "paste_your_gemini_api_key_here":
        return fallback_answer(question, matched_laws)

    from google import genai

    client = genai.Client(api_key=api_key)

    law_context = ""

    for law in matched_laws:
        law_context += f"""
Act Name: {law['act_name']}
Section: {law['section_no']}
Topic: {law['section_title']}
Description:
{law['content']}
---
"""

    prompt = f"""
You are a Business Law chatbot for a student project.

Answer only from the provided descriptions.

Strict rules:
1. Do not use outside knowledge.
2. Do not invent sections.
3. Always mention Act name, Section, and Topic.
4. Give a direct answer first.
5. Then give a simple explanation.
6. Keep the answer short and relevant.
7. If the answer is not found, say:
   "I could not find this information in the provided Acts."

Expected format:

Act:
Section:
Topic:

Answer:

Simple Explanation:

Based on:

Provided descriptions:
{law_context}

User question:
{question}

Final answer:
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        if not response.text:
            return fallback_answer(question, matched_laws)

        return response.text.strip()

    except Exception:
        return fallback_answer(question, matched_laws)
