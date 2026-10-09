from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import re
import html as html_module
from urllib.parse import urlencode

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://comix.to/",
}

BASE_URL = "https://comix.to"

def fetch_page(path="/home", return_resp=False):
    resp = requests.get(
        f"{BASE_URL}{path}",
        headers=HEADERS,
        impersonate="chrome124",
        timeout=30,
    )
    return resp if return_resp else resp.text

def parse_item(item_el):
    data = {}

    rank_div = item_el.find("div", class_="num")
    if rank_div:
        data["rank"] = int(rank_div.get_text(strip=True))

    poster_link = item_el.find("a", class_="poster")
    if not poster_link:
        poster_link = item_el.find("a", href=lambda h: h and "/title/" in h)
    if poster_link:
        href = poster_link.get("href", "")
        data["url"] = BASE_URL + href if href.startswith("/") else href
        slug = href.split("/title/")[-1] if "/title/" in href else ""
        data["id"] = slug.split("-")[0] if slug else ""

    img = item_el.find("img")
    if img:
        data["cover"] = img.get("src", "")
        data["title"] = html_module.unescape(img.get("alt", ""))

    title_link = item_el.find("a", class_="title")
    if title_link:
        data["title"] = html_module.unescape(title_link.get_text(strip=True))
    title_div = item_el.find("div", class_="title")
    if title_div and "title" not in data:
        data["title"] = html_module.unescape(title_div.get_text(strip=True))

    metadata_div = item_el.find("div", class_="metadata")
    if metadata_div:
        spans = metadata_div.find_all("span")
        if len(spans) >= 1:
            data["latest_chapter"] = spans[0].get_text(strip=True)
        if len(spans) >= 2:
            data["updated_at"] = spans[1].get_text(strip=True)

    type_span = item_el.find("span", class_="news")
    if type_span:
        data["type"] = type_span.get_text(strip=True)

    return data

def parse_main_section(section_el):
    items = []
    for item_div in section_el.find_all("div", class_="item"):
        parsed = parse_item(item_div)
        if parsed.get("title"):
            items.append(parsed)
    return items

def parse_sidebar_section(section_el):
    items = []
    for item_a in section_el.find_all("a", class_="item"):
        parsed = parse_item(item_a)
        if parsed.get("title"):
            items.append(parsed)
    return items

def parse_comments(section_el):
    comments = []
    for item_a in section_el.find_all("a", class_="item"):
        comment = {}
        head = item_a.find("div", class_="comment-head")
        if head:
            span = head.find("span")
            if span:
                comment["context"] = html_module.unescape(span.get_text(strip=True))
            img = head.find("img")
            if img:
                comment["poster"] = img.get("src", "")
        body = item_a.find("div", class_="comment-body")
        if body:
            comment["text"] = html_module.unescape(body.get_text(strip=True))
        foot = item_a.find("div", class_="comment-foot")
        if foot:
            spans = foot.find_all("span")
            if len(spans) >= 1:
                comment["user"] = spans[0].get_text(strip=True)
            if len(spans) >= 2:
                comment["time"] = spans[1].get_text(strip=True)
        href = item_a.get("href", "")
        if href:
            comment["url"] = BASE_URL + href if href.startswith("/") else href
        if comment:
            comments.append(comment)
    return comments

def parse_home(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    result = {}

    main_aside = soup.find("aside", class_="main")
    if main_aside:
        for sec in main_aside.find_all("section"):
            title_span = sec.find("span", class_="section-title")
            if title_span:
                section_name = title_span.get_text(strip=True)
                key = section_name.lower().replace(" ", "_")
                items = parse_main_section(sec)
                if items:
                    result[key] = {"title": section_name, "items": items}

    sidebar = soup.find("aside", class_="sidebar")
    if sidebar:
        added_box = sidebar.find("section", class_="added-box")
        if added_box:
            tab_div = added_box.find("div", class_="section-tab")
            tab_names = []
            if tab_div:
                tab_names = [s.get_text(strip=True) for s in tab_div.find_all("span")]
            items = parse_sidebar_section(added_box)
            key = tab_names[0].lower().replace(" ", "_") if tab_names else "recently_added"
            if items:
                result[key] = {"title": tab_names[0] if tab_names else "Recently Added", "items": items}

        comments_box = sidebar.find("section", class_="comments-box")
        if comments_box:
            comments = parse_comments(comments_box)
            if comments:
                result["latest_comments"] = {"title": "Latest Comments", "items": comments}

    return result

def find_json_object(html, key):
    for pattern in [fr'\\\"{key}\\\":\s*([{{\[].*)', fr'"{key}":\s*([{{\[].*)']:
        match = re.search(pattern, html)
        if match:
            raw_chunk = match.group(1)
            is_obj = raw_chunk.startswith('{') or raw_chunk.startswith('\\{')
            is_arr = raw_chunk.startswith('[') or raw_chunk.startswith('\\[')
            
            start_char = '{' if is_obj else '['
            end_char = '}' if is_obj else ']'
            
            count = 0
            json_str = ""
            for char in raw_chunk:
                if char == start_char:
                    count += 1
                elif char == end_char:
                    count -= 1
                
                json_str += char
                if count == 0:
                    break
            
            if json_str:
                try:
                    if '\\"' in json_str or '\\\\' in json_str:
                        json_str = json_str.replace('\\"', '"').replace('\\\\', '\\')
                    return json.loads(json_str)
                except:
                    continue
    return None

def fetch_manga_details(id_or_slug):
    path = f"/title/{id_or_slug}"
    html_text = fetch_page(path)
    data = find_json_object(html_text, "manga")
    if data:
        return data
    return {"error": "Could not extract manga details", "id": id_or_slug}

def fetch_chapters(hash_id, page=1, limit=20, order="desc"):
    api_url = f"{BASE_URL}/api/v2/manga/{hash_id}/chapters?limit={limit}&page={page}&order[number]={order}"
    resp = requests.get(api_url, headers=HEADERS, impersonate="chrome124", timeout=30)
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"Failed to fetch chapters: {resp.status_code}", "id": hash_id}

def fetch_chapter_images(manga_slug, chapter_slug):
    path = f"/title/{manga_slug}/{chapter_slug}"
    html_text = fetch_page(path)
    data = find_json_object(html_text, "images")
    if data:
        return data
    return {"error": "Could not extract images", "manga": manga_slug, "chapter": chapter_slug}

def fetch_chapter_images_by_id(hash_id, chapter_id, chapter_number):
    resp = fetch_page(f"/title/{hash_id}", return_resp=True)
    manga_slug = hash_id
    if "/title/" in resp.url:
        manga_slug = resp.url.split("/title/")[-1].split("?")[0].split("/")[0]

    chapter_slug = f"{chapter_id}-chapter-{chapter_number}"
    return fetch_chapter_images(manga_slug, chapter_slug)

def search_manga(keyword, limit=20, page=1, order="relevance", genres=None):
    params = {
        f"order[{order}]": "desc",
        "keyword": keyword,
        "limit": limit,
        "page": page
    }
    api_url = f"{BASE_URL}/api/v2/manga"
    if genres:
        genre_params = "&".join([f"genres[]={g}" for g in genres])
        api_url += f"?{genre_params}&{urlencode(params)}"
        resp = requests.get(api_url, headers=HEADERS, impersonate="chrome124", timeout=30)
    else:
        resp = requests.get(api_url, params=params, headers=HEADERS, impersonate="chrome124", timeout=30)
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"Failed to search manga: {resp.status_code}", "keyword": keyword}
