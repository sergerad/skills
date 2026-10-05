# Delivering as review comments

The default delivery of [`pr-review`](SKILL.md): each change becomes a paste-ready comment for the PR's "Files changed" view, shown in the conversation as soon as it is verified. Nothing is pushed or posted.

## When to show a comment

Show a change's comment immediately after its gates pass and it is committed in the review worktree, then keep going with the next change; the user reads while the review continues.

Hold a comment back only when a later change may still alter its code: changes that touch each other are applied and tested together, then shown together. When every change cascades into the next, the whole set is shown at the end.

If a later change does alter code a shown comment proposed, show that comment again in full, marked `(revised)` on its anchor line.

**Snippets come from the worktree**: the code as it stands there (`git show` of the change's commit), trimmed to the changed items. They are copied from tested code, never written from memory. After the final gate run, every shown snippet must match the final state; re-show any that drifted.

## Comment format

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

## Finish

Before the first comment, give one line: the head SHA under review. After the last one, give the wrap-up from `SKILL.md`, then remove the review worktree (`git worktree remove --force`).
