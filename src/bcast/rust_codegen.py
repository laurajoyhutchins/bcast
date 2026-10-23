"""Lower reviewed, source-pinned regulatory rule IR into standalone Rust.

This does NOT extract, infer or verify legal meaning from publication text.
The upstream interpretation is a separate review and evidence boundary.
"""

from __future__ import annotations

import json
import re
from importlib.resources import files
from typing import Any

CONTRACT = "bcast.rule_ir/0.1.0"
HEX_ID = re.compile(r"^(?:bcastpub|bcastpkg|bcastobj):sha256:[0-9a-f]{64}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
DECIMAL = re.compile(r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]{1,6})?$")
UCUM_TOKEN = re.compile(r"^[A-Za-z0-9%./\[\]_{}+-]{1,64}$")
OPERATORS = {"eq": "Eq", "ne": "Ne", "lt": "Lt", "le": "Le", "gt": "Gt", "ge": "Ge"}


class RuleCompilationError(ValueError):
    """The supplied rule IR cannot safely be lowered."""


def _fail(message: str) -> None:
    raise RuleCompilationError(message)


def _mapping(value: Any, path: str, required: set[str], optional: set[str] = frozenset()) -> dict:
    if not isinstance(value, dict) or set(value) - (required | optional) or required - set(value):
        _fail(f"{path}: required fields {sorted(required)}, optional {sorted(optional)}")
    return value


