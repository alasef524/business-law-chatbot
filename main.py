from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database import (
    create_tables,
    seed_sample_data,
    add_law,
    get_all_laws,
    search_laws,
    save_chat
)
from gemini_client import generate_answer


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    seed_sample_data()
    yield


app = FastAPI(
    title="Business Law Chatbot",
    lifespan=lifespan
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


ALLOWED_ACTS = [
    "Companies Act, 1994",
    "Contract Act, 1872",
    "Sale of Goods Act, 1930",
    "Negotiable Instruments Act, 1881",
    "Partnership Act, 1932"
]


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    laws = get_all_laws()

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "laws": laws,
            "acts": ALLOWED_ACTS,
            "answer": None,
            "question": None,
            "message": None
        }
    )


@app.post("/add-law", response_class=HTMLResponse)
def add_law_route(
    request: Request,
    act_name: str = Form(...),
    section_no: str = Form(...),
    section_title: str = Form(""),
    content: str = Form(...)
):
    if act_name not in ALLOWED_ACTS:
        message = "Invalid Act selected."
    else:
        add_law(act_name, section_no, section_title, content)
        message = "Law section added successfully."

    laws = get_all_laws()

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "laws": laws,
            "acts": ALLOWED_ACTS,
            "answer": None,
            "question": None,
            "message": message
        }
    )


@app.post("/ask", response_class=HTMLResponse)
def ask_question(
    request: Request,
    question: str = Form(...)
):
    matched_laws = search_laws(question)

    # Important:
    # Always send the question to Gemini.
    # If it is outside the five Acts, gemini_client.py will answer generally.
    answer = generate_answer(question, matched_laws)

    matched_law_id = matched_laws[0]["id"] if matched_laws else None
    save_chat(question, answer, matched_law_id)

    laws = get_all_laws()

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "laws": laws,
            "acts": ALLOWED_ACTS,
            "answer": answer,
            "question": question,
            "message": None
        }
    )
