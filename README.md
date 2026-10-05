# skills

Agent skills for [Claude Code](https://claude.com/claude-code), packaged as a plugin.

## Skills

| Skill | What it does |
| --- | --- |
| [`pr-review`](skills/pr-review/SKILL.md) | Reviews a GitHub PR: summarizes it (context, problem, solution, and a map of the key modules it changes), finds issues, applies and tests each fix in a checkout of the PR, and delivers the fixes as paste-ready review comments or, after your approval, as PRs on the reviewed one: a GitHub stack with a summary comment, or a single PR when one is enough. It also checks the PR's existing review threads against the current head, and asks which delivery you want when the request does not say. Requires the [`gh` CLI](https://cli.github.com); the stack delivery also needs the `gh stack` extension (`gh extension install github/gh-stack`). |

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
```

`pr-review` keeps its shared steps in `SKILL.md` and each delivery in its own file (`DELIVER-COMMENTS.md`, `DELIVER-STACK.md`).

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md` with `name` and `description` frontmatter.
2. Add a row to the table above.
3. Bump `version` in `.claude-plugin/plugin.json`, commit and push; installed copies pick it up with the update commands above.
