# 📚 MangaVault API

<p align="center">
  <a href="https://github.com/walterwhite-69/MangaVault/stargazers"><img src="https://img.shields.io/github/stars/walterwhite-69/MangaVault?style=for-the-badge&color=6c63ff" alt="Stars"></a>
  <a href="https://github.com/walterwhite-69/MangaVault/network/members"><img src="https://img.shields.io/github/forks/walterwhite-69/MangaVault?style=for-the-badge&color=a78bfa" alt="Forks"></a>
  <a href="https://github.com/walterwhite-69/MangaVault/blob/main/LICENSE"><img src="https://img.shields.io/github/license/walterwhite-69/MangaVault?style=for-the-badge&color=6c63ff" alt="LICENSE"></a>
</p>

---

**MangaVault** is a high-performance, unified REST API built with **FastAPI** that aggregates manga content from multiple sources, providing a seamless experience for developers.

## ✨ Features

- 🚀 **FastAPI Core**: Blazing fast performance and automatic OpenAPI documentation.
- 🛡️ **Anti-Bot Bypass**: Specialized headers and session management for resilient scraping.
- 📂 **Multi-Source Support**:
  - **Manganato**: Popular, Latest, Details, and Image extraction.
  - **Atsumaru**: Search, Trending, and Chapter management.
  - **Comix**: Advanced Search, Chapters, and High-res images.
- ⚡ **Optimized Scrapers**: Comment-free, lightweight code for maximum efficiency.
- 🎨 **Beautiful Documentation**: Built-in interactive documentation page.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI
- **Networking**: `requests`, `curl_cffi` (for impersonation)
- **Parsing**: `BeautifulSoup4`, `Regex`
- **Server**: `uvicorn`

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/walterwhite-69/MangaVault.git
cd MangaVault/comix
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the API
```bash
python api.py
```

The API will be available at `http://127.0.0.1:8000`. You can access the interactive documentation at the root URL.

---

## 📡 API Endpoints

### Manganato
- `GET /nato/home`: Fetch trending and latest updates.
- `GET /nato/manga/{slug}/details`: Get full metadata and chapter lists.
- `GET /nato/manga/{manga_slug}/{chapter_slug}/images`: Extract panel images.

### Atsumaru
- `GET /atsu/home`: Get trending manga.
- `GET /atsu/search?keyword={query}`: Search for manga.

### Comix
- `GET /comix/home`: Recently added and trending titles.
- `GET /comix/search?keyword={query}`: Advanced search functionality.

---

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">Made by walter for the Manga Community</p>
