---
name: pr-review-comments
description: Review a GitHub pull request and output ordered, paste-ready review comments with file/line anchors, source links and change snippets. Use when the user asks to review a PR, or gives a GitHub pull request URL or number to review.
---

# PR review comments

Produce one **coherent** review of a GitHub PR: an ordered set of paste-ready comments, each self-contained, with cascading changes merged into the one comment where they start. Every proposed change is **applied and tested** in a checkout of the PR before its comment is shown, and each comment is shown as soon as it is verified.

The argument is a PR URL or number.

## 1. Read the PR at its head commit

- `gh pr view <n> --json title,body,baseRefName,headRefOid,files` for the head SHA and base branch.
- `git fetch origin pull/<n>/head` and the base branch, then diff from their merge-base. Review `FETCH_HEAD`, whatever the local branch holds.
- Check the head out as a detached worktree in the scratchpad: `git worktree add --detach <scratch>/pr-<n> FETCH_HEAD`. This **review worktree** is where every proposed change gets applied; the user's own checkout stays untouched.
- Read every changed source file in full at the head SHA with line numbers (`git show <sha>:<path> | cat -n`). Lockfiles: skim only what the manifests changed.
- Read the repo's `CLAUDE.md` and any memory on review conventions; they are review criteria.

Done when every changed non-lockfile file has been read at the head SHA and the review worktree exists.

## 2. Find and verify

Look for correctness and security bugs first, then operability (timeouts, retries, error messages an operator will read, logging), simplification (redundant calls, unreachable code, speculative generality), and departures from the repo's conventions.

Every suspicion is checked against a source before it becomes a finding: the code path itself, the dependency's source at the locked version (`~/.cargo/registry/src/`), `cargo tree`, the base branch's lockfile. A suspicion that fails its check is dropped silently. Keep track of what was checked by reading and what was run.

Done when each finding has a named piece of evidence behind it.

## 3. Arrange into one coherent series

- **Merge cascades:** findings that touch the same code, or where one change forces or reshapes another, become a single comment. A removed flag, the config struct it simplifies, the call site that follows and the tests that change with it are one comment with one combined snippet set showing the end state.
- **Anchor a merged comment** at the first, most relevant line: where the root cause sits. The other locations it touches are linked from its body.
- **Keep independent findings separate:** two comments stay apart only when either could be applied without the other.
- **Order:** bugs first, then by importance, nits last.

Done when no two comments edit the same code and every finding from step 2 lives in exactly one comment.

## 4. Apply, test, then show — one comment at a time

Work through the comments in order. For each one:

1. **Apply** its change in the review worktree, on top of the changes already applied for earlier comments. Include everything the change forces: call sites, tests, docs.
2. **Test** it with the repo's own gates, as its `CLAUDE.md`, CI workflow or `justfile` define them: build, the tests of the crates touched, formatting, lints. Start the first build early; it is the slow part. A change that cannot be made to pass is reworked, or its finding is dropped or restated as a question with the failure quoted.
3. **Take the snippets from the worktree**: the code as it now stands there (`git diff` for the comment's files), trimmed to the changed items. Snippets are copied from tested code, never written from memory.
4. **Show the comment immediately**, in the step 5 format, as soon as its gates pass. Keep going with the next comment; the user reads while the review continues.

Hold a comment back only when a later one may still change its code: comments whose changes touch each other are applied and tested together, then shown together. When every comment cascades into the next, the whole set is shown at the end.

If a later change does alter code a shown comment proposed, show that comment again in full, marked `(revised)` on its anchor line, with snippets from the current worktree.

After the last comment, run the full gates once over the worktree with every change applied. That final state is what the review recommends, and every shown snippet must match it; re-show any that drifted. Then remove the worktree (`git worktree remove`). Nothing is committed, pushed or posted to the PR.

Done when every comment has been shown with snippets identical to the final worktree state, and the full gates passed on that state.

## 5. Comment format

Each comment is:

1. An **anchor line** outside the block: its position in the order, the file path, and the line or line range to attach the comment to in "Files changed". The anchor is a line the PR adds or changes. The position number lives only here; it is lost when the comment is posted.
2. The **comment body** in a four-backtick `markdown` fence, so it copies as raw markdown:
   - A **title** on the first line: bold, a few words naming the change, unnumbered (`**Drop the single-value provider flag**`). Titles are unique within the review.
   - A short paragraph stating the problem and its consequence. The comment sits on its anchor, so the body refers to the anchored code in words ("this flag", "the call here") and links only the *other* locations it mentions, each labelled by its lines: `[L28–L36](https://github.com/<owner>/<repo>/blob/<head-sha>/<path>#L28-L36)`. A link into a different file than the anchor names that file: `[tests.rs L93–L106](…)`.
   - A `**Fix:**` sentence saying what to change, across every location the comment covers.
   - A reference to another comment, when one is needed, quotes that comment's title ("see *Drop the single-value provider flag*"), since titles are all a PR reader can see of the order.
   - **Change snippets**: the replacement code in fenced blocks (`rust`, `toml`), or a `diff` block when the change is mostly deletion. A merged comment has one snippet per location, each opening with a `// <file or item>` line, and together they show the final state.

Template:

`````
**3. `path/to/file.rs` — lines 102–111**

````markdown
**<Short title of the change>**

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

- Every line number against the file at the head SHA (the PR's own lines, before any proposed change).
- The body has no link to its own anchor range.
- The body opens with its title and names other comments by title only.
- The snippet matches the surrounding code's naming, error style and comment style.

## 6. Wrap up

Before the first comment, give one line: the head SHA under review. After the last one:

1. The verdict: blockers or none.
2. What ran: the gate commands and their results on the final worktree state.
3. Caveats: findings left as questions because their change could not be tested (for example, one that needs live credentials or a running service), and anything the author must confirm.
