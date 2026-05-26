# BNDRY FormKit theme reference

This document describes how BNDRY renders FormKit schemas — what styling and behaviour the platform applies automatically, and what schema authors are responsible for. It is the bundled source of truth for theme-related decisions when building or auditing schemas. The rules below capture observed runtime behaviour, not implementation details.

If something visual is wrong with a schema and the cause is not covered here, the answer is almost always one of: a missing `outerClass`, a missing `!col-span-2` on an `$el` node, a missing `stepInnerClass` on a step, or an inline `style` attribute fighting the theme.

---

## What the BNDRY theme handles automatically

BNDRY applies a centralised theme to every `$formkit` input. Schema authors **must not duplicate or override** the following — they are handled for you:

- **Input styling** — backgrounds, borders, focus rings, error states, validation message styling, and dark mode variants are all applied automatically to `$formkit` nodes.
- **Width sizing** — by default, every `$formkit` input is set to `max-w-none`. You do not need to add this class to fields.
- **Label colour and weight** — labels use a consistent token across the form. `$el` heading text should match this token (see [Heading classes](#heading-classes)).
- **Button appearance** — submit buttons, multi-step prev/next buttons, and repeater add buttons are styled by the theme. Do not add button-related class overrides.
- **Dark mode** — the theme handles dark/light variants automatically. Schemas must not hardcode colours that assume one mode.
- **Multi-step tab styling** — when `tab-style: "progress"` is set on the multi-step root, the theme provides step indicator dots, connecting lines, active and visited colour changes, and dark mode variants. These styles do not activate without the `tab-style` attribute.
- **Repeater layout chrome** — the wrapper, add-item button, and per-entry framing are styled by the theme.

The theme does **not** set the following on fields or steps — schema authors must specify them where needed:

- `col-span` (any variant — `col-span-1`, `col-span-2`, `!col-span-2`)
- `grid`, `grid-cols-*`, or `gap-*`
- `stepInnerClass` (no default — must be set on every step)

Because the theme sets none of these, adding them in `outerClass` / `contentClass` / `stepInnerClass` is safe and has zero conflict risk.

---

## What schemas must specify

### Safe `outerClass` values for `$formkit` fields

Only these values should appear in `outerClass` on a regular `$formkit` field:

```
"outerClass": "!col-span-2"   ← full-width
"outerClass": "!col-span-1"   ← half-width pair
```

**Do not** add `!max-w-none` to regular field `outerClass` — the theme already applies `max-w-none` globally. `!max-w-none` is needed **only** on:

- The multi-step root node (the theme constrains its width)
- Repeater nodes (the theme constrains their width)

**Do not** add spacing, colour, display, or border classes to `outerClass`. The theme handles those.

### Multi-step root

Every BNDRY form uses the multi-step plugin. The multi-step root node must include:

```json
{
  "$formkit": "multi-step",
  "name": "<stable_form_name>",
  "tab-style": "progress",
  "outerClass": "!max-w-none",
  "wrapperClass": "!max-w-none",
  "steps-class": "...",
  "children": [ ... ]
}
```

- **`name`** — required. Without a stable `name`, draft autosave keys collide on remount and saved values are lost.
- **`tab-style: "progress"`** — required. Activates the styled progress indicators.
- **`outerClass` and `wrapperClass: "!max-w-none"`** — required. The theme constrains multi-step width without these.
- **No `allow-incomplete`** — this attribute must not be present in deployed schemas.
- **No `!w-full`** — strip if present; use `!max-w-none` instead.

### Steps

Each step is a `$formkit: "step"` node with:

```json
{
  "$formkit": "step",
  "name": "<step_name>",
  "label": "<short label>",
  "stepInnerClass": "grid grid-cols-2 gap-4",
  "children": [ ... ]
}
```

- **`stepInnerClass: "grid grid-cols-2 gap-4"`** — required on every step. Without it, `!col-span-1` and `!col-span-2` on children have no effect.
- **`name`** — required. Becomes part of the data key for the step's fields.
- **`label`** — required. Appears in the progress bar.

### Direct step children

Inside a step, every direct child must declare its grid placement:

- **`$formkit` fields** — `outerClass: "!col-span-2"` (full width) or `"!col-span-1"` (half width, paired with a sibling). No `!max-w-none`.
- **`$el` nodes** (headings, description divs, conditional wrappers) — `attrs.class` must include `!col-span-2`.

If you omit grid placement on an `$el` direct child, it renders in a single grid column and looks broken.

### Conditional wrappers

Conditional `$el: "div"` wrappers (nodes with `if` and `key`) must include `!col-span-2` in `attrs.class`:

```json
{
  "$el": "div",
  "if": "$get(some_field).value === 'yes'",
  "key": "some_conditional_block",
  "attrs": { "class": "!col-span-2" },
  "children": [ ... ]
}
```

Layout-only `$el: "div"` wrappers (no `if`, no `key`, no meaningful class — used purely to group fields) must be removed. Apply `!col-span-1`/`!col-span-2` to the children directly.

### Repeaters

Repeaters that are direct step children need:

```json
{
  "$formkit": "repeater",
  "outerClass": "!max-w-none !col-span-2",
  ...
}
```

If the repeater's children are short fields (e.g. paired name + contact fields), add `contentClass: "grid grid-cols-2 gap-4"` to enable a two-column grid inside each row, and give each child an appropriate `!col-span-1` or `!col-span-2`.

Do not add `validation` directly to a repeater node — it is ignored. Use `min: 1` to require at least one entry.

### Heading classes

`$el` headings are raw HTML and the theme engine cannot reach them. Apply the label colour tokens explicitly via `attrs.class`. Use the pattern below as the template:

```json
{
  "$el": "h2",
  "attrs": { "class": "<label-colour> font-bold <dark-label-colour> !block mb-1.5 formkit-label !col-span-2" },
  "children": "Step Title"
}
```

```json
{
  "$el": "h3",
  "attrs": { "class": "<label-colour> font-bold <dark-label-colour> !block mb-1.5 mt-2 formkit-label !col-span-2" },
  "children": "Section Title"
}
```

- Use `!block` on every h2 and h3. Not `!inline-flex`.
- Do not include a redundant leading `block` alongside `!block` — keep only `!block`.
- Both heading levels need `!col-span-2`.
- h3 immediately after another heading should add `mt-2`.

### Spacing for `$el` elements

`$el` nodes have no automatic spacing — adjacent `$el` elements run together without explicit margin classes.

- **Intro/instructional text divs** — `attrs.class: "mb-4 !col-span-2"`.
- **Computed display blocks** — wrap related score/rating elements in a parent `$el: "div"` with `attrs.class: "mt-4 mb-6 !col-span-2"`. Use `text-2xl font-semibold` on the value display and `text-sm opacity-70` on helper text for hierarchy.

---

## Style overrides to avoid

Schemas must never:

- Add **inline `style` attributes** on any node. Inline styles prevent rolling out theme fixes across schemas.
- Override **section-level classes** (`labelClass`, `inputClass`, `wrapperClass`) on `$formkit` nodes — these duplicate or conflict with theme-applied classes.
- Add **hardcoded colours or backgrounds** on `$formkit` nodes — the theme handles all of this.
- Use **hardcoded colours that assume light or dark mode** — schemas must work in both.

If a schema needs visual treatment the theme doesn't support, flag it to your BNDRY contact rather than adding inline classes. New styles belong in the theme, not in individual schemas.

---

## Inputs available in BNDRY schemas

### Standard inputs

`text`, `textarea`, `select`, `radio`, `checkbox`, `date`, `datetime-local`, `file`, `number`, `email`, `tel`, `url`, `hidden`.

### FormKit Pro inputs

These are pre-registered in BNDRY and available for use in schemas (no additional setup required):

`datepicker`, `dropdown`, `repeater`, `currency`, `mask`, `autocomplete`, `slider`, `rating`, `taglist`, `toggle`, `togglebuttons`, `colorpicker`, `transferList`, `unit`.

When recommending or implementing a Pro input, mention that it is a Pro input in any user-facing summary.

### BNDRY custom inputs

- **`signature`** — canvas-based signature capture. Stores a file reference (not a base64 string). Must not be placed inside a repeater (canvas inputs do not scale correctly within repeater rows).

### Plugin behaviour you can rely on

- **Textareas auto-expand** — do not set fixed heights on `textarea` inputs.
- **File inputs** — extension validation and size validation are applied automatically. Do not add `fileExt`, `fileSize`, or `fileUpload` to the `validation` string (causes double-validation errors). Supported extensions: `doc`, `docx`, `ppt`, `pptx`, `xls`, `xlsx`, `csv`, `txt`, `odt`, `ods`, `odp`, `pdf`, `jpg`, `jpeg`, `png`. Any other extension will be rejected on upload regardless of what `accept` shows.
- **Draft autosave** — form state is autosaved to localStorage. Renaming a field or step in a deployed schema causes existing user drafts to pre-populate stale values into the wrong fields. Treat `name` changes on deployed schemas as breaking.

### Locale

BNDRY runs with `en-AU` as the locale. Use Australian conventions in labels, placeholders, and validation messages.
