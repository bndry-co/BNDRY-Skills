#!/usr/bin/env python3
"""Mechanical validator for BNDRY FormKit JSON schemas.

Checks every rule from the bndry-formkit-schema skill that can be verified
deterministically. Judgement calls (layout taste, terminology, theme
cross-referencing) remain with the reviewer — this script only covers the
checks marked [auto] in the skill's rules checklist.

Usage:
    python3 validate_schema.py <schema.json> [<schema.json> ...]

Exit codes:
    0  no CRASH or BUG findings
    1  at least one CRASH or BUG finding
    2  file unreadable / not valid JSON
"""

import json
import re
import sys

# Severity order matches the skill's checklist groups.
CRASH = "CRASH"
BUG = "BUG"
TYPE = "TYPE"  # input type / Australian defaults
LAYOUT = "LAYOUT"
THEME = "THEME"
COSMETIC = "COSMETIC"

SEVERITY_ORDER = [CRASH, BUG, TYPE, LAYOUT, THEME, COSMETIC]

SUPPORTED_FILE_EXTS = {
    "doc", "docx", "ppt", "pptx", "xls", "xlsx", "csv", "txt",
    "odt", "ods", "odp", "pdf", "jpg", "jpeg", "png",
}

# FormKit validation rule names that may legitimately follow a `|` separator.
KNOWN_VALIDATION_RULES = re.compile(r"^[*+]?[a-z_]+(:.*)?$")

GET_REF = re.compile(r"\$get\(\s*([\w-]+)\s*\)")
DOLLAR_TOKEN = re.compile(r"\$([A-Za-z_][\w]*)")
METHOD_CHAIN = re.compile(r"\.value\s*\.\s*\w")
ARITHMETIC_REF = re.compile(r"\$get\(\s*([\w-]+)\s*\)\.value\s*[*+/%-]")


