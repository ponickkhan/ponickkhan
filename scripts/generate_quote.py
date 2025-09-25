# scripts/generate_quote.py
import time
import json
import random
import urllib.request
import urllib.error
import re
import html
from typing import Optional, Dict, Any

# Primary API (may be blocked in some environments; script has robust fallback)
URL_ENG = "https://dev-quote.42web.io"
UA = "Mozilla/5.0 (compatible; GitHubActionsBot/1.0; +https://github.com/ponickkhan)"

# Curated fallback quotes (used if API fails/blocks)
FALLBACK_QUOTES = [
    {"quote": "Programs must be written for people to read, and only incidentally for machines to execute.", "author": "Harold Abelson"},
    {"quote": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"},
    {"quote": "Simplicity is the soul of efficiency.", "author": "Austin Freeman"},
    {"quote": "Premature optimization is the root of all evil.", "author": "Donald Knuth"},
    {"quote": "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "author": "Martin Fowler"},
    {"quote": "First, solve the problem. Then, write the code.", "author": "John Johnson"},
    {"quote": "Experience is the name everyone gives to their mistakes.", "author": "Oscar Wilde"},
    {"quote": "Java is to JavaScript what car is to Carpet.", "author": "Chris Heilmann"},
    {"quote": "Code is like humor. When you have to explain it, it’s bad.", "author": "Cory House"},
    {"quote": "Fix the cause, not the symptom.", "author": "Steve Maguire"},
    {"quote": "Optimism is an occupational hazard of programming: feedback is the treatment.", "author": "Kent Beck"},
    {"quote": "Simplicity is prerequisite for reliability.", "author": "Edsger W. Dijkstra"},
    {"quote": "Before software can be reusable it first has to be usable.", "author": "Ralph Johnson"},
    {"quote": "The most disastrous thing that you can ever learn is your first programming language.", "author": "Alan Kay"},
    {"quote": "Controlling complexity is the essence of computer programming.", "author": "Brian Kernighan"},
    {"quote": "The best way to get a project done faster is to start sooner.", "author": "Jim Highsmith"},
    {"quote": "Programming isn’t about what you know; it’s about what you can figure out.", "author": "Chris Pine"},
    {"quote": "Deleted code is debugged code.", "author": "Jeff Sickel"},
    {"quote": "Testing leads to failure, and failure leads to understanding.", "author": "Burt Rutan"},
    {"quote": "Weeks of coding can save you hours of planning.", "author": "Unknown"},
    {"quote": "The best error message is the one that never shows up.", "author": "Thomas Fuchs"},
    {"quote": "The function of good software is to make the complex appear simple.", "author": "Grady Booch"},
    {"quote": "The best performance improvement is the transition from the nonworking state to the working state.", "author": "John Ousterhout"},
    {"quote": "Walking on water and developing software from a specification are easy if both are frozen.", "author": "Edward V. Berard"},
    {"quote": "Measuring programming progress by lines of code is like measuring aircraft building progress by weight.", "author": "Bill Gates"},
    {"quote": "One man’s crappy software is another man’s full-time job.", "author": "Jessica Gaston"},
    {"quote": "A language that doesn’t affect the way you think about programming is not worth knowing.", "author": "Alan Perlis"},
    {"quote": "If debugging is the process of removing bugs, then programming must be the process of putting them in.", "author": "Edsger W. Dijkstra"},
    {"quote": "Inside every large program, there is a small program trying to get out.", "author": "Tony Hoare"},
    {"quote": "Good code is its own best documentation.", "author": "Steve McConnell"},
    {"quote": "Any sufficiently advanced technology is indistinguishable from magic.", "author": "Arthur C. Clarke"},
    {"quote": "The trouble with programmers is that you can never tell what a programmer is doing until it’s too late.", "author": "Seymour Cray"},
    {"quote": "Good code is short, simple, and symmetrical – the challenge is figuring out how to get there.", "author": "Sean Parent"},
    {"quote": "The only way to learn a new programming language is by writing programs in it.", "author": "Dennis Ritchie"},
    {"quote": "Simplicity carried to the extreme becomes elegance.", "author": "Jon Franklin"},
    {"quote": "Debugging is like being the detective in a crime movie where you are also the murderer.", "author": "Filipe Fortes"},
    {"quote": "There are only two kinds of programming languages: those people always complain about and those nobody uses.", "author": "Bjarne Stroustrup"},
    {"quote": "Any problem in computer science can be solved with another layer of indirection. But that usually will create another problem.", "author": "David Wheeler"},
    {"quote": "Software is a gas; it expands to fill its container.", "author": "Nathan Myhrvold"},
    {"quote": "Without requirements or design, programming is the art of adding bugs to an empty text file.", "author": "Louis Srygley"},
    {"quote": "When in doubt, use brute force.", "author": "Ken Thompson"},
]

def fetch_json(url: str, max_retries: int = 5, base_delay: float = 2.0) -> Optional[Dict[str, Any]]:
    """
    Fetch JSON with a UA header and retry/backoff on 429/5xx/network errors.
    Returns parsed dict or None.
    """
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status == 200:
                    txt = r.read().decode("utf-8")
                    # Try standard JSON decode; if API returns single quotes/unquoted keys, normalize.
                    try:
                        return json.loads(txt)
                    except json.JSONDecodeError:
                        txt2 = re.sub(r"(?P<k>\b\w+\b):", r'"\g<k>":', txt)  # quote unquoted keys
                        txt2 = txt2.replace("'", '"')  # single -> double quotes
                        return json.loads(txt2)
                if r.status == 429 or 500 <= r.status < 600:
                    raise urllib.error.HTTPError(url, r.status, "retryable", r.headers, None)
                raise RuntimeError(f"Non-OK status: {r.status}")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            code = getattr(e, "code", None)
            if code == 429 or (code and 500 <= code < 600) or isinstance(e, urllib.error.URLError):
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.75)
                time.sleep(delay)
                continue
            # Non-retryable
            return None
    return None

def md_escape(s: str) -> str:
    """Minimal Markdown/HTML escape to avoid breaking README formatting."""
    return html.escape(s, quote=False)

def ensure_markers(readme: str) -> str:
    """
    Ensure README has the markers. If missing, append them once at the end.
    This makes the first run non-destructive.
    """
    if "<!--QUOTE_START-->" in readme and "<!--QUOTE_END-->" in readme:
        return readme
    return readme.rstrip() + "\n\n<!--QUOTE_START-->\n> “Stay curious.” — **Unknown**\n<!--QUOTE_END-->\n"

def main() -> None:
    # Try API, then fallback list
    data = fetch_json(URL_ENG)

    if data and isinstance(data, dict):
        # API schema: {"author": "...", "quote": "..."}
        quote = data.get("quote") or data.get("content") or "Keep learning; keep shipping."
        author = data.get("author") or data.get("by") or "Unknown"
    else:
        q = random.choice(FALLBACK_QUOTES)
        quote = q["quote"]
        author = q["author"]

    quote = md_escape(quote.strip())
    author = md_escape(author.strip())

    # Load README
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    # Ensure markers exist
    readme = ensure_markers(readme)

    # Build new block (the content BETWEEN markers)
    new_block = f'> “{quote}” — **{author}**'

    # Replace ONLY the content between markers, preserving the markers
    pattern = re.compile(r"(<!--QUOTE_START-->)(.*?)(<!--QUOTE_END-->)", flags=re.DOTALL)

    # Optional: Skip update if the quote hasn't changed (prevents noisy commits)
    current = pattern.search(readme)
    if current:
        current_quote = current.group(2).strip()
        if current_quote == new_block:
            return  # nothing to change

    updated = pattern.sub(lambda m: f"{m.group(1)}\n{new_block}\n{m.group(3)}", readme)

    if updated != readme:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(updated)

if __name__ == "__main__":
    main()
