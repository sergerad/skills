# Delivering as PRs

One of the two deliveries of [`pr-review`](SKILL.md): each change becomes a PR stacked on the reviewed PR, and one short comment on the reviewed PR indexes the stack. A review with one change is a single PR and no stack. This pushes branches and posts on someone else's work, so the user signs off twice: on the **plan**, before any code is written, and on the **finished stack**, before anything is published.

## 1. Shape the stack

- One PR per substantive change, in review order, the most important at the bottom so the author can take it without the rest.
- All nits go together in one last PR at the top.
- A finding that is a question, or whose change could not be tested, gets no PR; it goes in the summary comment.
- **One PR is not a stack.** When the review's changes fit in a single PR, deliver that one PR on the reviewed PR's head branch and skip everything stack-specific: no `gh stack` check, no linking. The two sign-offs still apply. Post the summary comment only when there are questions or notes for the author beyond the PR; the PR's own "follow-up to #<n>" line already links it from the reviewed PR.

## 2. Get the plan signed off

Before applying anything (step 5 of `SKILL.md`), show the user the planned stack and stop. For each planned PR, in order:

- its working title;
- the problem, in a sentence or two, with links to the lines at the reviewed head SHA;
- the intended change: which files it touches and the approach, in plain words, without code;
- what it depends on or might disturb: the open PRs based on the reviewed PR's head branch, found in step 1 of `SKILL.md`.

Then list the findings that get no PR and why.

Take the user's answer as the plan: drop, merge, reorder or reshape PRs as they say, and show the plan again if it changed materially. Write code only for a plan the user has signed off in the conversation. If applying a change later shows the plan was wrong (the fix needs a different shape, or a finding does not reproduce), say so and get the changed part signed off again.

## 3. Build it locally

Once step 5 of `SKILL.md` has applied and tested the signed-off changes, each one is a commit in the review worktree, each on top of the last. Give every commit its branch:

```sh
git branch review/pr-<n>/<nn>-<slug> <commit>
```

Commit messages, like the PR texts below, follow the repo's and the user's rules for format, signing and attribution (`CLAUDE.md`, the user's memory). Reword with `git commit --amend` or an autosquash rebase before branching if they do not.

## 4. Draft the text

For each PR:

- **Title:** the change in the repo's commit style.
- **Description**, under the headings the repo's or the user's PR convention gives, or these when there is none:
  - *Context*: what is wrong and its consequence, linking the lines at the reviewed head SHA (`https://github.com/<owner>/<repo>/blob/<head-sha>/<path>#L28-L36`) and the review comment it follows up, if any.
  - *Changes*: what the PR does, including the call sites and tests it carries.
  - *Testing*: the gate commands run and their results, and any evidence gathered (a reproduced failure, a new test).
  - A closing line: "Stacked on #<n>" for the first, "Stacked on <previous PR>" for the rest ("Follow-up to #<n>" for a single PR), what the author must confirm, and which open PRs it will conflict with.

For the reviewed PR, one **summary comment**, short enough to read in a glance (with a single PR, only when there are questions or notes to carry):

```markdown
Review of <short head SHA>: <verdict in one sentence>. Proposed changes, stacked on this PR in order:

1. #<pr> **<title>** — <one sentence>. ([file L24](<link>))
2. #<pr> **<title>** — <one sentence>. ([file L339](<link>))

Questions and notes:
- <question the author must answer, or a finding that got no PR>
```

Every link in these texts is one you fetched: a line link checked against the head SHA, a comment URL from the thread list, a PR number from `gh`. A link you cannot look up is left out and the thing is named in words.

## 5. Get the stack signed off

Show the user the finished stack: the branches in order with their diffstats, each PR's title and description, and the summary comment. Then stop. Publishing happens only after the user approves this in the conversation; the plan sign-off, or any earlier or general go-ahead, does not cover it.

## 6. Publish as a GitHub stack

The PRs are linked into a real GitHub stack with the `gh stack` extension, so GitHub shows them as one stack and can rebase and merge them in order. Chained base branches alone are not a stack.

With a single PR, do only steps 2, 3, 5 (when a comment is due) and 6.

1. Check the extension is there: `gh extension list` shows `github/gh-stack`. If it is missing, stop and ask the user to run `gh extension install github/gh-stack`.
2. Confirm the reviewed PR's head is still the SHA you reviewed; if it moved, stop and tell the user. Then push the branches to the repository that holds the reviewed PR's head branch (a PR's base must live there). Without push access, stop and say so.
3. Open the PRs bottom-up with the signed-off titles and descriptions: the first with `gh pr create --base <reviewed PR's head branch> --head <branch 1> --title … --body-file …`, each later one with `--base <previous branch>`. (`gh stack submit --auto` would open them as drafts with generated titles, so the PRs are created directly.)
4. Link them, bottom to top: `gh stack link --base <reviewed PR's head branch> <pr 1> <pr 2> …`. It prints the stack number.
5. Fill the real PR numbers into the summary comment and post it with `gh pr comment <n>`.
6. Report the stack number, the PR URLs and the comment URL, then give the wrap-up from `SKILL.md`.

A GitHub stack is a single line of PRs. The review stack is its own stack whose bottom targets the reviewed PR's branch; it does not join a stack the reviewed PR already belongs to.

Tell the user the stack goes stale when the reviewed PR gets new commits: it then needs `gh stack rebase` and `gh stack push`, or a manual rebase bottom-up.

Remove the review worktree once the PRs are open; the branches keep the commits.
