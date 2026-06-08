import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def fallback_answer(question, matched_laws):
    answer = "Based on the provided Acts, I found these relevant section(s):\n\n"

    for law in matched_laws:
        answer += f"{law['act_name']} - {law['section_no']}\n"
        if law["section_title"]:
            answer += f"Title: {law['section_title']}\n"
        answer += f"Rule: {law['content']}\n\n"

    answer += "Simple explanation: The answer should be understood only from the above provided law section(s)."
    return answer


def generate_answer(question, matched_laws):
    if not api_key or api_key == "paste_your_gemini_api_key_here":
        return fallback_answer(question, matched_laws)

    from google import genai

    client = genai.Client(api_key=api_key)

    law_context = ""

    for law in matched_laws:
        law_context += f"""
Act Name: {law['act_name']}
Section No: {law['section_no']}
Section Title: {law['section_title']}
Section Content:
{law['content']}
---
"""

    prompt = f"""
You are a Business Law chatbot for a student project.

You must answer only from the provided law sections.

Allowed Acts:
1. Companies Act, 1994
2. Contract Act, 1872
3. Sale of Goods Act, 1930
4. Negotiable Instruments Act, 1881
5. Partnership Act, 1932

Strict Rules:
1. Do not use outside knowledge.
2. If the answer is not found in the provided sections, say:
   "I could not find this information in the provided Acts."
3. Always mention the Act name and section number.
4. Explain in simple language.
5. Do not claim to be a real lawyer.
6. Do not give personal legal advice.
7. If multiple Acts are relevant, separate the answer Act-wise.

Provided Law Sections:
{law_context}

User Question:
{question}

Answer:
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        if not response.text:
            return fallback_answer(question, matched_laws)

        return response.text.strip()

    except Exception as error:
        return f"Gemini API error: {error}\n\nFallback answer:\n\n{fallback_answer(question, matched_laws)}"
