---
name: bndry-custom-fields-schema
description: Generate BNDRY custom field schemas (JSON) from freeform notes, lists, or CSVs describing fields to add to Individual, Company, or Trust entities in BNDRY. Use whenever the user mentions custom fields, extending the BNDRY data model, adding fields to entities, CustomFieldSetting, CustomFieldSchema, or pastes a CSV/list of fields they want to capture. Also trigger when someone says "add a custom field for X in BNDRY", "extend the individual entity with Y", "I need a schema for Z in our tenant", or asks to write JSON that will be pasted into BNDRY's Settings page. The output is a `CustomFieldSchema` JSON object (a top-level `groups` array) ready to paste into BNDRY's Settings UI.
argument-hint: "[schema-json-or-csv-or-description] [--audit | --build]"
---

# BNDRY custom field schema generator

This skill generates and audits `CustomFieldSchema` JSON for BNDRY entities (Individual, Company, Trust). Output is a `{ "groups": [...] }` payload ready to paste into BNDRY's Settings page.

Before building, consult `references/references.md` — it is the bundled source of truth for available field types, validation rules, and JSON encoding. Do not proceed without reading it.

**What custom fields are for:** extending entity data with fields that BNDRY doesn't capture natively. Before adding a field, consider whether it's already captured via core entity fields, registrations, contacts, tags, risk details, activity logs, notes, or forms. Custom fields are for structured data that genuinely has no home elsewhere.

---

## 1. Parse Arguments and Determine Mode

Interpret `$ARGUMENTS` to determine the workflow:

**Audit mode** — validate an existing schema and report violations:
- **`--audit`** with no other content → prompt the user to paste their schema
- **`--audit <file-path>`** → read the file, validate, report violations
- **JSON file path** (e.g. `schemas/individual.json`, ends in `.json`) → **Audit mode** — read the file, validate
- **Pasted JSON in conversation** with no other instructions → **Audit mode** — treat inline JSON as the schema to validate

**Build mode** — generate a new schema from requirements:
- **`--build`** with no other content → ask the user for their requirements (entity type, fields, groups)
- **`--build <file-path>`** → read the file (CSV or JSON field list) as source requirements and generate a schema
- **`--build "<description>"`** → treat the quoted string as a natural language description of the fields to generate
- **CSV file path** (e.g. `fields.csv`, ends in `.csv`) → **Build mode** — read the CSV as field specifications and generate a schema
- **No arguments / natural language description only** → **Build mode** — generate a new schema from requirements in the conversation

If a file path is given, read it immediately before proceeding.

### Schema update workflow

If the operator provides both an existing schema and new requirements (e.g. "update this schema to add X"), this is not a distinct mode — handle it as:

1. **Audit** the existing schema to identify what is wrong or outdated
2. **Build** a new schema from the new requirements, carrying forward **every** field from the existing schema

**Never remove a field from the existing schema** as part of this workflow unless the operator has explicitly approved its removal. Fields that look stale, redundant, or off-style still get carried forward — flag them in the summary instead. If you genuinely cannot fix a malformed field without removing it, ask the operator before acting.

Tell the operator: "I'll audit your existing schema first, then build a revised version incorporating the existing fields and your new requirements. I won't drop any of your existing fields unless you tell me to." If the operator has not pasted their existing schema, ask for it before proceeding.

---

## 2. Planning Phase (all modes)

Before writing or auditing any JSON:

- Confirm the entity type: `individual`, `company`, or `trust`. If not stated, ask — do not default.
- Confirm field groupings, types, required/optional status, and any validation the user wants
- If a CSV or list is provided, read it fully before asking questions — only ask about things that are genuinely ambiguous after reading
- If requirements are ambiguous, ask one consolidated clarifying question before generating
- For anything the user asked for that isn't supported (date comparisons, conditional logic, cross-field validation), flag it **before generating** — do not silently omit or approximate

Good reasons to ask before proceeding:
- Entity type not specified
- "Choose from a list" with no indication of radio vs select vs checkbox
- A validation constraint that doesn't exist (e.g. "must be over 18" on a date field)
- A CSV column whose meaning is unclear

Do not ask about trivial things — derive a sensible default and note it in the summary.

---

## 3. Build Phase

### Reference templates

Before generating, read the template for the relevant entity type to understand what good looks like — the groups that are typically used, how fields are named and typed, and what level of detail is appropriate. Do not copy the template verbatim; generate the schema fresh from the user's requirements.

