from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
import json
import os
import logging

app = FastAPI()

REDIRECT_FILE = "redirects.json"
logger = logging.getLogger(__name__)

def load_redirects():
    """Load redirect mappings from the JSON file, creating it if it doesn’t exist."""
    if not os.path.exists(REDIRECT_FILE):
        with open(REDIRECT_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(REDIRECT_FILE) as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in redirects file")
        return []
    except Exception as e:
        logger.error(f"Error loading redirects: {e}")
        return []

def save_redirects(data):
    """Save redirect mappings to the JSON file with error handling."""
    try:
        with open(REDIRECT_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving redirects: {e}")

class Redirect(BaseModel):
    subdomain: str
    url: str

@app.middleware("http")
async def redirect_middleware(request: Request, call_next):
    """Handle subdomain redirects and root domain redirect."""
    host = request.headers.get("host", "").lower()
    # Only process requests for gamblecodez.com or its subdomains
    if not host.endswith(".gamblecodez.com") and host != "gamblecodez.com":
        return await call_next(request)

    # Redirect root domain and www to a specific URL
    if host == "gamblecodez.com" or host == "www.gamblecodez.com":
        return RedirectResponse("https://t.me/GambleCodezDrops")

    # Extract subdomain and check redirect map
    subdomain = host.split(".")[0]
    redirects = load_redirects()
    match = next((r for r in redirects if r["subdomain"].lower() == subdomain), None)
    if match:
        return RedirectResponse(match["url"])
    return await call_next(request)

@app.get("/admin", response_class=HTMLResponse)
def dashboard():
    """Display the admin dashboard with current redirects."""
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
    """Add a new redirect mapping."""
    redirects = load_redirects()
    if any(r["subdomain"] == subdomain for r in redirects):
        raise HTTPException(status_code=400, detail="Subdomain already exists")
    redirects.append({"subdomain": subdomain, "url": url})
    save_redirects(redirects)
    return RedirectResponse("/admin", status_code=303)

@app.get("/delete/{subdomain}")
def delete_redirect(subdomain: str):
    """Delete a redirect mapping by subdomain."""
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
