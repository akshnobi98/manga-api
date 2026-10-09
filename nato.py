import requests
from bs4 import BeautifulSoup
import re
import json

BASE_URL = "https://www.manganato.gg"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Referer": "https://www.manganato.gg/",
    "Sec-Ch-Ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    "Sec-Ch-Ua-Arch": '"x86"',
    "Sec-Ch-Ua-Bitness": '"64"',
    "Sec-Ch-Ua-Full-Version": '"145.0.7632.160"',
    "Sec-Ch-Ua-Full-Version-List": '"Not:A-Brand";v="99.0.0.0", "Google Chrome";v="145.0.7632.160", "Chromium";v="145.0.7632.160"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Model": '""',
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Ch-Ua-Platform-Version": '"10.0.0"',
    "X-Requested-With": "XMLHttpRequest"
}

_session = None

def get_session():
    global _session
    if _session is None:
        _session = requests.Session()
        try:
            _session.get(
                BASE_URL, 
                headers=HEADERS, 
                timeout=15
            )
        except:
            pass
    return _session

def fetch_url(url, is_json=False):
    sess = get_session()
    try:
        resp = sess.get(
            url, 
            headers=HEADERS, 
            timeout=15,
            allow_redirects=True
        )
        resp.raise_for_status()
        return resp.json() if is_json else resp.text
    except Exception as e:
        raise e

def parse_home(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    result = {}

    popular = []
    for item in soup.select('.owl-carousel .item'):
        a_tag = item.select_one('h3 a')
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)
        url = a_tag.get('href', '')
        slug = url.rstrip('/').split('/')[-1] if url else ''
        img_tag = item.select_one('img')
        cover = img_tag.get('src') if img_tag else ''
            
        chap_a = item.select_one('.slide-caption > a')
        latest = chap_a.get_text(strip=True) if chap_a else ''
        
        popular.append({
            "title": title,
            "slug": slug,
            "cover": cover,
            "url": f"/nato/manga/{slug}",
            "latest": latest
        })
        
    if popular:
         result["popular"] = {
             "title": "Popular Manga",
             "items": popular
         }

    latest_items = []
    for item in soup.select('.doreamon .itemupdate'):
        a_title = item.select_one('h3 a')
        if not a_title:
             continue
        title = re.sub(r'\s+', ' ', a_title.get_text(strip=True)).strip()
        
        url = a_title.get('href', '')
        slug = url.rstrip('/').split('/')[-1] if url else ''
        
        img_a = item.select_one('a.tooltip img')
        cover = img_a.get('src') if img_a else ''
            
        first_chap = item.select_one('ul li:nth-of-type(2) span a')
        latest = first_chap.get_text(strip=True) if first_chap else ''
        
        latest_items.append({
            "title": title,
            "slug": slug,
            "cover": cover,
            "url": f"/nato/manga/{slug}",
            "latest": latest
        })
        
    if latest_items:
         result["latest"] = {
             "title": "Latest Manga Releases",
             "items": latest_items
         }
         
    return result

def get_manga_details(slug):
    url = f"{BASE_URL}/manga/{slug}"
    html = fetch_url(url)
    soup = BeautifulSoup(html, "html.parser")
    
    info_top = soup.select_one('.manga-info-top') or soup.select_one('.comic-info-wrap')
    if not info_top:
        return None
        
    title = info_top.select_one('h1').get_text(strip=True)
    img = info_top.select_one('img')
    cover = img.get('src') if img else ''
    
    info_list = info_top.select('.manga-info-text li') or info_top.select('.info-wrap > div')
    
    details = {
        "title": title,
        "cover": cover,
        "description": "",
        "authors": "Unknown",
        "status": "Unknown",
        "updated": "Unknown",
        "views": "0",
        "genres": []
    }
    
    desc_node = soup.select_one('#contentBox')
    if desc_node:
        details["description"] = re.sub(r'^.*summary:\s*', '', desc_node.get_text(strip=True), flags=re.IGNORECASE)

    for li in info_list:
        text = li.get_text(strip=True)
        if "Author" in text:
            details["authors"] = text.split(':')[-1].strip()
        elif "Status" in text:
            details["status"] = text.split(':')[-1].strip()
        elif "Last updated" in text:
            details["updated"] = text.split(':')[-1].strip()
        elif "View" in text:
            details["views"] = text.split(':')[-1].strip()
        elif "Genres" in text:
            genres_list = li.select('a')
            details["genres"] = [g.get_text(strip=True) for g in genres_list]

    api_url = f"{BASE_URL}/api/manga/{slug}/chapters"
    try:
        api_data = fetch_url(api_url, is_json=True)
        chapters = []
        if api_data and "data" in api_data and "chapters" in api_data["data"]:
            for c in api_data["data"]["chapters"]:
                chapters.append({
                    "id": c["chapter_slug"],
                    "title": c["chapter_name"],
                    "updated": c["updated_at"]
                })
        details["chapters"] = chapters
    except:
        details["chapters"] = []
        
    return details

def get_chapter_images(manga_slug, chapter_slug):
    url = f"{BASE_URL}/manga/{manga_slug}/{chapter_slug}"
    html = fetch_url(url)
    
    match = re.search(r'var\s+chapterImages\s*=\s*(.*?);', html)
    if not match:
        return []
        
    try:
        paths = json.loads(match.group(1))
        cdn_match = re.search(r'var\s+cdns\s*=\s*(.*?);', html)
        if cdn_match:
            cdns = json.loads(cdn_match.group(1))
            base_cdn = cdns[0] if cdns else "https://img-r1.2xstorage.com/"
        else:
            base_cdn = "https://img-r1.2xstorage.com/"
            
        return [f"{base_cdn}{p}" for p in paths]
    except:
        return []

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        with open("nato.html", "r", encoding="utf-8") as f:
            html = f.read()
        print(json.dumps(parse_home(html), indent=2))
    else:
        cmd = sys.argv[1]
        if cmd == "details" and len(sys.argv) > 2:
            print(json.dumps(get_manga_details(sys.argv[2]), indent=2))
        elif cmd == "images" and len(sys.argv) > 3:
            print(json.dumps(get_chapter_images(sys.argv[2], sys.argv[3]), indent=2))
