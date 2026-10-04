---
name: pr-review-comments
description: Review a GitHub pull request and output ordered, paste-ready review comments with file/line anchors, source links and change snippets. Use when the user asks to review a PR, or gives a GitHub pull request URL or number to review.
---

# PR review comments

Produce one **coherent** review of a GitHub PR: an ordered set of paste-ready comments, each self-contained, with cascading changes merged into the one comment where they start.

The argument is a PR URL or number.

## 1. Read the PR at its head commit

- `gh pr view <n> --json title,body,baseRefName,headRefOid,files` for the head SHA and base branch.
- `git fetch origin pull/<n>/head` and the base branch, then diff from their merge-base. Review `FETCH_HEAD`, whatever the local branch holds.
- Read every changed source file in full at the head SHA with line numbers (`git show <sha>:<path> | cat -n`). Lockfiles: skim only what the manifests changed.
- Read the repo's `CLAUDE.md` and any memory on review conventions; they are review criteria.

Done when every changed non-lockfile file has been read at the head SHA.

## 2. Find and verify

Look for correctness and security bugs first, then operability (timeouts, retries, error messages an operator will read, logging), simplification (redundant calls, unreachable code, speculative generality), and departures from the repo's conventions.

Every suspicion is checked against a source before it becomes a finding: the code path itself, the dependency's source at the locked version (`~/.cargo/registry/src/`), `cargo tree`, the base branch's lockfile. A suspicion that fails its check is dropped silently. Keep track of what was checked by reading and what was run.

Done when each finding has a named piece of evidence behind it.

## 3. Arrange into one coherent series

- **Merge cascades:** findings that touch the same code, or where one change forces or reshapes another, become a single comment. A removed flag, the config struct it simplifies, the call site that follows and the tests that change with it are one comment with one combined snippet set showing the end state.
- **Anchor a merged comment** at the first, most relevant line: where the root cause sits. The other locations it touches are linked from its body.
- **Keep independent findings separate:** two comments stay apart only when either could be applied without the other.
- **Order:** bugs first, then by importance, nits last.

Done when no two comments edit the same code, no comment's snippet depends on another comment being applied, and every finding from step 2 lives in exactly one comment.

## 4. Write each comment

Number the comments. Each one is:

1. An **anchor line** outside the block: the file path and the line or line range to attach the comment to in "Files changed". The anchor is a line the PR adds or changes.
2. The **comment body** in a four-backtick `markdown` fence, so it copies as raw markdown:
   - A short paragraph stating the problem and its consequence. The comment sits on its anchor, so the body refers to the anchored code in words ("this flag", "the call here") and links only the *other* locations it mentions, each labelled by its lines: `[L28–L36](https://github.com/<owner>/<repo>/blob/<head-sha>/<path>#L28-L36)`. A link into a different file than the anchor names that file: `[tests.rs L93–L106](…)`.
   - A `**Fix:**` sentence saying what to change, across every location the comment covers.
   - **Change snippets**: the replacement code in fenced blocks (`rust`, `toml`), or a `diff` block when the change is mostly deletion. A merged comment has one snippet per location, each opening with a `// <file or item>` line, and together they show the final state.

Template:

`````
**3. `path/to/file.rs` — lines 102–111**

````markdown
<Problem and consequence of the anchored code, in words. Other places it reaches: [L161–L167](https://github.com/<owner>/<repo>/blob/<head-sha>/path/to/file.rs#L161-L167), [main.rs L65–L69](https://github.com/<owner>/<repo>/blob/<head-sha>/path/to/main.rs#L65-L69).>

**Fix:** <what to change, here and at the linked locations.>

```rust
// file.rs
<replacement code>
```

```rust
// main.rs
<replacement code>
```
````
`````

Before finishing each comment, check:

- Every line number against the file at the head SHA.
- The body has no link to its own anchor range.
- Every API a snippet calls exists at the locked dependency version.
- The snippet matches the surrounding code's naming, error style and comment style.

## 5. Output

1. One line: the head SHA reviewed and the verdict (blockers or none).
2. The numbered comments.
3. Caveats: what was read versus run, snippets that were not compiled, and anything the author must confirm.
