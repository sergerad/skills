# Lesson format

How [`explain-code`](SKILL.md) writes its output: the files, the two page types, and the markup that `scripts/lesson.py` checks.

## Files

```
<output-dir>/
  index.html            # the overview: summary, map, glossary, lesson list, sources, leads
  01-<flow-slug>.html   # one lesson per flow, numbered in reading order
  02-<flow-slug>.html
  assets/
    lesson.css          # copied from this skill's assets/
    quiz.js             # copied from this skill's assets/
```

Copy `assets/` from this skill's directory as it is.

The output directory is a complete **static site**, uploaded as it stands to a host such as Netlify. `index.html` sits at its root, every link between its files is relative, file names are lowercase (hosts are case-sensitive where macOS is not), a page needs nothing from the network, and the directory holds only the files above: working files stay in the scratchpad.

Every page starts from this skeleton:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="explain-code:sha" content="<full 40-character sha>">
  <title><page title> · <repo></title>
  <link rel="stylesheet" href="assets/lesson.css">
  <script defer src="assets/quiz.js"></script>
</head>
<body>
  <header class="page-header">
    <p class="crumbs"><a href="index.html"><repo></a> · <scope></p>
    <h1><page title></h1>
    <p class="pin"><owner>/<repo> at <code><short sha></code>, <date>. <"Uncommitted changes in the working tree are left out." when there were any></p>
    <lesson nav>
  </header>
  <main> … </main>
</body>
</html>
```

The **lesson nav** links a page to its neighbours in reading order, which runs from the overview through the lessons. The overview has only the `next` link, to the first lesson; the first lesson's `prev` link is the overview (`← Overview`); the last lesson has only the `prev` link. A scope written as one page has no nav:

```html
<nav class="lesson-nav">
  <a rel="prev" href="01-<flow-slug>.html">← <previous lesson's title></a>
  <a rel="next" href="03-<flow-slug>.html"><next lesson's title> →</a>
</nav>
```

## Writing

- Plain prose for a senior engineer who is new to this repo. Explain what is particular to this codebase and its domain; leave general programming knowledge unsaid.
- Use the glossary's term for a thing every time, and the code's own identifiers in `<code>`.
- Every claim about behaviour rests on a citation. Every claim about *why* is either cited to its source or wrapped in `<span class="inferred">…</span>`, which the stylesheet labels as an inference.
- Design and implementation stay together: a design point is made at the frame that implements it.

## Citations

A citation is a link to code at the pinned commit, and the only way a lesson refers to code:

```html
<a class="src" data-path="crates/relayer/src/submit.rs" data-lines="88-131"
   data-symbol="Relayer::submit_mint"
   href="https://github.com/<owner>/<repo>/blob/<full sha>/crates/relayer/src/submit.rs#L88-L131"
   target="_blank" rel="noopener">submit.rs L88–L131</a>
```

- `data-path` is relative to the repo root; `data-lines` is `N` or `N-M`, the lines of the item at the pinned commit.
- `data-symbol` names what the range holds. Its last segment (`submit_mint`) must appear inside the range. Every frame and type citation carries one; a citation of a bare statement may leave it out.
- `href` is the link base followed by the path and the lines: the GitHub permalink above (`#L88` for a single line).
- `target="_blank"` opens the source in a new tab, so the reader keeps their place in the lesson.
- The visible text is the file name and the lines. Give the fuller path when two files in the lesson share a name.
- A citation into a dependency's source links to that dependency's repo at its locked version, takes `class="src ext"`, drops the `data-` attributes, and keeps `target="_blank"`.

## `index.html`

In this order:

1. **Summary**: what the scope does and how, in three paragraphs at most: the problem it solves, the shape of the solution, and the one idea a reader must hold to follow the rest.
2. **Map**: the scope as a table that follows its directory and module hierarchy down from the repo root, so the reader sees where every file sits. One row per directory and per module file, in tree order, in the markup below. Within a directory the root of the module tree (`lib.rs`, `mod.rs`, `__init__.py`, `index.ts`) comes first and its row says which modules it declares and which of them are public; the modules follow in the order it declares them. A directory of the wider project appears only as a neighbour the scope talks to, as a single row. Neighbours outside the repo (dependencies, services) follow in a second table.
3. **Glossary**: a `<dl class="glossary">` of the domain and codebase terms the lessons use. One or two sentences each, saying what the thing is, with a citation where the term is a type.
4. **Lessons**: an ordered list. Each entry links to the lesson and gives its flow as `entry point → effect` in a line.
5. **Left out**: the modules and flows of the scope the lessons do not cover, with the reason, so the reader knows the edge of what they learned.
6. **Sources**: the material outside the code that the lessons draw on (docs, ADRs, PRs, issues, specs), each a link with a line on what it supplied.
7. **Leads for a simplification review**: a `<ul class="leads">`, one item per lead: a citation and one sentence on what looks heavier than the flow needs. The section opens by saying the leads are unverified observations made while tracing.

When the whole scope is one short flow, the lesson's sections follow the glossary in `index.html` and there is no lesson list.

### Map markup

