---
name: bndry-formkit-schema
description: Use when building, editing, or auditing FormKit JSON schemas for BNDRY. Covers multi-step form structure, expression syntax, conditional fields, computed displays, styling, and known failure modes.
argument-hint: "[file-path] [--audit]"
---

# BNDRY FormKit Schema

A bad schema will brick the BNDRY app with no graceful failure. Follow every rule in this guide — each one guards against a real failure mode.

Before building anything, review the official FormKit docs: [Schema](https://formkit.com/essentials/schema), [Inputs](https://formkit.com/inputs), [Multi-Step](https://formkit.com/plugins/multi-step), and [Expressions](https://formkit.com/essentials/schema#expressions). BNDRY uses standard FormKit with no custom expression engine.

---

## FormKit Fundamentals

**Node tree** — FormKit is a node tree, not a bag of fields. Inputs, forms, groups, and lists are all nodes with value, props, state, validation, messages, and plugins. Prefer declarative configuration through props, validation rules, schema, classes, sections, and plugins.

**Core node types:**
- `form` — submission boundary and top-level value collector
- `group` — object collector (children keyed by `name`)
- `list` — array collector (children ordered by index)
- `input` — the leaf or higher-order field node

**Events are an antipattern** — FormKit already collects and reconciles state. Prefer reacting to value, validation state, form state, and node structure instead of wiring event chains. Reach for imperative handlers only when there is no clear node- or state-driven alternative.

**Runtime** — BNDRY's form rendering is Vue-based. No React. All FormKit docs should use the Vue flavour.

**Schema pipeline** — BNDRY is full-stack schema-driven. FormKit schemas are stored against the form definition and rendered dynamically by the app. The JSON schema you author is the source of truth for form layout and field configuration.

---

## Pulling FormKit Docs

When you need deeper FormKit reference during schema work, fetch the Vue-flavoured markdown directly:

```
https://formkit.com/<page>.vue.md
```

The full route index with every page URL is in [references/docs-index.md](references/docs-index.md). Pro inputs are annotated and BNDRY-relevant plugins are called out.

**Key pages for BNDRY schema work:**

| Topic | Route |
|-------|-------|
| Schema essentials | `/essentials/schema` |
| Forms | `/essentials/forms` |
| Validation | `/essentials/validation` |
| Styling | `/essentials/styling` |
| Configuration | `/essentials/configuration` |
| Architecture | `/essentials/architecture` |
| Multi-step plugin | `/plugins/multi-step` |
| LocalStorage plugin | `/plugins/local-storage` |
| Specific input type | `/inputs/<type>` (e.g. `/inputs/datepicker`, `/inputs/repeater`, `/inputs/select`) |

Start with the specific `/inputs/<type>` page for the input you're working with, then branch out to essentials or plugins as needed. See [references/docs-index.md](references/docs-index.md) for the complete list.

---

## 1. Parse Arguments and Determine Mode

Interpret `$ARGUMENTS` to determine the workflow:

- **File path** (e.g., `schemas/intake.json`) → **Edit mode** — read the file, apply changes per user request
- **`--audit`** (with optional file path) → **Audit mode** — validate existing schema against all rules, report violations
- **No arguments / description only** → **Build mode** — generate a new schema from scratch
- **Pasted JSON in conversation** → **Edit mode** — treat inline JSON as the schema to modify

If a file path is given, read it immediately with the Read tool.

---

## 2. Planning Phase (all modes)

Before writing any JSON:

- Confirm the form's steps, fields per step, conditional logic, and any computed outputs
- If requirements are ambiguous, **ask clarifying questions** before proceeding
- If editing, read the existing schema and identify what needs to change
- Check the entity first — don't add fields for data BNDRY already holds on the entity
- If scoring/rating is involved, confirm scale, number of factors, and band thresholds upfront — changing these later means rewriting every computed expression

---

## 3. Build / Edit Phase

- For new schemas, start from [multi-step-skeleton.json](templates/multi-step-skeleton.json)
- Apply all rules from the Reference section below, tracking progress against the Rules Checklist
- **Before delivering**, write the JSON to a file and run the mechanical validator; fix every CRASH and BUG finding:

```
python3 scripts/validate_schema.py <schema.json>
```

### Rules Checklist (all modes)

One checklist drives both build and audit. In **build/edit mode**, copy it as a progress tracker and tick items off as you work. In **audit mode**, evaluate every item against the schema (see §4).

Items tagged **[auto]** are verified mechanically by [scripts/validate_schema.py](scripts/validate_schema.py) — run it rather than eyeballing them (but don't write violations in the first place). Untagged items are judgement calls the script can't make. The Reference section below holds the full explanation and fix for every item.

**Process (build mode):**

- [ ] Checked references/bndry-theme-reference.md — theme behaviour, safe classes, available inputs and plugin behaviour

**A. App crash:**

- [ ] Schema parses as valid JSON [auto]
- [ ] Schema root is a JSON array `[ ... ]`, not an object — an object root is rejected by the platform before the form can be saved [auto]
- [ ] Computed displays use `$el` divs — no `$formkit` input with a computed `value` expression (infinite re-render) [auto]
- [ ] No method chaining after `.value` (`.includes()`, `.length`, `.trim()`) [auto]
- [ ] `children` expressions start with `$:` prefix [auto]

**B. Silent bugs:**

- [ ] All fields have `name` [auto]
- [ ] All `$get()`-referenced fields have `id` [auto]
- [ ] `id` equals `name` on every field that has both [auto]
- [ ] No field `name` matches any step `name` in the same form [auto]
- [ ] No duplicate field `name` values within the same step [auto]
- [ ] Multi-step root has a stable `name` property (prevents hydration key mismatch on reload) [auto]
- [ ] Expressions use only `$get(id).value` (no `$field_name`) [auto]
- [ ] No `|| 0` fallbacks in `children` expressions (causes literal text rendering) [auto]
- [ ] Select arithmetic uses `* 1` cast; scoring selects have default `value: "0"` to prevent NaN [auto: missing default]
- [ ] Conditional nodes have `key`; all `$formkit` children inside conditional `$el` wrapper divs have their own `key` [auto]
- [ ] No checkbox groups used as conditional triggers — `radio` for a single Yes/No gate; one single-checkbox field per option for a "select all that apply" checklist where each option gates its own section [auto]
- [ ] Single checkbox conditionals use `=== true` (boolean), not `=== 'true'` or `=== 'yes'` [auto]
- [ ] Whole-topic conditionals put `if` (and `key`) on the `$formkit: "step"` node itself — never a step whose entire content is conditional wrappers (leaves a stub step in the progress bar)
- [ ] No separate sibling `checkbox`/`radio` gating an "Other — specify" field — fold "Other" into the parent group's `options` array, or render the specify field unconditionally
- [ ] No `$get()` inside repeater children (resolves at form scope, not row scope) [auto]
- [ ] No `validation` property on repeater nodes — FormKit ignores it; use `min: 1` [auto]
- [ ] No curly-brace quantifiers or pipe `|` alternation in `matches` regex patterns [auto]
- [ ] No `required` where it should be conditional — gate the field behind an `if` (and mark it required there) or make it optional. Never `required` an identifier only some entity types have (e.g. ACN on a form that allows sole traders)

**C. Input types / Australian defaults:**

- [ ] Phone fields use `$formkit: "tel"` (not `"text"`)
- [ ] Date-only fields use `$formkit: "datepicker"` (not native `"date"` [auto]) with standard config (clearable, format.date long, overlay, pickerOnly, sequence day)
- [ ] Date+time datepickers use `format.time: "short"` — `"2-digit"` makes the field completely non-interactive [auto]
- [ ] No hardcoded `maxDate`/`minDate` used as age gates — age-based validation belongs in application logic
- [ ] Currency fields use `$formkit: "currency"` with `currency: "AUD"`, `displayLocale: "en-AU"`, `decimals: 2`, `minDecimals: 2`, `min: 0` [auto: AUD/locale/minDecimals]
- [ ] File fields default to `multiple: true` (omit only when explicitly single-file); `accept` set and within the plugin's supported list [auto]; no manual fileExt/fileSize/fileUpload in the validation string [auto]
- [ ] `dropdown` used by default for picklists, with `deselect: !required`, `selectionRemovable: !required`, `popover: true`; `select` only for scoring fields or other narrow special cases
- [ ] `$formkit: "signature"` fields have `outerClass: "!col-span-2"` and are not inside a repeater [auto]

**D. Layout / configuration:**

- [ ] Multi-step root has `tab-style: "progress"`, `outerClass`/`wrapperClass` set to `"!max-w-none"` (no `!w-full`), and no `allow-incomplete` property [auto]
- [ ] If the progress bar is hidden (`tabsClass: "!hidden"`), confirmed with BNDRY that the `!hidden` utility is enabled for schemas AND every step has its own `$el` h2 heading as first child
- [ ] No non-standard utility class used — only classes BNDRY has compiled into its stylesheet have any effect (see references/bndry-theme-reference.md for the safe set); anything else silently does nothing
- [ ] Every step has `stepInnerClass: "grid grid-cols-2 gap-4"` [auto]
- [ ] Every `$formkit` direct step child has `outerClass: "!col-span-2"` or `"!col-span-1"` [auto]
- [ ] Every `$el` direct step child (including conditional div wrappers) has `!col-span-2` in `attrs.class` [auto]
- [ ] No layout-only `$el` div wrappers (use `!col-span-1` pairs on children directly)
- [ ] Repeaters have `outerClass: "!max-w-none !col-span-2"` [auto]; repeaters with short-field children have `contentClass: "grid grid-cols-2 gap-4"`
- [ ] All `$el` h2 and h3 elements use `!block` (not `!inline-flex`) [auto]
- [ ] At most one h3 heading per step by default; no "Section N" numbered headings [auto]; distinct topics live in separate steps (see Steps vs sections guidance)
- [ ] Required fields with long question/sentence labels override via `validationMessages: { "required": "This question is required" }` (short noun labels keep the default)

**E. Theme compatibility** (cross-reference [references/bndry-theme-reference.md](references/bndry-theme-reference.md)):

- [ ] `outerClass` on `$formkit` fields contains only `!col-span-1` or `!col-span-2` — no `!max-w-none` (theme's global outer already applies it [auto]); other classes risk conflicting with the theme
- [ ] `$el` heading classes use the same colour tokens as the theme's label section — no arbitrary colours
- [ ] No redundant `block` alongside `!block` [auto]
- [ ] No section-level class overrides (labelClass, inputClass, wrapperClass) that duplicate what the theme already applies

**F. Content / cosmetic:**

- [ ] No inline `style` attributes [auto]; no custom colours or backgrounds on `$formkit` nodes; schema works in both light and dark mode
- [ ] `$el` headings have standard heading classes; intro text divs have `mb-4 !col-span-2`; adjacent headings have `mt-2` on the second
- [ ] No empty/dead `$el` divs or remnant markup [auto]
- [ ] Intro/instructional text is concise and consistent with other schemas
- [ ] No club/venue/brand-specific names in labels, option values, help text, or placeholders — flag to the user and ask before genericising
- [ ] "player"/"gaming" terminology, never "gambler"/"gambling" (unless quoting legislation verbatim)
- [ ] Prose-bearing fields follow the style rules in Australian Defaults (sentence case for help text; Title Case labels)
- [ ] Validation rules applied where the requirements call for them

---

## 4. Audit Phase (audit mode only)

1. **Run the mechanical validator first** — it covers every item tagged [auto] in the Rules Checklist (§3) and reports severity, location, and fix for each finding:

   ```
   python3 scripts/validate_schema.py <schema.json>
   ```

   Include its findings in the report verbatim. Do not re-derive them by eye, and do not skip the script — eyeballing is exactly where these checks get missed.

2. **Walk the untagged checklist items** (§3) manually — these are the judgement calls: theme cross-referencing against references/bndry-theme-reference.md, steps-vs-sections structure, conditional-`required` traps, content and terminology.

3. **For each violation found, report:**
   - **Rule violated**
   - **Location** in schema (field name / JSON path)
   - **Severity**: checklist group — A app crash, B silent bug, C input type, D layout, E theme, F cosmetic
   - **Fix**: specific remediation (the Reference section below holds the full fix for every rule)

---

## 5. Output

- **Build mode**: Output the complete JSON schema, ready to paste into BNDRY
- **Edit mode**: Apply edits to the file using the Edit tool (or output the modified JSON if working with pasted content)
- **Audit mode**: Output a findings report grouped by severity

---

## Reference — Rules

### Form Skeleton

Every BNDRY form must use the multi-step skeleton for full-width rendering. Use [multi-step-skeleton.json](templates/multi-step-skeleton.json) as a starting point. (The skeleton's heading colour tokens were verified against the theme's label tokens as of June 2026 — if they've since diverged, references/bndry-theme-reference.md is authoritative.)

**The schema root must be a JSON array** — the top-level value must start with `[` and end with `]`, even when the form has a single root multi-step node. BNDRY stores the schema as a list of nodes and only accepts a JSON array root. If you submit a schema whose root is a JSON **object** (e.g. `{ "$formkit": "multi-step", ... }` instead of `[ { "$formkit": "multi-step", ... } ]`), the save is rejected before the request reaches the server and the user sees only a generic "Error creating form" toast.

The centralised theme constrains multi-step form width by default. To get full-width rendering, add `outerClass` and `wrapperClass` directly on the multi-step node — do **not** use `sections-schema` attrs (they don't override the theme):

```json
"tab-style": "progress",
"outerClass": "!max-w-none",
"wrapperClass": "!max-w-none"
```

**`tab-style: "progress"`** must be set on every multi-step root. The BNDRY theme provides full styling for this mode via `data-[tab-style=progress]` selectors: step indicator dots, connecting lines between steps, active/visited colour changes, and dark mode variants. These styles only activate when `tab-style` is set — omitting it leaves the tab bar unstyled.

Each step needs a `name` and a short `label` (appears in the tab bar).

**Hiding the progress/tab bar.** The whole bar lives in the `multi-step__tabs` section; the prev/next buttons live in separate sections, so hiding the bar leaves navigation intact. On long forms the step labels squish together and can't be made legible no matter the styling — when that happens (or when prev/next is navigation enough), hide it with `tabsClass: "!hidden"` on the multi-step root. The `!important` is required because the multistep addon ships a high-specificity `display:flex` on `.formkit-tabs` that a plain `hidden` can't beat.

```json
"tab-style": "progress",
"outerClass": "!max-w-none",
"wrapperClass": "!max-w-none",
"tabsClass": "!hidden"
```

**This is NOT always a pure schema change — `tabsClass: "!hidden"` only works if the `!hidden` utility is enabled for schemas in your BNDRY environment.** Utility classes used only in schema JSON must already be compiled into BNDRY's stylesheet (see [Runtime utility classes must already be compiled](#runtime-utility-classes-must-already-be-compiled) below). If the bar doesn't hide, that's why — confirm with BNDRY before relying on it.

Keep `tab-style: "progress"` set regardless — deleting the `tabsClass` line reverts cleanly.

**When the bar is hidden, every step MUST carry its own `$el: "h2"` heading as its first child** — with the tab bar gone, that heading is the only "where am I" cue the user has. (Steps should already have these per the styling rules; it becomes mandatory once the bar is hidden.) Do not reach for `hideProgressLabels` for this — it only drops the tab text and leaves the dots/connectors, which is rarely what you want.

**Draft autosave** — all portal forms auto-save form state to the browser's localStorage every second (30-minute expiry). On reload, users are prompted to continue their draft or discard it. The draft key is derived from the workspace form record's name — not the schema's `name` property. However, **renaming fields or steps** in a schema after a form has been deployed causes existing user drafts to pre-populate stale values into the wrong fields. Treat `name` changes on deployed schemas as a breaking change — coordinate with users or accept that in-progress drafts will be stale.

**Every step must have `stepInnerClass: "grid grid-cols-2 gap-4"`** — this enables 2-column grid layout for the step's direct children. Without it, `!col-span-1` and `!col-span-2` on child fields have no effect.

**Every `$formkit` field that is a direct child of a step** must have `outerClass` with either `!col-span-2` (full-width) or `!col-span-1` (half-width, for fields that pair naturally side by side). Do not include `!max-w-none` — the global theme outer already sets `max-w-none` for all `$formkit` inputs:

```json
"outerClass": "!col-span-2"
```

```json
"outerClass": "!col-span-1"
```

**Every `$el` node that is a direct child of a step** (headings, description divs, conditional wrappers, decorative blocks) must have `!col-span-2` in its `attrs.class` to span both grid columns.

**Conditional `$el: "div"` wrappers** (nodes with `if` and `key` properties) must include `!col-span-2` in their `attrs.class`:

```json
{
  "$el": "div",
  "if": "$get(some_field).value === 'yes'",
  "key": "some_conditional_block",
  "attrs": { "class": "!col-span-2" },
  "children": [...]
}
```

**Layout-only `$el: "div"` wrappers** (no `if`, no `key`, no meaningful class — used purely to group fields) must be removed. Give the children `!col-span-1` or `!col-span-2` directly instead. These wrappers are no-ops in a CSS grid context.

**Prefer steps over numbered sections.** The default behaviour is to break form content up into separate steps — not into "Section 1", "Section 2", "Section 3" headings within a single step. Steps make the progress bar meaningful, give users a sense of momentum, let them save and resume work mid-form, and surface conditional logic cleanly via `if` on the step node. Numbered section headings inside a single step bury structure that the multi-step UI is designed to surface.

However: don't end up with 16 steps when you could have 4 steps with 4 sub-sections each. Steps come with overhead (a tab, a progress dot, a "Next" click) so very short steps feel choppy. Use this rough guide:

- **2–8 fields on a single topic → one step.** No internal headings needed; the step's own `label` is the heading.
- **9–20 fields on a single topic → one step with sub-headings allowed.** Use a single `$el: "h3"` at the top and at most one or two `$el: "h3"` sub-headings within the step if the topic genuinely splits. Avoid "Section 1 / Section 2" numbering — use descriptive headings like "Personal details" and "Contact information".
- **Multiple distinct topics, each 2+ fields → separate steps.** This is the common case.
- **More than ~20 fields on one topic, or content that splits into clearly different sub-topics → separate steps.**

When in doubt, prefer the extra step over the extra section. Numbered "Section N" headings are almost never right — they suggest the content was lifted from a paper form. Use a descriptive heading or split into a step instead.

The "at most one h3 heading per step" rule still applies as a default — break the default only when keeping content together produces a more coherent form than splitting it.

**Repeaters** that are direct step children need `outerClass: "!max-w-none !col-span-2"`. Repeaters whose children contain short fields (e.g. name + contact pairs) should also have `contentClass: "grid grid-cols-2 gap-4"`, with appropriate `!col-span-1`/`!col-span-2` on each repeater child.

### Field Rules

- `name` is **mandatory** on every field — it becomes the key in submitted data.
- `id` is **mandatory** on any field referenced by `$get()`.
- **`id` must always equal `name`** on the same field. They serve different purposes (`id` is for `$get()` expression scoping; `name` is the submitted data key) but must be kept in sync. If they diverge, `$get(id)` resolves correctly but the data is keyed under `name` — creating a confusing disconnect that is hard to debug.
- **Field `name` values must never match any step `name` in the same multi-step form.** FormKit's scope resolution can confuse a field node with a step node of the same name, producing wrong `$get()` results and garbled submitted data. If a step is named `incident_details`, no field anywhere in the form should also be named `incident_details` — rename the field (e.g. `incident_description`).
- Field `name` values must be unique within their step.
- Select option values are **always strings** — use `* 1` to cast when doing arithmetic.
- **`select` vs `dropdown`**: Default to `$formkit: "dropdown"` (FormKit Pro) for all picklists — short fixed lists, long lists, and searchable lists alike. Standard BNDRY attrs: `deselect: !required`, `selectionRemovable: !required`, `popover: true` (the custom-fields converter applies these automatically; hand-written schemas should set them explicitly). Use `$formkit: "select"` only for narrow special cases — primarily **scoring fields**, where option values feed arithmetic expressions (`* 1` casts, `$get(id).value` summed across fields) and the native `select` is a better fit than the Pro dropdown.
- **Keep validation co-located** with the inputs that own it — don't centralise validation rules in a separate structure.
- **Prefer `form`, `group`, and `list` composition** over manual object or array assembly in submit handlers.

**Available input types:**

Standard: `text`, `textarea`, `select`, `radio`, `checkbox`, `date`, `datetime-local`, `file`, `number`, `email`, `tel`, `url`, `hidden`

FormKit Pro (pre-registered in BNDRY): `datepicker`, `dropdown`, `repeater`, `currency`, `mask`, `autocomplete`, `slider`, `rating`, `taglist`, `toggle`, `togglebuttons`, `colorpicker`, `transferList`, `unit`

BNDRY Custom: `signature`

**FormKit Pro inputs** are commercial FormKit add-ons. In BNDRY they are all pre-registered and available — no additional setup is needed. However, when recommending or implementing a Pro input, mention that it is a Pro input in any user-facing summary.

### Theme Compatibility

At build, edit, and audit time, schemas must be evaluated against [references/bndry-theme-reference.md](references/bndry-theme-reference.md) — the bundled reference for what the BNDRY theme handles automatically, the safe classes schemas may set, the available inputs, and the plugin behaviour you can rely on.

**Platform facts you can rely on:**
- `$formkit: "multi-step"` and `"step"` are available
- All FormKit Pro inputs are available (datepicker, dropdown, repeater, taglist, etc.)
- Textareas auto-expand — do not set fixed heights
- The `signature` custom input is available — see Signature Input Rules below
- Locale is `en-AU`

**Key facts from the theme** (verify current values against references/bndry-theme-reference.md — do not rely on this list alone):

- **Global `outer` section** — the theme applies `max-w-none` to all `$formkit` inputs by default. `!col-span-1`/`!col-span-2` in `outerClass` are safe because the theme sets no `col-span` or grid placement classes on fields.
- **`multi-step__outer`** — the theme constrains multi-step width (narrower than `max-w-none`). `outerClass: "!max-w-none"` on the multi-step root overrides this to get full-width rendering.
- **`multi-step__wrapper`** — `tab-style: "progress"` activates a set of `group-data-[tab-style=progress]/wrapper:` selectors across `multi-step__tabs`, `multi-step__tab`, and `multi-step__badge` — providing step dots, connector lines, visited/active colour changes, and full dark mode support. These styles do not activate without the `tab-style` attribute.
- **`repeater__outer`** — the theme constrains repeater width (narrower than `max-w-none`). `outerClass: "!max-w-none"` on repeaters overrides this.
- **`repeater__content`** — the theme applies a flex column layout by default. `contentClass: "grid grid-cols-2 gap-4"` overrides the display to grid. This is the correct and safe pattern.
- **`stepInnerClass`** — the theme defines nothing for this prop. It must always be set explicitly on every step: `"stepInnerClass": "grid grid-cols-2 gap-4"`.
- **Grid placement classes** — the theme does not set `col-span`, `gap-`, or `grid-cols-` classes on fields or steps (only inside the datepicker's internal calendar UI, which never affects step or field layout). Grid placement classes in `outerClass`/`contentClass`/`stepInnerClass` have zero conflict risk.
- **Label colour tokens** — confirm the current colour tokens in references/bndry-theme-reference.md. `$el` heading classes must use the same tokens for visual consistency.
- **Button styling** — the theme controls all button appearance (submit, multi-step prev/next, repeater add). Schemas must not add button-related class overrides.

**Safe `outerClass` values for `$formkit` fields:**

```
"outerClass": "!col-span-2"   ← full-width
"outerClass": "!col-span-1"   ← half-width pair
```

Do not add `!max-w-none` to regular field `outerClass` — the global theme outer already applies `max-w-none` to every `$formkit` input, so adding it is redundant noise. `!max-w-none` is only needed on the multi-step root and repeater nodes, where the theme constrains their width. Everywhere else it is unnecessary.

Do not add spacing, colour, display, or border classes to `outerClass` — the theme handles all of those for `$formkit` nodes.

#### Runtime utility classes must already be compiled

BNDRY's stylesheet is compiled from the platform's own source and theme — **never from form schemas**, which live in the database. A utility class generates CSS only when it appears in that compiled set.

Consequence: a utility class that appears **only** in a schema's JSON has no CSS rule generated for it, so it silently does nothing at runtime. This is why the common layout classes are safe (`!col-span-1`, `!col-span-2`, `!max-w-none`, `!block`, `!inline-flex`, the heading/​colour tokens) — they are part of the compiled theme. But reach for any *other* utility in a schema (e.g. `!hidden`, an arbitrary variant, a one-off colour) and it may be absent from the build and have zero effect — with no error.

Before using a non-standard utility in a schema, stick to the classes documented in [references/bndry-theme-reference.md](references/bndry-theme-reference.md). If a schema genuinely needs one that isn't documented there, ask BNDRY to enable it rather than assuming it works. Do **not** debug this by staring at the schema: the schema can be perfect and the class still be a no-op because the CSS was never generated.

### Australian Defaults

BNDRY is an Australian platform. All schemas must use Australian conventions unless explicitly told otherwise:

- **Phone**: Use `tel` type (not `text`). Placeholder format: `04XX XXX XXX` (mobile) or `+61 X XXXX XXXX` (landline).
- **Address**: Use "City / Suburb", "State / Territory" (as a `dropdown` with AU states: NSW, VIC, QLD, SA, WA, TAS, NT, ACT), and "Postcode" (4-digit, validation: `matches:/^\d\d\d\d$/`). Never use "Zip Code".
- **Currency amounts**: Use `$formkit: "currency"` (FormKit Pro), not `"number"` or `"text"`. Always configure with Australian locale:

  ```json
  {
    "$formkit": "currency",
    "currency": "AUD",
    "displayLocale": "en-AU",
    "decimals": 2,
    "minDecimals": 2,
    "min": 0
  }
  ```

  Use `"step": 0.01` for cent-precision entry. Only add `"max"` when there is a documented business reason for the cap — do not set arbitrary maximums on financial amount fields. The `currency` prop takes an ISO 4217 code; `displayLocale` controls number formatting (thousands separators, decimal symbol).

- **Currency label** — always AUD, not USD. Never use `$`.
- **Legal terminology**: Use "criminal offence" (not "felony"), "secondary school" (not "high school"), "university" (not "college").
- **Gaming terminology**: Use **"player"** (not "gambler"). BNDRY schemas serve clubs, casinos, and gaming venues where "player" is the standard, neutral, customer-respecting term — "gambler" carries pejorative and stigmatising connotations that don't fit a regulated-customer context. Applies to labels, option values, help text, and placeholders. Only use "gambler" if the user explicitly asks for it, or if quoting legislation/regulator material that uses the term verbatim.
- **No club-specific names**: Never embed specific club, venue, or brand names (e.g. "Souths", "The Juniors", "Easts", "Wests", "Norths", "[Club Name] Loyalty Member", "Top 30 [Venue]") in schema labels, option values, help text, placeholders, or examples. BNDRY schemas are reused across many tenants — a Souths-specific label is wrong everywhere else. Use generic equivalents: "high-tier loyalty member", "high-value player", "the venue", "the club". If the user pastes content containing a club-specific name, **ask before stripping or replacing it** — they may have pasted source material from a specific tenant and want the generic version, or they may genuinely need a tenant-specific schema. Don't silently rewrite; flag and confirm. Same rule for input documents the user references — assume the source is one tenant's flavour of a generic form.
- **Citizenship**: Reference Australia, not the United States.
- **BNDRY style** — all prose-bearing fields (`help`, `placeholder`, `$el` heading text) follow these rules: sentence case, Australian English (`-ise`, `-our`, `-re`), no full stops inside acronyms, single space after full stops, no banned filler phrases (`please note`, `in order to`, `utilise`, `leverage`). These cover schema work; the full BNDRY style guide is `references/bndry-style-reference.md` — consult it only when unsure about a specific term, name, or convention (regulator names, legislation citation, apostrophes in compliance terminology).
  - **Field labels and option labels stay in Title Case** ("Date of Birth", "Source of Funds", "Full-time") — deliberate UI convention for form-field captions in dense Settings layouts. This is the one departure from the reference's sentence-case default.
- **Dates**: Use `$formkit: "datepicker"` (FormKit Pro) for all date-only fields — not `$formkit: "date"` (native HTML). Native date inputs have inconsistent mobile UX, no BNDRY theming, and submit ISO `YYYY-MM-DD` strings. The standard datepicker config:

  ```json
  {
    "$formkit": "datepicker",
    "clearable": true,
    "format": { "date": "long" },
    "overlay": true,
    "pickerOnly": true,
    "sequence": ["day"]
  }
  ```

  For fields requiring both a date and a time, use `$formkit: "datepicker"` with `sequence: ["day", "time"]`, `pickerOnly: true`, and `overlay: true`. The time format must be `"short"` — `"2-digit"` is not a valid value and causes the field to be completely non-interactive (no typing, no picker opens). Do not set `pickerOnly: false` — typing dates is error-prone and the picker is the preferred UX.

  **Do not use hardcoded `maxDate` or `minDate` as age gates** (e.g. `"maxDate": "2002-12-31"` to enforce 18+). These values become stale as time passes — a date that was under-18 last year is over-18 this year, and the field will reject it. If the form genuinely needs a fixed calendar boundary (e.g. "incident must have occurred before 2025-01-01"), `maxDate`/`minDate` are appropriate. For age-based restrictions, validation belongs in application logic, not the schema.

### File Input Rules

All `$formkit: "file"` inputs are automatically enhanced by BNDRY's file handling. Understanding what it does automatically prevents double-handling and misuse.

**What the plugin does automatically:**
- Adds `fileExt` validation — rejects files with unsupported extensions or double extensions (e.g. `file.backup.pdf`)
- Adds `fileSize` validation — rejects files over the configured limit (default: 10,240 KB)
- Renders a file viewer below the input showing uploaded files with preview/download
- Skips re-validation on already-uploaded files (those with a `.resource` property from a prior save)

**Supported extensions** — the plugin's `fileExt` validation only permits these types. Any extension outside this list will be rejected on validation, regardless of what `accept` shows in the picker:

```
doc, docx, ppt, pptx, xls, xlsx, csv, txt, odt, ods, odp, pdf, jpg, jpeg, png
```

Video formats (`.mp4`, `.mov`, `.avi`, `.mkv`), email formats (`.msg`, `.eml`), GIF (`.gif`), and all other formats are **not supported** and must not appear in `accept`.

**Default accepted extensions** (when no `accept` is specified): all of the above.

**Key props to set explicitly:**

- **`accept`** — comma-separated extension list (e.g. `".pdf,.png,.jpg,.jpeg"`). Controls the **browser's file picker dialog only** — the plugin's `fileExt` validation enforces the actual restriction. Always specify `accept` to guide the user; it must be a subset of the plugin's supported extensions (see below) — any extension not in that list will appear in the picker but be rejected on validation.
- **`multiple: true`** — allows multiple files in one field. **Default to `multiple: true` for all file fields** unless the field is explicitly single-file (e.g. a single ID document, single profile photo). Most real-world document uploads benefit from accepting multiples, so the burden is on justifying a single-file field, not on enabling multiple.
- **`validation: "required"`** — works as expected; field is invalid until at least one file is attached or already uploaded.

**Do not** add `fileExt`, `fileSize`, or `fileUpload` to the `validation` string — the plugin applies these automatically. Adding them manually causes double-validation errors.

---

### Signature Input Rules

BNDRY includes a custom `$formkit: "signature"` input. It provides canvas-based signature capture, uploads the drawn signature as a JPEG to BNDRY's file storage, and displays existing uploaded signatures with a re-sign flow.

**Available props:**
- `penColor` — ink colour (default: `'navy'`). Leave unset to use the BNDRY default.
- `backgroundColor` — canvas background colour. Leave unset to use the theme default.
- `strokeWidth` — line width for the signature stroke. Leave unset to use the default.

**Rules:**
- Use `outerClass: "!col-span-2"` like all other direct step children.
- `validation: "required"` works and marks the field invalid until a signature is drawn and saved.
- The stored value is a **file reference** to the Files service — not a base64 data URL or string. Treat it like a file field value.
- Do **not** place a `signature` input inside a `repeater` — canvas-based inputs do not scale correctly within repeater rows.
- Do **not** override `penColor` or `backgroundColor` with arbitrary colours — the BNDRY defaults are intentional and consistent with brand guidelines.

**Minimal signature field:**
```json
{
  "$formkit": "signature",
  "name": "signed_by",
  "label": "Signature",
  "validation": "required",
  "outerClass": "!col-span-2"
}
```

---

### Expression Rules

FormKit uses a limited expression parser — **not JavaScript**.

The only safe way to reference a field's live value is `$get(field_id).value`.

**Valid operators:** `+`, `-`, `*`, `/`, `%`, `&&`, `||`, `===`, `!==`, `==`, `!=`, `>=`, `<=`, `>`, `<`

**`children` expression strings must start with `$:`** — FormKit only evaluates `children` strings as expressions when they begin with `$:`. The `if` property always evaluates expressions regardless of prefix. If a `children` string starts with `(` or any other character, it renders as literal text.

**Arithmetic on select values** — always cast with `* 1`:

```
$get(score).value * 1 + $get(other).value * 1
```

**Preventing NaN on unselected fields** — when a select has no value yet, `$get(id).value` returns `undefined` and `undefined * 1 = NaN`. Do **not** use `|| 0` fallbacks in `children` expressions (this adds a `(` prefix which breaks expression parsing). Instead, set a default `value: "0"` on the select's first option and on the select itself so the value is never undefined.

**Forbidden patterns:**

- **No method chaining after `.value`** — `.includes()`, `.length`, `.trim()` etc. will **hard-crash the app**.
- **No `$field_name` references** — this looks at the schema data scope which BNDRY doesn't populate. It silently resolves to `undefined` and logic will never trigger. Always use `$get(field_id).value`.
- **No `|| 0` fallbacks in `children` expressions** — wrapping with `($get(x).value || 0)` causes the string to start with `(` instead of `$:`, so FormKit renders it as literal text instead of evaluating the expression.

### Conditional Fields

- The **trigger field must have an `id`** — without it, `$get()` can't find it.
- The **conditional node must have a `key`** — without it, Vue reuses DOM nodes and you get ghost values and rendering bugs.
- Use `===` not `==`.
- For OR conditions, repeat `$get()` on each side: `$get(f).value === 'a' || $get(f).value === 'b'`
- **When multiple mutually exclusive conditional `$el: "div"` sections are siblings** (e.g. different decision types each showing different fields), adding `key` to the wrapper div alone is **not enough**. Every `$formkit` field inside each conditional section must also have a `key` property (use the field's `name` as its `key`). Without this, Vue reuses DOM nodes positionally across sections — a text field at position 3 in section A gets the rendered output of a radio at position 3 in section B, causing wrong input types, ghost values, and broken styling.

**Conditional steps — `if` on a `$formkit: "step"` node** hides the entire step and removes it from the progress bar when the expression is false. Use this whenever a whole topic is only relevant under certain answers (e.g. a Family & Associates step that only applies when the user picked "Tier 4 — family member/close associate" earlier). Prefer this over wrapping every field in the step inside a conditional `$el: "div"` — the latter leaves a stub step in the progress bar with nothing inside it. The step still needs a `key` (because it's a conditional node) and the usual `name`, `label`, `stepInnerClass`.

```json
{
  "$formkit": "step",
  "if": "$get(pep_tier).value === 'tier_4'",
  "key": "family_and_associates_step",
  "name": "family_and_associates",
  "label": "Family & Associates",
  "stepInnerClass": "grid grid-cols-2 gap-4",
  "children": [...]
}
```

**Checkbox groups cannot be used as conditional triggers.** Checkbox groups return arrays, so `$get(id).value === 'value'` compares an array to a string — it will **never match**. And you cannot use `.includes()` (method chaining crashes the app). If you need a Yes/No toggle that gates other fields, use a `radio` input instead.

**"Select all that apply" where each option gates its own section — use individual single checkboxes, not a checkbox group.** When the source form is a multi-select *and* each selected option needs to reveal its own follow-up fields (e.g. "Who is your business regulated by?" → AUSTRAC / ASIC / AFCA, each unlocking that regulator's licence details), the instinct is one `checkbox` field with an `options` array. That cannot work: a checkbox group returns an array, so no `$get(group).value === 'austrac'` gate will ever fire, and `.includes()` crashes. Do **not** fall back to a stack of separate Yes/No `radio` fields — it reads as an interrogation, not a checklist, and is the wrong UX.

Instead, render **one single-checkbox field per option** (each a bare boolean `checkbox` with no `options` array, its own `name`/`id`, laid out with `!col-span-1` to form a compact 2-column checklist under a shared `$el: "h3"` heading). Visually this is identical to the multi-select the form intended — a "select all that apply" checklist — but because each box is its own boolean field, each one gates its section cleanly with `=== true`, and each becomes an independently filterable/reportable field (often *better* for downstream reporting than a single array field). This is the canonical BNDRY pattern for "multi-select that drives conditionals".

```json
{ "$el": "h3", "children": "Who is your business regulated by?", "attrs": { "class": "<heading classes> !col-span-2" } },
{ "$formkit": "checkbox", "name": "regulated_by_austrac", "id": "regulated_by_austrac", "label": "AUSTRAC", "outerClass": "!col-span-1" },
{ "$formkit": "checkbox", "name": "regulated_by_asic",    "id": "regulated_by_asic",    "label": "ASIC",    "outerClass": "!col-span-1" }
```
```json
{ "$formkit": "step", "if": "$get(regulated_by_austrac).value === true", "key": "austrac_step", "name": "austrac_details", "label": "AUSTRAC", "stepInnerClass": "grid grid-cols-2 gap-4", "children": [ ... ] }
```

The gate uses `=== true` (boolean), never `=== 'true'`/`=== 'yes'`/`=== 'austrac'`. Reserve the "fold Other into a checkbox group's options array" guidance below for the case where the options do **not** each need to gate a distinct section — if they do, one boolean field per option is the only thing that works.

**Multi-select with an "Other" option** — do **not** add a separate sibling `checkbox`/`radio` ("Other method used") above the "specify" text field. That sibling renders as a full grid row with its own label, leaving a visible vertical gap below the main checkbox group, and the checkbox-group-can't-gate-conditionals problem means you can't use the group itself anyway. Two cleaner options:

1. **Fold "Other" into the same options array** of the parent checkbox group (preferred when the "specify" field is short or can be always-visible). The "Other" option is just another value alongside the rest.
2. **Always render the "specify" text field** unconditionally below the checkbox group. Skipping the gating logic entirely avoids the gap and the array-vs-string footgun.

**Single checkbox fields** (no `options` — a bare boolean toggle) return `true` or `false`, not a string. Conditional expressions must use `=== true` (boolean):

```json
"if": "$get(some_checkbox).value === true"
```

Do **not** write `=== 'true'` or `=== 'yes'` — the condition will silently never trigger. This is different from `radio` and `select` inputs where values are always strings.

**`$get()` inside repeater children** — `$get()` resolves at the **form/step scope**, not the current repeater row. You cannot use `$get()` to reference a sibling field within the same repeater row. There is no safe way to implement intra-row conditionals in FormKit JSON schemas. If intra-row conditional logic is required, it must be handled at the app level.

**`required` cannot be made conditional in the validation string.** There is no `requiredIf`-style rule that reads another field — `validation` is static per field. So a field that should only be mandatory under some answers has two schema-level options:

1. **Put the field inside a conditional `$el: "div"` / step that only renders under that answer**, and mark it `required` there. When the wrapper is hidden the field isn't rendered, so `required` doesn't block submission (this is exactly how the gated AUSTRAC/ASIC fields work — `required` on them only bites when their step is shown).
2. **Make it plainly optional** (drop `required`, keep any format `matches`) when it's always visible but only sometimes applicable.

Corollary — **don't make an identifier `required` that only some entity/answer types possess.** Requiring an ACN (companies only) on a form whose `entity_type` includes Sole Trader / Partnership / Trust silently blocks those entities from submitting — they have no ACN to enter. Either gate a `required` copy behind the company-type condition, or make the field optional. The same trap applies to any "everyone fills this" field that's really "only some do".

### Computed Display Fields

- **NEVER** use a `$formkit` input with a `value` expression for calculated fields — this creates an infinite re-render loop that bricks the app.
- Use `$el` divs instead — they render the expression result without feeding it back into form state.
- For banded ratings (Low / Medium / High), use nested `if/then/else` objects in the `children` property of an `$el` div.
- The full sum expression must be **repeated in every `if` condition** — there is no way to store intermediate values in FormKit schema.

### Styling Conventions

BNDRY has a **centralised FormKit theme** (documented in [references/bndry-theme-reference.md](references/bndry-theme-reference.md)) that applies Tailwind classes for every `$formkit` input based on its type and section. This theme handles all styling for `$formkit` nodes — schemas must not override it.

**Core rules:**

- **No inline `style` attributes** on any schema node. Inline styles override the centralised theme and prevent rolling out fixes and improvements across all schemas.
- **No custom colours, backgrounds, or borders** on `$formkit` nodes. The theme handles these and must be the single source of truth.
- **Dark/light mode agnosticism** — schemas must work in both themes. Never hardcode colours that assume light or dark mode. The centralised theme already handles dark mode via Tailwind's `dark:` variants.

**`$el` elements** (divs, headings, paragraphs) are raw HTML — the centralised FormKit theme engine cannot reach them. This is a FormKit limitation, not a design choice. Without explicit classes, `$el` nodes render as unstyled browser-default HTML.

**Section headings** (`$el: "h3"` or `$el: "h2"`) currently need Tailwind classes via `attrs.class` as a workaround for this limitation. Both h2 and h3 use `!block`. All headings are direct step children inside a CSS grid, so they also need `!col-span-2`. The colour tokens must match the theme's label tokens — confirm the current values in references/bndry-theme-reference.md. Example (verify colour tokens against the reference before using):

```json
{
  "$el": "h2",
  "attrs": { "class": "<label-colour-tokens> font-bold <label-dark-tokens> !block mb-1.5 formkit-label !col-span-2" },
  "children": "Step Title"
}
```

```json
{
  "$el": "h3",
  "attrs": { "class": "<label-colour-tokens> font-bold <label-dark-tokens> !block mb-1.5 mt-2 formkit-label !col-span-2" },
  "children": "Section Title"
}
```

Replace `<label-colour-tokens>` and `<label-dark-tokens>` with the actual text colour and dark mode classes from the heading-classes section of references/bndry-theme-reference.md.

Styling headings via `attrs.class` is the supported pattern for `$el` headings — it is not an override of the centralised theme (which cannot reach raw `$el` HTML).

- Do not wrap headings in a parent `$el: "div"` — use the `h3` directly as a child of the step.
- If a schema needs visual treatment that the current theme doesn't support, flag it to the user rather than adding inline styles. New styles should be added to the centralised theme, not to individual schemas.

**Spacing for `$el` elements** — because `$el` nodes bypass the theme engine, they have no automatic spacing. Without explicit margin classes, adjacent `$el` elements will run together visually.

- **Intro/instructional text divs** (wrapper `$el: "div"` containing `$el: "p"`) must have `attrs.class: "mb-4 !col-span-2"` to separate them from the fields below and to span both grid columns.
- **`$el` heading immediately after another `$el` heading** (e.g. h3 after h2) — add `mt-2` to the second heading's class to prevent them running together.
- **Computed display blocks** — wrap related score/rating elements in a parent `$el: "div"` with `attrs.class: "mt-4 mb-6 !col-span-2"` for visual separation. Use `text-2xl font-semibold` on the value display and `text-sm opacity-70` on helper text for hierarchy.

**`$el` is raw HTML — use real elements, not just `div`/`p`.** Any tag name works (FormKit renders `$el` through Vue's `h()`). Two patterns earn their keep for reference/instructional content:

- **Long reference content → a real list, not a comma run-on.** A sentence like "Sanctioned countries include: A, B, C, … N" crammed into one `$el: "p"` is hard to scan. Use `$el: "ul"` (`list-disc pl-5`) with an `$el: "li"` per item.
- **Reference content that shouldn't dominate the step → a native `<details>`/`<summary>` disclosure.** `$el: "details"` with an `$el: "summary"` child is a collapsible block with pointer text — no JS, no form state, keyboard-accessible, light/dark safe, collapsed by default (add `"open": true` to start open). Style with utility classes (the theme can't reach `$el`), and keep them to ones the build compiles (`cursor-pointer`, `select-none`, `list-disc`, `pl-5`, `opacity-70`, etc.).

```json
{
  "$el": "details",
  "attrs": { "class": "mb-4 !col-span-2" },
  "children": [
    { "$el": "summary", "attrs": { "class": "cursor-pointer select-none text-sm font-medium" }, "children": "Which countries and regions are sanctioned?" },
    { "$el": "ul", "attrs": { "class": "list-disc pl-5 mt-2 text-sm opacity-70 space-y-1" }, "children": [
      { "$el": "li", "children": "Afghanistan" },
      { "$el": "li", "children": "Belarus" }
    ] }
  ]
}
```

### Validation Messages for Long Labels

FormKit's default `required` message is `"<label> is required."`. When a field's label is a full question or long sentence — common on compliance forms ("Does your business, its Shareholders or Company Directors trade in products or services that originate from…?") — the default message echoes the entire question back, which reads badly.

Override the message per rule with `validationMessages` (an object keyed by rule name):

```json
{
  "$formkit": "radio",
  "name": "sanctioned_trade",
  "id": "sanctioned_trade",
  "label": "Does your business … trade in products or services …?",
  "validation": "required",
  "validationMessages": { "required": "This question is required" }
}
```

Apply this to every **required** field whose label is a question or long sentence (radios, sentence-labelled numbers/text/textarea). **Leave short noun labels on the default** — `"Legal Company Name is required"` is clearer than `"This question is required"` for a plainly-labelled input. Don't blanket every field; the override only earns its place where the label is too long to repeat.

`validationMessages` is per-input — there is no schema-level or form-level inheritance for it (global defaults are not configurable from a schema). For a batch rollout across many fields, edit the JSON with a script that targets fields by `name` rather than hand-editing each — radios share near-identical option blocks, so exact-string edits are error-prone.

### Regex in `matches` Validation

FormKit's string-style validation parser has two characters that **cannot appear inside `matches` regex patterns** because the parser consumes them before the regex engine ever sees them:

1. **Curly braces `{` `}`** — the expression parser treats these as its own syntax, so quantifiers like `\d{4}` or `[0-9 ]{9,12}` silently break. The regex never matches and the field becomes impossible to fill in.

2. **Pipe `|`** — the validation parser splits on `|` to separate rules (e.g. `required|matches:...`). A pipe inside a regex (e.g. `(\+?61|0)` for alternation) is split at the `|`, producing two broken partial rules. The field rejects all input.

**Rules:**
- **Never use curly-brace quantifiers** (`{n}`, `{n,m}`) — repeat the character class or `\d` explicitly instead.
- **Never use pipe `|` for alternation** — restructure the pattern to avoid it (use character classes `[ab]`, optional segments `a?b?`, or `*`/`+` quantifiers).

| Instead of | Write |
|---|---|
| `\d{4}` | `\d\d\d\d` |
| `\d{3}` | `\d\d\d` |
| `[0-9 ]{9,12}` | Spell out the grouping structure, e.g. `\d\d\d ?\d\d\d ?\d\d\d` |
| `(\+?61\|0)` | `\+?\d` or spell out as optional segments |
| `(yes\|no)` | Use a character class or restructure the logic |

For variable-length patterns (e.g. phone numbers), use `*` or `+` quantifiers instead — these are single characters and are not affected.

### Known Failure Modes

Every one of these is a real failure mode. Ordered from worst to least bad.

| Failure | Cause | Fix |
|---|---|---|
| Form save fails before request leaves the browser | Schema root is a JSON object (`{ "$formkit": "multi-step", ... }`) instead of a JSON array — the platform only accepts an array root, so the save is rejected before the request leaves the browser and the user sees only a generic "Error creating form" toast | Wrap the schema root in `[ ... ]`. Even a form with a single root multi-step node must be `[ { "$formkit": "multi-step", ... } ]` |
| App freezes (infinite loop) | `$formkit` input with computed `value` expression | Use `$el` divs for all computed displays |
| App crashes (no error) | Method chaining after `.value` (e.g. `.includes()`) | Restructure logic — use equality checks or separate fields |
| Regex validation never matches | Curly-brace quantifiers (`{4}`, `{9,12}`) in `matches` regex — FormKit's expression parser consumes the braces instead of passing them to the regex engine | Rewrite without curly braces: repeat `\d` explicitly or use `*`/`+` quantifiers |
| Regex validation rejects all input | Pipe `\|` used for alternation (e.g. `(\+?61\|0)`) inside `matches` regex — the validation parser splits on `\|` as a rule separator, producing two broken partial rules | Restructure without pipes: use character classes `[ab]`, optional segments `\+?\d`, or separate the logic |
| Conditionals silently broken | Used `$field_name` instead of `$get(id).value` | Always use `$get()` |
| `$get()` returns undefined | Trigger field missing `id` property | Add `id` to every field used in expressions |
| Fields show wrong data | Conditional node missing `key` property | Add `key` to every conditional node |
| Fields render as wrong input type across conditional sections | Multiple mutually exclusive conditional `$el: "div"` siblings — wrapper divs have `key` but child `$formkit` fields do not. Vue reuses child DOM nodes positionally across sections | Add `key` (matching `name`) to every `$formkit` field inside each conditional wrapper div, not just the wrapper itself |
| Arithmetic returns NaN | Numeric values stored as strings without `* 1` cast | Cast with `* 1` in every arithmetic expression |
| Arithmetic returns NaN (undefined) | Scoring selects with no default value — `$get(id).value` returns `undefined`, `undefined * 1 = NaN` | Set `value: "0"` on the select so the value is never undefined |
| Expression renders as literal text | `children` string starts with `(` instead of `$:` — FormKit treats it as plain text | Ensure `children` expressions always start with `$:`. Never use `\|\| 0` wrappers that add leading parentheses |
| Checkbox group conditional never triggers | Checkbox group used as conditional trigger — `$get(id).value === 'value'` compares array to string, always false | Use `radio` for Yes/No toggles. For multi-select with "Other", fold "Other" into the options array or render the "specify" text field unconditionally |
| "Select all that apply" checklist can't gate its sections (or reads as a stack of Yes/No questions) | Author used one checkbox *group* (array — can't gate) or fell back to N separate Yes/No `radio` fields (clunky UX) when each option needs to reveal its own follow-up section | Render one **single-checkbox** field per option (bare boolean, own `name`/`id`, `!col-span-1` under a shared `h3`) — looks like the intended multi-select checklist, each box gates its section with `=== true`, and each is independently filterable |
| Visible gap below checkbox group | Separate `checkbox`/`radio` sibling ("Other method used") placed above an "Other — specify" text field to gate it — the sibling consumes a full grid row with its own label, leaving an awkward gap below the main checkbox group, and it doesn't actually work as a gate when the group is a checkbox (array vs string) | Fold "Other" into the parent checkbox group's `options` array, or drop the gate entirely and show the "specify" text field unconditionally |
| Entire topic only relevant under one answer leaves a stub step | Author wrapped every field inside a step in conditional `$el: "div"` blocks — the step still appears in the progress bar with no visible content when the condition is false | Put `if` directly on the `$formkit: "step"` node (with a `key`) — FormKit Pro multi-step hides the step and removes it from the progress bar |
| Single checkbox conditional never triggers | `$get(id).value === 'true'` (string) on a single checkbox — single checkboxes return boolean `true`/`false`, not a string | Use `=== true` (boolean) in conditionals on single checkbox fields |
| `$get()` inside repeater returns wrong value | `$get()` inside repeater children resolves at form/step scope, not the current row — references the wrong field | No intra-row conditionals in JSON schemas; handle at app level if required |
| Currency displayed as raw number | Monetary field uses `$formkit: "number"` or `"text"` — no currency symbol, no locale formatting | Use `$formkit: "currency"` with `currency: "AUD"`, `displayLocale: "en-AU"`, `decimals: 2`, `minDecimals: 2`, `min: 0` |
| Date input rendered as browser-native (poor UX) | `$formkit: "date"` used — inconsistent mobile rendering, no BNDRY theming, ISO string output | Replace with `$formkit: "datepicker"` with standard BNDRY config (`clearable`, `format.date long`, `overlay`, `pickerOnly`, `sequence day`) |
| Date+time datepicker completely non-interactive | `format.time: "2-digit"` — not a valid datepicker time format value. Causes the field to lock entirely: no typing, no picker, nothing. Affects fields with `sequence: ["day", "time"]` | Use `format.time: "short"` for all date+time datepicker fields |
| File double-validation errors | `fileExt`, `fileSize`, or `fileUpload` added manually to `validation` string — BNDRY's file handling already applies these automatically | Remove manual file validation rules; the plugin handles them |
| File rejected despite being in `accept` list | `accept` includes an extension not in the plugin's supported list (e.g. `.mp4`, `.mov`, `.gif`, `.msg`, `.eml`) — the browser picker shows the file as selectable but `fileExt` validation rejects it on upload | Only use extensions from the plugin's supported list: `doc, docx, ppt, pptx, xls, xlsx, csv, txt, odt, ods, odp, pdf, jpg, jpeg, png` |
| Draft pre-fills wrong fields after schema rename | Field or step `name` changed after deployment — localStorage drafts are keyed by old names; stale values pre-populate into wrong fields | Treat `name` changes on deployed schemas as a breaking change; coordinate with users or accept drafts will be stale |
| Fields have no grid placement | `stepInnerClass` missing from step — `!col-span-1`/`!col-span-2` on fields have no effect without a CSS grid parent | Add `stepInnerClass: "grid grid-cols-2 gap-4"` to every step |
| Fields span wrong width | `$formkit` field missing `outerClass` with `!col-span-1`/`!col-span-2` | Add `outerClass: "!col-span-2"` or `"!col-span-1"` to every direct-step-child field — do not include `!max-w-none` (the theme's global outer already handles `max-w-none` for all `$formkit` inputs) |
| `$el` elements bleed to full row or collapse | `$el` node (heading, description div, conditional wrapper) missing `!col-span-2` in `attrs.class` — renders in a single grid column | Append `!col-span-2` to `attrs.class` on every `$el` direct step child |
| `$el` elements run together | Adjacent `$el` nodes (headings, text divs) have no automatic spacing from the theme engine | Add `mb-4 !col-span-2` to intro text wrapper divs, `mt-2` to h3 after h2, `mt-4 mb-6 !col-span-2` to computed display blocks |
| Adjacent headings concatenate into one line | `$el` heading with `!inline-flex` directly followed by another `$el` heading — both are inline-flex siblings so they flow side by side | Use `!block` on all h2 and h3 elements (not `!inline-flex`) |
| Unstyled section headings | `$el` headings (h2/h3) without Tailwind classes — the theme engine cannot reach `$el` nodes | Add the standard heading classes via `attrs.class` (see references/bndry-theme-reference.md for the tokens) |
| Invisible/unreadable elements | Inline `style` attributes with hardcoded colours that assume light or dark mode | Remove inline styles — rely on the centralised FormKit theme |
| Repeater `validation` silently ignored | `validation: "required"` (or any rule) set directly on a repeater node — FormKit does not apply validation to the repeater wrapper itself, so the field always passes regardless of row count | Remove `validation` from the repeater node; use `min: 1` to require at least one entry |
| Dead markup / empty divs | Remnant `$el` divs left after stripping custom UI (e.g. progress bars) — render as invisible empty elements | Remove empty `$el` nodes that have no children, attrs, or conditional logic |
| Sub-sections within a step | Multiple `$el: "h3"` headings in one step dividing it into separate topics — makes the step unfocused, harder to read, and the progress bar loses meaning | Split each topic into its own step with a single heading |
| Verbose intro blocks | Multi-paragraph instructional text inconsistent with other schemas | Condense to a single concise paragraph |
| Field name collides with step name | A field `name` matches a step `name` in the same multi-step form (e.g. step named `incident_details` and a textarea in another step also named `incident_details`) — FormKit's scope resolution can confuse the two nodes, causing wrong `$get()` resolution and garbled submitted data structure | Rename the field to something distinct (e.g. `incident_description`) — step names win the namespace |
| Saved form data lost on reload | `$formkit: "multi-step"` node has no `name` — FormKit auto-assigns an incrementing key (`multi-step_1`, `multi-step_2`, etc.) on each mount. Data saved under `multi-step_2` won't be found when the form remounts as `multi-step_1`, so the form appears blank | Add a stable `name` to the multi-step node (e.g. `"name": "incident_uar"`) so saved data is always keyed consistently |
| Datepicker rejects valid dates | Hardcoded `maxDate` or `minDate` on a datepicker (e.g. `"maxDate": "2002-12-31"` on a DOB field intended to enforce 18+) — the constraint becomes stale as time passes and blocks legitimately valid dates | Do not use hardcoded date bounds as age gates. Remove `maxDate`/`minDate` unless the field genuinely requires a fixed calendar boundary (e.g. "date must be before 2025-01-01"). Age-based validation belongs in application logic, not the schema |
| Signature canvas doesn't render or scale | `$formkit: "signature"` placed inside a `repeater` — canvas scaling doesn't work correctly within repeater rows | Place signature fields as direct step children, not inside repeaters |
| Schema class does nothing (e.g. progress bar won't hide) | A utility class used only in schema JSON — `tabsClass: "!hidden"`, an arbitrary variant, a one-off colour — isn't in BNDRY's compiled stylesheet, so the rule was never generated and the class is inert (no error) | Use a class documented in references/bndry-theme-reference.md, or ask BNDRY to enable the class for schemas. Don't debug by re-reading the schema — the schema is fine; the CSS is missing |
| Validation error echoes the whole question | Default `required` message is `"<label> is required."`; on a sentence/question label it repeats the entire question | Add `validationMessages: { "required": "This question is required" }` to that field (keep short noun labels on the default) |
| An entity type can't submit | A `required` identifier that only some `entity_type`s possess (e.g. ACN required, but Sole Trader/Partnership/Trust selected) blocks those users — they have nothing valid to enter | `required` can't be conditional in the validation string; gate a required copy behind an `if` for the applicable types, or make the field optional |
