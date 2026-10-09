from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import scraper as comix
import atsu
import nato
import time
from typing import Optional

app = FastAPI(
    title="MangaVault API",
    description="Unified REST API for multiple manga sources",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MangaVault API - Docs</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #0b0d12; --surface: #111318; --surface2: #181c24; --border: #1e2330;
      --accent: #6c63ff; --accent2: #a78bfa; --text: #e6eaf5; --muted: #6b7280;
      --get: #22c55e; --radius: 12px;
    }
    html { scroll-behavior: smooth; }
    body { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; line-height: 1.7; min-height: 100vh; }
    .hero {
      position: relative; overflow: hidden; text-align: center;
      padding: 100px 24px 80px;
      background: radial-gradient(ellipse 80% 60% at 50% 0%, #1d1545 0%, transparent 70%);
    }
    .hero::before {
      content: ''; position: absolute; inset: 0;
      background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%231e2330' stroke-width='1'%3E%3Cpath d='M0 0h60v60H0z'/%3E%3C/g%3E%3C/svg%3E");
      opacity: 0.4;
    }
    .badge {
      display: inline-block; background: linear-gradient(135deg,#6c63ff22,#a78bfa22);
      border: 1px solid #6c63ff44; color: var(--accent2); font-size: 12px; font-weight: 600;
      letter-spacing: 1.5px; text-transform: uppercase; padding: 6px 16px; border-radius: 100px; margin-bottom: 24px;
    }
    .hero h1 {
      font-size: clamp(2.2rem,5vw,3.8rem); font-weight: 700;
      background: linear-gradient(135deg,#fff 30%,var(--accent2));
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
      line-height: 1.15; margin-bottom: 16px;
    }
    .hero p { font-size: 1.1rem; color: var(--muted); max-width: 520px; margin: 0 auto 36px; }
    .hero-pills { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
    .hero-pills span { background: var(--surface2); border: 1px solid var(--border); padding: 6px 16px; border-radius: 100px; font-size: 13px; color: var(--muted); }
    .hero-pills span strong { color: var(--text); }
    .container { max-width: 900px; margin: 0 auto; padding: 60px 24px 100px; }
    .section-label { font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: var(--accent2); margin-top: 40px; margin-bottom: 24px; }
    .endpoint { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 16px; overflow: hidden; transition: border-color 0.2s, box-shadow 0.2s; }
    .endpoint:hover { border-color: #6c63ff55; box-shadow: 0 0 0 1px #6c63ff22, 0 8px 32px #00000044; }
    .ep-header { display: flex; align-items: flex-start; gap: 16px; padding: 20px 24px; cursor: pointer; user-select: none; }
    .method { flex-shrink: 0; background: #22c55e18; color: var(--get); font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; letter-spacing: 1px; padding: 4px 10px; border-radius: 6px; border: 1px solid #22c55e33; margin-top: 3px; }
    .ep-title { flex: 1; }
    .ep-path { font-family: 'JetBrains Mono', monospace; font-size: 15px; color: var(--text); font-weight: 500; margin-bottom: 4px; }
    .ep-path .param { color: var(--accent2); }
    .ep-desc { font-size: 13.5px; color: var(--muted); }
    .ep-chevron { flex-shrink: 0; color: var(--muted); transition: transform 0.25s; font-size: 18px; margin-top: 2px; }
    .endpoint.open .ep-chevron { transform: rotate(180deg); }
    .ep-body { display: none; padding: 0 24px 24px; border-top: 1px solid var(--border); }
    .endpoint.open .ep-body { display: block; }
    .ep-params-title { font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--muted); margin: 20px 0 12px; }
    .param-table { width: 100%; border-collapse: collapse; }
    .param-table th, .param-table td { text-align: left; padding: 10px 12px; font-size: 13.5px; border-bottom: 1px solid var(--border); }
    .param-table th { color: var(--muted); font-weight: 500; font-size: 12px; letter-spacing: 0.5px; }
    .param-table td:first-child { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: var(--accent2); }
    .param-table td:last-child { color: var(--muted); }
    .required { background: #f9731622; color: #fb923c; font-size: 10px; font-weight: 600; letter-spacing: 0.5px; padding: 2px 7px; border-radius: 4px; border: 1px solid #f9731633; margin-left: 8px; vertical-align: middle; }
    .example-block { margin-top: 20px; }
    .example-label { font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--muted); margin-bottom: 10px; }
    .code-block { background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 14px 18px; font-family: 'JetBrains Mono', monospace; font-size: 13px; color: var(--accent2); word-break: break-all; position: relative; }
    .copy-btn { position: absolute; top: 10px; right: 12px; background: var(--border); border: none; color: var(--muted); font-size: 11px; font-family: 'Inter', sans-serif; padding: 4px 10px; border-radius: 6px; cursor: pointer; transition: background 0.15s, color 0.15s; }
    .copy-btn:hover { background: #6c63ff44; color: var(--accent2); }
    .copy-btn.copied { color: var(--get); }
    footer { text-align: center; padding: 40px 24px; border-top: 1px solid var(--border); color: var(--muted); font-size: 13px; }
    footer a { color: var(--accent2); text-decoration: none; }
    footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>
<section class="hero">
  <div class="badge">REST API - v1.0.0</div>
  <h1>MangaVault<br>API Docs</h1>
  <p>Unified API for Manganato, Atsumaru, and Comix.</p>
  <div class="hero-pills">
    <span>Unauthenticated</span>
    <span>Fast Responses</span>
    <span>JSON Output</span>
    <span>Multi Source</span>
  </div>
</section>
<div class="container">
  <p class="section-label">Source: Manganato (manganato.gg)</p>
  
  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/nato/home</div>
        <div class="ep-desc">Returns popular and latest manga from Manganato.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_nato_home">http://127.0.0.1:8000/nato/home<button class="copy-btn" onclick="copy('ex_nato_home',this)">Copy</button></div>
      </div>
    </div>
  </div>


  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/nato/manga/<span class="param">{slug}</span>/details</div>
        <div class="ep-desc">Get metadata and full chapter list for a manga.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_nato_details">http://127.0.0.1:8000/nato/manga/bitch-im-a-young-lady-with-hax/details<button class="copy-btn" onclick="copy('ex_nato_details',this)">Copy</button></div>
      </div>
    </div>
  </div>

  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/nato/manga/<span class="param">{manga_slug}</span>/<span class="param">{chapter_slug}</span>/images</div>
        <div class="ep-desc">Get panel images for a specific chapter.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_nato_images">http://127.0.0.1:8000/nato/manga/bitch-im-a-young-lady-with-hax/chapter-313/images<button class="copy-btn" onclick="copy('ex_nato_images',this)">Copy</button></div>
      </div>
    </div>
  </div>

  <p class="section-label">Source: Atsumaru (atsu.moe)</p>

  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/atsu/home</div>
        <div class="ep-desc">Returns trending and latest manga from Atsumaru.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_atsu_home">http://127.0.0.1:8000/atsu/home<button class="copy-btn" onclick="copy('ex_atsu_home',this)">Copy</button></div>
      </div>
    </div>
  </div>

  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/atsu/search</div>
        <div class="ep-desc">Search manga by keyword.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_atsu_search">http://127.0.0.1:8000/atsu/search?keyword=solo leveling<button class="copy-btn" onclick="copy('ex_atsu_search',this)">Copy</button></div>
      </div>
    </div>
  </div>

  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/atsu/manga/<span class="param">{id}</span>/details</div>
        <div class="ep-desc">Get manga details and full chapter list.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_atsu_details">http://127.0.0.1:8000/atsu/manga/v8Kbg/details<button class="copy-btn" onclick="copy('ex_atsu_details',this)">Copy</button></div>
      </div>
    </div>
  </div>

  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/atsu/manga/<span class="param">{manga_id}</span>/chapter/<span class="param">{chapter_id}</span>/images</div>
        <div class="ep-desc">Get panel images for a chapter.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_atsu_img">http://127.0.0.1:8000/atsu/manga/v8Kbg/chapter/SRw28/images<button class="copy-btn" onclick="copy('ex_atsu_img',this)">Copy</button></div>
      </div>
    </div>
  </div>

  <p class="section-label">Source: Comix.to</p>

  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/comix/home</div>
        <div class="ep-desc">Returns trending, popular, and recently added manga.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_comix_home">http://127.0.0.1:8000/comix/home<button class="copy-btn" onclick="copy('ex_comix_home',this)">Copy</button></div>
      </div>
    </div>
  </div>

  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/comix/search</div>
        <div class="ep-desc">Advanced search with keywords and filters.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_comix_search">http://127.0.0.1:8000/comix/search?keyword=martial arts<button class="copy-btn" onclick="copy('ex_comix_search',this)">Copy</button></div>
      </div>
    </div>
  </div>

  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/comix/manga/<span class="param">{slug}</span>/details</div>
        <div class="ep-desc">Get metadata for a specific manga.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_comix_details">http://127.0.0.1:8000/comix/manga/q9w8x/details<button class="copy-btn" onclick="copy('ex_comix_details',this)">Copy</button></div>
      </div>
    </div>
  </div>

  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/comix/manga/<span class="param">{hash_id}</span>/chapters</div>
        <div class="ep-desc">Get full chapter list with pagination.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_comix_chaps">http://127.0.0.1:8000/comix/manga/q9w8x/chapters<button class="copy-btn" onclick="copy('ex_comix_chaps',this)">Copy</button></div>
      </div>
    </div>
  </div>

  <div class="endpoint">
    <div class="ep-header" onclick="toggle(this)">
      <span class="method">GET</span>
      <div class="ep-title">
        <div class="ep-path">/comix/manga/<span class="param">{hash_id}</span>/<span class="param">{chapter_id}</span>/<span class="param">{num}</span>/images</div>
        <div class="ep-desc">Get panel images for a chapter.</div>
      </div>
      <span class="ep-chevron">⌄</span>
    </div>
    <div class="ep-body">
      <div class="example-block">
        <p class="example-label">Example Request</p>
        <div class="code-block" id="ex_comix_img">http://127.0.0.1:8000/comix/manga/q9w8x/7217264/0/images<button class="copy-btn" onclick="copy('ex_comix_img',this)">Copy</button></div>
      </div>
    </div>
  </div>

</div>
<footer>
  <p>MangaVault Powered by Manganato, Atsumaru and Comix</p>
</footer>
<script>
  function toggle(header) { header.closest('.endpoint').classList.toggle('open'); }
  function copy(id, btn) {
    const text = document.getElementById(id).firstChild.textContent.trim();
    navigator.clipboard.writeText(text).then(() => {
      btn.textContent = 'Copied!'; btn.classList.add('copied');
      setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1800);
    });
  }
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def docs():
    return DOCS_HTML

@app.get("/nato/home")
def nato_home():
    start_time = time.time()
    try:
        html = nato.fetch_url(nato.BASE_URL)
        data = nato.parse_home(html)
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nato/manga/{slug}/details")
def nato_details(slug: str):
    start_time = time.time()
    try:
        data = nato.get_manga_details(slug)
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nato/manga/{manga_slug}/{chapter_slug}/images")
def nato_images(manga_slug: str, chapter_slug: str):
    start_time = time.time()
    try:
        data = nato.get_chapter_images(manga_slug, chapter_slug)
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comix/home")
def comix_home():
    start_time = time.time()
    try:
        html = comix.fetch_page("/home")
        data = comix.parse_home(html)
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comix/manga/{id_or_slug}/details")
def comix_details(id_or_slug: str):
    start_time = time.time()
    try:
        data = comix.fetch_manga_details(id_or_slug)
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comix/manga/{hash_id}/chapters")
def comix_chapters(hash_id: str, page: int = 1, limit: int = 20, order: str = "desc"):
    start_time = time.time()
    try:
        data = comix.fetch_chapters(hash_id, page=page, limit=limit, order=order)
        if "result" in data and "items" in data["result"]:
            manga_slug = hash_id
            for item in data["result"]["items"]:
                chapter_id = item.get("chapter_id") or item.get("id")
                number = item.get("number")
                if chapter_id and number is not None:
                    item["url"] = f"/comix/manga/{manga_slug}/{chapter_id}/{number}/images"
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comix/manga/{hash_id}/{chapter_id}/{chapter_number}/images")
def comix_images(hash_id: str, chapter_id: str, chapter_number: str):
    start_time = time.time()
    try:
        data = comix.fetch_chapter_images_by_id(hash_id, chapter_id, chapter_number)
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comix/search")
def comix_search(keyword: str, limit: int = 20, page: int = 1, order: str = "relevance", genres: Optional[str] = None):
    start_time = time.time()
    try:
        genre_list = genres.split(",") if genres else None
        data = comix.search_manga(keyword, limit=limit, page=page, order=order, genres=genre_list)
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/atsu/home")
def atsu_home():
    start_time = time.time()
    try:
        data = atsu.parse_home()
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/atsu/search")
def atsu_search(keyword: str, limit: int = 12):
    start_time = time.time()
    try:
        data = atsu.parse_search(keyword, limit=limit)
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/atsu/manga/{manga_id}/details")
def atsu_details(manga_id: str):
    start_time = time.time()
    try:
        data = atsu.parse_manga_details(manga_id)
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/atsu/manga/{manga_id}/chapter/{chapter_id}/images")
def atsu_images(manga_id: str, chapter_id: str):
    start_time = time.time()
    try:
        data = atsu.parse_chapter_images(manga_id, chapter_id)
        elapsed = time.time() - start_time
        return {"success": True, "took": float(f"{elapsed:.2f}"), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
