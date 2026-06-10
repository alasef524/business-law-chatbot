@'
import os
import time
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY", "").strip()
primary_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip()

BACKUP_MODELS = []

if primary_model:
    BACKUP_MODELS.append(primary_model)

if "gemini-2.5-flash-lite" not in BACKUP_MODELS:
    BACKUP_MODELS.append("gemini-2.5-flash-lite")

if "gemini-2.5-flash" not in BACKUP_MODELS:
    BACKUP_MODELS.append("gemini-2.5-flash")


def clean_api_error(error_text: str) -> str:
    if (
        "429" in error_text
        or "RESOURCE_EXHAUSTED" in error_text
        or "Quota exceeded" in error_text
        or "quota" in error_text.lower()
    ):
        return """AI quota is temporarily finished.

Reason:
The Gemini API free usage limit has been reached. Please try again later."""

    if (
        "503" in error_text
        or "UNAVAILABLE" in error_text
        or "high demand" in error_text.lower()
    ):
        return """Gemini is temporarily busy.

Reason:
The model is currently experiencing high demand. Please try again after a short time."""

    if "API key" in error_text or "INVALID_ARGUMENT" in error_text:
        return """Gemini API key problem.

Reason:
The API key may be missing, invalid, or incorrectly added in the environment variables."""

    return """Something went wrong while generating the answer.

Please try again."""


def generate_answer(question, matched_laws=None):
    if not api_key or api_key == "paste_your_gemini_api_key_here":
        return """Gemini is not active.

Reason:
GEMINI_API_KEY is missing or invalid in environment variables."""

    from google import genai

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a helpful AI chatbot for a student project.

The chatbot has two answer modes:

MODE 1: Business Law Mode
Use this mode when the question is related to any of these five Acts:
1. Companies Act, 1994
2. Contract Act, 1872
3. Sale of Goods Act, 1930
4. Negotiable Instruments Act, 1881
5. Partnership Act, 1932

For questions related to these five Acts:
- Identify the legal issue.
- Apply the relevant Act.
- Mention Act/Law.
- Mention Section No.
- If the question needs a yes/no answer, start with "Yes." or "No."
- Keep the answer exam-style, short, and direct.

Business Law yes/no answer format:

Yes/No:
[Yes or No in one sentence]

Reasoning:
[Apply the law to the facts]

Act/Law:
[Relevant Act]

Section No:
[Relevant section]

Business Law non-yes/no answer format:

Answer:
[Direct answer]

Reasoning:
[Short explanation]

Act/Law:
[Relevant Act]

Section No:
[Relevant section]

MODE 2: General Answer Mode
Use this mode when the question is outside the five Acts.

For outside questions:
- Answer normally and helpfully.
- Do not force Act/Law.
- Do not invent section numbers.
- Keep it clear and concise.
- Add this note at the end:
  "Note: This question is outside the selected five Acts used in the Business Law project."

General answer format:

Answer:
[General answer]

Note:
This question is outside the selected five Acts used in the Business Law project.

Important rules:
1. Do not invent fake sections.
2. Do not mention Gemini, API, model, prompt, or technical details.
3. If the question is related to the five Acts but exact section is uncertain, say "Exact section not confidently found."
4. For legal case questions, answer like a business law student: issue, reasoning, Act/Law, section.
5. Do not give long unnecessary theory unless the user asks for details.

Examples:

Question:
A buyer purchases a used mobile phone without checking its condition. Later, he discovers minor scratches. Can the buyer claim compensation?

Answer:
No.

Reasoning:
The buyer purchased a used phone without checking its condition. Minor scratches are defects that could normally be discovered by ordinary inspection. Under the principle of caveat emptor, the buyer is expected to examine the goods before buying. Therefore, he generally cannot claim compensation.

Act/Law:
Sale of Goods Act, 1930

Section No:
Section 16

Question:
Rahim writes and signs a document stating, "I promise to pay Karim Tk. 50,000 on 1 July 2026." Is this a promissory note?

Answer:
Yes.

Reasoning:
The document is in writing, signed by Rahim, contains an unconditional promise to pay a certain sum of money, and names Karim as the payee. Therefore, it satisfies the essentials of a promissory note.

Act/Law:
Negotiable Instruments Act, 1881

Section No:
Section 4

Question:
What is photosynthesis?

Answer:
Photosynthesis is the process by which green plants use sunlight, carbon dioxide, and water to produce food in the form of glucose. Oxygen is released as a by-product.

Note:
This question is outside the selected five Acts used in the Business Law project.

Now answer this user question:

{question}
"""

    last_error = None

    for model in BACKUP_MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response.text:
                    return response.text.strip()

            except Exception as error:
                error_text = str(error)
                last_error = error_text

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "high demand" in error_text.lower()
                ):
                    time.sleep(2)
                    continue

                return clean_api_error(error_text)

    if last_error:
        return clean_api_error(last_error)

    return """Something went wrong while generating the answer.

Please try again."""
'@ | Set-Content gemini_client.py