import re
import requests
from bs4 import BeautifulSoup
import trafilatura
from readability import Document

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BlogScraper/1.0; +https://example.com/bot)"
}
REQUEST_TIMEOUT = 12


def fetch_html(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception as e:
        raise RuntimeError(f"Error fetching {url}: {e}")


def extract_article_text(html, url=None):
    try:
        downloaded = trafilatura.extract(html, include_comments=False, with_metadata=True)
        if downloaded and len(downloaded) > 200:
            return {"title": None, "text": downloaded}
    except Exception:
        pass

    try:
        doc = Document(html)
        summary_html = doc.summary()
        title = doc.title()
        soup = BeautifulSoup(summary_html, "lxml")
        text = soup.get_text(separator="\n").strip()
        if text and len(text) > 150:
            return {"title": title, "text": text}
    except Exception:
        pass

    soup = BeautifulSoup(html, "lxml")
    candidates = soup.find_all(["article", "div", "main"], limit=40)
    best = ""
    for c in candidates:
        classes = " ".join(c.get("class") or [])
        if re.search(r"nav|menu|footer|header|advert|cookie|subscribe", classes, re.I):
            continue
        txt = c.get_text(separator="\n").strip()
        if len(txt) > len(best):
            best = txt
    if len(best) > 100:
        return {"title": (soup.title.string if soup.title else None), "text": best}

    page_text = soup.get_text(separator="\n").strip()
    return {"title": (soup.title.string if soup.title else None), "text": page_text[:5000]}


COMMENT_KEYWORDS = re.compile(
    r"(comment|reply|discussion|thread|responses|comments-list|feedback|disqus)", re.I
)

NOISE_WORDS = re.compile(
    r"\b(reply|share|expand full comment|liked by|like|report|posted by|author)\b",
    re.I
)

def extract_comments_from_html(html, url):
    soup = BeautifulSoup(html, "lxml")
    comments = []

    # Step 1: find likely comment blocks
    nodes = soup.find_all(lambda tag: (
        tag.get("id") and COMMENT_KEYWORDS.search(tag.get("id"))
    ) or (
        tag.get("class") and COMMENT_KEYWORDS.search(" ".join(tag.get("class")))
    ))

    candidates = []
    for node in nodes:
        # Each direct child may represent a comment
        for child in node.find_all(["div", "li", "article", "section"], recursive=True):
            txt = child.get_text(separator=" ").strip()
            if 20 < len(txt) < 2000:
                candidates.append(txt)

    # Step 2: fallback to generic selectors
    for el in soup.select(".comment, .comment-body, li.comment, div.reply, .comment-entry"):
        txt = el.get_text(separator=" ").strip()
        if 20 < len(txt) < 2000:
            candidates.append(txt)

    # Step 3: clean and filter
    for txt in candidates:
        # remove noise (buttons, metadata)
        txt = NOISE_WORDS.sub("", txt)
        txt = re.sub(r"\s+", " ", txt).strip()

        # discard likely usernames only
        if len(txt.split()) < 4:
            continue

        # heuristic: must have punctuation typical of sentences
        if not re.search(r"[.!?]", txt):
            continue

        comments.append(txt)

    # Step 4: deduplicate
    seen = set()
    out = []
    for c in comments:
        c = c.strip()
        if c and c not in seen:
            seen.add(c)
            out.append(c)

    return out[:50]



# --- Orchestrator ---
def extract_article_and_comments(url):
    """Main orchestrator for article + comment extraction."""
    try:
        html = fetch_html(url)
    except Exception as e:
        return {"url": url, "error": str(e)}

    article = extract_article_text(html, url=url)
    comments = extract_comments_from_html(html, url)

    return {
        "url": url,
        "title": article.get("title"),
        "text": article.get("text"),
        "comments": comments[:30],
    }


if __name__ == "__main__":
    urls = [
        "https://www.wpbeginner.com/beginners-guide/how-to-choose-the-best-domain-registrar/",
    ]
    results = []
    for u in urls:
        print("Scraping:", u)
        res = extract_article_and_comments(u)
        results.append(res)

    import json
    print(json.dumps(results, indent=2, ensure_ascii=False))