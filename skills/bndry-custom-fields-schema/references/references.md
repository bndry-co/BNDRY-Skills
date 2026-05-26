# Custom field schema reference

The source of truth for everything in this document is the `CustomFieldSchema` API exposed by BNDRY's Settings page. This file captures every field type, configuration option, and validation rule available, along with the JSON shape they take.

For generic JSON encoding rules not covered here (lowerCamelCase field names, oneof flattening, enum string serialisation, omission of unset optional fields), consult the official proto3 JSON mapping standard: <https://protobuf.dev/programming-guides/proto3/#json>.

---

## Top-level structure

A `CustomFieldSchema` is a single JSON object with one required key, `groups`. Each group contains one or more field definitions.

```json
{
  "groups": [
    {
      "key": "worldpay",
      "label": "Worldpay",
      "fieldDefinitions": [
        { "key": "merchant_id", "label": "Merchant ID", "text": {} }
      ]
    }
  ]
}
```

### `CustomFieldSchema`

| Field    | Type    | Required | Notes                                              |
| -------- | ------- | -------- | -------------------------------------------------- |
| `groups` | array   | yes      | 1–20 groups. Each `key` must be unique within the schema. |

### `CustomFieldGroup`

| Field              | Type    | Required | Notes                                                                |
| ------------------ | ------- | -------- | -------------------------------------------------------------------- |
| `key`              | string  | yes      | 1–63 chars, matches `^[a-z][a-z0-9_]*$`. Stable machine identifier.  |
| `label`            | string  | yes      | 1–255 chars. User-facing label.                                      |
| `fieldDefinitions` | array   | yes      | 1–100 entries. Each `key` must be unique within the group.           |

### `CustomFieldDefinition`

