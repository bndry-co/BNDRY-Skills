---
name: bndry-formkit-schema
description: Use when building or editing FormKit JSON schemas for BNDRY. Covers multi-step form structure, expression syntax, conditional fields, computed displays, styling, and known failure modes.
argument-hint: "[file-path] [--audit]"
---

# BNDRY FormKit Schema

A bad schema can prevent a BNDRY form from saving or rendering correctly. Follow every rule in this guide — each one addresses a specific failure mode in how the platform consumes schemas.

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

**Runtime** — BNDRY renders FormKit schemas in a Vue frontend. All FormKit docs should use the Vue flavour.

**Schema pipeline** — schemas are JSON, stored by BNDRY, and rendered dynamically. The JSON itself is the source of truth for form layout and field configuration; render-time behaviour is described in [references/bndry-theme-reference.md](references/bndry-theme-reference.md).

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
- Apply all rules from the Reference section below
- Copy and update this progress tracker as you work:

```
Schema Progress:
- [ ] Schema root is a JSON array — top-level value starts with `[` and ends with `]`. An object root is rejected by the platform and the form cannot be saved.
- [ ] Reviewed [references/bndry-theme-reference.md](references/bndry-theme-reference.md) — captures what the BNDRY theme handles automatically and what schemas must specify explicitly
- [ ] outerClass on $formkit fields contains only !col-span-1 or !col-span-2 — do NOT add !max-w-none to regular fields (the global theme outer already sets max-w-none; only the multi-step root and repeater nodes need !max-w-none because the theme constrains their width)
- [ ] $el heading classes use the same colour tokens as the theme's label section — no arbitrary colours
- [ ] Multi-step root has outerClass/wrapperClass set to "!max-w-none" (no !w-full)
- [ ] Multi-step root has tab-style: "progress" (styled by BNDRY theme — dots, connectors, dark mode)
- [ ] Multi-step root has no `allow-incomplete` property — remove if present
- [ ] Every step has stepInnerClass: "grid grid-cols-2 gap-4"
- [ ] Every $formkit field (direct step child) has outerClass: "!col-span-2" or "!col-span-1" (no !max-w-none — see above)
- [ ] Every $el direct step child has !col-span-2 in attrs.class
- [ ] Each step has at most one h3 heading by default — sub-sections only used when splitting into more steps would produce too many short steps (see Steps vs sections guidance)
- [ ] No "Section N" / numbered section headings in `$el` content — use descriptive headings or split into a step
- [ ] Distinct topics live in separate steps unless each topic is small enough that splitting would create choppy 1–2 field steps
- [ ] Conditional $el div wrappers (with if/key) have !col-span-2 in attrs.class
- [ ] No layout-only $el div wrappers (use !col-span-1 pairs on children directly)
- [ ] Repeaters have outerClass: "!max-w-none !col-span-2"
- [ ] Repeaters with short-field children have contentClass: "grid grid-cols-2 gap-4"
- [ ] No `validation` property on repeater nodes — FormKit ignores it; use `min: 1` to require at least one entry
- [ ] All $el h2 and h3 elements use !block (not !inline-flex)
- [ ] All fields have `name`
- [ ] All referenced fields have `id`
- [ ] Expressions use only `$get(id).value` (no `$field_name`)
- [ ] `children` expressions start with `$:` prefix
- [ ] No method chaining after `.value`
- [ ] No `|| 0` fallbacks in `children` expressions (causes literal text rendering)
- [ ] Select arithmetic uses `* 1` cast
- [ ] Scoring selects have default `value: "0"` to prevent NaN
- [ ] Conditional nodes have `key` property
- [ ] All `$formkit` children inside conditional `$el` wrapper divs have `key` properties
- [ ] No checkbox groups used as conditional triggers (use `radio` instead)
- [ ] Computed displays use `$el` divs (no `$formkit` with computed `value`)
- [ ] No inline `style` attributes — rely on centralised FormKit theme
- [ ] No custom colours or backgrounds on `$formkit` nodes
- [ ] No $formkit node has section-level class overrides (labelClass, inputClass, wrapperClass) that duplicate what the theme already applies
- [ ] No $el heading class contains redundant leading `block` alongside `!block` — use `!block` only
- [ ] `$el` headings have standard heading classes
- [ ] `$el` intro text divs have `mb-4 !col-span-2` spacing class
- [ ] Adjacent `$el` headings have `mt-2` spacing on the second heading
- [ ] Schema works in both light and dark mode
- [ ] No empty/dead `$el` divs or remnant markup
- [ ] Intro/instructional text is concise and consistent with other schemas
- [ ] Validation rules applied
- [ ] No curly-brace quantifiers in `matches` regex patterns
- [ ] No pipe `|` alternation in `matches` regex patterns
- [ ] Phone fields use `$formkit: "tel"` (not `"text"`)
- [ ] Date-only fields use `$formkit: "datepicker"` (not native `"date"`) with standard config (clearable, format.date long, overlay, pickerOnly, sequence day)
- [ ] No hardcoded `maxDate`/`minDate` used as age gates on datepickers — age-based validation belongs in application logic, not the schema
- [ ] Date+time fields use `$formkit: "datepicker"` with `sequence: ["day", "time"]`, `pickerOnly: true`, `overlay: true`, and `format: { "date": "long", "time": "short" }` — `"2-digit"` is not a valid time format and causes the field to be completely non-interactive
- [ ] Currency fields use `$formkit: "currency"` with `currency: "AUD"`, `displayLocale: "en-AU"`, `decimals: 2`, `minDecimals: 2`, `min: 0`
- [ ] File fields default to `multiple: true` (omit only when the field is explicitly single-file) and have an `accept` attribute; no manual fileExt/fileSize/fileUpload in validation string
- [ ] All extensions in `accept` are within BNDRY's supported list: `doc, docx, ppt, pptx, xls, xlsx, csv, txt, odt, ods, odp, pdf, jpg, jpeg, png` — video, .gif, .msg, .eml and other formats are not supported and will be rejected
- [ ] `$formkit: "signature"` fields have `outerClass: "!col-span-2"` and are not inside a repeater
- [ ] Single checkbox conditionals use `=== true` (boolean), not `=== 'true'` or `=== 'yes'`
- [ ] `id` equals `name` on every field that has both
- [ ] No `$get()` inside repeater children (resolves at form scope, not row scope)
- [ ] `dropdown` used by default for picklists, with `deselect: !required`, `selectionRemovable: !required`, `popover: true`; `select` only used for scoring fields or other narrow special cases
- [ ] Multi-step root has a stable `name` property (prevents hydration key mismatch on reload)
- [ ] No field `name` matches any step `name` in the same form (name collision)
- [ ] No duplicate field `name` values within the same step
```

