# skills

Agent skills for [Claude Code](https://claude.com/claude-code), packaged as a plugin.

## Skills

| Skill | What it does |
| --- | --- |
| [`pr-review`](skills/pr-review/SKILL.md) | Reviews a GitHub PR: summarizes it (context, problem, solution, and a map of the key modules it changes), finds issues, applies and tests each fix in a checkout of the PR, and delivers the fixes as paste-ready review comments or, after your approval, as PRs on the reviewed one: a GitHub stack with a summary comment, or a single PR when one is enough. It also checks the PR's existing review threads against the current head, and asks which delivery you want when the request does not say. Requires the [`gh` CLI](https://cli.github.com); the stack delivery also needs the `gh stack` extension (`gh extension install github/gh-stack`). |
| [`explain-code`](skills/explain-code/SKILL.md) | Explains a codebase, or one component of it, as HTML lessons pinned to a commit: an overview with a map and a glossary, then one lesson per critical flow that traces it frame by frame through the real source (functions, types, boundaries, asynchronous work), every frame linked to its lines. Each lesson ends in a multiple-choice quiz. A script checks every citation against the commit and a cold reader has to pass each quiz from the lesson alone. It also records leads for a later simplification review. Lessons are written to `~/code-explanations/` as a static site that can be uploaded as a directory to a host such as Netlify. Invoked by name only. The explained commit must be on a GitHub remote, because every citation is a GitHub permalink. Requires `python3`; the [`gh` CLI](https://cli.github.com) is used for PR and issue context when present. |

## Install

### As a plugin (recommended)

In Claude Code:

```
/plugin marketplace add sergerad/skills
/plugin install sergerad-skills@sergerad
```

Skills fire on their own when a request matches (for example, "review this PR: <url>"), and can be invoked by name under the plugin's prefix:

```
/sergerad-skills:pr-review https://github.com/<owner>/<repo>/pull/<n>
```

`explain-code` runs only when invoked by name:

```
/sergerad-skills:explain-code <repo path or GitHub URL> <what to explain>
```

Update later from a terminal, then run `/reload-plugins` in any open session:

```sh
claude plugin marketplace update sergerad
claude plugin update sergerad-skills@sergerad
```

### As a personal skill

Clone the repo and link the skills you want into `~/.claude/skills/`:

```sh
git clone https://github.com/sergerad/skills.git ~/Source/skills
ln -s ~/Source/skills/skills/pr-review ~/.claude/skills/pr-review
```

The skill fires on its own in the same way, and is invoked by name without a prefix:

```
/pr-review https://github.com/<owner>/<repo>/pull/<n>
```

To use a skill in one project only, link or copy it into that project's `.claude/skills/` instead.

## Layout

```
.claude-plugin/
  plugin.json         # the plugin manifest
  marketplace.json    # lets this repo be added as a plugin marketplace
skills/
  <skill-name>/
    SKILL.md          # the skill: frontmatter + instructions
    <OTHER>.md        # optional reference the skill points to, loaded only when needed
    assets/           # optional files the skill copies into its output
    scripts/          # optional scripts the skill runs
```

`pr-review` keeps its shared steps in `SKILL.md` and each delivery in its own file (`DELIVER-COMMENTS.md`, `DELIVER-STACK.md`).

`explain-code` keeps its steps in `SKILL.md` and the lesson markup in `LESSON-FORMAT.md`; `assets/` holds the stylesheet and quiz script every lesson links, and `scripts/lesson.py` checks the lessons it writes.

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md` with `name` and `description` frontmatter.
2. Add a row to the table above.
3. Bump `version` in `.claude-plugin/plugin.json`, commit and push; installed copies pick it up with the update commands above.