- `templates/individual.json` — employment type/industry, source of funds, source of wealth
- `templates/company.json` — business profile, operations, payment solutions, AUSTRAC
- `templates/trust.json` — trust profile (deed date, purpose, industry), operations, payment solutions, AUSTRAC

### Build checklist

Copy and check off as you work:

```
Schema build checklist:
- [ ] Entity type confirmed (individual / company / trust)
- [ ] Fields not already captured natively (core fields, registrations, contacts, tags, risk details, activity logs, notes, forms)
- [ ] Unsupported validation requests intercepted and surfaced explicitly (date comparisons, conditional logic, cross-field beyond `confirm`) — never silently omit
- [ ] All structural field names are camelCase — check every key in the output against the closed list: `fieldDefinitions`, `helpText`, `numberType`, `minItems`, `maxItems`, `addLabel`, `characterSet`, `fieldKey`. These are the only names that must be camelCase; field `key` values use snake_case and that is correct.
- [ ] Field and group ordering preserves input order — do not reorder for aesthetic reasons
- [ ] All group keys match ^[a-z][a-z0-9_]*$ (lowercase, starts with letter, underscores only, ≤ 63 chars)
- [ ] Group keys are unique within the schema
- [ ] All field keys match ^[a-z][a-z0-9_]*$ (same rules as above)
- [ ] Field keys are unique within each group
- [ ] Every field has exactly one type branch set — even types with no config use {}
- [ ] Every validation rule has exactly one rule branch set
- [ ] radio and select fields have at least one option
- [ ] repeater has at least one entry in `fieldDefinitions`, all child keys unique within the repeater, and contains no nested repeater
- [ ] repeater.minItems ≤ repeater.maxItems (when both are set)
- [ ] `file` fields: every value in `accept` is one of the supported extensions (`.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.csv`, `.txt`, `.odt`, `.ods`, `.odp`, `.pdf`, `.jpg`, `.jpeg`, `.png`, `.json`); leading dot included; `accept` may be omitted to allow all supported types
- [ ] No date comparison rules used (they don't exist)
- [ ] Output shape is { "groups": [...] } — not wrapped in { "name": ..., "schema": { ... } }
- [ ] Optional fields explicitly called out in summary
- [ ] Unsupported requests noted in summary with alternatives offered
- [ ] Output JSON validated by running it through jq or python3 (see post-generation validation step below)

---

## 4. Audit Phase (audit mode only)

**Never delete an existing field from a schema during an audit.** Audit mode reports violations and proposes fixes — it does not remove fields. Even when a field is malformed, deprecated, off-style, or appears redundant, leave it in place and flag it. The only path to removing a field is the operator explicitly approving the removal. If a fix to a violation would require removing the field (e.g. an unrecoverably broken type branch), surface the trade-off and ask before acting.

The same rule applies in the [schema update workflow](#schema-update-workflow): when carrying fields forward from an existing schema into a revised version, every field from the original schema must be preserved unless the operator has explicitly approved its removal.

Validate the schema against all rules. For each violation found, report:

- **Rule violated**
- **Location** (group key / field key / JSON path)
- **Severity**: Rejected by BNDRY, Silent bug, or Cosmetic
- **Fix**: The specific corrected value or change — not just a description of what is wrong. Example: `Fix: Rename field key "tax_file_number" → "taxFileNumber"`

If no violations are found, output: **"Schema is valid — safe to paste."** Do not produce an empty report.

**Audit checklist — ordered by severity:**

**Rejected by BNDRY (hard failures):**
- Wrong root shape — schema wrapped in `{ "name": ..., "schema": { ... } }` instead of `{ "groups": [...] }`
- Any `snake_case` structural field names (`field_definitions`, `help_text`, `number_type`, `min_items`, `max_items`, `add_label`, `character_set`, `field_key`) — every field with one of these will fail individually
- Use of `fieldDefinition` (singular) inside a `repeater` — the schema only defines `fieldDefinitions` (plural array). Convert to `fieldDefinitions: [ ... ]`.
- Any field missing a type branch entirely
- Any field with more than one type branch set
- Any validation rule with more than one rule branch set
- radio or select field with zero options
- Group or field key not matching `^[a-z][a-z0-9_]*$`
- Duplicate group keys within the schema
- Duplicate field keys within a group
- More than 20 groups in the schema
- More than 100 field definitions in a group
- More than 20 rules on a field
- More than 100 options on a radio / select / checkbox
- Nested repeater (any child in `repeater.fieldDefinitions` that itself uses a `repeater` type)
- Repeater with empty or missing `fieldDefinitions`, or duplicate child `key` values within the same repeater
- More than 100 child fields in a repeater's `fieldDefinitions`
- `repeater.minItems` > `repeater.maxItems`
- `file` field with any `accept` entry not in the supported set (`.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.csv`, `.txt`, `.odt`, `.ods`, `.odp`, `.pdf`, `.jpg`, `.jpeg`, `.png`, `.json`) or missing the leading `.`
- `file` field with more than 40 entries in `accept`

**Silent bugs:**
- Any date comparison validation rule (doesn't exist — BNDRY will reject the rule but may not surface a clear error)
- Any conditional logic attempt in the schema (not supported — fields silently always render)
- Any cross-field validation other than `confirm` (not supported)
- `repeater.minItems` or `repeater.maxItems` set to values outside 0–100

**Cosmetic / conventions:**
- Group label not in Title Case
- Field label not in Title Case
- `helpText`, `placeholder`, or `$el` heading text breaches the BNDRY style reference (see `references/bndry-style-reference.md`) — sentence case, no full stops inside acronyms, no double spaces, Australian English, no banned filler phrases
- Key not following label-derived convention (lowercase, non-word chars replaced with `_`)

---

## 5. Output

- **Build mode**: Output the complete JSON schema in a fenced `json` block, ready to paste into BNDRY Settings. Follow with the pre-paste instructions and summary described below.
- **Audit mode**: Output a findings report grouped by severity (Rejected by BNDRY → Silent bugs → Cosmetic). If no violations are found, output "Schema is valid — safe to paste." and stop.

### Post-generation JSON validation

After generating the JSON block, validate it before presenting it to the operator. Run:

```bash
echo '<generated_json>' | jq . > /dev/null
```

Or write to a temp file and validate:

```bash
cat > /tmp/bndry_schema_output.json << 'EOF'
<generated_json>
EOF
jq . /tmp/bndry_schema_output.json > /dev/null
```

If `jq` is not available, fall back to:

```bash
python3 -c "import json, sys; json.load(open('/tmp/bndry_schema_output.json')); print('valid')"
```

If validation fails, attempt to fix the output. If the fix succeeds, re-validate before presenting. If the JSON cannot be fixed, present it anyway with a prominent warning: "⚠ JSON validation failed — this output may be malformed. Please run it through https://jsonlint.com before pasting into BNDRY Settings." If validation passes, proceed to output.

### Build mode pre-paste instructions

After the JSON block, always include these instructions prominently before the summary:

```
⚠ Before pasting:
1. Run Audit mode on this output — paste the JSON above back into this conversation with no other instructions.
2. Save your current schema from BNDRY Settings before replacing it — BNDRY does not version custom field schemas and there is no undo.
3. If BNDRY rejects the schema after pasting, your previous schema is still active — nothing is lost.
```

### Build mode summary

After the pre-paste instructions, always include:

- Generation timestamp (e.g. `Generated: 2026-04-23T14:32Z`)
- The entity type and group structure
- **Structural field name corrections** (if any snake_case structural names were found and corrected to camelCase): list each one (e.g. `field_definitions` → `fieldDefinitions`). These are deterministic — the closed list of structural names is known and the correction is always correct.
- Any assumptions made (e.g. "I set `risk_score` as integer 1–10; say the word if you want floats")
- **An explicit list of fields left optional** — phrase it: "I left these fields optional (you didn't mark them required): X, Y, Z. Tell me if any should be required." Silent optional-ness is a common source of schema bugs.
- **Unsupported requests** — anything requested that couldn't be honoured, with alternatives: e.g. "You asked for 'must be 18 or older' on date of birth — date comparison rules don't exist. I left it as an optional date field. Use a `number` age field with `min`/`max` if you need validation."
- Anything to double-check (regex patterns, option values, derived keys)

For schemas longer than ~100 lines, also save a `.json` file to `/mnt/user-data/outputs/` and present it via `present_files`.

---

## Reference — Field Types and Output Rules

### Picking the field type

Pick the most specific type that fits. A user saying "phone number" should get `tel`, not `text`.

| User says... | Use this type |
|---|---|
| "name", "description", "note" (one-liner), "reference number", "ID" | `text` |
| "description" (long), "comments", "notes" (multi-line), "address block" | `textarea` |
| "age", "amount", "count", "percentage", "score" | `number` |
| "email", "email address" | `email` |
| "phone", "phone number", "mobile", "telephone" | `tel` |
| "date", "DOB", "date of birth", "expiry date", "start date" | `date` |
| "choose one", "pick one", "single select" with ≤3 options | `radio` |
| "dropdown", "pick one" with >3 options, long lists | `select` |
| "check all that apply", "multi-select", "tags" with ≤3 options | `checkbox` |
| "check all that apply", "multi-select" with >3 options | `select` (single-select dropdown — no multi-select dropdown exists in the schema; flag this trade-off to the user) |
| "list of ...", "multiple ...", "one or more ..." | `repeater` |
| "upload", "attachment", "document", "file", "PDF/scan/image upload" | `file` |

If the user's description is ambiguous (e.g. "preferred contact method" — could be radio, select, or checkbox), **ask**.

> **Note on `select`:** the BNDRY JSON contract still uses `"select": {}` as the field type, but the converter (`customSchemaConverter.ts`) renders it as a FormKit `dropdown` input (popover-style, with `deselect`/`selectionRemovable` derived from whether the field is required) — not the native HTML `select`. Authors don't need to do anything different in the JSON; just be aware the runtime UX is the Pro dropdown.

### Inferring validation rules

#### Apply automatically (note in summary)

- `{ "required": {} }` — only if the user said "required", "mandatory", "must", or similar. Otherwise leave optional and note it.
- `{ "email": {} }` — always add on `email` fields.
- `{ "url": {} }` — always add on fields described as URLs (use `text` type — no URL field type exists). The rule is named `url` — **not** `pattern`, `regex`, or `uri`. Those names do not exist and the schema will reject them with `rules[N]: Invalid input`.

#### Apply only when the user asks

- `length`, `min`, `max`, `between` — only when the user gives explicit bounds.
- `matches` with a regex — only when the user provides or clearly describes a pattern. The rule is named `matches` — **not** `pattern` or `regex`. Put the regex between `/` delimiters in the `values` array. Confirm the regex back to the user.
- `alpha`, `alphanumeric`, `lowercase`, `uppercase`, character-set rules — only when explicitly requested.
- `is` / `not` — when the user gives a finite whitelist or blacklist.
- `starts_with` / `ends_with` — when explicitly mentioned.
- `confirm` — for "confirm password" / "confirm email" style paired fields.

#### Rules that don't exist — intercept and surface these proactively

When Build mode receives a request for any of the following, **surface it explicitly before generating output** — never silently omit the constraint or approximate it with a different rule:

- **No date comparison rules** — cannot enforce "must be at least 18", "date in the past", "date before/after X". Say: "Date comparison validation is not supported. Field `[name]` will be generated without that constraint — enforce this outside the schema." Suggest a `number` field with `min`/`max` as an alternative if age validation is needed.
- **No conditional logic** — the schema renders all fields in a group unconditionally. Say: "Conditional field rendering is not supported. All fields in a group always render." Suggest separate groups or app-level handling.
- **No cross-field validation other than `confirm`** — sum constraints, ratio checks, mutual exclusivity. Say: "Cross-field validation (beyond `confirm`) is not supported. Enforce this outside the schema."
- **No signatures, rich text, colour pickers, currency, country pickers** — these types don't exist in the schema. (File uploads *are* supported via the `file` type — see the File upload section.)

### Reading a CSV of field specs

Likely columns:

- `group` (optional) — group key or label
- `key` — stable field identifier (derive from `label` if missing: lowercase, non-word chars → `_`)
- `label` — user-facing label (required)
- `type` — infer from label if missing
- `required` — truthy/falsy
- `help_text` / `help` / `description` → `helpText`
- `options` — pipe- or comma-separated list for radio/select/checkbox
- `min` / `max` — note: `number.min`/`max` are rendering hints; `MinRule`/`MaxRule` are validation. A user saying "min 2 max 100" on a text field means `LengthRule`.
- `placeholder`

If columns are unfamiliar, ask before generating.

### Key derivation

Given a label like "Date of Birth":
1. Lowercase → `date of birth`
2. Replace non-word chars with `_` → `date_of_birth`
3. Collapse multiple `_` → `date_of_birth`
4. Trim leading/trailing `_`
5. If it starts with a digit, prefix with `f_` and warn the user

Keys must be ≤ 63 chars. Truncate and warn if longer.

**camelCase vs snake_case:** Field `key` values use `snake_case` (required by `^[a-z][a-z0-9_]*$`) — do not convert them. Only structural field names must be camelCase, and these are a closed list: `fieldDefinitions`, `helpText`, `numberType`, `minItems`, `maxItems`, `fieldDefinition`, `addLabel`, `characterSet`, `fieldKey`. If an operator-supplied schema uses snake_case structural names (e.g. `field_definitions`, `help_text`), correct them deterministically — there is no ambiguity.

### Label conventions

**Field labels, group labels, and option labels:** Title Case (e.g. "Date of Birth", "POI ID", "Loyalty Tier", "Full-time", "5 Star Plus"). This is a deliberate UI convention for form-field captions — Title Case scans faster in dense Settings layouts. Keep proper-noun capitalisation as published (e.g. "PEP Screening", "AUSTRAC").

**`helpText` and `placeholder`:** Follow the BNDRY style reference at `references/bndry-style-reference.md`. Read it before writing any prose-bearing values. Key rules to apply: sentence case, Australian English (`-ise`, `-our`, `-re`), no full stops inside acronyms, single space after full stops, no banned filler phrases (`please note`, `in order to`, `utilise`, `leverage`).

**Don't echo the key back as the label.**

### Output shape

The BNDRY Settings UI textbox expects **just the inner schema**:

```json
{
  "groups": [ ... ]
}
```

No outer wrapper. No `name` field. No `schema` key.

Only wrap in `{ "name": ..., "schema": { ... } }` if the user explicitly says they're calling the API directly:

```json
{
  "name": "tenants/{tenant}/customFieldSettings/{individual|company|trust}",
  "schema": {
    "groups": [ ... ]
  }
}
```

`json_schema`, `revision`, `create_time`, `update_time` are `OUTPUT_ONLY` — never emit these.

### Worked example

```json
{
  "groups": [
    {
      "key": "custom",
      "label": "Custom Fields",
      "fieldDefinitions": [
        {
          "key": "full_name",
          "label": "Full Name",
          "rules": [
            { "required": {} },
            { "length": { "min": 2, "max": 100 } }
          ],
          "text": { "placeholder": "e.g. Jane Smith" }
        },
        {
          "key": "age",
          "label": "Age",
          "rules": [{ "between": { "min": 0, "max": 120 } }],
          "number": { "min": 0, "max": 120, "numberType": "NUMBER_TYPE_INTEGER" }
        },
        {
          "key": "preferred_contact",
          "label": "Preferred Contact Method",
          "rules": [{ "required": {} }],
          "radio": {
            "options": [
              { "value": "email", "label": "Email" },
              { "value": "phone", "label": "Phone" },
              { "value": "post", "label": "Post" }
            ]
          }
        }
      ]
    }
  ]
}
```

### Repeater

`RepeaterFieldDefinition` wraps an array of child fields under `fieldDefinitions` (plural). Each repeater entry contains the same set of child fields. Nested repeaters are forbidden — no child in `fieldDefinitions` may itself be a `repeater`. Child `key` values must be unique within the repeater. Up to 100 child fields per repeater; `minItems` and `maxItems` are each in 0–100.

**Single-field repeater** — for a flat list of one value per entry:

```json
{
  "key": "aliases",
  "label": "Known Aliases",
  "repeater": {
    "fieldDefinitions": [
      {
        "key": "alias",
        "label": "Alias",
        "text": {}
      }
    ],
    "minItems": 0,
    "maxItems": 10,
    "draggable": true,
    "addLabel": "+ Add alias"
  }
}
```

**Group repeater** — for repeating sub-forms where each entry has multiple named fields (e.g. "a list of beneficial owners with name and percentage", "a repeater for address with street, suburb, state, postcode"):

```json
{
  "key": "beneficial_owners",
  "label": "Beneficial Owners",
  "repeater": {
    "fieldDefinitions": [
      { "key": "full_name", "label": "Full Name", "text": {} },
      {
        "key": "ownership_percentage",
        "label": "Ownership %",
        "rules": [{ "between": { "min": 0, "max": 100 } }],
        "number": { "min": 0, "max": 100, "numberType": "NUMBER_TYPE_FLOAT" }
      },
      { "key": "date_acquired", "label": "Date Acquired", "date": {} }
    ],
    "minItems": 1,
    "maxItems": 20,
    "draggable": true,
    "addLabel": "+ Add owner"
  }
}
```

When you see a request describing repeated sub-forms ("a repeater for X with fields A, B, C…"; "a list of entries each with…"; "repeated sections where each entry has…"), generate a single group repeater. Do **not** split into multiple single-child repeaters — that pattern is no longer required.

If the operator's request would require nesting (a child field that is itself a repeater), halt and explain: nested repeaters remain forbidden. Suggest flattening the structure or modelling the inner list as a separate top-level repeater referencing the parent via a key field.

### File upload

`FileFieldDefinition` (`file` type branch) handles file uploads. Configuration:

- `accept` — optional array of allowed extensions, each starting with `.`. Supported set is fixed: `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.csv`, `.txt`, `.odt`, `.ods`, `.odp`, `.pdf`, `.jpg`, `.jpeg`, `.png`, `.json`. Omit `accept` to allow any of the supported types. Up to 40 entries.
- `multiple` — bool. The schema default is `false`, but **this skill defaults to `true`** when generating file fields: custom field uploads are typically evidence-gathering (attachments, scans, screenshots) where a single entry frequently needs more than one file, and the cost of being wrong in the other direction (operator can't add a second file) is higher than the cost of being wrong here (operator uploads only one file anyway). Emit `"multiple": true` unless the operator explicitly says "one file only" / "single file" / "max one attachment", in which case emit `"multiple": false` and note it in the summary.

Map operator wording to `accept`:

- "PDF only" → `[".pdf"]`
- "Word documents" → `[".doc", ".docx"]`
- "spreadsheets" → `[".xls", ".xlsx", ".csv", ".ods"]`
- "images" → `[".jpg", ".jpeg", ".png"]`

If the operator names an unsupported type (e.g. `.heic`, `.zip`, `.mp4`), surface this before generating: "BNDRY only accepts the following file types: …. I'll omit `[unsupported]` from `accept` — if you need it, contact BNDRY to request additional types be supported."

Minimal example:

```json
{
  "key": "supporting_documents",
  "label": "Supporting Documents",
  "file": {
    "accept": [".pdf", ".doc", ".docx"],
    "multiple": true
  }
}
```

Files attached to custom field uploads appear on the entity profile alongside the rest of the custom field group.

**Single-file limit:** there is no separate "max one file" config. Setting `multiple: false` (or omitting the field — schema default is false) caps the value at one file — the validator enforces this. If an operator asks "can I limit to one file", the answer is `"multiple": false`.

**Stored value shape (for context, not part of schema generation):** file fields persist as objects of the form `{ "name": "<original filename>", "resource": "files/<id>" }`. The schema generator only emits the field definition; values are produced by the upload flow. Mention this only if an operator asks how uploaded files are stored or referenced.

---

## Known rejection causes

| Failure | Cause | Fix |
|---|---|---|
| `groups: Invalid input` at root | Schema wrapped in `{ "name": ..., "schema": { ... } }` — Settings UI wants `{ "groups": [...] }` at root | Remove the outer wrapper |
| `groups[N].fieldDefinitions[M]: Invalid input` on every field with a structural key | `snake_case` structural field names (`help_text`, `field_definitions`, etc.) instead of camelCase | Rename to camelCase — see build checklist |
| `groups[N].fieldDefinitions[M]: Invalid input` on a specific field | Field missing a type branch, or has zero options (radio/select), or key fails regex | Add the missing type `{}`, add options, or fix the key |
| `groups[N].fieldDefinitions[M].rules[K]: Invalid input` | Rule name doesn't exist in the schema. Common invented names: `pattern`, `regex`, `uri`, `http`, `numeric` (use `number` type), `date_after`, `date_before`. | Replace with the real rule name. URL → `url`. Regex → `matches` with `values: ["/regex/"]`. Date comparisons don't exist — drop the rule and enforce at app level. If unsure, remove the rule rather than guessing. |
| Schema accepted but field never renders | Attempted conditional logic — not supported; all fields in a group always render | Remove conditional logic; split into separate groups or handle at app level |
| Schema accepted but validation never triggers | Used a date comparison rule — these don't exist | Remove the rule; use a `number` age field with `min`/`max` instead |
| Schema accepted but cross-field rule silently ignored | Cross-field validation other than `confirm` — not supported | Remove the rule; handle at app level |
| Repeater always requires at least N entries unexpectedly | `minItems` set higher than intended | Review `minItems` vs `maxItems` |
