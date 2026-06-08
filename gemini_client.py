import os
import time
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY", "").strip()
primary_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

BACKUP_MODELS = [
    primary_model,
    "gemini-2.5-flash-lite"
]


def fallback_answer():
    return """The AI model is temporarily busy. Please try again in a few moments.

Reason:
Gemini is currently experiencing high demand, so the request could not be completed right now."""


def generate_answer(question, matched_laws=None):
    if not api_key or api_key == "paste_your_gemini_api_key_here":
        return "Gemini is not active. Please check GEMINI_API_KEY in environment variables."

    from google import genai

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a Business Law chatbot for a student project.

You may answer ONLY from these five Acts:
1. Companies Act, 1994
2. Contract Act, 1872
3. Sale of Goods Act, 1930
4. Negotiable Instruments Act, 1881
5. Partnership Act, 1932

Important rules:
1. Do not use any law outside these five Acts.
2. If the question is a case/problem question, identify the legal issue and apply the relevant Act.
3. If the question asks "can", "is", "does", "whether", or clearly needs a yes/no answer, start with "Yes." or "No."
4. After yes/no, give reasoning.
5. Then mention Act/Law.
6. Then mention Section No.
7. Keep the answer short, exam-style, and direct.
8. Do not dump long theory.
9. If the question is outside the five Acts, say: "This question is outside the selected five Acts."
10. If the exact section is uncertain, mention the most relevant Act and say "Exact section not confidently found" instead of inventing.

Use this format for yes/no questions:

Yes/No:
[Yes or No in one sentence]

Reasoning:
[Apply the law to the facts]

Act/Law:
[Relevant Act]

Section No:
[Relevant section]

Use this format for non-yes/no questions:

Answer:
[Direct answer]

Reasoning:
[Short explanation]

Act/Law:
[Relevant Act]

Section No:
[Relevant section]

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
A agrees to sell his only white horse to B for Tk. 50,000. Before delivery, the horse dies naturally without the fault of either party.

Answer:
The contract becomes void.

Reasoning:
The horse is a specific good because it is clearly identified as A's only white horse. Since that specific good perishes before delivery without fault of either party, the contract cannot be performed.

Act/Law:
Sale of Goods Act, 1930

Section No:
Section 7

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
                last_error = str(error)

                if "503" in last_error or "UNAVAILABLE" in last_error or "high demand" in last_error.lower():
                    time.sleep(2)
                    continue

                return f"Gemini API error: {error}"

    return f"""{fallback_answer()}

Technical note:
Last Gemini error: {last_error}
"""