---

## 4. Audit Phase (audit mode only)

Run every check below against the schema. For each violation found, report:

- **Rule violated**
- **Location** in schema (field name / JSON path)
- **Severity**: App crash, silent bug, or cosmetic
- **Fix**: Specific remediation

**Audit checklist** (ordered by severity):

1. **App crash checks:**
   - Schema root is **not** a JSON array (top-level value is an object `{ ... }` instead of `[ ... ]`)? → Wrap the existing root in `[ ... ]`. The schema root must always be an array; an object root is rejected and the form cannot be saved.
   - Any `$formkit` input with a computed `value` expression? → Use `$el` div instead
   - Any method chaining after `.value` (`.includes()`, `.length`, `.trim()`)? → Restructure logic
   - Any `children` expression string that doesn't start with `$:`? → Add `$:` prefix

2. **Silent bug checks:**
   - Any field missing a `name` property? → Add `name` — it becomes the key in submitted data and is mandatory on every field
   - Any `matches:` regex using curly-brace quantifiers (`{n}`, `{n,m}`)? → Rewrite without curly braces (see Regex in `matches` Validation)
   - Any `matches:` regex using pipe `|` for alternation (e.g. `(a|b)`)? → Restructure without pipes (see Regex in `matches` Validation)
   - Any `$get(id)` where the referenced field has no `id` property? → Add `id`
   - Any conditional node missing a `key` property? → Add `key`
   - Any `$formkit` fields inside conditional `$el` wrapper divs missing `key` properties? → Add `key` matching field `name`
   - Any `$field_name` references instead of `$get(id).value`? → Replace with `$get()`
   - Any checkbox group used as a conditional trigger (`$get(checkbox_id).value === 'value'`)? → Replace with `radio` input
   - Any scoring select without a default `value: "0"`? → Add default value
   - Any arithmetic on select values without `* 1` cast? → Add `* 1`
   - Any `|| 0` fallback in a `children` expression? → Remove and use default values instead
   - Any field `name` that matches a step `name` anywhere in the same multi-step form? → Rename the field — FormKit's scope resolution can confuse the step node with the field, causing `$get()` to resolve the wrong node and producing unexpected data structure or silent mismatch
   - Any duplicate field `name` values within the same step? → Each `name` must be unique within its step
   - `$formkit: "multi-step"` node missing a `name` property? → Add a unique stable name (e.g. `"name": "incident_uar"`) — without it FormKit auto-assigns an incrementing key (`multi-step_1`, `multi-step_2`, etc.) on each mount, so saved data keyed under one mount is not found on the next
   - Any field where `id` and `name` differ? → Make them match — diverging values create a confusing disconnect between expression scoping and submitted data keys
   - Any `$get()` used inside a repeater's children? → Remove; `$get()` resolves at form/step scope, not the current repeater row, so the result is always the form-level value — intra-row conditionals must be handled at the app level
   - Any repeater node with a `validation` property? → Remove it — FormKit does not apply validation to the repeater wrapper; use `min: 1` to require at least one entry
   - Any single checkbox conditional using `=== 'true'` or `=== 'yes'` instead of `=== true`? → Fix to boolean comparison — single checkboxes return `true`/`false`, not strings
   - Any step whose entire content is wrapped in conditional `$el: "div"` blocks driven by the same expression? → Move the `if` (and a `key`) onto the `$formkit: "step"` node itself so the step is hidden from the progress bar when not applicable, instead of rendering an empty step
   - Any separate `checkbox`/`radio` sibling field used to gate an "Other — specify" text input below a checkbox group? → Fold "Other" into the parent checkbox group's `options` array, or render the "specify" text field unconditionally — the sibling field creates a visible gap and (for checkbox groups) can't gate the conditional anyway

