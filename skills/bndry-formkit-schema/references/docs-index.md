# FormKit Docs URL Index (Vue)

BNDRY is Vue-only. All URLs use the `.vue.md` suffix.

Fetch any page directly:

```
https://formkit.com/<page>.vue.md
```

Pro inputs are marked with **(Pro)** — `@formkit/pro` is already registered in BNDRY, so all Pro inputs are available without additional setup.

---

## Getting Started

- [What is FormKit?](https://formkit.com/getting-started/what-is-formkit.vue.md)
- [Installation](https://formkit.com/getting-started/installation.vue.md)
- [Your first form](https://formkit.com/getting-started/your-first-form.vue.md)
- [Community & support](https://formkit.com/getting-started/community.vue.md)

## Essentials

- [Inputs](https://formkit.com/essentials/inputs.vue.md)
- [Forms](https://formkit.com/essentials/forms.vue.md)
- [Validation](https://formkit.com/essentials/validation.vue.md)
- [Styling](https://formkit.com/essentials/styling.vue.md)
- [Icons](https://formkit.com/essentials/icons.vue.md)
- [Internationalization (i18n)](https://formkit.com/essentials/internationalization.vue.md)
- [Custom Inputs](https://formkit.com/essentials/custom-inputs.vue.md)
- [FormKit Schema](https://formkit.com/essentials/schema.vue.md)
- [Configuration](https://formkit.com/essentials/configuration.vue.md)
- [Architecture](https://formkit.com/essentials/architecture.vue.md)
- [Examples](https://formkit.com/essentials/examples.vue.md)

## Inputs

### Core Inputs

- [Button](https://formkit.com/inputs/button.vue.md)
- [Checkbox](https://formkit.com/inputs/checkbox.vue.md)
- [Color](https://formkit.com/inputs/color.vue.md)
- [Date](https://formkit.com/inputs/date.vue.md) — native HTML; BNDRY prefers `datepicker` (Pro)
- [Datetime-local](https://formkit.com/inputs/datetime-local.vue.md)
- [Email](https://formkit.com/inputs/email.vue.md)
- [File](https://formkit.com/inputs/file.vue.md)
- [Form](https://formkit.com/inputs/form.vue.md)
- [Group](https://formkit.com/inputs/group.vue.md)
- [Hidden](https://formkit.com/inputs/hidden.vue.md)
- [List](https://formkit.com/inputs/list.vue.md)
- [Meta](https://formkit.com/inputs/meta.vue.md)
- [Month](https://formkit.com/inputs/month.vue.md)
- [Number](https://formkit.com/inputs/number.vue.md)
- [Password](https://formkit.com/inputs/password.vue.md)
- [Radio](https://formkit.com/inputs/radio.vue.md)
- [Range](https://formkit.com/inputs/range.vue.md)
- [Search](https://formkit.com/inputs/search.vue.md)
- [Select](https://formkit.com/inputs/select.vue.md) — reserved for scoring fields; default picklist is `dropdown` (Pro)
- [Submit](https://formkit.com/inputs/submit.vue.md)
- [Tel (Telephone)](https://formkit.com/inputs/tel.vue.md)
- [Text](https://formkit.com/inputs/text.vue.md)
- [Textarea](https://formkit.com/inputs/textarea.vue.md)
- [Time](https://formkit.com/inputs/time.vue.md)
- [URL](https://formkit.com/inputs/url.vue.md)
- [Week](https://formkit.com/inputs/week.vue.md)

### Pro Inputs

- [Autocomplete](https://formkit.com/inputs/autocomplete.vue.md) **(Pro)**
- [Barcode](https://formkit.com/inputs/barcode.vue.md) **(Pro)**
- [Colorpicker](https://formkit.com/inputs/colorpicker.vue.md) **(Pro)**
- [Currency](https://formkit.com/inputs/currency.vue.md) **(Pro)** — BNDRY default for monetary fields
- [Datepicker](https://formkit.com/inputs/datepicker.vue.md) **(Pro)** — BNDRY default for all date fields
- [Dropdown](https://formkit.com/inputs/dropdown.vue.md) **(Pro)** — BNDRY default for picklists (use `deselect: !required`, `selectionRemovable: !required`, `popover: true`)
- [Mask](https://formkit.com/inputs/mask.vue.md) **(Pro)**
- [Multi-step](https://formkit.com/inputs/multi-step.vue.md) **(Pro)** — every BNDRY form uses this
- [Rating](https://formkit.com/inputs/rating.vue.md) **(Pro)**
- [Repeater](https://formkit.com/inputs/repeater.vue.md) **(Pro)**
- [Slider](https://formkit.com/inputs/slider.vue.md) **(Pro)**
- [Taglist](https://formkit.com/inputs/taglist.vue.md) **(Pro)**
- [Toggle](https://formkit.com/inputs/toggle.vue.md) **(Pro)**
- [Toggle Buttons](https://formkit.com/inputs/togglebuttons.vue.md) **(Pro)**
- [Transfer List](https://formkit.com/inputs/transfer-list.vue.md) **(Pro)**
- [Unit](https://formkit.com/inputs/unit.vue.md) **(Pro)**

## Plugins

- [AutoAnimate](https://formkit.com/plugins/auto-animate.vue.md)
- [Auto-Height Textarea](https://formkit.com/plugins/auto-height-textarea.vue.md) — registered in BNDRY config
- [Barcode input](https://formkit.com/plugins/barcode.vue.md)
- [Floating labels](https://formkit.com/plugins/floating-labels.vue.md)
- [Inertia](https://formkit.com/plugins/inertia.vue.md)
- [Save to LocalStorage](https://formkit.com/plugins/local-storage.vue.md) — BNDRY autosaves form drafts to localStorage; renaming fields/steps in a deployed schema is a breaking change for in-progress drafts
- [Multi-Step Input Plugin](https://formkit.com/plugins/multi-step.vue.md) — registered in BNDRY config
- [Zod Plugin](https://formkit.com/plugins/zod.vue.md)

## Guides

- [Create a custom input](https://formkit.com/guides/create-a-custom-input.vue.md)
- [Create a Tailwind CSS theme](https://formkit.com/guides/create-a-tailwind-theme.vue.md)
- [Export and restructure inputs](https://formkit.com/guides/export-and-restructure-inputs.vue.md)
- [Optimizing for production](https://formkit.com/guides/optimizing-for-production.vue.md)

## API Reference

- [The Context Object](https://formkit.com/api-reference/context.vue.md)
- [formkit/addons](https://formkit.com/api-reference/formkit-addons.vue.md)
- [formkit/common](https://formkit.com/api-reference/formkit-common.vue.md)
- [formkit/core](https://formkit.com/api-reference/formkit-core.vue.md)
- [formkit/i18n](https://formkit.com/api-reference/formkit-i18n.vue.md)
- [formkit/inputs](https://formkit.com/api-reference/formkit-inputs.vue.md)
- [formkit/observer](https://formkit.com/api-reference/formkit-observer.vue.md)
- [formkit/schema](https://formkit.com/api-reference/formkit-schema.vue.md)
- [formkit/themes](https://formkit.com/api-reference/formkit-themes.vue.md)
- [formkit/utils](https://formkit.com/api-reference/formkit-utils.vue.md)
- [formkit/validation](https://formkit.com/api-reference/formkit-validation.vue.md)
- [formkit/vue](https://formkit.com/api-reference/formkit-vue.vue.md)
- [formkit/zod](https://formkit.com/api-reference/formkit-zod.vue.md)
