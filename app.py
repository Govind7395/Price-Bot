from fastapi import FastAPI, Request, Form
from fastapi import Header, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from urllib.parse import quote
import asyncio
from main import scrape_product

app = FastAPI(title="PriceBot")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def index_post(request: Request, product: str = Form(...)):
    return RedirectResponse(url=f"/results?query={quote(product)}", status_code=303)


@app.get("/results", response_class=HTMLResponse)
async def results(request: Request, query: str | None = None):
    if not query:
        return RedirectResponse("/", status_code=303)

    results_data = await asyncio.to_thread(lambda: asyncio.run(scrape_product(query)))

    return templates.TemplateResponse(
        "results.html", {"request": request, "query": query, "results": results_data}
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})


@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )
    raise exc
