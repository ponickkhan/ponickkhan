# scripts/generate_quote.py
import time, json, random, urllib.request, urllib.error, re, html

URL_ENG = "https://programming-quotesapi.vercel.app/api/random"  # new API
UA = "Mozilla/5.0 (compatible; GitHubActionsBot/1.0; +https://github.com/ponickkhan)"

FALLBACK_QUOTES = [
    {"quote": "Programs must be written for people to read, and only incidentally for machines to execute.", "author": "Harold Abelson"},
    {"quote": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"},
    {"quote": "Simplicity is the soul of efficiency.", "author": "Austin Freeman"},
    {"quote": "Premature optimization is the root of all evil.", "author": "Donald Knuth"},
    {"quote": "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "author": "Martin Fowler"},
    {"quote": "First, solve the problem. Then, write the code.", "author": "John Johnson"},
    {"quote": "Experience is the name everyone gives to their mistakes.", "author": "Oscar Wilde"},
    {"quote": "In order to be irreplaceable, one must always be different.", "author": "Coco Chanel"},
    {"quote": "Java is to JavaScript what car is to Carpet.", "author": "Chris Heilmann"},
    {"quote": "Knowledge is power.", "author": "Francis Bacon"},
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
    {"quote": "Programming is the art of telling another human being what one wants the computer to do.", "author": "Donald Knuth"},
    {"quote": "A language that doesn’t affect the way you think about programming is not worth knowing.", "author": "Alan Perlis"},
    {"quote": "If debugging is the process of removing bugs, then programming must be the process of putting them in.", "author": "Edsger W. Dijkstra"},
    {"quote": "The sooner you start to code, the longer the program will take.", "author": "Roy Carlson"},
    {"quote": "The cheapest, fastest, and most reliable components are those that aren’t there.", "author": "Gordon Bell"},
    {"quote": "Programs are meant to be read by humans and only incidentally for computers to execute.", "author": "Donald Knuth"},
    {"quote": "Inside every large program, there is a small program trying to get out.", "author": "Tony Hoare"},
    {"quote": "A good programmer is someone who always looks both ways before crossing a one-way street.", "author": "Doug Linder"},
    {"quote": "Programming is like writing a book... except if you miss out a single comma on page 126 the whole thing makes no sense.", "author": "Unknown"},
    {"quote": "You can’t have great software without a great team, and most software teams behave like dysfunctional families.", "author": "Jim McCarthy"},
    {"quote": "Good code is its own best documentation.", "author": "Steve McConnell"},
    {"quote": "Any sufficiently advanced technology is indistinguishable from magic.", "author": "Arthur C. Clarke"},
    {"quote": "The trouble with programmers is that you can never tell what a programmer is doing until it’s too late.", "author": "Seymour Cray"},
    {"quote": "Good code is short, simple, and symmetrical – the challenge is figuring out how to get there.", "author": "Sean Parent"},
    {"quote": "The computer was born to solve problems that did not exist before.", "author": "Bill Gates"},
    {"quote": "A computer once beat me at chess, but it was no match for me at kickboxing.", "author": "Emo Philips"},
    {"quote": "Programming languages, like pizzas, come in only two sizes: too small and too big.", "author": "Richard Pattis"},
    {"quote": "The only way to learn a new programming language is by writing programs in it.", "author": "Dennis Ritchie"},
    {"quote": "Simplicity carried to the extreme becomes elegance.", "author": "Jon Franklin"},
    {"quote": "Debugging is like being the detective in a crime movie where you are also the murderer.", "author": "Filipe Fortes"},
    {"quote": "The computing scientist’s main challenge is not to get confused by the complexities of his own making.", "author": "Edsger W. Dijkstra"},
    {"quote": "There are only two kinds of programming languages: those people always complain about and those nobody uses.", "author": "Bjarne Stroustrup"},
    {"quote": "The question of whether a computer can think is no more interesting than the question of whether a submarine can swim.", "author": "Edsger W. Dijkstra"},
    {"quote": "Any problem in computer science can be solved with another layer of indirection. But that usually will create another problem.", "author": "David Wheeler"},
    {"quote": "Software is a gas; it expands to fill its container.", "author": "Nathan Myhrvold"},
    {"quote": "Without requirements or design, programming is the art of adding bugs to an empty text file.", "author": "Louis Srygley"},
    {"quote": "The best programmers are not marginally better than merely good ones. They are an order-of-magnitude better, measured by whatever standard: conceptual creativity, speed, ingenuity of design, or problem-solving ability.", "author": "Randall E. Stross"},
    {"quote": "The proper use of comments is to compensate for our failure to express ourself in code.", "author": "Robert C. Martin"},
    {"quote": "The best way to predict the future is to invent it.", "author": "Alan Kay"},
    {"quote": "If you think your users are idiots, only idiots will use it.", "author": "Linus Torvalds"},
    {"quote": "Controlling complexity is the essence of computer programming.", "author": "Brian Kernighan"},
    {"quote": "Machines take me by surprise with great frequency.", "author": "Alan Turing"},
    {"quote": "Computer science education cannot make anybody an expert programmer any more than studying brushes and pigment can make somebody an expert painter.", "author": "Eric S. Raymond"},
    {"quote": "Computers are good at following instructions, but not at reading your mind.", "author": "Donald Knuth"},
    {"quote": "When in doubt, use brute force.", "author": "Ken Thompson"},
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
        rf"\n{new_block}\n",
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
