import re
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import trafilatura
from readability import Document

# --- Config ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BlogScraper/1.0; +https://example.com/bot)"
}
REQUEST_TIMEOUT = 12
SELENIUM_RENDER = False  # set True if you want to use selenium fallback
# If using Selenium, configure here:
SELENIUM_DRIVER = None  # placeholder for webdriver instance if you enable selenium


# --- Helpers ---
def fetch_html(url, use_selenium=False):
    """Fetch HTML. Falls back to Selenium if requested or if site requires JS."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception as e:
        if use_selenium and SELENIUM_DRIVER:
            # Selenium fallback (basic)
            SELENIUM_DRIVER.get(url)
            time.sleep(2)  # let JS load
            return SELENIUM_DRIVER.page_source
        raise


# --- Article extraction ---
def extract_article_text(html, url=None):
    """
    Try multiple strategies to get the main article text and title.
    Returns dict: {"title":..., "text":..., "excerpt":..., "lang":...}
    """
    # 1) trafilatura (very good at long-form extraction)
    try:
        downloaded = trafilatura.extract(html, include_comments=False, with_metadata=True)
        if downloaded and len(downloaded) > 200:
            # trafilatura returns a string (cleaned text) or None
            return {"title": None, "text": downloaded}
    except Exception:
        pass

    # 2) readability-lxml (Document)
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

    # 3) Heuristic: find the largest <article> or largest <div> by text length
    soup = BeautifulSoup(html, "lxml")
    candidates = soup.find_all(["article", "div", "main"], limit=40)
    best = ""
    for c in candidates:
        # exclude navigation, footer by class keywords
        classes = " ".join(c.get("class") or [])
        if re.search(r"nav|menu|footer|header|advert|cookie|subscribe", classes, re.I):
            continue
        txt = c.get_text(separator="\n").strip()
        if len(txt) > len(best):
            best = txt
    if len(best) > 100:
        return {"title": (soup.title.string if soup.title else None), "text": best}

    # 4) Last resort: page text
    page_text = soup.get_text(separator="\n").strip()
    return {"title": (soup.title.string if soup.title else None), "text": page_text[:5000]}


# --- Comment extraction ---
COMMENT_KEYWORDS = re.compile(
    r"(comment|reply|discussion|thread|responses|comments-list|fb-comments|disqus)", re.I
)

def extract_comments_from_html(html, url):
    """Return a list of comment strings found in the HTML using heuristics."""
    soup = BeautifulSoup(html, "lxml")
    comments = []

    # 1) find nodes with id/class matching comment keywords
    nodes = soup.find_all(lambda tag: (
        tag.get("id") and COMMENT_KEYWORDS.search(tag.get("id")) ) or (
        tag.get("class") and COMMENT_KEYWORDS.search(" ".join(tag.get("class")))
    ))
    for node in nodes:
        # gather descendant text blocks that look like comments (smallish blocks)
        for child in node.find_all(["p", "div", "li"], recursive=True):
            txt = child.get_text(separator=" ").strip()
            if 20 < len(txt) < 2000:  # keep reasonable length
                comments.append(txt)

    # 2) Some comment systems use <li class="comment"> or <div class="comment-body">
    for el in soup.select(".comment, .comment-body, li.comment, div.reply, .comment-entry"):
        txt = el.get_text(separator=" ").strip()
        if 20 < len(txt) < 2000:
            comments.append(txt)

    # unique & trimmed
    seen = set()
    out = []
    for c in comments:
        c = re.sub(r"\s+", " ", c).strip()
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    # limit to top 50
    return out[:50]


# --- WordPress REST comments attempt ---
def try_wordpress_comments(url):
    """
    Attempt to fetch comments via WordPress REST API, if WP is used.
    Returns list of comments or [].
    """
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    # Many WP sites expose /wp-json/wp/v2/comments?post=POSTID but we need post ID.
    # Simpler: try general comments endpoint without post filter (may be limited)
    rest_url = base + "/wp-json/wp/v2/comments"
    try:
        r = requests.get(rest_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            data = r.json()
            out = []
            for item in data[:50]:
                content = item.get("content", {}).get("rendered", "")
                if content:
                    text = BeautifulSoup(content, "lxml").get_text(separator=" ").strip()
                    if text:
                        out.append(text)
            return out
    except Exception:
        pass
    return []


# --- Common third-party comment detection ---
def detect_disqus(html):
    """Return shortname if disqus embed found in page"""
    m = re.search(r"disqus_shortname\s*[:=]\s*['\"]([^'\"]+)['\"]", html, re.I)
    if m:
        return m.group(1)
    m2 = re.search(r"//(\w+)\.disqus.com/embed.js", html, re.I)
    if m2:
        return m2.group(1)
    return None

def detect_facebook_comments(html):
    """Return True if facebook comments plugin found."""
    return "xfbml" in html or "facebook.com/plugins/comments.php" in html

# --- Orchestrator ---
def extract_article_and_comments(url, use_selenium=False):
    try:
        html = fetch_html(url, use_selenium=use_selenium)
    except Exception as e:
        return {"url": url, "error": str(e)}

    article = extract_article_text(html, url=url)
    comments = extract_comments_from_html(html, url)

    # try WordPress REST if no comments found
    if not comments:
        wp_comments = try_wordpress_comments(url)
        if wp_comments:
            comments = wp_comments

    # detect disqus / facebook
    disqus_short = detect_disqus(html)
    if disqus_short:
        # adding detection note. We don't call the Disqus API here (needs key)
        comments.insert(0, f"[Disqus thread detected: shortname={disqus_short}]")

    if detect_facebook_comments(html):
        comments.insert(0, "[Facebook Comments plugin detected on page]")

    # Final return
    return {
        "url": url,
        "title": article.get("title"),
        "text": article.get("text"),
        "comments": comments[:30],  
    }


if __name__ == "__main__":
    urls = [
        'https://www.wpbeginner.com/beginners-guide/how-to-choose-the-best-domain-registrar/',
        # ...
    ]
    results = []
    for u in urls:
        print("Scraping:", u)
        res = extract_article_and_comments(u, use_selenium=False)
        results.append(res)
        time.sleep(1.2)
    import json
    print(json.dumps(results, indent=2, ensure_ascii=False))