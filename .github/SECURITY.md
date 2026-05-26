# Security Policy

This repository publishes LLM "skills" — prompts, instructions, and small helper scripts — that help users work with specific BNDRY product features. It is maintained by the BNDRY team.

## Supported Versions

There are no formal releases. The latest commit on `main` is the only version that receives security fixes. If you're using an older snapshot, pull the latest before reporting.

| Version       | Supported          |
| ------------- | ------------------ |
| `main` (HEAD) | :white_check_mark: |
| Anything else | :x:                |

## Reporting a Vulnerability

If you've found a security issue, please **do not open a public issue**. Report it privately through one of these channels:

- **Preferred:** GitHub's private vulnerability reporting — use the *Report a vulnerability* button under the **Security** tab of this repo.
- **Backup:** email security@bndry.net.

Include enough detail to reproduce: which skill, what input or prompt triggered it, expected vs. actual behaviour, and the impact you think it has. A proof-of-concept is great but not required.

### What to expect

- **Acknowledgement:** within 5 business days.
- **Initial triage:** within 14 days — we'll let you know whether we're treating it as a vulnerability, a regular bug, or something we won't fix, and why.
- **Fix or decision:** depends on severity and complexity. Critical issues get prioritised; low-severity issues may end up as documented limitations.
- **Disclosure:** once a fix is merged (or we've decided not to fix), we're happy to credit you in the commit message or release notes if you'd like. Please don't publicly disclose before then.

### Scope

In scope:

- Skill instructions or prompts that could be manipulated to exfiltrate data, leak secrets, or produce harmful output when used as documented.
- Helper scripts that ship with skills in this repo.
- Documentation that, if followed, would cause a user to do something insecure.

Out of scope:

- Vulnerabilities in the underlying LLM, Claude Code, or other tooling that runs these skills. Report those to the relevant vendor (Anthropic, the IDE vendor, etc.).
- Vulnerabilities in the BNDRY product itself — those go through the BNDRY product security process, not this repo.
- Issues that depend on a user pasting attacker-controlled prompts into their own session against documented guidance.
- Social engineering, physical attacks, or anything targeting BNDRY infrastructure rather than this repo's contents.

### No bounty

There's no bug bounty for this repository. Credit and thanks are what's on offer. Thanks for taking the time anyway.
