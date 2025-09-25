# scripts/generate_quote.py
import time, json, random, urllib.request, urllib.error

URL_ENG = "https://api.quotable.io/random?tags=technology|famous-quotes"  # example API; adjust to what you use
UA = "Mozilla/5.0 (compatible; GitHubActionsBot/1.0; +https://github.com/ponickkhan)"

FALLBACK_QUOTES = [
    {"content": "Programs must be written for people to read.", "author": "Harold Abelson"},
    {"content": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"},
    {"content": "Simplicity is the soul of efficiency.", "author": "Austin Freeman"},
    {"content": "Premature optimization is the root of all evil.", "author": "Donald Knuth"},
]

def fetch_json(url, max_retries=5, base_delay=2.0):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status == 200:
                    return json.loads(r.read().decode("utf-8"))
                # treat all non-200 as transient except 4xx (but retry 429)
                if r.status == 429 or 500 <= r.status < 600:
                    raise urllib.error.HTTPError(url, r.status, "retryable", r.headers, None)
                raise RuntimeError(f"Non-OK status: {r.status}")
        except urllib.error.HTTPError as e:
            if e.code == 429 or 500 <= e.code < 600:
                # exponential backoff with jitter
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                time.sleep(delay)
                continue
            raise
        except urllib.error.URLError:
            delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
            time.sleep(delay)
            continue
    return None

def main():
    data = fetch_json(URL_ENG)
    if not data:
        # fallback to local quotes if API unavailable
        q = random.choice(FALLBACK_QUOTES)
        quote = q["content"]
        author = q["author"]
    else:
        # adapt to your API schema
        quote = data.get("content") or data.get("quote") or "Keep learning; keep shipping."
        author = data.get("author") or data.get("by") or "Unknown"

    # --- update README.md (example) ---
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    # Replace a marker block in README
    import re
    new_block = f'> “{quote}” — **{author}**'
    readme = re.sub(
        r"(<!--QUOTE_START-->)(.*?)(<!--QUOTE_END-->)",
        rf"\1\n{new_block}\n\3",
        readme,
        flags=re.DOTALL,
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
