from curl_cffi import requests

BASE_URL = "https://atsu.moe"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://atsu.moe/",
}

def fetch_json(url):
    resp = requests.get(
        url,
        headers=HEADERS,
        impersonate="chrome124",
        timeout=30,
    )
    return resp.json()

def parse_home():
    data = fetch_json(f"{BASE_URL}/api/home/page")
    result = {}
    
    if "homePage" in data and "sections" in data["homePage"]:
        for section in data["homePage"]["sections"]:
            key = section.get("key", "unknown_section")
            title = section.get("title", key.replace('-', ' ').title())
            items = []
            for item in section.get("items", []):
                items.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "slug": item.get("id"),
                    "cover": f"{BASE_URL}/{item.get('image')}" if item.get("image") else "",
                    "type": item.get("type"),
                    "isAdult": item.get("isAdult", False),
                    "url": f"/atsu/manga/{item.get('id')}/details"
                })
            if items:
                result[key.replace("-", "_")] = {
                    "title": title,
                    "items": items
                }
    return result

def parse_manga_details(manga_id):
    details_data = fetch_json(f"{BASE_URL}/api/manga/page?id={manga_id}")
    info_data = fetch_json(f"{BASE_URL}/api/manga/info?mangaId={manga_id}")
    
    manga_page = details_data.get("mangaPage", {})
    
    result = {
        "id": manga_id,
        "title": info_data.get("title", ""),
        "type": info_data.get("type", ""),
        "views": manga_page.get("views", ""),
        "released": manga_page.get("released"),
        "url": f"{BASE_URL}/title/{manga_id}"
    }
    
    if manga_page.get("banner") and manga_page["banner"].get("url"):
        result["cover"] = f"{BASE_URL}/{manga_page['banner']['url']}"
    
    scanlators = [s.get("name") for s in manga_page.get("scanlators", []) if s.get("name")]
    if scanlators:
        result["scanlators"] = scanlators
        
    chapters = []
    for chap in info_data.get("chapters", []):
        chapters.append({
            "id": chap.get("id"),
            "number": chap.get("number"),
            "title": chap.get("title", ""),
            "scanId": chap.get("scanId", ""),
            "pageCount": chap.get("pageCount", 0),
            "url": f"/atsu/manga/{manga_id}/chapter/{chap.get('id')}/images"
        })
    
    result["chapters"] = chapters
    result["chapter_count"] = len(chapters)
    
    return result

def parse_chapter_images(manga_id, chapter_id):
    data = fetch_json(f"{BASE_URL}/api/read/chapter?mangaId={manga_id}&chapterId={chapter_id}")
    
    read_chap = data.get("readChapter", {})
    pages = []
    for page in read_chap.get("pages", []):
        img_url = page.get("image")
        if img_url:
            if img_url.startswith("/"):
                pages.append(f"{BASE_URL}{img_url}")
            else:
                pages.append(f"{BASE_URL}/{img_url}")
                
    return pages

def parse_search(query, limit=12):
    import urllib.parse
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"{BASE_URL}/collections/manga/documents/search?filter_by=&q={encoded_query}&limit={limit}&query_by=title%2CenglishTitle%2CotherNames%2Cauthors&query_by_weights=4%2C3%2C2%2C1&include_fields=id%2Ctitle%2CenglishTitle%2Cposter%2CposterSmall%2CposterMedium%2Ctype%2CisAdult%2Cstatus%2Cyear&num_typos=4%2C3%2C2%2C1"
    
    data = fetch_json(search_url)
    results = []
    
    for hit in data.get("hits", []):
        doc = hit.get("document", {})
        if doc:
            poster_path = doc.get("poster") or doc.get("posterMedium") or doc.get("posterSmall")
            results.append({
                "id": doc.get("id"),
                "title": doc.get("title") or doc.get("englishTitle"),
                "slug": doc.get("id"),
                "cover": f"{BASE_URL}{poster_path}" if poster_path else "",
                "type": doc.get("type"),
                "isAdult": doc.get("isAdult", False),
                "status": doc.get("status"),
                "year": doc.get("year"),
                "url": f"/atsu/manga/{doc.get('id')}/details"
            })
            
    return {
        "found": data.get("found", 0),
        "items": results
    }
