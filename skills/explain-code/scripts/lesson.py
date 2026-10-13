#!/usr/bin/env python3
"""Checks for the lessons that the explain-code skill writes.

    lesson.py check <output-dir> <repo>   verify citations, links, lesson nav and quizzes against the pinned commit
    lesson.py blind <lesson.html>         print a lesson with its quiz answers and explanations removed
    lesson.py key <lesson.html>           print the answer key, one "<question number>: <option>" per line

`check` exits 1 and lists every problem when a lesson does not hold up.
"""

import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "wbr"}
SHA_META = "explain-code:sha"
ASSETS = ("assets/lesson.css", "assets/quiz.js", "assets/highlight.js")
QUESTIONS_PER_LESSON = range(5, 9)
OPTIONS_PER_QUESTION = 4
MAX_OPTION_WORD_SPREAD = 2


class Page(HTMLParser):
    """Collects what `check` needs from one page: ids, links, citations, frames and questions."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.sha = None
        self.header_nav = {}
        self.same_tab = []
        self.types = []
        self.plain_code = []
        self.tree = {}
        self.tree_lists = 0
        self.ids = set()
        self.links = []
        self.citations = []
        self.frames = []
        self.questions = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        if tag == "meta" and attrs.get("name") == SHA_META:
            self.sha = attrs.get("content")
        if "id" in attrs:
            self.ids.add(attrs["id"])

        if "frame" in classes:
            depth = re.search(r"--depth:\s*(\d+)", attrs.get("style") or "")
            self.frames.append(
                {"id": attrs.get("id"), "symbols": 0, "depth": int(depth[1]) if depth else None, "code": 0}
            )
        elif "question" in classes:
            self.questions.append(
                {"answer": attrs.get("data-answer"), "options": [], "explained": False, "proof": False}
            )
        elif tag == "li" and "data-option" in attrs and self.questions:
            self.questions[-1]["options"].append({"key": attrs["data-option"], "text": ""})
        elif "explanation" in classes and self.questions:
            self.questions[-1]["explained"] = tag

        if self._inside("types"):
            if tag == "dt":
                self.types.append({"line": self.getpos()[0], "named": False})
            elif tag == "code" and self.types and any(open_tag == "dt" for open_tag, _, _ in self.stack):
                self.types[-1]["named"] = True

        if tag == "ul" and ("calltree" in classes or self.tree_lists):
            self.tree_lists += 1
        if tag == "code" and self.stack and self.stack[-1][0] == "pre":
            if not any(name.startswith("language-") for name in classes):
                self.plain_code.append(self.getpos()[0])
            if self._inside("frame"):
                self.frames[-1]["code"] += 1

        if tag in ("link", "script") and (attrs.get("href") or attrs.get("src")):
            self.links.append({"href": attrs.get("href") or attrs.get("src"), "line": self.getpos()[0]})

        if tag == "a":
            href = attrs.get("href") or ""
            line = self.getpos()[0]
            if "src" in classes and attrs.get("target") != "_blank":
                self.same_tab.append(line)
            if "src" in classes and "ext" not in classes:
                self.citations.append({"attrs": attrs, "line": line})
                if attrs.get("data-symbol") and self._inside("frame"):
                    self.frames[-1]["symbols"] += 1
            else:
                self.links.append({"href": href, "line": line})
            if self.tree_lists:
                self.tree.setdefault(href, self.tree_lists - 1)
            if attrs.get("rel") in ("prev", "next") and self._inside("page-header"):
                self.header_nav[attrs["rel"]] = href
            if self._inside("explanation") and self.questions:
                self.questions[-1]["proof"] = True

        if tag not in VOID:
            self.stack.append((tag, classes, "data-option" in attrs))

    def handle_endtag(self, tag):
        if tag == "ul" and self.tree_lists:
            self.tree_lists -= 1
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self.questions and self.questions[-1]["options"] and any(option for _, _, option in self.stack):
            self.questions[-1]["options"][-1]["text"] += data

    def _inside(self, cls):
        return any(cls in classes for _, classes, _ in self.stack)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def last_segment(symbol):
    names = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", re.sub(r"<.*>", "", symbol))
    return names[-1] if names else symbol


def check_citation(citation, sha, repo, sources):
    """Return the problems with one citation, as a list of strings."""
    attrs = citation["attrs"]
    path, lines, symbol, href = (attrs.get(k) for k in ("data-path", "data-lines", "data-symbol", "href"))
    if not path or not lines:
        return ["citation needs data-path and data-lines"]
    match = re.fullmatch(r"(\d+)(?:-(\d+))?", lines)
    if not match:
        return [f'{path}: data-lines "{lines}" is not N or N-M']
    first, last = int(match[1]), int(match[2] or match[1])

    if path not in sources:
        shown = git(repo, "show", f"{sha}:{path}")
        sources[path] = shown.stdout.splitlines() if shown.returncode == 0 else None
    source = sources[path]
    if source is None:
        return [f"{path}: no such file at {sha[:12]}"]

    problems = []
    if not 1 <= first <= last <= len(source):
        return [f"{path}: lines {lines} are outside the file ({len(source)} lines)"]
    if symbol and last_segment(symbol) not in "\n".join(source[first - 1 : last]):
        problems.append(f'{path}: "{last_segment(symbol)}" (from {symbol}) is not in lines {lines}')

    href = href or ""
    anchor = f"#L{first}" if first == last else f"#L{first}-L{last}"
    if not href.startswith("https://github.com/"):
        problems.append(f"{path}: href is not a GitHub permalink")
    elif not href.endswith(f"/blob/{sha}/{path}{anchor}"):
        problems.append(f"{path}: href should end with /blob/{sha}/{path}{anchor}")
    return problems


def check_link(link, page_name, pages, site_files):
    href = link["href"]
    if not href or re.match(r"[a-z][a-z0-9+.-]*:", href):
        return []
    target, _, fragment = href.partition("#")
    target = target or page_name
    if target.startswith("/"):
        return [f"link to {target} must be relative, so the site works from any URL"]
    if target not in pages:
        # Compared with the names on disk exactly: a static host is case-sensitive where macOS is not.
        return [] if target in site_files else [f"link to missing file {target}"]
    if fragment and fragment not in pages[target].ids:
        return [f"link to missing anchor {target}#{fragment}"]
    return []


def check_quiz(page):
    problems = []
    if page.frames and len(page.questions) not in QUESTIONS_PER_LESSON:
        problems.append(
            f"{len(page.questions)} questions; a lesson has "
            f"{QUESTIONS_PER_LESSON.start} to {QUESTIONS_PER_LESSON.stop - 1}"
        )
    for number, question in enumerate(page.questions, 1):
        keys = [option["key"] for option in question["options"]]
        if len(keys) != OPTIONS_PER_QUESTION or len(set(keys)) != len(keys):
            problems.append(f"question {number}: needs {OPTIONS_PER_QUESTION} options with distinct data-option values")
        if question["answer"] not in keys:
            problems.append(f"question {number}: data-answer does not name one of its options")
        counts = [len(option["text"].split()) for option in question["options"]]
        if counts and max(counts) - min(counts) > MAX_OPTION_WORD_SPREAD:
            problems.append(f"question {number}: options run from {min(counts)} to {max(counts)} words")
        if not question["explained"]:
            problems.append(f"question {number}: no explanation")
        elif question["explained"] != "p":
            problems.append(f'question {number}: the explanation must be a <p class="explanation">')
        elif not question["proof"]:
            problems.append(f"question {number}: the explanation links to no frame or citation")
    return problems


def check_frames(page):
    problems = []
    for number, frame in enumerate(page.frames, 1):
        if frame["id"] != f"frame-{number}":
            problems.append(f'frame {number} has id "{frame["id"]}", expected "frame-{number}"')
        if not frame["symbols"]:
            problems.append(f"frame {number} has no citation with a data-symbol")
        if not frame["code"]:
            problems.append(f"frame {number} has no code block for its signature")
        in_tree = page.tree.get(f"#frame-{number}")
        if in_tree is None:
            problems.append(f"frame {number} is not linked from the call tree")
        elif frame["depth"] != in_tree:
            problems.append(f"frame {number} has --depth {frame['depth']}; the call tree puts it at {in_tree}")
    problems += [f'line {line}: a code block needs class="language-…"' for line in page.plain_code]
    return problems


def check(out_dir, repo):
    out_dir, repo = Path(out_dir).expanduser(), Path(repo).expanduser()
    files = sorted(out_dir.glob("*.html"))
    if not files:
        sys.exit(f"no .html files in {out_dir}")

    pages = {}
    for file in files:
        page = Page()
        page.feed(file.read_text(encoding="utf-8"))
        pages[file.name] = page

    site_files = {
        path.relative_to(out_dir).as_posix()
        for path in out_dir.rglob("*")
        if path.is_file() and not path.name.startswith(".")
    }
    problems = [f"missing {asset}" for asset in ASSETS if asset not in site_files]
    if "index.html" not in pages:
        problems.append("missing index.html")
    for name in sorted(site_files - set(pages) - set(ASSETS)):
        problems.append(f"{name} is not part of the site; keep working files out of the output directory")
    problems += [f"{name}: file names are lowercase" for name in sorted(site_files) if name != name.lower()]

    shas = {page.sha for page in pages.values()}
    sha = next(iter(shas)) if len(shas) == 1 else None
    if sha is None or not re.fullmatch(r"[0-9a-f]{40}", sha):
        problems.append(f'every page needs the same full sha in <meta name="{SHA_META}">; found {sorted(map(str, shas))}')
        sha = None
    elif git(repo, "cat-file", "-e", f"{sha}^{{commit}}").returncode != 0:
        problems.append(f"{repo} has no commit {sha}")
        sha = None

    sources = {}
    citations = 0
    for name, page in pages.items():
        found = check_frames(page) + check_quiz(page)
        found += [f'line {line}: a source link needs target="_blank"' for line in page.same_tab]
        found += [f"line {t['line']}: a type's <dt> names the type in <code>" for t in page.types if not t["named"]]
        for link in page.links:
            found += [f"line {link['line']}: {p}" for p in check_link(link, name, pages, site_files)]
        if sha:
            for citation in page.citations:
                citations += 1
                found += [f"line {citation['line']}: {p}" for p in check_citation(citation, sha, repo, sources)]
        problems += [f"{name}: {p}" for p in found]

    lessons = sorted(name for name, page in pages.items() if page.frames and name != "index.html")
    reading_order = [name for name in ["index.html", *lessons] if name in pages]
    for name, following in zip(reading_order, reading_order[1:]):
        if pages[name].header_nav.get("next") != following:
            problems.append(f'{name}: the page header needs <a rel="next" href="{following}">')
        if pages[following].header_nav.get("prev") != name:
            problems.append(f'{following}: the page header needs <a rel="prev" href="{name}">')

    if not any(page.frames for page in pages.values()):
        problems.append("no page has a trace")

    if problems:
        print("\n".join(problems))
        sys.exit(1)
    frames = sum(len(page.frames) for page in pages.values())
    questions = sum(len(page.questions) for page in pages.values())
    print(f"ok: {len(pages)} pages, {frames} frames, {citations} citations, {questions} questions at {sha[:12]}")


def blind(lesson):
    html = Path(lesson).expanduser().read_text(encoding="utf-8")
    html = re.sub(r'\sdata-answer="[^"]*"', "", html)
    html = re.sub(r'<p class="explanation"[^>]*>.*?</p>\s*', "", html, flags=re.DOTALL)
    sys.stdout.write(html)


def key(lesson):
    page = Page()
    page.feed(Path(lesson).expanduser().read_text(encoding="utf-8"))
    for number, question in enumerate(page.questions, 1):
        print(f"{number}: {question['answer']}")


def main():
    commands = {"check": (check, 2), "blind": (blind, 1), "key": (key, 1)}
    args = sys.argv[1:]
    if not args or args[0] not in commands or len(args) - 1 != commands[args[0]][1]:
        sys.exit(__doc__)
    commands[args[0]][0](*args[1:])


if __name__ == "__main__":
    main()