```html
<table class="map">
  <thead><tr><th>Path</th><th>Responsible for</th><th>Lessons</th></tr></thead>
  <tbody>
    <tr class="dir"><td class="path" style="--depth: 0"><code>crates/</code></td><td></td><td></td></tr>
    <tr class="dir"><td class="path" style="--depth: 1"><code>relayer/</code></td><td>The scope: the deposit relayer, a library and its binary.</td><td></td></tr>
    <tr class="dir"><td class="path" style="--depth: 2"><code>src/</code></td><td></td><td></td></tr>
    <tr><td class="path" style="--depth: 3"><a class="src" …>lib.rs</a></td><td>The crate root: declares the modules below; <code>submit</code> is public.</td><td></td></tr>
    <tr><td class="path" style="--depth: 3"><a class="src" …>submit.rs</a></td><td>Builds and submits mint notes.</td><td>2, 3</td></tr>
  </tbody>
</table>
```

- `--depth` is the row's depth below the repo root; the stylesheet indents the first cell by it.
- A directory row (`<tr class="dir">`) names the directory with a trailing `/`, and says what it holds when that is not plain from its rows.
- A module row cites the module's root file. Here alone a citation shows only the file name, since the tree gives the rest of its path.

## A lesson page

In this order:

1. **The flow**: one paragraph. What starts it, what it ends in, and the path between in a sentence. Then the frames as a one-line chain of identifiers (`a → b → c`), so the reader sees the whole trace before its parts.
2. **Types**: the types this flow moves, as a `<dl class="types">`. Each `<dt>` is the type's name as a citation; each `<dd>` says what it represents, the fields the flow depends on, which frame builds it and which consume it.
3. **Trace**: the frames and boundaries in execution order, in the markup below. A diagram is added, as inline SVG, when three or more actors exchange messages and the order between them is the point.
4. **Why it is built this way**: the design choices the trace showed, each tied to its frame (`<a href="#frame-4">frame 4</a>`), with the alternative it rules out and the reason, cited or marked as an inference.
5. **Quiz**: in the markup below.
6. **Footer**: a `<footer class="page-footer">` holding the lesson nav again, so the reader can move on from the top of the page or the bottom, then a link to the overview and a line telling the reader to ask the agent about anything unclear.

### Trace markup

```html
<ol class="trace">
  <li class="frame" id="frame-1">
    <h3><code>Relayer::submit_mint</code> <a class="src" …>submit.rs L88–L131</a></h3>
    <dl>
      <dt>Receives</dt><dd>…the arguments and state it is handed, by type…</dd>
      <dt>Does</dt><dd>…what it decides, checks or transforms, and what makes it fail…</dd>
      <dt>Hands on</dt><dd>…what it returns, sends or writes, and to which frame…</dd>
      <dt>Runs in</dt><dd>…the task, thread, process or transaction, when that differs from the frame before…</dd>
    </dl>
    <pre><code>…the few lines that are the point of the frame…</code></pre>
  </li>
  <li class="boundary">
    <strong>Task → RPC</strong> The signed transaction crosses as <code>ProvenTransaction</code> bytes over gRPC; the task awaits the reply, and a timeout leaves the deposit marked pending.
  </li>
  <li class="frame" id="frame-2"> … </li>
</ol>
```

- Frames are numbered by their `id`, `frame-1` upward, in the order they run.
- An excerpt is included when the code itself teaches something the prose cannot: a non-obvious check, an ordering, a lock. It is copied from the pinned commit and kept under fifteen lines.
- A boundary names the two contexts, the shape that crosses, the mechanism, and for asynchronous work what waits on what and what is left behind on failure.
- Where the flow forks (an error path, a retry, a branch by variant), the frame says which branch the trace follows and gives the other a sentence and a citation.

### Quiz markup

```html
<section class="quiz">
  <h2>Quiz</h2>
  <p class="score" aria-live="polite"></p>
  <article class="question" data-answer="c">
    <p class="prompt">A deposit attestation arrives whose nonce is already in the faucet's map. Where does the mint stop?</p>
    <ol class="options">
      <li data-option="a">The relayer drops it before building the note</li>
      <li data-option="b">The node rejects the transaction at the mempool</li>
      <li data-option="c">The faucet's mint procedure fails its nonce assertion</li>
      <li data-option="d">The note script refuses to run on consumption</li>
    </ol>
    <p class="explanation">The relayer does not track nonces; the check is the map lookup in <a href="#frame-6">frame 6</a>.</p>
  </article>
</section>
```

- Five to eight questions a lesson, four options each, one correct.
- A question asks about this codebase: which frame decides something, what crosses a boundary, what happens when a step fails or is removed, why a check sits where it does. A reader who knows the domain but skipped the lesson should have to guess.
- Mix the two aims in every quiz: questions on the design (why) and questions on the implementation (where and how).
- The wrong options are what a reader who skimmed would believe: the neighbouring frame, the plausible layer, the design the code did not choose.
- The options of a question are alike in form and within two words of each other in length, so the format gives nothing away. `quiz.js` shuffles them on load.
- The explanation says why the answer is right and links to the frame that proves it.