3. **Input type / Australian defaults checks:**
   - Any `$formkit: "date"` field? → Replace with `$formkit: "datepicker"` using the standard BNDRY config (`clearable`, `format: { date: "long" }`, `overlay`, `pickerOnly`, `sequence: ["day"]`)
   - Any `$formkit: "datepicker"` with `"time"` in its `sequence` using `format.time: "2-digit"`? → Change to `format.time: "short"` — `"2-digit"` is not a valid value and causes the field to be completely non-interactive (no typing, no picker)
   - Any `$formkit: "datepicker"` with a hardcoded `maxDate` or `minDate` used as an age gate (e.g. `"maxDate": "2002-12-31"` to enforce 18+)? → Remove — hardcoded date bounds become stale over time and block valid dates; age-based validation belongs in application logic
   - Any monetary amount field using `$formkit: "text"` or `$formkit: "number"`? → Replace with `$formkit: "currency"` with `currency: "AUD"`, `displayLocale: "en-AU"`, `decimals: 2`, `minDecimals: 2`, `min: 0`
   - Any `$formkit: "currency"` field missing `currency: "AUD"` or `displayLocale: "en-AU"`? → Add BNDRY defaults
   - Any `$formkit: "currency"` field missing `minDecimals: 2`? → Add it — without it the field displays an integer (no cents) even though `decimals: 2` is set
   - Any file field with `fileExt`, `fileSize`, or `fileUpload` in the `validation` string? → Remove — these are applied automatically; manual addition causes double-validation errors
   - Any file field missing `multiple: true`? → Add it unless the field is explicitly single-file (e.g. single ID document, single profile photo) — `multiple: true` is the default for BNDRY file fields
   - Any file field missing an `accept` attribute where a specific type restriction is appropriate? → Add extension filter (BNDRY's default accepted list is broad; `accept` narrows the picker dialog to guide users)
   - Any `accept` value containing extensions outside BNDRY's supported list (video formats, `.gif`, `.msg`, `.eml`, etc.)? → Remove them — extension validation will reject these files regardless of what appears in the picker
   - Any `$formkit: "select"` used for a non-scoring picklist? → Replace with `$formkit: "dropdown"` and set `deselect: !required`, `selectionRemovable: !required`, `popover: true`. `select` is reserved for scoring fields (where arithmetic on string option values matters) and other narrow special cases
   - Any `$formkit: "signature"` inside a `repeater`? → Move outside — canvas inputs do not scale correctly within repeater rows
   - Any `$formkit: "signature"` missing `outerClass: "!col-span-2"`? → Add it

4. **Layout / configuration checks:**
   - Root multi-step node missing `tab-style: "progress"`? → Add it (the BNDRY theme styles progress dots, connectors, visited state, and dark mode under `data-[tab-style=progress]`)
   - Any root multi-step node with `allow-incomplete` property? → Remove it; this attribute must not appear in deployed schemas
   - Root multi-step missing `outerClass: "!max-w-none"` or `wrapperClass: "!max-w-none"`? → Add them (theme constrains multi-step width without these)
   - Any root multi-step with `!w-full` in `outerClass` or `wrapperClass`? → Strip to `"!max-w-none"`
   - Any step missing `stepInnerClass: "grid grid-cols-2 gap-4"`? → Add it
   - Any `$formkit` field (direct step child) missing `outerClass`? → Add `outerClass: "!col-span-2"` (or `!col-span-1` if it pairs with a sibling)
   - Any `$el` direct step child without `!col-span-2` in `attrs.class`? → Append `!col-span-2`
   - Any conditional `$el: "div"` wrapper (has `if`/`key`) missing `!col-span-2` in `attrs.class`? → Add `"attrs": {"class": "!col-span-2"}`
   - Any layout-only `$el: "div"` wrapper (no `if`, no `key`, no meaningful class) grouping fields? → Remove the wrapper; give children `!col-span-1` or `!col-span-2` directly
   - Any step containing more than one `$el: "h3"` heading (sub-sections within a step)? → Default response: split into separate steps. Only keep the multi-heading step if splitting would produce very short (<3 field) steps and the sub-headings genuinely belong on the same topic — see Steps vs sections guidance
   - Any `$el` heading text starting with "Section N", "Part N", or similar numbered-section labelling? → Rename to a descriptive heading, or split the content into a separate step. Numbered sections inside a step are almost always a sign the form should have been multi-step in the first place
   - Any repeater (direct step child) missing `outerClass: "!max-w-none !col-span-2"`? → Add it
   - Any repeater with short-field children missing `contentClass: "grid grid-cols-2 gap-4"`? → Add it and give child fields appropriate `!col-span-1`/`!col-span-2`
   - Any `$el: "h2"` or `$el: "h3"` with `!inline-flex` in `attrs.class`? → Change to `!block`
   - Any phone field using `$formkit: "text"` instead of `"tel"`? → Change to `tel`

5. **Theme compatibility checks** (cross-reference [references/bndry-theme-reference.md](references/bndry-theme-reference.md)):
   - Any `outerClass` on a `$formkit` field containing `!max-w-none`? → Remove it — the global theme outer already sets `max-w-none` for all `$formkit` inputs; `!max-w-none` is only needed on the multi-step root and repeater nodes where the theme constrains their width
   - Any `outerClass` on a `$formkit` field containing classes other than `!col-span-1`, `!col-span-2`? → Other classes risk duplicating or conflicting with theme-applied classes; remove unless there's a documented reason
   - Any `$el` heading using colour classes that don't match the theme's label colour tokens? → Replace with the label colour tokens (see [references/bndry-theme-reference.md](references/bndry-theme-reference.md))
   - Any `$el` heading class containing the redundant leading `block` alongside `!block`? → Remove `block`, keep only `!block`
   - Any `$formkit` node with section-level class overrides (`labelClass`, `inputClass`, `wrapperClass`) that duplicate what the theme already applies? → Remove the redundant override

6. **Styling/cosmetic checks:**
   - Any inline `style` attributes? → Remove, rely on the centralised theme
   - Any `$el` heading (h2/h3) without the standard Tailwind heading classes? → Add classes
   - Any `$el` intro text div without `class: "mb-4 !col-span-2"`? → Add spacing and col-span
   - Any `$el` heading immediately after another heading without `mt-2` on the second heading? → Add spacing
   - Any hardcoded colours or backgrounds on `$formkit` nodes? → Remove
   - Any empty/dead `$el` divs with no children or attrs? → Remove
   - Any verbose multi-paragraph intro text? → Condense to single paragraph
   - Any club/venue/brand-specific names in labels, option values, help text, or placeholders (e.g. "Souths", "The Juniors", "Easts", "Top 30 [Venue]", "[Club] Loyalty Member")? → Flag to the user and ask whether to genericise — schemas are reused across tenants
   - Any uses of "gambler" / "gambling" terminology where "player" / "gaming" would fit? → Replace with the neutral term unless quoting legislation verbatim

---

## 5. Output

- **Build mode**: Output the complete JSON schema, ready to paste into BNDRY
- **Edit mode**: Apply edits to the file using the Edit tool (or output the modified JSON if working with pasted content)
- **Audit mode**: Output a findings report grouped by severity

---

## Reference — Rules

### Form Skeleton

Every BNDRY form must use the multi-step skeleton for full-width rendering. Use [multi-step-skeleton.json](templates/multi-step-skeleton.json) as a starting point.

**The schema root must be a JSON array** — the top-level value must start with `[` and end with `]`, even when the form has a single root multi-step node. A schema whose root is a JSON object (e.g. `{ "$formkit": "multi-step", ... }` instead of `[ { "$formkit": "multi-step", ... } ]`) is rejected by the platform and the form cannot be saved.

The centralised theme constrains multi-step form width by default. To get full-width rendering, add `outerClass` and `wrapperClass` directly on the multi-step node — do **not** use `sections-schema` attrs (they don't override the theme):

```json
"tab-style": "progress",
"outerClass": "!max-w-none",
"wrapperClass": "!max-w-none"
```

**`tab-style: "progress"`** must be set on every multi-step root. The BNDRY theme provides full styling for this mode via `data-[tab-style=progress]` selectors: step indicator dots, connecting lines between steps, active/visited colour changes, and dark mode variants. These styles only activate when `tab-style` is set — omitting it leaves the tab bar unstyled.

Each step needs a `name` and a short `label` (appears in the tab bar).

**Draft autosave** — BNDRY auto-saves form state to localStorage. On reload, users are prompted to continue their draft or discard it. **Renaming fields or steps** in a schema after a form has been deployed causes existing user drafts to pre-populate stale values into the wrong fields. Treat `name` changes on deployed schemas as a breaking change — coordinate with users or accept that in-progress drafts will be stale.

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
- **`select` vs `dropdown`**: Default to `$formkit: "dropdown"` (FormKit Pro) for all picklists — short fixed lists, long lists, and searchable lists alike. Standard BNDRY attrs: `deselect: !required`, `selectionRemovable: !required`, `popover: true`. Use `$formkit: "select"` only for narrow special cases — primarily **scoring fields**, where option values feed arithmetic expressions (`* 1` casts, `$get(id).value` summed across fields) and the native `select` is a better fit than the Pro dropdown.
- **Keep validation co-located** with the inputs that own it — don't centralise validation rules in a separate structure.
- **Prefer `form`, `group`, and `list` composition** over manual object or array assembly in submit handlers.

**Available input types:**

Standard: `text`, `textarea`, `select`, `radio`, `checkbox`, `date`, `datetime-local`, `file`, `number`, `email`, `tel`, `url`, `hidden`

FormKit Pro: `datepicker`, `dropdown`, `repeater`, `currency`, `mask`, `autocomplete`, `slider`, `rating`, `taglist`, `toggle`, `togglebuttons`, `colorpicker`, `transferList`, `unit`

BNDRY custom: `signature`

**FormKit Pro inputs** are available in BNDRY schemas with no additional setup needed. When recommending or implementing a Pro input, mention that it is a Pro input in any user-facing summary.

### Theme compatibility

The full reference for what the BNDRY theme handles automatically and what schemas must specify is at [references/bndry-theme-reference.md](references/bndry-theme-reference.md). Read it before building or auditing.

**Quick reference** — safe `outerClass` values for `$formkit` fields:

```
"outerClass": "!col-span-2"   ← full-width
"outerClass": "!col-span-1"   ← half-width pair
```

Do not add `!max-w-none` to regular field `outerClass` — the BNDRY theme applies `max-w-none` to every `$formkit` input by default. `!max-w-none` is only needed on the multi-step root and repeater nodes, where the theme constrains their width.

Do not add spacing, colour, display, or border classes to `outerClass` — the theme handles those for `$formkit` nodes.

Locale is `en-AU`; textareas auto-expand (do not set fixed heights); `multi-step` and `step` inputs are available; FormKit Pro inputs are pre-registered.

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
- **BNDRY style reference** — all prose-bearing fields (`help`, `placeholder`, `$el` heading text) must follow `references/bndry-style-reference.md`. Read it before writing those values. Key rules: sentence case, Australian English (`-ise`, `-our`, `-re`), no full stops inside acronyms, single space after full stops, no banned filler phrases (`please note`, `in order to`, `utilise`, `leverage`).
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

All `$formkit: "file"` inputs are automatically enhanced by BNDRY's file handling. Understanding what is applied automatically prevents double-handling and misuse.

**What is applied automatically:**
- File extension validation — rejects files with unsupported extensions or double extensions (e.g. `file.backup.pdf`).
- File size validation — rejects files over the configured limit.
- A file viewer is rendered below the input showing uploaded files with preview/download.
- Already-uploaded files are not re-validated on form re-render.

**Supported extensions** — only these types are permitted. Any extension outside this list will be rejected on validation, regardless of what `accept` shows in the picker:

```
doc, docx, ppt, pptx, xls, xlsx, csv, txt, odt, ods, odp, pdf, jpg, jpeg, png
```

Video formats (`.mp4`, `.mov`, `.avi`, `.mkv`), email formats (`.msg`, `.eml`), GIF (`.gif`), and all other formats are **not supported** and must not appear in `accept`.

**Default accepted extensions** (when no `accept` is specified): all of the above.

**Key props to set explicitly:**

- **`accept`** — comma-separated extension list (e.g. `".pdf,.png,.jpg,.jpeg"`). Controls the **browser's file picker dialog only** — the platform's extension validation enforces the actual restriction. Always specify `accept` to guide the user; it must be a subset of the supported extensions listed above — any extension not in that list will appear in the picker but be rejected on validation.
- **`multiple: true`** — allows multiple files in one field. **Default to `multiple: true` for all file fields** unless the field is explicitly single-file (e.g. a single ID document, single profile photo). Most real-world document uploads benefit from accepting multiples, so the burden is on justifying a single-file field, not on enabling multiple.
- **`validation: "required"`** — works as expected; field is invalid until at least one file is attached or already uploaded.

**Do not** add `fileExt`, `fileSize`, or `fileUpload` to the `validation` string — these are applied automatically. Adding them manually causes double-validation errors.

---

### Signature Input Rules

BNDRY includes a custom `$formkit: "signature"` input. It provides canvas-based signature capture, stores the drawn signature as a file reference, and supports a re-sign flow on previously captured signatures.

**Available props:**
- `penColor` — ink colour (default: `'navy'`). Leave unset to use the BNDRY default.
- `backgroundColor` — canvas background colour. Leave unset to use the theme default.
- `strokeWidth` — line width for the signature stroke. Leave unset to use the default.

**Rules:**
- Use `outerClass: "!col-span-2"` like all other direct step children.
- `validation: "required"` works and marks the field invalid until a signature is drawn and saved.
- The stored value is a **file reference** — not a base64 data URL or string. Treat it like a file field value.
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

**Multi-select with an "Other" option** — do **not** add a separate sibling `checkbox`/`radio` ("Other method used") above the "specify" text field. That sibling renders as a full grid row with its own label, leaving a visible vertical gap below the main checkbox group, and the checkbox-group-can't-gate-conditionals problem means you can't use the group itself anyway. Two cleaner options:

1. **Fold "Other" into the same options array** of the parent checkbox group (preferred when the "specify" field is short or can be always-visible). The "Other" option is just another value alongside the rest.
2. **Always render the "specify" text field** unconditionally below the checkbox group. Skipping the gating logic entirely avoids the gap and the array-vs-string footgun.

**Single checkbox fields** (no `options` — a bare boolean toggle) return `true` or `false`, not a string. Conditional expressions must use `=== true` (boolean):

```json
"if": "$get(some_checkbox).value === true"
```

Do **not** write `=== 'true'` or `=== 'yes'` — the condition will silently never trigger. This is different from `radio` and `select` inputs where values are always strings.

**`$get()` inside repeater children** — `$get()` resolves at the **form/step scope**, not the current repeater row. You cannot use `$get()` to reference a sibling field within the same repeater row. There is no safe way to implement intra-row conditionals in FormKit JSON schemas. If intra-row conditional logic is required, it must be handled at the app level.

### Computed Display Fields

- **NEVER** use a `$formkit` input with a `value` expression for calculated fields — this creates an infinite re-render loop that bricks the app.
- Use `$el` divs instead — they render the expression result without feeding it back into form state.
- For banded ratings (Low / Medium / High), use nested `if/then/else` objects in the `children` property of an `$el` div.
- The full sum expression must be **repeated in every `if` condition** — there is no way to store intermediate values in FormKit schema.

### Styling conventions

BNDRY has a **centralised FormKit theme** that applies Tailwind classes for every `$formkit` input based on its type and section. The theme handles all styling for `$formkit` nodes — schemas must not override it.

**Core rules:**

- **No inline `style` attributes** on any schema node. Inline styles override the centralised theme and prevent rolling out fixes and improvements across all schemas.
- **No custom colours, backgrounds, or borders** on `$formkit` nodes. The theme handles these and must be the single source of truth.
- **Dark/light mode agnosticism** — schemas must work in both themes. Never hardcode colours that assume light or dark mode. The centralised theme already handles dark mode via Tailwind's `dark:` variants.

**`$el` elements** (divs, headings, paragraphs) are raw HTML — the FormKit theme engine does not reach them. Without explicit classes, `$el` nodes render as unstyled browser-default HTML.

**Section headings** (`$el: "h3"` or `$el: "h2"`) therefore need Tailwind classes applied via `attrs.class`. Both h2 and h3 use `!block`. All headings are direct step children inside a CSS grid, so they also need `!col-span-2`. The colour tokens must match the BNDRY label colour tokens — see [references/bndry-theme-reference.md](references/bndry-theme-reference.md) for the canonical pattern. Example:

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

Replace `<label-colour-tokens>` and `<label-dark-tokens>` with the actual text colour and dark mode classes from the theme's `label` section (e.g. if the theme label uses `text-midnight-700` and `dark:text-midnight-300`, use those).

Use the inline class pattern above. Do not invent new colour values — read the actual tokens from the theme and apply them as written.

- Do not wrap headings in a parent `$el: "div"` — use the `h3` directly as a child of the step.
- If a schema needs visual treatment that the current theme doesn't support, flag it to the user rather than adding inline styles. New styles should be added to the centralised theme, not to individual schemas.

**Spacing for `$el` elements** — because `$el` nodes bypass the theme engine, they have no automatic spacing. Without explicit margin classes, adjacent `$el` elements will run together visually.

- **Intro/instructional text divs** (wrapper `$el: "div"` containing `$el: "p"`) must have `attrs.class: "mb-4 !col-span-2"` to separate them from the fields below and to span both grid columns.
- **`$el` heading immediately after another `$el` heading** (e.g. h3 after h2) — add `mt-2` to the second heading's class to prevent them running together.
- **Computed display blocks** — wrap related score/rating elements in a parent `$el: "div"` with `attrs.class: "mt-4 mb-6 !col-span-2"` for visual separation. Use `text-2xl font-semibold` on the value display and `text-sm opacity-70` on helper text for hierarchy.

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

### Common pitfalls

Each row below is a recurring schema authoring mistake. Apply the corresponding fix when generating or auditing schemas. Ordered roughly by severity (most disruptive first).

| Failure | Cause | Fix |
|---|---|---|
| Form save fails before request leaves the browser | Schema root is a JSON object (`{ "$formkit": "multi-step", ... }`) instead of a JSON array. The schema root must always be a JSON array; an object root is rejected client-side and the user sees a generic "Error creating form" toast | Wrap the schema root in `[ ... ]`. Even a form with a single root multi-step node must be `[ { "$formkit": "multi-step", ... } ]` |
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
| Visible gap below checkbox group | Separate `checkbox`/`radio` sibling ("Other method used") placed above an "Other — specify" text field to gate it — the sibling consumes a full grid row with its own label, leaving an awkward gap below the main checkbox group, and it doesn't actually work as a gate when the group is a checkbox (array vs string) | Fold "Other" into the parent checkbox group's `options` array, or drop the gate entirely and show the "specify" text field unconditionally |
| Entire topic only relevant under one answer leaves a stub step | Author wrapped every field inside a step in conditional `$el: "div"` blocks — the step still appears in the progress bar with no visible content when the condition is false | Put `if` directly on the `$formkit: "step"` node (with a `key`) — FormKit Pro multi-step hides the step and removes it from the progress bar |
| Single checkbox conditional never triggers | `$get(id).value === 'true'` (string) on a single checkbox — single checkboxes return boolean `true`/`false`, not a string | Use `=== true` (boolean) in conditionals on single checkbox fields |
| `$get()` inside repeater returns wrong value | `$get()` inside repeater children resolves at form/step scope, not the current row — references the wrong field | No intra-row conditionals in JSON schemas; handle at app level if required |
| Currency displayed as raw number | Monetary field uses `$formkit: "number"` or `"text"` — no currency symbol, no locale formatting | Use `$formkit: "currency"` with `currency: "AUD"`, `displayLocale: "en-AU"`, `decimals: 2`, `minDecimals: 2`, `min: 0` |
| Date input rendered as browser-native (poor UX) | `$formkit: "date"` used — inconsistent mobile rendering, no BNDRY theming, ISO string output | Replace with `$formkit: "datepicker"` with standard BNDRY config (`clearable`, `format.date long`, `overlay`, `pickerOnly`, `sequence day`) |
| Date+time datepicker completely non-interactive | `format.time: "2-digit"` — not a valid datepicker time format value. Causes the field to lock entirely: no typing, no picker, nothing. Affects fields with `sequence: ["day", "time"]` | Use `format.time: "short"` for all date+time datepicker fields |
| File double-validation errors | `fileExt`, `fileSize`, or `fileUpload` added manually to `validation` string — file fields already have these applied automatically | Remove manual file validation rules; they are applied for you |
| File rejected despite being in `accept` list | `accept` includes an extension that BNDRY does not accept (e.g. `.mp4`, `.mov`, `.gif`, `.msg`, `.eml`) — the browser picker shows the file as selectable but extension validation rejects it on upload | Only use extensions from BNDRY's supported list: `doc, docx, ppt, pptx, xls, xlsx, csv, txt, odt, ods, odp, pdf, jpg, jpeg, png` |
| Draft pre-fills wrong fields after schema rename | Field or step `name` changed after deployment — localStorage drafts are keyed by old names; stale values pre-populate into wrong fields | Treat `name` changes on deployed schemas as a breaking change; coordinate with users or accept drafts will be stale |
| Fields have no grid placement | `stepInnerClass` missing from step — `!col-span-1`/`!col-span-2` on fields have no effect without a CSS grid parent | Add `stepInnerClass: "grid grid-cols-2 gap-4"` to every step |
| Fields span wrong width | `$formkit` field missing `outerClass` with `!col-span-1`/`!col-span-2` | Add `outerClass: "!col-span-2"` or `"!col-span-1"` to every direct-step-child field — do not include `!max-w-none` (the theme's global outer already handles `max-w-none` for all `$formkit` inputs) |
| `$el` elements bleed to full row or collapse | `$el` node (heading, description div, conditional wrapper) missing `!col-span-2` in `attrs.class` — renders in a single grid column | Append `!col-span-2` to `attrs.class` on every `$el` direct step child |
| `$el` elements run together | Adjacent `$el` nodes (headings, text divs) have no automatic spacing from the theme engine | Add `mb-4 !col-span-2` to intro text wrapper divs, `mt-2` to h3 after h2, `mt-4 mb-6 !col-span-2` to computed display blocks |
| Adjacent headings concatenate into one line | `$el` heading with `!inline-flex` directly followed by another `$el` heading — both are inline-flex siblings so they flow side by side | Use `!block` on all h2 and h3 elements (not `!inline-flex`) |
| Unstyled section headings | `$el` headings (h2/h3) without Tailwind classes — the theme engine cannot reach `$el` nodes | Add the standard heading classes via `attrs.class` (see the inline-class pattern in the `$el` Headings section) |
| Invisible/unreadable elements | Inline `style` attributes with hardcoded colours that assume light or dark mode | Remove inline styles — rely on the centralised FormKit theme |
| Repeater `validation` silently ignored | `validation: "required"` (or any rule) set directly on a repeater node — FormKit does not apply validation to the repeater wrapper itself, so the field always passes regardless of row count | Remove `validation` from the repeater node; use `min: 1` to require at least one entry |
| Dead markup / empty divs | Remnant `$el` divs left after stripping custom UI (e.g. progress bars) — render as invisible empty elements | Remove empty `$el` nodes that have no children, attrs, or conditional logic |
| Sub-sections within a step | Multiple `$el: "h3"` headings in one step dividing it into separate topics — makes the step unfocused, harder to read, and the progress bar loses meaning | Split each topic into its own step with a single heading |
| Verbose intro blocks | Multi-paragraph instructional text inconsistent with other schemas | Condense to a single concise paragraph |
| Field name collides with step name | A field `name` matches a step `name` in the same multi-step form (e.g. step named `incident_details` and a textarea in another step also named `incident_details`) — FormKit's scope resolution can confuse the two nodes, causing wrong `$get()` resolution and garbled submitted data structure | Rename the field to something distinct (e.g. `incident_description`) — step names win the namespace |
| Saved form data lost on reload | `$formkit: "multi-step"` node has no `name` — FormKit auto-assigns an incrementing key (`multi-step_1`, `multi-step_2`, etc.) on each mount. Data saved under `multi-step_2` won't be found when the form remounts as `multi-step_1`, so the form appears blank | Add a stable `name` to the multi-step node (e.g. `"name": "incident_uar"`) so saved data is always keyed consistently |
| Datepicker rejects valid dates | Hardcoded `maxDate` or `minDate` on a datepicker (e.g. `"maxDate": "2002-12-31"` on a DOB field intended to enforce 18+) — the constraint becomes stale as time passes and blocks legitimately valid dates | Do not use hardcoded date bounds as age gates. Remove `maxDate`/`minDate` unless the field genuinely requires a fixed calendar boundary (e.g. "date must be before 2025-01-01"). Age-based validation belongs in application logic, not the schema |
| Signature canvas doesn't render or scale | `$formkit: "signature"` placed inside a `repeater` — the `ResizeObserver`-based canvas scaling doesn't work correctly within repeater rows | Place signature fields as direct step children, not inside repeaters |
