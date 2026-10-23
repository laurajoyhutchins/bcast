//! Native Rust compiler for reviewed, source-independent BCAST rule IR.
//! No legal text extraction, edition adoption or interpretation occurs here.
mod sbvr;
pub use sbvr::{compile_combined, PROPOSAL_CONTRACT};
use serde::Deserialize;
use std::collections::BTreeSet;
use std::error::Error;
use std::fmt;

pub const CONTRACT: &str = "bcast.rule_ir/0.1.0";
pub const MAX_BYTES: usize = 4_000_000;
const MAX_ITEMS: usize = 10_000;
const MAX_DEPTH: usize = 20;
const RUNTIME: &str = include_str!("runtime.rs");

#[derive(Debug)]
pub struct CompileError(String);

impl fmt::Display for CompileError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(f)
    }
}
impl Error for CompileError {}

fn fail(message: impl Into<String>) -> CompileError {
    CompileError(message.into())
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Document {
    schema_version: String,
    editions: Vec<CodeEdition>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct CodeEdition {
    publication: Publication,
    package_id: String,
    rules: Vec<Rule>,
    unsupported: Vec<Unsupported>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Publication {
    namespace: String,
    family: String,
    edition: String,
    publication_id: String,
    revision: Option<String>,
}

impl Publication {
    fn revision(&self) -> &str {
        self.revision.as_deref().unwrap_or("")
    }
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Source {
    object_id: String,
    locator: String,
    text_sha256: String,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Review {
    reviewer: String,
    review_ref: String,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Rule {
    id: String,
    source: Source,
    review: Review,
    when: Option<Expr>,
    unless: Option<Expr>,
    must: Expr,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Unsupported {
    source: Source,
    reason: String,
}

#[derive(Deserialize)]
#[serde(untagged)]
enum Expr {
    All(AllExpr),
    Any(AnyExpr),
    Not(NotExpr),
    Compare(Comparison),
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct AllExpr {
    all: Vec<Expr>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct AnyExpr {
    any: Vec<Expr>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct NotExpr {
    not: Box<Expr>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Comparison {
    fact: String,
    op: Operator,
    value: Operand,
}

#[derive(Clone, Copy, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Operator {
    Eq,
    Ne,
    Lt,
    Le,
    Gt,
    Ge,
}

impl Operator {
    fn rust(self) -> &'static str {
        match self {
            Self::Eq => "Eq",
            Self::Ne => "Ne",
            Self::Lt => "Lt",
            Self::Le => "Le",
            Self::Gt => "Gt",
            Self::Ge => "Ge",
        }
    }
    fn equality(self) -> bool {
        matches!(self, Self::Eq | Self::Ne)
    }
}

#[derive(Deserialize)]
#[serde(untagged)]
enum Operand {
    Text(TextOperand),
    Bool(BoolOperand),
    Quantity(QuantityOperand),
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct TextOperand {
    text: String,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct BoolOperand {
    #[serde(rename = "bool")]
    value: bool,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct QuantityOperand {
    quantity: Quantity,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Quantity {
    decimal: String,
    unit: String,
}

fn checked_text(value: &str, path: &str) -> Result<(), CompileError> {
    if value.is_empty() || value.len() > 512 || value.chars().any(char::is_control) {
        return Err(fail(format!("{path}: expected a nonempty printable string")));
    }
    Ok(())
}

fn checked_id(value: &str, prefix: &str) -> Result<(), CompileError> {
    let expected = format!("{prefix}:sha256:");
    let Some(digest) = value.strip_prefix(&expected) else {
        return Err(fail(format!("expected {prefix} identity")));
    };
    if !is_digest(digest) {
        return Err(fail(format!("invalid {prefix} SHA-256 identity")));
    }
    Ok(())
}

fn is_digest(s: &str) -> bool {
    s.len() == 64 && s.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}

fn checked_namespace(s: &str) -> Result<(), CompileError> {
    if s.len() > 253 || !s.contains('.') ||
        !s.split('.').all(|part| {
            !part.is_empty() && part.len() <= 63 &&
                part.as_bytes().first().is_some_and(u8::is_ascii_alphanumeric) &&
                part.as_bytes().last().is_some_and(u8::is_ascii_alphanumeric) &&
                part.bytes().all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-')
        }) {
        return Err(fail("publication namespace must be canonical lowercase DNS"));
    }
    Ok(())
}

fn checked_family(s: &str) -> Result<(), CompileError> {
    if s.is_empty() || s.len() > 256 || s.starts_with('-') || s.ends_with('-') ||
        s.contains("--") || !s.bytes().all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-') {
        return Err(fail("publication family must be canonical lowercase slug"));
    }
    Ok(())
}

fn checked_source(source: &Source) -> Result<(), CompileError> {
    checked_id(&source.object_id, "bcastobj")?;
    checked_text(&source.locator, "source.locator")?;
    if !is_digest(&source.text_sha256) {
        return Err(fail("source.text_sha256 must be lowercase SHA-256"));
    }
    Ok(())
}

fn limited_len(len: usize, label: &str, allow_empty: bool) -> Result<(), CompileError> {
    if len > MAX_ITEMS || (!allow_empty && len == 0) {
        return Err(fail(format!("{label}: invalid bounded list size")));
    }
    Ok(())
}

fn literal(s: &str) -> String {
    // Rust's Debug formatter produces a Rust-compatible escaped string literal.
    format!("{s:?}")
}

fn decimal(input: &str) -> Result<(i128, u32), CompileError> {
    let digits = input.strip_prefix('-').unwrap_or(input);
    let (whole, fraction) = digits.split_once('.').unwrap_or((digits, ""));
    if whole.is_empty() || (whole.len() > 1 && whole.starts_with('0')) ||
        !whole.bytes().all(|b| b.is_ascii_digit()) ||
        (digits.contains('.') && fraction.is_empty()) ||
        fraction.len() > 6 || !fraction.bytes().all(|b| b.is_ascii_digit()) ||
        whole.len() + fraction.len() > 25 {
        return Err(fail("quantity.decimal is not a bounded canonical fixed decimal"));
    }
    let normalized = format!("{}{}{}", if input.starts_with('-') { "-" } else { "" }, whole, fraction);
    let mantissa = normalized.parse::<i128>().map_err(|_| fail("quantity exceeds i128"))?;
    Ok((mantissa, fraction.len() as u32))
}

fn emit_expr(node: &Expr, depth: usize) -> Result<String, CompileError> {
    if depth > MAX_DEPTH {
        return Err(fail("expression nesting exceeds 20"));
    }
    match node {
        Expr::All(items) => {
            limited_len(items.all.len(), "all", false)?;
            let children = items.all.iter()
                .map(|x| emit_expr(x, depth + 1))
                .collect::<Result<Vec<_>, _>>()?;
            Ok(format!("all(&[{}])", children.join(", ")))
        }
        Expr::Any(items) => {
            limited_len(items.any.len(), "any", false)?;
            let children = items.any.iter()
                .map(|x| emit_expr(x, depth + 1))
                .collect::<Result<Vec<_>, _>>()?;
            Ok(format!("any(&[{}])", children.join(", ")))
        }
        Expr::Not(item) => Ok(format!("not({})", emit_expr(&item.not, depth + 1)?)),
        Expr::Compare(compare) => {
            checked_text(&compare.fact, "fact")?;
            let key = literal(&compare.fact);
            let op = compare.op.rust();
            match &compare.value {
                Operand::Text(value) => {
                    if !compare.op.equality() { return Err(fail("text supports eq/ne only")); }
                    checked_text(&value.text, "value.text")?;
                    Ok(format!("text(facts, {key}, Op::{op}, {})", literal(&value.text)))
                }
                Operand::Bool(value) => {
                    if !compare.op.equality() { return Err(fail("boolean supports eq/ne only")); }
                    Ok(format!("boolean(facts, {key}, Op::{op}, {})", value.value))
                }
                Operand::Quantity(value) => {
                    let (n, scale) = decimal(&value.quantity.decimal)?;
                    let unit = &value.quantity.unit;
                    if unit.is_empty() || unit.len() > 64 ||
                        !unit.bytes().all(|b| b.is_ascii_alphanumeric() || b"%./[]_{}+-".contains(&b)) {
                        return Err(fail("quantity.unit is not a bounded unit token"));
                    }
                    Ok(format!("number(facts, {key}, Op::{op}, {n}i128, {scale}u32, {})", literal(unit)))
                }
            }
        }
    }
}

/// Compile reviewed machine-readable rule IR into dependency-free, standalone Rust.
/// The returned evaluations are predicates, never legal compliance certifications.
pub fn compile(input: &str) -> Result<String, CompileError> {
    if input.len() > MAX_BYTES {
        return Err(fail("input exceeds 4 MB"));
    }
    let mut doc: Document = serde_json::from_str(input)
        .map_err(|e| fail(format!("invalid rule IR: {e}")))?;
    if doc.schema_version != CONTRACT {
        return Err(fail("unsupported rule IR schema_version"));
    }
    limited_len(doc.editions.len(), "editions", false)?;
    doc.editions.sort_by(|a, b| {
        (&a.publication.namespace, &a.publication.family, &a.publication.edition, a.publication.revision())
            .cmp(&(&b.publication.namespace, &b.publication.family, &b.publication.edition, b.publication.revision()))
    });
    let mut edition_keys = BTreeSet::new();
    let mut edition_rows = Vec::new();
    let mut arms = Vec::new();

    for mut edition in doc.editions {
        let pubn = &edition.publication;
        checked_namespace(&pubn.namespace)?;
        checked_family(&pubn.family)?;
        checked_text(&pubn.edition, "publication.edition")?;
        if pubn.revision.is_some() { checked_text(pubn.revision(), "publication.revision")?; }
        checked_id(&pubn.publication_id, "bcastpub")?;
        checked_id(&edition.package_id, "bcastpkg")?;
        let key = (&pubn.namespace, &pubn.family, &pubn.edition, pubn.revision());
        if !edition_keys.insert((
            key.0.to_string(), key.1.to_string(), key.2.to_string(), key.3.to_owned()
        )) { return Err(fail("duplicate edition/revision coordinate")); }
        limited_len(edition.rules.len(), "rules", true)?;
        limited_len(edition.unsupported.len(), "unsupported", true)?;
        if edition.rules.is_empty() && edition.unsupported.is_empty() {
            return Err(fail("edition cannot silently declare empty coverage"));
        }
        edition.rules.sort_by(|a, b| a.id.cmp(&b.id));
        edition.unsupported.sort_by(|a, b| a.source.object_id.cmp(&b.source.object_id));
        let mut rule_ids = BTreeSet::new();
        let mut compiled_sources = BTreeSet::new();
        let mut findings = Vec::new();
        for rule in &edition.rules {
            checked_text(&rule.id, "rule.id")?;
            if !rule_ids.insert(&rule.id) { return Err(fail("duplicate rule id")); }
            checked_source(&rule.source)?;
            compiled_sources.insert(&rule.source.object_id);
            checked_text(&rule.review.reviewer, "review.reviewer")?;
            checked_text(&rule.review.review_ref, "review.review_ref")?;
            let applicable = rule.when.as_ref().map_or(Ok("Truth::Yes".to_owned()), |x| emit_expr(x, 0))?;
            let exception = rule.unless.as_ref().map_or(Ok("Truth::No".to_owned()), |x| emit_expr(x, 0))?;
            let requirement = emit_expr(&rule.must, 0)?;
            findings.push(format!(
                "            Finding {{ rule_id: {}, source_object_id: {}, source_locator: {}, source_text_sha256: {}, review_ref: {}, reason: \"\", decision: decide({applicable}, {exception}, {requirement}) }}",
                literal(&rule.id), literal(&rule.source.object_id), literal(&rule.source.locator),
                literal(&rule.source.text_sha256), literal(&rule.review.review_ref)
            ));
        }
        let mut unsupported_sources = BTreeSet::new();
        for item in &edition.unsupported {
            checked_source(&item.source)?;
            checked_text(&item.reason, "unsupported.reason")?;
            if compiled_sources.contains(&item.source.object_id) ||
                !unsupported_sources.insert(&item.source.object_id) {
                return Err(fail("duplicate or contradictory unsupported source"));
            }
            findings.push(format!(
                "            Finding {{ rule_id: {}, source_object_id: {}, source_locator: {}, source_text_sha256: {}, review_ref: \"\", reason: {}, decision: Decision::Unsupported }}",
                literal(&format!("unsupported:{}", item.source.locator)),
                literal(&item.source.object_id), literal(&item.source.locator),
                literal(&item.source.text_sha256), literal(&item.reason)
            ));
        }
        edition_rows.push(format!(
            "    Edition {{ namespace: {}, family: {}, edition: {}, revision: {}, publication_id: {}, package_id: {}, compiled_rules: {}, unsupported_objects: {} }},",
            literal(&pubn.namespace), literal(&pubn.family), literal(&pubn.edition),
            literal(pubn.revision()), literal(&pubn.publication_id), literal(&edition.package_id),
            edition.rules.len(), edition.unsupported.len()
        ));
        arms.push(format!(
            "        ({}, {}, {}, {}) => Some(vec![\n{}\n        ]),",
            literal(&pubn.namespace), literal(&pubn.family), literal(&pubn.edition),
            literal(pubn.revision()), findings.join(",\n")
        ));
    }
    Ok(format!(
        "// AUTO-GENERATED by native BCAST Rust compiler. Do not edit.\n\
         // Partial reviewed rules only, never a whole-code compliance determination.\n\
         {RUNTIME}\n\
         pub const RULE_IR_CONTRACT: &str = \"bcast.rule_ir/0.1.0\";\n\
         pub static EDITIONS: &[Edition] = &[\n{}\n];\n\
         pub fn evaluate(namespace: &str, family: &str, edition: &str, revision: &str, facts: &[Fact<'_>]) -> Option<Vec<Finding>> {{\n\
             match (namespace, family, edition, revision) {{\n{}\n        _ => None,\n    }}\n}}\n",
        edition_rows.join("\n"), arms.join("\n")
    ))
}
