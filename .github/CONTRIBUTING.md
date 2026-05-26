# Contributing

Thanks for taking a look. Before opening anything, a quick note on scope.

This repository exists to publish a set of LLM "skills" that help BNDRY customers and partners work with specific BNDRY features — things like form schemas and custom fields. The skills are maintained by the BNDRY team to support our product. They're shared publicly under MIT in case they're useful to others, but the canonical use case is BNDRY's own.

That means:

- The shape, scope, and direction of each skill is driven by what BNDRY needs.
- Issues and PRs are welcome, but changes outside the BNDRY use case may be declined.
- If a skill doesn't fit your needs, fork freely — the MIT licence is permissive on purpose.

## Reporting issues

Good issues are specific and reproducible. Please include:

- Which skill you used and what you asked it to do.
- The Claude (or other LLM) version and environment, if relevant.
- What you expected, and what actually happened — including the model's output where useful.
- A minimal reproduction if you have one.

For feature requests, describe the underlying problem first and the proposed change second. The problem is usually more useful than the solution.

## Security issues

Don't open a public issue for anything that looks like a vulnerability. See [SECURITY.md](SECURITY.md) for how to report it privately.

## Proposing changes

Before spending real time on a non-trivial change, open an issue to sketch the idea. That avoids both sides discovering at PR review that the change doesn't fit.

For small fixes (typos, broken links, clarifying a skill description, tightening a prompt), a PR is fine.

When you open a PR:

- Keep it focused on one skill or one concern.
- The description should say what changed and why.
- Include before/after examples if you've changed prompt behaviour.
- Update the skill's README or front-matter in the same PR.

By submitting a contribution you agree it can be released under the project's [MIT licence](../LICENSE).

## Style and quality

Skills here typically combine:

- A `SKILL.md` with name, description, and trigger guidance.
- Markdown reference material the skill loads on demand.
- Occasional helper scripts (Bash or Python).

Match the style of what's already there. A few specifics:

- Skill descriptions should be precise about when to trigger and when not to. Vague descriptions lead to misfires.
- Keep reference material focused. Long, rambling docs cost tokens and degrade skill performance.
- If a skill is BNDRY-specific (references our product, conventions, or internal tooling), say so plainly in the description.

## Commits and branches

- Write commit messages as commands: "Add X", "Fix Y".
- One logical change per commit where practical.
- Branch from `main`; branches are deleted on merge.

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Questions

If you're not sure whether something belongs here, open an issue and ask before writing. That's nearly always faster than guessing.
