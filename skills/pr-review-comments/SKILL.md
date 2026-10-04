---
name: pr-review-comments
description: Review a GitHub pull request and output ordered, paste-ready review comments with file/line anchors, source links and change snippets. Use when the user asks to review a PR, or gives a GitHub pull request URL or number to review.
---

# PR review comments

Produce one **coherent** review of a GitHub PR: an ordered series of paste-ready comments that read as a single patch series, where each comment assumes the ones before it were applied.

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

- **Order:** bugs first, then by importance, nits last. A comment that others build on moves ahead of them.
- **Build forward:** a later comment's prose and snippet use the types, names and signatures that earlier comments introduced, and say so ("with the `KmsKeyArn` from comment 2").
- **Resolve overlap:** when two findings touch the same code, either merge them into one comment or make the later one start from the earlier one's result. When one finding deletes code another edits, the deletion goes first and the edit is retargeted at what remains.

Done when the snippets, applied in order as a patch series, each apply to the result of the previous ones, and the last one leaves the code in the state the whole review recommends.

## 4. Write each comment

Number the comments. Each one is:

1. An **anchor line** outside the block: the file path and the line or line range to attach the comment to in "Files changed". The anchor is a line the PR adds or changes.
2. The **comment body** in a four-backtick `markdown` fence, so it copies as raw markdown:
   - A short paragraph stating the problem and its consequence, with every code reference as an inline link labelled by its lines: `[L28–L36](https://github.com/<owner>/<repo>/blob/<head-sha>/<path>#L28-L36)`. Links to another file name it: `[tests.rs L93–L106](…)`.
   - A `**Fix:**` sentence saying what to change.
   - A **change snippet**: the replacement code in a fenced block (`rust`, `toml`), or a `diff` block when the change is mostly deletion.

Template:

`````
**3. `path/to/file.rs` — lines 102–111**

````markdown
<Problem and consequence, with [L102–L111](https://github.com/<owner>/<repo>/blob/<head-sha>/path/to/file.rs#L102-L111) links.>

**Fix:** <what to change, referring to earlier comments where it builds on them.>

```rust
<replacement code>
```
````
`````

Before finishing each comment, check:

- Every line number against the file at the head SHA.
- Every API a snippet calls exists at the locked dependency version.
- The snippet matches the surrounding code's naming, error style and comment style.

## 5. Output

1. One line: the head SHA reviewed and the verdict (blockers or none).
2. The numbered comments.
3. Caveats: what was read versus run, snippets that were not compiled, and anything the author must confirm.
