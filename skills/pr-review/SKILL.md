---
name: pr-review
description: Review a GitHub pull request by finding issues and applying and testing each fix in a checkout, then deliver the fixes as paste-ready review comments or as a stack of PRs on the reviewed one. Use when the user asks to review a PR, or gives a GitHub pull request URL or number to review.
---

# PR review

Produce one **coherent** review of a GitHub PR: an ordered set of **changes**, each self-contained, with cascading findings merged into the one change where they start. Every change is **applied and tested** in a checkout of the PR before it is delivered.

The argument is a PR URL or number.

## Delivery

The changes reach the author in one of two ways:

- **Review comments**: paste-ready comments shown in the conversation. Read [`DELIVER-COMMENTS.md`](DELIVER-COMMENTS.md).
- **Stack of PRs**: one PR per change on top of the reviewed PR, linked as a GitHub stack, plus one summary comment. When one PR holds all the changes, it is a single PR and no stack is made. The user signs off the planned PRs before step 4. Read [`DELIVER-STACK.md`](DELIVER-STACK.md).

The user's request decides which. "Comments", "review comments" or "what should I comment" means comments; "a stack", "PRs" or "open PRs for the fixes" means the stack. When the request names neither, as in a bare "review this PR", ask once, as soon as step 3 is done: list the arranged changes by title in a line each, then ask which delivery they want, calling the second option "a PR" when there is only one change. Reading and finding (steps 1 to 3) never wait on the answer.

Read the chosen delivery file before any code is written, and follow it from there.

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

- **Merge cascades:** findings that touch the same code, or where one fix forces or reshapes another, become a single change. A removed flag, the config struct it simplifies, the call site that follows and the tests that move with it are one change.
- **Keep independent findings separate:** two changes stay apart only when either could be applied without the other.
- **Order:** bugs first, then by importance, nits last.

Done when no two changes edit the same code and every finding from step 2 lives in exactly one change.

## 4. Apply, test, deliver — one change at a time

Work through the changes in order. For each one:

1. **Apply** it in the review worktree, on top of the changes before it. Include everything it forces: call sites, tests, docs.
2. **Test** it with the repo's own gates, as its `CLAUDE.md`, CI workflow or `justfile` define them: build, the tests of the crates touched, formatting, lints. Start the first build early; it is the slow part. Reproduce a claimed bug before fixing it when that is cheap. A change that cannot be made to pass is reworked, or its finding is dropped or restated as a question with the failure quoted.
3. **Commit** it locally in the review worktree: one commit per change. Local commits stay in the worktree; nothing is pushed here.
4. **Deliver** it as the delivery file says.

After the last change, run the full gates once over the worktree with every change applied. That final state is what the review recommends.

Done when every change is committed, delivered, and the full gates passed on the final state.

## 5. Wrap up

1. The verdict: blockers or none.
2. What ran: the gate commands and their results on the final worktree state, and what testing changed about the findings.
3. Caveats: findings left as questions because their change could not be tested (for example, one that needs live credentials or a running service), and anything the author must confirm.