def _string(value: Any, path: str, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value or len(value) > 512 or not value.isprintable():
        _fail(f"{path}: expected nonempty printable string")
    if pattern is not None and not pattern.fullmatch(value):
        _fail(f"{path}: invalid identifier or value")
    return value


def _id(value: Any, path: str, prefix: str) -> str:
    value = _string(value, path, HEX_ID)
    if not value.startswith(prefix + ":sha256:"):
        _fail(f"{path}: expected {prefix} identity")
    return value


def _list(value: Any, path: str) -> list:
    if not isinstance(value, list) or not value or len(value) > 10000:
        _fail(f"{path}: expected nonempty bounded array")
    return value


def _lit(s: str) -> str:
    # Printable strings produce Rust-compatible escaped literals.
    return json.dumps(s, ensure_ascii=False)


def _decimal(value: Any, path: str) -> tuple[int, int]:
    s = _string(value, path, DECIMAL)
    digits = s.lstrip("-").replace(".", "")
    if len(digits) > 25:
        _fail(f"{path}: decimal exceeds fixed-point bound")
    scale = len(s.split(".")[1]) if "." in s else 0
    return int(s.replace(".", "")), scale


def _expr(node: Any, path: str, depth: int = 0) -> str:
    if depth > 20:
        _fail(f"{path}: expression nesting exceeds 20")
    if not isinstance(node, dict):
        _fail(f"{path}: expected expression object")
    if set(node) == {"all"} or set(node) == {"any"}:
        operation = next(iter(node))
        items = _list(node[operation], path + "." + operation)
        rendered = [_expr(item, f"{path}.{operation}[{i}]", depth + 1) for i, item in enumerate(items)]
        return f"{operation}(&[{', '.join(rendered)}])"
    if set(node) == {"not"}:
        return f"not({_expr(node['not'], path + '.not', depth + 1)})"
    node = _mapping(node, path, {"fact", "op", "value"})
    key = _string(node["fact"], path + ".fact")
    op = node["op"]
    if not isinstance(op, str) or op not in OPERATORS:
        _fail(f"{path}.op: unsupported comparison")
    value = node["value"]
    if not isinstance(value, dict) or len(value) != 1:
        _fail(f"{path}.value: expected exactly one typed operand")
    kind = next(iter(value))
    if kind == "text":
        if op not in {"eq", "ne"}:
            _fail(f"{path}: text comparisons support eq/ne only")
        actual = _string(value[kind], path + ".value.text")
        return f"text(facts, {_lit(key)}, Op::{OPERATORS[op]}, {_lit(actual)})"
    if kind == "bool":
        if op not in {"eq", "ne"} or type(value[kind]) is not bool:
            _fail(f"{path}: booleans support eq/ne only")
        literal = "true" if value[kind] else "false"
        return f"boolean(facts, {_lit(key)}, Op::{OPERATORS[op]}, {literal})"
    if kind == "quantity":
        q = _mapping(value[kind], path + ".value.quantity", {"decimal", "unit"})
        n, scale = _decimal(q["decimal"], path + ".value.quantity.decimal")
        unit = _string(q["unit"], path + ".value.quantity.unit", UCUM_TOKEN)
        return f"number(facts, {_lit(key)}, Op::{OPERATORS[op]}, {n}i128, {scale}u32, {_lit(unit)})"
    _fail(f"{path}: unknown operand type")


def transpile_rules(document: dict) -> str:
    """Return deterministic Rust code from explicitly reviewed per-edition rules."""
    root = _mapping(document, "root", {"schema_version", "editions"})
    if root["schema_version"] != CONTRACT:
        _fail("root.schema_version: unsupported rule IR contract")
    editions = _list(root["editions"], "root.editions")
    edition_records = []
    match_arms = []
    seen_editions: set[tuple[str, str, str, str]] = set()
    for index, raw_edition in enumerate(editions):
        path = f"editions[{index}]"
        edition = _mapping(raw_edition, path, {"publication", "package_id", "rules", "unsupported"})
        pub = _mapping(
            edition["publication"], path + ".publication",
            {"namespace", "family", "edition", "publication_id"}, {"revision"},
        )
        namespace = _string(pub["namespace"], path + ".namespace")
        family = _string(pub["family"], path + ".family")
        number = _string(pub["edition"], path + ".edition")
        revision = _string(pub["revision"], path + ".revision") if "revision" in pub else ""
        pub_id = _id(pub["publication_id"], path + ".publication_id", "bcastpub")
        pkg_id = _id(edition["package_id"], path + ".package_id", "bcastpkg")
        identity = (namespace, family, number, revision)
        if identity in seen_editions:
            _fail(f"{path}: duplicate publication edition/revision")
        seen_editions.add(identity)
        if not isinstance(edition["rules"], list) or not isinstance(edition["unsupported"], list):
            _fail(f"{path}: rules and unsupported must be arrays")
        if not edition["rules"] and not edition["unsupported"]:
            _fail(f"{path}: empty input has no declared source coverage")
        rendered = []
        rule_ids = set()
        compiled_source_ids = set()
        for j, raw_rule in enumerate(edition["rules"]):
            where = f"{path}.rules[{j}]"
            rule = _mapping(raw_rule, where, {"id", "source", "review", "must"}, {"when", "unless"})
            rule_id = _string(rule["id"], where + ".id")
            if rule_id in rule_ids:
                _fail(f"{where}: duplicate rule id")
            rule_ids.add(rule_id)
            source = _source(rule["source"], where + ".source")
            compiled_source_ids.add(source["object_id"])
            review = _mapping(rule["review"], where + ".review", {"reviewer", "review_ref"})
            _string(review["reviewer"], where + ".review.reviewer")
            _string(review["review_ref"], where + ".review.review_ref")
            applicable = _expr(rule["when"], where + ".when") if "when" in rule else "Truth::Yes"
            exception = _expr(rule["unless"], where + ".unless") if "unless" in rule else "Truth::No"
            required = _expr(rule["must"], where + ".must")
            rendered.append(
                "Finding { rule_id: " + _lit(rule_id)
                + ", source_object_id: " + _lit(source["object_id"])
                + ", source_locator: " + _lit(source["locator"])
                + ", source_text_sha256: " + _lit(source["text_sha256"])
                + ", review_ref: " + _lit(review["review_ref"])
                + ", reason: """
                + f", decision: decide({applicable}, {exception}, {required}) }}"
            )
        for j, raw in enumerate(edition["unsupported"]):
            where = f"{path}.unsupported[{j}]"
            skipped = _mapping(raw, where, {"source", "reason"})
            source = _source(skipped["source"], where + ".source")
            if source["object_id"] in compiled_source_ids:
                _fail(f"{where}: source already declared as compiled")
            _string(skipped["reason"], where + ".reason")
            rendered.append(
                f"Finding {{ rule_id: {_lit('unsupported:' + source['locator'])}, "
                f"source_object_id: {_lit(source['object_id'])}, "
                f"source_locator: {_lit(source['locator'])}, "
                f"source_text_sha256: {_lit(source['text_sha256'])}, "
                f"review_ref: "", reason: {_lit(skipped['reason'])}, "
                "decision: Decision::Unsupported }"
            )
        fields = ", ".join(f"{key}: {_lit(val)}" for key, val in zip(
            ("namespace", "family", "edition", "revision", "publication_id", "package_id"),
            (namespace, family, number, revision, pub_id, pkg_id), strict=True,
        ))
        edition_records.append(
            f"    Edition {{ {fields}, compiled_rules: {len(edition['rules'])}, "
            f"unsupported_objects: {len(edition['unsupported'])} }},"
        )
        arm = ", ".join(map(_lit, identity))
        match_arms.append(f"        ({arm}) => Some(vec![\n            " + ",\n            ".join(rendered) + "\n        ]),")
    runtime = files("bcast").joinpath("rust_runtime.rs").read_text(encoding="utf-8")
    return (
        "// AUTO-GENERATED by bcast.rule_ir/0.1.0. Do not edit.\n"
        "// This is a partial reviewed rule selection, never whole-code compliance.\n"
        + runtime + "\n"
        + "pub const RULE_IR_CONTRACT: &str = \"bcast.rule_ir/0.1.0\";\n"
        + "pub static EDITIONS: &[Edition] = &[\n" + "\n".join(edition_records) + "\n];\n"
        + "pub fn evaluate(namespace: &str, family: &str, edition: &str, "
        + "revision: &str, facts: &[Fact<'_>]) -> Option<Vec<Finding>> {\n"
        + "    match (namespace, family, edition, revision) {\n"
        + "\n".join(match_arms) + "\n        _ => None,\n    }\n}\n"
    )


def _source(value: Any, path: str) -> dict:
    source = _mapping(value, path, {"object_id", "locator", "text_sha256"})
    _id(source["object_id"], path + ".object_id", "bcastobj")
    _string(source["locator"], path + ".locator")
    _string(source["text_sha256"], path + ".text_sha256", DIGEST)
    return source


def main(argv: list[str] | None = None) -> int:
    """Compile a JSON rule IR into standalone Rust, without reading a source corpus."""
    import argparse
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(prog="bcast-rust", description=__doc__)
    parser.add_argument("rules", help="Reviewed source-pinned rule IR JSON")
    parser.add_argument("output", help="Path for generated standalone Rust source")
    args = parser.parse_args(argv)
    try:
        data_path = Path(args.rules)
        if data_path.stat().st_size > 4_000_000:
            raise RuleCompilationError("input exceeds 4 MB")
        data = json.loads(data_path.read_text(encoding="utf-8"))
        result = transpile_rules(data)
        Path(args.output).write_text(result, encoding="utf-8")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())