| Field      | Type   | Required | Notes                                                                                              |
| ---------- | ------ | -------- | -------------------------------------------------------------------------------------------------- |
| `key`      | string | yes      | 1–63 chars, matches `^[a-z][a-z0-9_]*$`. Stable identifier.                                        |
| `label`    | string | yes      | 1–255 chars. User-facing label.                                                                    |
| `helpText` | string | no       | Up to 500 chars. Helper text shown alongside the field.                                            |
| `rules`    | array  | no       | Up to 20 validation rules (see [Validation rules](#validation-rules)).                              |
| *type*     | object | yes      | Exactly one of the field-type keys below: `text`, `textarea`, `number`, `email`, `tel`, `date`, `radio`, `select`, `checkbox`, `repeater`, `file`. |

---

## Field types

Each field definition must include exactly one of the following keys at the top level. The value is a configuration object (often `{}` when no config is needed).

### `text`

A single-line text input.

| Field         | Type   | Notes                            |
| ------------- | ------ | -------------------------------- |
| `placeholder` | string | Optional. Up to 255 chars.       |

### `textarea`

A multi-line text input.

| Field         | Type   | Notes                            |
| ------------- | ------ | -------------------------------- |
| `placeholder` | string | Optional. Up to 255 chars.       |

### `number`

A numeric input.

| Field        | Type    | Notes                                                                  |
| ------------ | ------- | ---------------------------------------------------------------------- |
| `min`        | number  | Optional. Rendering hint for minimum value.                            |
| `max`        | number  | Optional. Rendering hint for maximum value.                            |
| `step`       | number  | Optional. Rendering hint for step increment.                           |
| `numberType` | enum    | Optional. `"NUMBER_TYPE_INTEGER"` (default) or `"NUMBER_TYPE_FLOAT"`.  |

### `email`

An email input.

| Field         | Type   | Notes                            |
| ------------- | ------ | -------------------------------- |
| `placeholder` | string | Optional. Up to 255 chars.       |

### `tel`

A telephone number input.

| Field         | Type   | Notes                            |
| ------------- | ------ | -------------------------------- |
| `placeholder` | string | Optional. Up to 255 chars.       |

### `date`

A date picker. Configuration object is always `{}`.

### `radio`

A single-select radio group.

| Field     | Type  | Notes                                          |
| --------- | ----- | ---------------------------------------------- |
| `options` | array | Required. 1–100 entries (see [Option](#option)). |

### `select`

A single-select dropdown.

| Field         | Type   | Notes                                              |
| ------------- | ------ | -------------------------------------------------- |
| `options`     | array  | Required. 1–100 entries (see [Option](#option)).   |
| `placeholder` | string | Optional. Up to 255 chars.                         |

### `checkbox`

A multi-select checkbox group.

| Field     | Type  | Notes                                          |
| --------- | ----- | ---------------------------------------------- |
| `options` | array | Optional. Up to 100 entries (see [Option](#option)). |

### `repeater`

A repeating sub-form. Each entry contains the same set of child fields.

| Field              | Type    | Notes                                                                |
| ------------------ | ------- | -------------------------------------------------------------------- |
| `fieldDefinitions` | array   | Required. 1–100 entries. Each `key` must be unique within the repeater. |
| `minItems`         | int32   | Optional. 0–100. Defaults to 0.                                       |
| `maxItems`         | int32   | Optional. 0–100. Defaults to 100. Must be ≥ `minItems`.               |
| `draggable`        | bool    | Optional. Whether entries can be reordered by drag.                   |
| `addLabel`         | string  | Optional. Up to 255 chars. Label for the add-item button.             |

**Constraint:** repeater child field definitions must not themselves contain a repeater (no nested repeaters).

### `file`

A file upload field.

| Field      | Type    | Notes                                                                                                   |
| ---------- | ------- | ------------------------------------------------------------------------------------------------------- |
| `accept`   | array   | Optional. Up to 40 file extensions. Each must be one of the supported types listed below.               |
| `multiple` | bool    | Optional. Whether multiple files can be uploaded. Defaults to false.                                    |

**Supported file extensions:** `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.csv`, `.txt`, `.odt`, `.ods`, `.odp`, `.pdf`, `.jpg`, `.jpeg`, `.png`, `.json`.

### `Option`

Used by `radio`, `select`, and `checkbox`.

| Field   | Type   | Required | Notes                                              |
| ------- | ------ | -------- | -------------------------------------------------- |
| `value` | string | yes      | 1–255 chars. Stable machine-readable value.        |
| `label` | string | yes      | 1–255 chars. User-facing label.                    |

---

## Validation rules

Each entry in a field's `rules` array is an object with exactly one rule key. Rule keys map 1:1 to FormKit validation rules. Use `lowerCamelCase` for multi-word rule names in the JSON (e.g. `containsAlpha`, not `contains_alpha`).

| Rule key                | FormKit rule              | Config                                                                 |
| ----------------------- | ------------------------- | ---------------------------------------------------------------------- |
| `accepted`              | `accepted`                | `{}`. Value must be `yes`, `on`, `1`, or `true`.                       |
| `alpha`                 | `alpha[:latin]`           | `{ "characterSet": "CHARACTER_SET_DEFAULT" }` — see [Character sets](#character-sets). |
| `alphanumeric`          | `alphanumeric[:latin]`    | `{ "characterSet": ... }`.                                             |
| `alphaSpaces`           | `alpha_spaces[:latin]`    | `{ "characterSet": ... }`.                                             |
| `between`               | `between:min,max`         | `{ "min": <number>, "max": <number> }` — inclusive.                    |
| `confirm`               | `confirm[:field_name]`    | `{ "fieldKey": "other_field" }` (optional; defaults to `{field}_confirm`). |
| `containsAlpha`         | `contains_alpha[:latin]`  | `{ "characterSet": ... }`.                                             |
| `containsAlphanumeric`  | `contains_alphanumeric[:latin]` | `{ "characterSet": ... }`.                                       |
| `containsAlphaSpaces`   | `contains_alpha_spaces[:latin]` | `{ "characterSet": ... }`.                                       |
| `containsLowercase`     | `contains_lowercase[:latin]`  | `{ "characterSet": ... }`.                                         |
| `containsNumeric`       | `contains_numeric`        | `{}`.                                                                  |
| `containsSymbol`        | `contains_symbol`         | `{}`.                                                                  |
| `containsUppercase`     | `contains_uppercase[:latin]` | `{ "characterSet": ... }`.                                          |
| `email`                 | `email`                   | `{}`.                                                                  |
| `endsWith`              | `ends_with:value`         | `{ "values": ["suffix1", ...] }` — at least one value.                 |
| `is`                    | `is:value1,...`           | `{ "values": [...] }` — at least one value.                            |
| `length`                | `length:min[,max]`        | `{ "min": <int>, "max": <int> }` — `max` is optional.                  |
| `lowercase`             | `lowercase[:latin]`       | `{ "characterSet": ... }`.                                             |
| `matches`               | `matches:val1,...` / `matches:/regex/` | `{ "values": [...] }` — a single value wrapped in `/` delimiters is treated as a regex pattern. |
| `max`                   | `max:value`               | `{ "value": <number> }` — also validates array length for multi-value inputs. |
| `min`                   | `min:value`               | `{ "value": <number> }` — also validates array length for multi-value inputs. |
| `not`                   | `not:value1,...`          | `{ "values": [...] }`.                                                 |
| `required`              | `required[:trim]`         | `{ "trim": true }` (optional).                                         |
| `startsWith`            | `starts_with:value`       | `{ "values": [...] }`.                                                 |
| `symbol`                | `symbol`                  | `{}`.                                                                  |
| `uppercase`             | `uppercase[:latin]`       | `{ "characterSet": ... }`.                                             |
| `url`                   | `url`                     | `{}`. Must include protocol.                                           |

### Character sets

The `characterSet` field on alphabetical rules accepts:

| Value                       | Meaning                                                             |
| --------------------------- | ------------------------------------------------------------------- |
| `CHARACTER_SET_UNSPECIFIED` | Defaults to the default (accented) character set.                   |
| `CHARACTER_SET_DEFAULT`     | Includes accented Latin characters (ä, ù, ś, etc.).                 |
| `CHARACTER_SET_LATIN`       | Strict ASCII Latin only (`[a-zA-Z]`).                               |

Omit `characterSet` to accept the default.

---

## JSON encoding notes

- **Field naming:** use `lowerCamelCase` for all field and rule keys in the JSON. The wire-level field names use `snake_case`; the JSON representation must use `lowerCamelCase` (e.g. `fieldDefinitions`, `helpText`, `numberType`, `addLabel`, `characterSet`).
- **Oneof flattening:** the field-type union (`text`, `textarea`, etc.) and the validation-rule union are mutually exclusive — set exactly one key from each union per object.
- **Enums:** serialise as the full enum string (e.g. `"NUMBER_TYPE_INTEGER"`, `"CHARACTER_SET_LATIN"`), not as integers.
- **Optional fields:** omit unset optional fields rather than including them with empty values.
- **Empty configuration objects:** for field types and rules that take no configuration (`date`, `email` type, `accepted` rule, etc.), use `{}`.
