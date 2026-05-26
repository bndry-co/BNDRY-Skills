---
name: Bug report
about: A skill in this repo isn't behaving the way it should
title: ''
labels: bug
assignees: ''

---

> Before filing: please confirm you're running against the latest version of the skill on `main`. For anything that looks like a security issue (e.g. prompt-injection, data leakage via a skill), **don't open a public issue** — report it privately per [SECURITY.md](../SECURITY.md).

## Which skill

The name of the skill (e.g. `bndry-formkit-schema`, `bndry-custom-fields-schema`) and roughly which part of it (description trigger, reference doc, helper script).

## Environment

- LLM/runtime (e.g. `Claude Code 1.x`, `Claude API`, `Cursor`, `Amp`):
- Model (e.g. `claude-opus-4-7`, `claude-sonnet-4-6`):
- BNDRY feature being worked on (e.g. FormKit schema, custom fields on Individual):
- Anything else relevant:

## What you asked the skill to do

The prompt or task you gave the LLM. Paste it verbatim where possible, redacting anything sensitive.

```
<paste prompt here>
```

## What you expected

A short, specific description.

## What actually happened

Include the **model's output** (or the relevant portion). Use a code block. Redact tenant IDs, customer data, and anything sensitive.

```
<paste output here>
```

## Minimal reproduction

The shortest prompt/sequence that reliably triggers the bug. If you've already worked around it, describe the workaround — it often points at the root cause.

## Additional context

Anything else that might matter: recent skill changes, related output, links to relevant lines in the skill.
