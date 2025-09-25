# scripts/generate_quote.py
import time, json, random, urllib.request, urllib.error, re, html

URL_ENG = "https://programming-quotesapi.vercel.app/api/random"  # new API
UA = "Mozilla/5.0 (compatible; GitHubActionsBot/1.0; +https://github.com/ponickkhan)"

FALLBACK_QUOTES = [
    {"quote": "Programs must be written for people to read.", "author": "Harold Abelson"},
    {"quote": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"},
    {"quote": "Simplicity is the soul of efficiency.", "author": "Austin Freeman"},
    {"quote": "Premature optimization is the root of all evil.", "author": "Donald Knuth"},
]

def fetch_json(url, max_retries=5, base_delay=2.0):
    """Fetch JSON with simple UA and retry/backoff on 429/5xx/network errors."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status == 200:
                    txt = r.read().decode("utf-8")
                    # Some APIs may return single quotes; try to normalize if needed
                    try:
                        return json.loads(txt)
                    except json.JSONDecodeError:
                        # Try a naive fix for single-quoted pseudo-JSON
                        txt2 = re.sub(r"(?P<k>\\b\\w+\\b):", r'"\\g<k>":', txt)  # unquoted keys -> quoted
                        txt2 = txt2.replace("'", '"')
                        return json.loads(txt2)
                if r.status == 429 or 500 <= r.status < 600:
                    raise urllib.error.HTTPError(url, r.status, "retryable", r.headers, None)
                raise RuntimeError(f"Non-OK status: {r.status}")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            # Retry for 429/5xx/URLError; otherwise bubble up
            code = getattr(e, "code", None)
            if code == 429 or (code and 500 <= code < 600) or isinstance(e, urllib.error.URLError):
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.75)
                time.sleep(delay)
                continue
            raise
    return None

def md_escape(s: str) -> str:
    """Minimal Markdown escape to avoid breaking the README formatting."""
    # Use HTML escaping to be safe with symbols; keep it simple for blockquote usage
    return html.escape(s, quote=False)

def ensure_markers(readme: str) -> str:
    """Ensure README has the markers; if missing, append them at the end."""
    if "<!--QUOTE_START-->" in readme and "<!--QUOTE_END-->" in readme:
        return readme
    return readme.rstrip() + "\n\n<!--QUOTE_START-->\n> “Stay curious.” — **Unknown**\n<!--QUOTE_END-->\n"

def main():
    data = fetch_json(URL_ENG)

    if data and isinstance(data, dict):
        # API returns: {"author": "...", "quote": "..."}
        quote = data.get("quote") or data.get("content") or "Keep learning; keep shipping."
        author = data.get("author") or data.get("by") or "Unknown"
    else:
        q = random.choice(FALLBACK_QUOTES)
        quote = q["quote"]
        author = q["author"]

    quote = md_escape(quote.strip())
    author = md_escape(author.strip())

    # Update README
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    readme = ensure_markers(readme)

    new_block = f'> “{quote}” — **{author}**'
    updated = re.sub(
        r"(<!--QUOTE_START-->)(.*?)(<!--QUOTE_END-->)",
        rf"\\1\n{new_block}\n\\3",
        readme,
        flags=re.DOTALL,
    )

    if updated != readme:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(updated)
    else:
        # Nothing changed; avoid noisy commits
        pass

if __name__ == "__main__":
    main()