class Validator:
    def __init__(self):
        self.findings = []
        # collected on first walk
        self.ids = {}            # id -> node
        self.step_names = []     # (name, path)
        self.field_names = []    # (name, path, step_name)
        self.expressions = []    # (expr, path, context) context: 'if'|'children'|'value'

    def add(self, severity, path, rule, message):
        self.findings.append((severity, path, rule, message))

    # ---------- helpers ----------

    @staticmethod
    def node_label(node, index):
        if isinstance(node, dict):
            name = node.get("name")
            if name:
                return str(name)
            kind = node.get("$formkit") or node.get("$el")
            if kind:
                return f"{kind}[{index}]"
            if "if" in node:
                return f"if-block[{index}]"
        return f"[{index}]"

    @staticmethod
    def as_children_list(children):
        if children is None:
            return []
        if isinstance(children, list):
            return children
        if isinstance(children, dict):
            return [children]
        return []  # string children handled separately

    # ---------- pass 1: collect ----------

    def collect(self, node, path, step_name, index=0):
        if not isinstance(node, dict):
            return
        kind = node.get("$formkit")
        name = node.get("name")
        label = self.node_label(node, index)
        here = f"{path}/{label}" if path else label

        if kind == "step" and name:
            self.step_names.append((str(name), here))
            step_name = str(name)
        elif kind and kind not in ("multi-step", "step") and name:
            self.field_names.append((str(name), here, step_name))

        node_id = node.get("id")
        if node_id:
            self.ids[str(node_id)] = node

        for ctx in ("if", "value"):
            val = node.get(ctx)
            if isinstance(val, str) and "$" in val:
                self.expressions.append((val, here, ctx))
        children = node.get("children")
        if isinstance(children, str):
            self.expressions.append((children, here, "children"))
        for branch in ("then", "else"):
            val = node.get(branch)
            if isinstance(val, str) and "$" in val:
                self.expressions.append((val, here, branch))
            for i, child in enumerate(self.as_children_list(val)):
                self.collect(child, here, step_name, i)
        for i, child in enumerate(self.as_children_list(children)):
            self.collect(child, here, step_name, i)

    # ---------- pass 2: node checks ----------

    def check_node(self, node, path, *, direct_step_child, in_repeater,
                   in_conditional_wrapper, index):
        if not isinstance(node, dict):
            return
        label = self.node_label(node, index)
        here = f"{path}/{label}" if path else label
        kind = node.get("$formkit")
        el = node.get("$el")
        attrs = node.get("attrs") or {}
        attrs_class = attrs.get("class", "") if isinstance(attrs, dict) else ""

        if kind:
            self.check_formkit_node(node, kind, here, direct_step_child,
                                    in_repeater, in_conditional_wrapper)
        if el:
            self.check_el_node(node, el, here, attrs, attrs_class,
                               direct_step_child)

        # conditional node needs a key ($formkit and $el alike)
        if "if" in node and (kind or el) and "key" not in node:
            self.add(BUG, here, "missing-key",
                     "node has `if` but no `key` — Vue reuses DOM nodes, "
                     "causing ghost values; add a `key`")

        # inline styles
        if isinstance(attrs, dict) and "style" in attrs:
            self.add(COSMETIC, here, "inline-style",
                     "inline `style` attribute — remove; rely on the "
                     "centralised FormKit theme")
        if "style" in node:
            self.add(COSMETIC, here, "inline-style",
                     "inline `style` property — remove; rely on the "
                     "centralised FormKit theme")

        # redundant `block` alongside `!block`
        for cls in (attrs_class, node.get("outerClass", "")):
            if isinstance(cls, str):
                tokens = cls.split()
                if "block" in tokens and "!block" in tokens:
                    self.add(THEME, here, "redundant-block",
                             "class has both `block` and `!block` — keep "
                             "only `!block`")

        # recurse
        is_step = kind == "step"
        is_repeater = kind == "repeater"
        is_cond_wrapper = bool(el) and "if" in node
        for branch in ("then", "else"):
            for i, child in enumerate(self.as_children_list(node.get(branch))):
                self.check_node(child, here, direct_step_child=False,
                                in_repeater=in_repeater or is_repeater,
                                in_conditional_wrapper=in_conditional_wrapper
                                or is_cond_wrapper, index=i)
        for i, child in enumerate(self.as_children_list(node.get("children"))):
            self.check_node(child, here,
                            direct_step_child=is_step,
                            in_repeater=in_repeater or is_repeater,
                            in_conditional_wrapper=(in_conditional_wrapper
                                                    or is_cond_wrapper)
                            and not is_step,
                            index=i)

    def check_formkit_node(self, node, kind, here, direct_step_child,
                           in_repeater, in_conditional_wrapper):
        name = node.get("name")
        node_id = node.get("id")
        outer = node.get("outerClass", "")
        validation = node.get("validation", "")

        # name mandatory on every $formkit node
        if not name:
            sev = BUG
            msg = "missing `name` — it becomes the key in submitted data"
            if kind == "multi-step":
                msg = ("multi-step root missing stable `name` — FormKit "
                       "auto-assigns an incrementing key per mount and "
                       "saved data is lost on reload")
            self.add(sev, here, "missing-name", msg)

        # id == name
        if name and node_id and str(name) != str(node_id):
            self.add(BUG, here, "id-name-mismatch",
                     f"`id` ({node_id}) != `name` ({name}) — keep them "
                     "identical")

        # computed value expression on an input → infinite re-render
        value = node.get("value")
        if isinstance(value, str) and (value.startswith("$:")
                                       or "$get(" in value):
            self.add(CRASH, here, "computed-input-value",
                     "`$formkit` input with a computed `value` expression "
                     "— infinite re-render loop; use an `$el` div instead")

        # fields inside conditional wrappers need their own key
        if in_conditional_wrapper and "key" not in node:
            self.add(BUG, here, "missing-key-in-wrapper",
                     "`$formkit` field inside a conditional `$el` wrapper "
                     "without its own `key` — Vue reuses DOM nodes "
                     "positionally across sections")

        # validation string checks
        if isinstance(validation, str) and validation:
            self.check_validation_string(validation, here, kind)

        # type-specific checks
        if kind == "multi-step":
            self.check_multi_step(node, here)
        elif kind == "step":
            sic = node.get("stepInnerClass", "")
            if "grid" not in sic or "grid-cols-2" not in sic:
                self.add(LAYOUT, here, "step-inner-class",
                         'step missing `stepInnerClass: "grid grid-cols-2 '
                         'gap-4"` — col-span classes on children are inert '
                         "without it")
        elif kind == "repeater":
            if "validation" in node:
                self.add(BUG, here, "repeater-validation",
                         "`validation` on a repeater is silently ignored — "
                         "remove it; use `min: 1` to require an entry")
            if direct_step_child:
                if "!max-w-none" not in outer or "!col-span-2" not in outer:
                    self.add(LAYOUT, here, "repeater-outer-class",
                             'repeater needs `outerClass: "!max-w-none '
                             '!col-span-2"`')
        elif kind == "signature":
            if in_repeater:
                self.add(BUG, here, "signature-in-repeater",
                         "signature input inside a repeater — canvas "
                         "scaling breaks; move it to a direct step child")
            if "!col-span-2" not in outer:
                self.add(LAYOUT, here, "signature-col-span",
                         'signature needs `outerClass: "!col-span-2"`')
        elif kind == "date":
            self.add(TYPE, here, "native-date",
                     "native `date` input — replace with `datepicker` "
                     "using the standard BNDRY config")
        elif kind == "datepicker":
            fmt = node.get("format")
            if isinstance(fmt, dict) and fmt.get("time") == "2-digit":
                self.add(BUG, here, "datepicker-2-digit",
                         '`format.time: "2-digit"` is invalid and makes '
                         'the field completely non-interactive — use '
                         '`"short"`')
        elif kind == "file":
            accept = node.get("accept", "")
            if isinstance(accept, str) and accept:
                exts = {e.strip().lstrip(".").lower()
                        for e in accept.split(",") if e.strip()}
                bad = sorted(exts - SUPPORTED_FILE_EXTS)
                if bad:
                    self.add(TYPE, here, "unsupported-accept",
                             f"`accept` lists unsupported extensions "
                             f"({', '.join(bad)}) — the file plugin's "
                             "fileExt validation will reject them")
        elif kind == "currency":
            for prop, want in (("currency", "AUD"),
                               ("displayLocale", "en-AU")):
                if node.get(prop) != want:
                    self.add(TYPE, here, f"currency-{prop.lower()}",
                             f'currency field missing `{prop}: "{want}"`')
            if node.get("minDecimals") != 2:
                self.add(TYPE, here, "currency-min-decimals",
                         "currency field missing `minDecimals: 2` — "
                         "without it the field displays no cents")

        # layout: direct step children need a col-span outerClass
        if (direct_step_child and kind not in ("step",)
                and "!col-span-1" not in outer and "!col-span-2" not in outer):
            self.add(LAYOUT, here, "field-col-span",
                     "direct step child missing `outerClass` with "
                     "`!col-span-1` or `!col-span-2`")

        # theme: !max-w-none belongs only on multi-step root and repeaters
        if (kind not in ("multi-step", "repeater")
                and "!max-w-none" in outer):
            self.add(THEME, here, "redundant-max-w-none",
                     "`!max-w-none` on a regular field's `outerClass` — "
                     "the theme's global outer already applies it; remove")

    def check_multi_step(self, node, here):
        if node.get("tab-style") != "progress":
            self.add(LAYOUT, here, "tab-style",
                     'multi-step root missing `tab-style: "progress"` — '
                     "the BNDRY theme only styles the tab bar in this mode")
        if "allow-incomplete" in node or "allowIncomplete" in node:
            self.add(LAYOUT, here, "allow-incomplete",
                     "`allow-incomplete` is a temporary testing flag — "
                     "remove before deploy")
        for prop in ("outerClass", "wrapperClass"):
            val = node.get(prop, "")
            if "!max-w-none" not in val:
                self.add(LAYOUT, here, f"multi-step-{prop.lower()}",
                         f'multi-step root missing `!max-w-none` in '
                         f"`{prop}` — theme constrains its width")
            if "!w-full" in val:
                self.add(LAYOUT, here, "w-full",
                         f"`!w-full` in `{prop}` — strip to "
                         '`"!max-w-none"` only')

    def check_el_node(self, node, el, here, attrs, attrs_class,
                      direct_step_child):
        if direct_step_child and "!col-span-2" not in attrs_class:
            self.add(LAYOUT, here, "el-col-span",
                     "`$el` direct step child missing `!col-span-2` in "
                     "`attrs.class` — renders in a single grid column")
        if el in ("h2", "h3"):
            if "!inline-flex" in attrs_class:
                self.add(LAYOUT, here, "heading-inline-flex",
                         "heading uses `!inline-flex` — adjacent headings "
                         "concatenate onto one line; use `!block`")
            elif "!block" not in attrs_class:
                self.add(COSMETIC, here, "heading-block",
                         "heading missing `!block` in its classes")
            text = node.get("children")
            if isinstance(text, str) and re.match(
                    r"^\s*(section|part)\s+\d+\b", text, re.IGNORECASE):
                self.add(COSMETIC, here, "numbered-section",
                         f'numbered section heading ("{text.strip()}") — '
                         "use a descriptive heading or split into a step")
        if el == "div":
            children = node.get("children")
            meaningful = (children or "if" in node or "key" in node
                          or (isinstance(attrs, dict)
                              and any(k != "class" or v
                                      for k, v in attrs.items())))
            if not meaningful:
                self.add(COSMETIC, here, "empty-div",
                         "empty `$el` div with no children, attrs, or "
                         "conditional logic — remove")

    # ---------- validation string ----------

    def check_validation_string(self, validation, here, kind):
        if kind == "file":
            for rule in ("fileExt", "fileSize", "fileUpload"):
                if rule in validation:
                    self.add(TYPE, here, "manual-file-validation",
                             f"`{rule}` in validation string — the file "
                             "plugin applies it automatically; manual "
                             "addition causes double-validation errors")
        segments = validation.split("|")
        saw_matches = False
        for seg in segments:
            if seg.startswith("matches:") or seg.startswith("*matches:") \
                    or seg.startswith("+matches:"):
                saw_matches = True
                if "{" in seg or "}" in seg:
                    self.add(BUG, here, "matches-curly-braces",
                             "curly-brace quantifier inside `matches:` "
                             "regex — the parser consumes braces; repeat "
                             "the class explicitly or use `*`/`+`")
            elif saw_matches and not KNOWN_VALIDATION_RULES.match(seg):
                self.add(BUG, here, "matches-pipe",
                         f'`|` inside a `matches:` regex (stray segment '
                         f'"{seg}") — the parser splits rules on `|`; '
                         "restructure without alternation")

    # ---------- expression checks ----------

    def check_expressions(self):
        for expr, path, ctx in self.expressions:
            body = expr[2:] if expr.startswith("$:") else expr

            if METHOD_CHAIN.search(body):
                self.add(CRASH, path, "method-chaining",
                         f"method chaining after `.value` in `{ctx}` "
                         "expression — hard-crashes the app; restructure")

            if ctx == "children" and "$get(" in expr \
                    and not expr.startswith("$:"):
                self.add(CRASH, path, "children-prefix",
                         "`children` expression doesn't start with `$:` — "
                         "renders as literal text")

            if ctx == "children" and re.search(r"\|\|\s*0", body):
                self.add(BUG, path, "or-zero-fallback",
                         "`|| 0` fallback in a `children` expression — "
                         "set a default `value` on the field instead")

            for token in DOLLAR_TOKEN.findall(body):
                if token != "get":
                    self.add(BUG, path, "field-name-reference",
                             f"`${token}` reference — BNDRY doesn't "
                             "populate the schema data scope; use "
                             "`$get(id).value` (verify: may be a "
                             "legitimate FormKit token)")

            for ref in GET_REF.findall(body):
                if ref not in self.ids:
                    self.add(BUG, path, "get-missing-id",
                             f"`$get({ref})` but no field has `id: "
                             f'"{ref}"` — resolves to undefined; the '
                             "conditional/expression will never work")
                else:
                    self.check_get_comparison(body, ref, path)

            if "=== 'true'" in body or '=== "true"' in body:
                self.add(BUG, path, "string-true-comparison",
                         "`=== 'true'` comparison — single checkboxes "
                         "return boolean `true`/`false`; use `=== true`")

        # arithmetic on a select without a default value
        seen = set()
        for expr, path, _ in self.expressions:
            for ref in ARITHMETIC_REF.findall(expr):
                node = self.ids.get(ref)
                if node and node.get("$formkit") == "select" \
                        and "value" not in node and ref not in seen:
                    seen.add(ref)
                    self.add(BUG, path, "select-no-default",
                             f"arithmetic on `$get({ref}).value` but the "
                             f"select `{ref}` has no default `value` — "
                             "undefined * 1 = NaN; add `value: \"0\"`")

    def check_get_comparison(self, body, ref, path):
        node = self.ids.get(ref)
        if not node or node.get("$formkit") != "checkbox":
            return
        cmp_str = re.search(
            r"\$get\(\s*" + re.escape(ref) + r"\s*\)\.value\s*===?\s*'", body)
        if not cmp_str:
            return
        if "options" in node:
            self.add(BUG, path, "checkbox-group-trigger",
                     f"checkbox group `{ref}` used as a conditional "
                     "trigger — its value is an array, so a string "
                     "comparison never matches; use a radio or one "
                     "single-checkbox field per option")
        else:
            self.add(BUG, path, "checkbox-string-comparison",
                     f"single checkbox `{ref}` compared to a string — "
                     "bare checkboxes return boolean; use `=== true`")

    # ---------- repeater $get ----------

    def check_repeater_gets(self, node, path, in_repeater, index=0):
        if not isinstance(node, dict):
            return
        label = self.node_label(node, index)
        here = f"{path}/{label}" if path else label
        is_repeater = node.get("$formkit") == "repeater"
        if in_repeater:
            for ctx in ("if", "value"):
                val = node.get(ctx)
                if isinstance(val, str) and "$get(" in val:
                    self.add(BUG, here, "get-in-repeater",
                             f"`$get()` in `{ctx}` inside repeater "
                             "children — resolves at form scope, not the "
                             "current row; intra-row conditionals must be "
                             "handled at the app level")
            children = node.get("children")
            if isinstance(children, str) and "$get(" in children:
                self.add(BUG, here, "get-in-repeater",
                         "`$get()` in `children` inside repeater children "
                         "— resolves at form scope, not the current row")
        for branch in ("children", "then", "else"):
            for i, child in enumerate(
                    self.as_children_list(node.get(branch))):
                self.check_repeater_gets(child, here,
                                         in_repeater or is_repeater, i)

    # ---------- name collisions ----------

    def check_names(self):
        steps = {n for n, _ in self.step_names}
        for fname, fpath, _ in self.field_names:
            if fname in steps:
                self.add(BUG, fpath, "field-step-name-collision",
                         f"field `name: \"{fname}\"` matches a step name "
                         "in the same form — FormKit scope resolution can "
                         "confuse the two; rename the field")
        per_step = {}
        for fname, fpath, step in self.field_names:
            key = (step, fname)
            if key in per_step:
                self.add(BUG, fpath, "duplicate-field-name",
                         f"duplicate field `name: \"{fname}\"` within "
                         f"step `{step}` (also at {per_step[key]})")
            else:
                per_step[key] = fpath

    # ---------- entry point ----------

    def run(self, schema):
        if not isinstance(schema, list):
            self.add(CRASH, "(root)", "root-not-array",
                     "schema root must be a JSON array — the platform "
                     "rejects an object root before the form can be "
                     "saved; wrap the root in `[ ... ]`")
            schema = [schema] if isinstance(schema, dict) else []
        if not any(isinstance(n, dict) and n.get("$formkit") == "multi-step"
                   for n in schema):
            self.add(LAYOUT, "(root)", "no-multi-step",
                     "no `multi-step` root node — every BNDRY form must "
                     "use the multi-step skeleton")
        for i, node in enumerate(schema):
            self.collect(node, "", None, i)
        for i, node in enumerate(schema):
            self.check_node(node, "", direct_step_child=False,
                            in_repeater=False,
                            in_conditional_wrapper=False, index=i)
            self.check_repeater_gets(node, "", False, i)
        self.check_expressions()
        self.check_names()


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    worst_exit = 0
    for path in argv[1:]:
        try:
            with open(path, encoding="utf-8") as fh:
                schema = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"{path}: CRASH invalid-json — {exc}")
            return 2

        v = Validator()
        v.run(schema)
        v.findings.sort(key=lambda f: SEVERITY_ORDER.index(f[0]))

        print(f"== {path} ==")
        if not v.findings:
            print("clean — no mechanical findings "
                  "(judgement-call checks still apply)")
        for severity, loc, rule, message in v.findings:
            print(f"[{severity}] {rule} at {loc}\n    {message}")
        crash_or_bug = any(f[0] in (CRASH, BUG) for f in v.findings)
        print(f"-- {len(v.findings)} finding(s)")
        if crash_or_bug:
            worst_exit = 1
    return worst_exit


if __name__ == "__main__":
    sys.exit(main(sys.argv))
