import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/140.0 Safari/537.36"
    )
}

def cleaning_text(text):
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)
    return "\n".join(lines)

def scraper_url(url,max_chars = 12000):
    try:
        response = requests.get(
            url,headers=HEADERS,timeout=15
        )

        response.raise_for_status()


        content_type = response.headers.get(
            "content-Type",""
        )

        if "text/html" not in content_type:
            return {
                "url" : url,
                "success" : False,
                "content" : "",
                "error" : "Note an HTML page"
            }
        soup = BeautifulSoup(response.text,"html.parser")

        for element in soup([
            "script",
            "style",
            "noscript",
            "nav",
            "footer",
            "header",
            "aside"
        ]):
            element.decompose()

        title = ""

        if soup.title:
            title = soup.title.get_text(
                strip=True
            )

        text = soup.get_text(
            separator="\n"
        )

        text = cleaning_text(text)

        text = text[:max_chars]

        return {
            "url": url,
            "title": title,
            "success": True,
            "content": text
        }

    except Exception as e:

        return {
            "url": url,
            "success": False,
            "content": "",
            "error": str(e)
        }


def scrape_sources(sources, max_sources=10):

    scraped = []

    visited = set()

    for source in sources:

        url = source.get("url")

        if not url:
            continue

        if url in visited:
            continue

        visited.add(url)

        print(f"[Scraper] {url}")

        result = scraper_url(url)

        if result["success"]:
            scraped.append(result)

        if len(scraped) >= max_sources:
            break

    return scraped


