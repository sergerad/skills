# skills

Agent skills for [Claude Code](https://claude.com/claude-code), packaged as a plugin.

## Skills

| Skill | What it does |
| --- | --- |
| [`pr-review-comments`](skills/pr-review-comments/SKILL.md) | Reviews a GitHub PR and outputs an ordered series of paste-ready review comments, each with its file/line anchor, links to the source lines and a change snippet that was applied and tested in a checkout of the PR. Requires the [`gh` CLI](https://cli.github.com). |

## Install

### As a plugin (recommended)

In Claude Code:

```
/plugin marketplace add sergerad/skills
/plugin install sergerad-skills@sergerad
```

Skills fire on their own when a request matches (for example, "review this PR: <url>"), and can be invoked by name under the plugin's prefix:

```
/sergerad-skills:pr-review-comments https://github.com/<owner>/<repo>/pull/<n>
```

Update later with `/plugin marketplace update sergerad`.

### As a personal skill

Clone the repo and link the skills you want into `~/.claude/skills/`:

```sh
git clone https://github.com/sergerad/skills.git ~/Source/skills
ln -s ~/Source/skills/skills/pr-review-comments ~/.claude/skills/pr-review-comments
```

The skill fires on its own in the same way, and is invoked by name without a prefix:

```
/pr-review-comments https://github.com/<owner>/<repo>/pull/<n>
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
```

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md` with `name` and `description` frontmatter.
2. Add a row to the table above.
3. Bump `version` in `.claude-plugin/plugin.json`.
