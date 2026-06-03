# BNDRY Skills

Public repository of reusable AI agent skills for the BNDRY platform, published under the MIT licence.

Skills follow the [Agent Skills](https://agentskills.io) open standard and work with Claude Code, Cursor, ChatGPT, Gemini, Amp, and other compatible AI tools.

## Available Skills

| Directory | Purpose |
|-----------|---------|
| `skills/bndry-custom-fields-schema/` | Generate and audit `CustomFieldSchema` JSON for BNDRY entities |
| `skills/bndry-formkit-schema/` | Build, edit, and audit FormKit JSON schemas for BNDRY forms |

## Skill Structure

Each skill directory contains:

```
SKILL.md         # Required — YAML frontmatter + instructions
references/      # Supporting docs loaded on demand
templates/       # Starter files / examples
```

## CI

Three workflows run on push/PR to `main`:

- **markdownlint** — validates all Markdown files
- **shellcheck** — lints any shell scripts
- **CodeQL** — security analysis

All three must pass before merging. Run `markdownlint` locally before pushing:

```
markdownlint '**/*.md'
```

## Adding or Updating a Skill

1. Create or update the skill directory under `skills/<skill-name>/`.
2. Verify `markdownlint` passes locally before pushing.

## Public Repo Rules

This is a public repo under MIT licence:

- No internal BNDRY URLs, API keys, or customer data.
- Australian English in all user-facing text (skill instructions, README, docs).

## Commit Conventions

Conventional commits.
