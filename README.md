# BNDRY Skills

LLM skills that help users work with specific BNDRY product features.

## Contents

- [About](#about)
- [Available skills](#available-skills)
- [Using a skill](#using-a-skill)
  - [The free path — paste into any chat](#the-free-path--paste-into-any-chat)
  - [Save setup time with a paid plan](#save-setup-time-with-a-paid-plan)
    - [Claude.ai (Pro, Max, or Team)](#claudeai-pro-max-or-team)
    - [ChatGPT (Plus, Team, or Enterprise)](#chatgpt-plus-team-or-enterprise)
    - [Gemini (Google AI Pro or Advanced)](#gemini-google-ai-pro-or-advanced)
  - [Claude Code](#claude-code)
  - [API or SDK](#api-or-sdk)
  - [Other tools](#other-tools)
- [Licence](#licence)

## About

Each skill in this repository is a directory containing a `SKILL.md` plus reference material and templates. The `SKILL.md` tells the model how to approach a specific task — what rules to follow, what to check, what to produce.

The format is plain markdown and JSON. It originated with Anthropic's [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) specification but is fully portable — these skills work with any LLM that can follow instructions, including ChatGPT, Claude, Gemini, Copilot, and others. Nothing here is Claude-specific.

The skills are maintained by the BNDRY team to help customers and partners work with specific BNDRY product features.

## Available skills

| Skill | What it does |
| --- | --- |
| [`bndry-formkit-schema`](skills/bndry-formkit-schema) | Builds, edits, and audits FormKit JSON schemas for BNDRY forms. Covers multi-step form structure, expressions, conditional fields, validation, and the BNDRY rendering theme. |
| [`bndry-custom-fields-schema`](skills/bndry-custom-fields-schema) | Generates and audits `CustomFieldSchema` JSON for extending BNDRY entities (Individual, Company, Trust) with custom fields. Bundles the full field-type and validation-rule reference. |

Each skill directory has the same shape:

- `SKILL.md` — the skill's instructions to the LLM
- `references/` — supporting documentation the skill loads on demand
- `templates/` — example structures to adapt
- `scripts/` — deterministic helpers the skill runs instead of eyeballing (where present)

## Using a skill

The skills work with any LLM. The [free path](#the-free-path--paste-into-any-chat) below works on free tiers of ChatGPT, Claude.ai, Gemini, and others — no paid subscription required. If you'll be using a skill regularly, [save setup time with a paid plan](#save-setup-time-with-a-paid-plan) lets you load the skill once instead of pasting it into every chat.

### The free path — paste into any chat

Works in any chat-based LLM with no setup and no paid subscription.

1. Open the skill's `SKILL.md` on GitHub and copy its full contents.
2. In your AI chat of choice (ChatGPT free, Claude.ai free, Gemini, etc.), start a new conversation and paste, prefixed with: *"Follow the instructions in this skill for the rest of the conversation:"*
3. If the skill references files under `references/` or `templates/`, copy and paste those too — or attach them if your chat supports file uploads.
4. Describe what you want.

> **Heads-up on context limits:** the FormKit skill is long (~66KB). Free tiers with smaller context windows may truncate the paste. Workarounds: split the paste across two messages, or use one of the paid options below.

### Save setup time with a paid plan

If you'll use a skill regularly, load it once into your paid AI account instead of pasting it into every chat. Pick whichever AI you already pay for.

#### Claude.ai (Pro, Max, or Team)

Claude.ai natively supports the Agent Skills format. Upload the skill directly:

1. Zip the skill directory, keeping the folder name in the archive root:

   ```bash
   cd skills && zip -r bndry-formkit-schema.zip bndry-formkit-schema/
   ```

2. In Claude.ai, open **Settings → Capabilities → Skills**.
3. Click *Upload skill* and select the zip.
4. The skill activates automatically when your message matches its description.

#### ChatGPT (Plus, Team, or Enterprise)

If your plan includes native Skills support, upload the skill directly:

1. Zip the skill directory (same `zip -r` command as above).
2. In ChatGPT, open **Settings → Skills** (rollout varies by plan; if you don't see it, use the custom GPT path below).
3. Upload the zip.

**Alternative — custom GPT (available on every paid ChatGPT plan):**

1. *Create a GPT* → paste `SKILL.md` into the **Instructions** field.
2. Upload everything under `references/` and `templates/` as **Knowledge** files.
3. Save. The GPT behaves as the skill on every invocation.

#### Gemini (Google AI Pro or Advanced)

Create a Gem:

1. *Create a Gem* → paste `SKILL.md` into the **instructions**.
2. Attach the `references/` and `templates/` files.
3. Save and chat with the Gem to invoke the skill.

### Claude Code

Free for individuals; Anthropic API usage is billed separately.

```bash
git clone https://github.com/bndry-co/BNDRY-Skills.git
cp -R BNDRY-Skills/skills/bndry-formkit-schema ~/.claude/skills/
```

Restart Claude Code. The skill activates automatically when the conversation matches its description (e.g. *"Generate a BNDRY custom field schema for source of funds"*).

### API or SDK

For programmatic use (Anthropic, OpenAI, Google, or any other provider's API), load `SKILL.md` into your system prompt and attach the reference files to the conversation context. The Agent Skills format is documented in the [Agent Skills overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) — the same pattern applies regardless of provider.

### Other tools

Any tool that consumes Agent Skills format — Amp, Cursor with skill support, custom agents — can use these skills directly without modification.

> **Tip:** every option works best when the model has access to both `SKILL.md` *and* the bundled reference material. The `SKILL.md` often instructs the model to consult those files before producing output, so leaving them out will degrade results.

## Licence

[MIT](LICENSE). Fork, adapt, and reuse freely.
