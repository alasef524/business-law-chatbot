import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def fallback_answer(question, matched_laws):
    answer = "Relevant answer based on the provided description:\n\n"

    for law in matched_laws:
        answer += f"Act: {law['act_name']}\n"
        answer += f"Section: {law['section_no']}\n"
        if law["section_title"]:
            answer += f"Topic: {law['section_title']}\n"
        answer += f"Description: {law['content']}\n\n"

    answer += "Note: This answer is based only on the saved description. Add a valid Gemini API key for a more natural explanation."
    return answer


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

You must answer the user's question only from the provided description/context.

Allowed Acts:
1. Companies Act, 1994
2. Contract Act, 1872
3. Sale of Goods Act, 1930
4. Negotiable Instruments Act, 1881
5. Partnership Act, 1932

Strict rules:
1. Do not use outside knowledge.
2. Do not invent sections.
3. If the answer is not available in the provided description, say:
   "I could not find this information in the provided Acts."
4. Every answer must mention:
   - Act name
   - Relevant section number
   - Topic/title
5. Explain in simple student-friendly language.
6. Do not give professional legal advice.
7. If more than one section is relevant, explain them separately.
8. Keep the answer clear and organized.

Answer format:

Act:
Section:
Topic:

Answer:
[main answer]

Simple Explanation:
[easy explanation]

Based on:
[mention the exact provided description/topic used]

Provided Description/Context:
{law_context}

User Question:
{question}

Final Answer:
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
