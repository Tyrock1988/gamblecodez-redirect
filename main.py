from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import List
from pydantic import BaseModel
import json
import os

app = FastAPI()

REDIRECT_FILE = "redirects.json"

def load_redirects():
    if not os.path.exists(REDIRECT_FILE):
        with open(REDIRECT_FILE, "w") as f:
            json.dump([], f)
    with open(REDIRECT_FILE) as f:
        return json.load(f)

def save_redirects(data):
    with open(REDIRECT_FILE, "w") as f:
        json.dump(data, f, indent=2)

class Redirect(BaseModel):
    subdomain: str
    url: str

@app.middleware("http")
async def redirect_middleware(request: Request, call_next):
    host = request.headers.get("host", "")
    if not host or "gamblecodez.com" not in host:
        return await call_next(request)

    subdomain = host.split(".")[0].lower()
    redirects = load_redirects()
    match = next((r for r in redirects if r["subdomain"].lower() == subdomain), None)
    if match:
        return RedirectResponse(match["url"])
    return await call_next(request)

@app.get("/admin", response_class=HTMLResponse)
def dashboard():
    redirects = load_redirects()
    html = """
    <html><head><title>GambleCodez Redirect Dashboard</title></head><body>
    <h1>Redirect Manager</h1>
    <form method='post' action='/add'>
        <input name='subdomain' placeholder='Subdomain' required>
        <input name='url' placeholder='Destination URL' required>
        <button type='submit'>Add</button>
    </form>
    <table border='1'><tr><th>Subdomain</th><th>URL</th><th>Delete</th></tr>
    """
    for r in redirects:
        html += f"<tr><td>{r['subdomain']}</td><td>{r['url']}</td>"
        html += f"<td><a href='/delete/{r['subdomain']}'>Delete</a></td></tr>"
    html += "</table></body></html>"
    return HTMLResponse(content=html)

@app.post("/add")
def add_redirect(subdomain: str = Form(...), url: str = Form(...)):
    redirects = load_redirects()
    if any(r["subdomain"] == subdomain for r in redirects):
        raise HTTPException(status_code=400, detail="Subdomain already exists")
    redirects.append({"subdomain": subdomain, "url": url})
    save_redirects(redirects)
    return RedirectResponse("/admin", status_code=303)

@app.get("/delete/{subdomain}")
def delete_redirect(subdomain: str):
    redirects = load_redirects()
    redirects = [r for r in redirects if r["subdomain"] != subdomain]
    save_redirects(redirects)
    return RedirectResponse("/admin", status_code=303)

INITIAL_REDIRECTS = [
    {"subdomain": "group", "url": "https://t.me/GambleCodezPrizeHub"},
    {"subdomain": "channel", "url": "https://t.me/GambleCodezDrops"},
    {"subdomain": "x", "url": "https://x.com/GambleCodez"},
    {"subdomain": "runewager", "url": "https://runewager.com/r/GambleCodez"},
    {"subdomain": "discord", "url": "https://discord.gg/7fcr69AHxt"},
    {"subdomain": "winna", "url": "https://winna.com/?r=4lwGeA"},
    {"subdomain": "fishtables", "url": "https://fishtables.io/pre-register?ref=zpvfkfmea5"},
]
if not os.path.exists(REDIRECT_FILE):
    save_redirects(INITIAL_REDIRECTS)
