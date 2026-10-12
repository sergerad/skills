---
name: explain-code
description: Explain a codebase, or one component of it, as HTML lessons that trace its critical flows through the real source at a pinned commit, each ending in a quiz.
disable-model-invocation: true
argument-hint: "<repo path or GitHub URL> [what to explain]"
---

# Explain code

Teach the user how a codebase works, its design **and** its implementation, as a set of HTML **lessons**. Each lesson follows one **flow** through the real source as a **trace**: the ordered **frames** (the functions, methods and procedures the flow runs through), the types it moves and the boundaries it crosses, every one linked to its lines at a pinned commit. Each lesson ends in a multiple-choice quiz that can be answered from the lesson.

The arguments are a repo (a local path or a GitHub URL; the current directory when none is given) and what to explain (a component, a behaviour, a question; the whole project when nothing is said).

The reader is a senior engineer who is new to this repo and its domain. A hint in the request ("I know Rust, not MASM") moves that line.

## 1. Pin the source

Everything the lessons say is about one commit.

- Resolve the repo and its commit: `HEAD` for a local path, the default branch's head for a URL (clone it into the scratchpad).
- Fix the **link base**: `https://github.com/<owner>/<repo>/blob/<full sha>/`, taken from the repo's GitHub remote. Every citation is a GitHub permalink, so that remote must contain the commit (`git fetch`, then `git branch -r --contains <sha>`). When the repo has no GitHub remote, or the commit is not on it yet, stop here and tell the user which of the two it is.
- Read from a tree that matches that commit: the repo itself when its tree is clean, otherwise a detached worktree in the scratchpad (`git worktree add --detach <scratch>/<name> <sha>`). A dirty tree is named in the lessons' header as left out.
- Create the output directory: `~/code-explanations/<owner>-<repo>/<scope-slug>-<short-sha>/`, or the path the user gave. Lessons are written only there; the explained repo stays untouched.

Done when the full SHA, the tree to read from, the link base and the output directory are fixed.

## 2. Survey

Learn the whole project at the breadth of a **map** before going deep anywhere, whatever the scope: a component is explained by where it sits.

- In the repo: the README, docs, ADRs, `CLAUDE.md` / `AGENTS.md`, the manifests (members, dependencies and their locked versions), the directory layout, and the entry points (binaries, commands, handlers, exported API, on-chain procedures, scheduled jobs). Test names are a cheap list of the behaviours the authors cared about.
- Around the repo, as far as it pays for the scope: the PRs and issues behind the design (`gh`), the specs and protocol docs the repo points to, and a dependency's source at its locked version where the scope leans on it.

Done when every top-level module (crate, package, service) has a one-line responsibility, and every entry point inside the scope is listed with its location.

## 3. Choose the flows and plan the lessons

A **flow** is one thing the system does, from its **entry point** (what starts it) to its **effect** (the state written, the message sent, the value returned).

Choose the flows that carry the scope, in this order:

1. What the user asked about.
2. What the scope exists to do: the flows that move value, change durable state, or cross a trust boundary.
3. What those depend on (startup, sync, configuration), when the others cannot be understood without it.

Then plan the lessons. The amount of material decides how many there are:

- One flow per lesson. A lesson is one sitting: about fifteen frames at most. A longer flow splits where it crosses a boundary.
- Machinery that three or more flows run through gets its own lesson, placed before them, and those lessons link to it.
- A scope with a single short flow is one page: the overview and the trace together in `index.html`.

Tell the user the plan in a few lines, one per lesson as `entry point → effect`, and go straight on to step 4. A correction from the user is taken when it arrives.

Done when every flow has an entry point and an effect located in the code, and every module of the scope on the map is either on a flow or listed as left out, with the reason.

## 4. Trace

For each flow, walk from the entry point to the effect, reading the body of every frame in full at the pinned commit. Record as you go:

- **Frames**: each function, method or procedure where the flow decides, transforms or hands on. A wrapper that only forwards folds into the frame it wraps, and becomes a lead.
- **Types**: the structs, enums, traits, messages, tables and storage slots the flow builds, carries or writes, with the frame that builds each and the frames that consume it.
- **Boundaries**: every change of context: process, package, language, network, storage, thread or task, sync to async, off-chain to on-chain. For each, the exact shape of the data that crosses and the mechanism that carries it (call, channel, queue, RPC, spawn, note).
- **Asynchronous work**: what is spawned and what is awaited, what runs concurrently, what orders or retries it, and what state is left behind when it fails halfway.
- **Why**: the reason behind each design choice the flow shows. A reason found in a doc, ADR, PR, commit message or comment is cited; a reason you worked out yourself is recorded as an **inference**.
- **Leads**: whatever looks heavier than the flow needs (indirection that carries nothing, a second path to the same effect, a layer the data passes through unchanged, state that is written and never read). A lead is an observation with a location; judging it belongs to a later review.

Follow dynamic dispatch to the implementation that runs in this flow (the trait object's concrete type, the registered handler, the generated code) and trace that.

Done when the trace is **unbroken**: every frame is reached from the one before it by a line you can point to (a call, a send matched with its receive, a registration matched with its dispatch), all the way from the entry point to the effect.

## 5. Write the lessons

Read [`LESSON-FORMAT.md`](LESSON-FORMAT.md) and follow it: the files, the page structure, the citation and quiz markup, and the shared assets to copy in.

Fix the glossary before the first lesson is written; every lesson uses its terms.

Done when `index.html` and every planned lesson exist, and each frame, type and boundary recorded in step 4 appears in a lesson.

## 6. Verify

1. **Citations.** Run `python3 <this skill's directory>/scripts/lesson.py check <output-dir> <repo>`. It checks every citation against the pinned commit (the file, the line range, the named symbol inside that range, the link), every internal link, and every quiz's shape. Fix a failure by reading the code again and correcting the lesson.
2. **Cold reader.** For each lesson, run `python3 <this skill's directory>/scripts/lesson.py blind <lesson.html>` and hand its output, and nothing else, to a fresh sub-agent. It answers each question with the frame it relied on, or says the lesson does not tell it. Compare with the answer key. A miss means a gap in the lesson or a flaw in the question: fix whichever it is, and run the cold reader again on that lesson.

Done when `check` exits 0 and the cold reader answers every question of every lesson correctly.

## 7. Hand over

Open `index.html` for the user (`open` on macOS, `xdg-open` on Linux), then tell them:

- where the lessons are, the commit they describe, and the lessons in reading order;
- that the directory is a static site they can upload as it stands, for Netlify with `netlify deploy --dir <output-dir> --prod`, and that uploading publishes the lessons and their code excerpts;
- what the verification covered, and anything in the lessons that rests on inference;
- how many leads were recorded, and that they are unverified starting points for a simplification review;
- that they can ask about anything unclear, or have a narrower scope explained in another run.

Remove any worktree or clone made in step 1.
