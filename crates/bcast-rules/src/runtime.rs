// Public, source-independent evaluation kernel. Embedded into generated Rust.
// Source extraction, publication adoption and legal interpretation are external.
use std::cmp::Ordering;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Truth { Yes, No, Unknown }

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Decision {
    Satisfied, Violated, NotApplicable, Excepted, InsufficientFacts, Unsupported,
    Permitted, PermissionNotEstablished,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Value<'a> {
    Bool(bool),
    Text(&'a str),
    Quantity { mantissa: i128, scale: u32, unit: &'a str },
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Fact<'a> {
    pub name: &'a str,
    pub value: Value<'a>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Op { Eq, Ne, Lt, Le, Gt, Ge }

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Edition {
    pub namespace: &'static str,
    pub family: &'static str,
    pub edition: &'static str,
    pub revision: &'static str,
    pub publication_id: &'static str,
    pub package_id: &'static str,
    pub compiled_rules: usize,
    pub unsupported_objects: usize,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Finding {
    pub rule_id: &'static str,
    pub source_object_id: &'static str,
    pub source_locator: &'static str,
    pub source_text_sha256: &'static str,
    pub review_ref: &'static str,
    pub reason: &'static str,
    pub decision: Decision,
}

// Duplicate facts fail closed even when duplicate values happen to agree.
fn lookup<'a>(facts: &'a [Fact<'a>], name: &str) -> Option<Value<'a>> {
    let mut found = None;
    for fact in facts {
        if fact.name == name {
            if found.is_some() { return None; }
            found = Some(fact.value);
        }
    }
    found
}

fn order_to_truth(found: Ordering, op: Op) -> Truth {
    let matches = match op {
        Op::Eq => found == Ordering::Equal,
        Op::Ne => found != Ordering::Equal,
        Op::Lt => found == Ordering::Less,
        Op::Le => found != Ordering::Greater,
        Op::Gt => found == Ordering::Greater,
        Op::Ge => found != Ordering::Less,
    };
    if matches { Truth::Yes } else { Truth::No }
}

fn compare_fixed(a: i128, a_scale: u32, b: i128, b_scale: u32) -> Option<Ordering> {
    if a_scale > 18 || b_scale > 18 { return None; }
    let left = a.checked_mul(10_i128.checked_pow(b_scale)?)?;
    let right = b.checked_mul(10_i128.checked_pow(a_scale)?)?;
    Some(left.cmp(&right))
}

// Compare fixed-point quantities by exact rational unit factors.
// All multiplications are checked: an unrepresentable comparison is Unknown,
// never a guessed pass or fail.
fn compare_quantity(
    a: i128, a_scale: u32, a_unit: &str,
    b: i128, b_scale: u32, b_unit: &str,
) -> Option<Ordering> {
    if a_scale > 18 || b_scale > 18 { return None; }
    let first = unit_spec(a_unit)?;
    let second = unit_spec(b_unit)?;
    if first.dimension != second.dimension { return None; }
    let lhs = a.checked_mul(first.numerator)?
        .checked_mul(second.denominator)?
        .checked_mul(10_i128.checked_pow(b_scale)?)?;
    let rhs = b.checked_mul(second.numerator)?
        .checked_mul(first.denominator)?
        .checked_mul(10_i128.checked_pow(a_scale)?)?;
    Some(lhs.cmp(&rhs))
}

pub fn number(facts: &[Fact<'_>], key: &str, op: Op, n: i128, scale: u32, unit: &str) -> Truth {
    match lookup(facts, key) {
        Some(Value::Quantity { mantissa, scale: got_scale, unit: got_unit }) => {
            compare_quantity(mantissa, got_scale, got_unit, n, scale, unit)
                .map_or(Truth::Unknown, |order| order_to_truth(order, op))
        }
        _ => Truth::Unknown,
    }
}

pub fn text(facts: &[Fact<'_>], key: &str, op: Op, expected: &str) -> Truth {
    match lookup(facts, key) {
        Some(Value::Text(found)) => order_to_truth(found.cmp(expected), op),
        _ => Truth::Unknown,
    }
}

pub fn boolean(facts: &[Fact<'_>], key: &str, op: Op, expected: bool) -> Truth {
    match lookup(facts, key) {
        Some(Value::Bool(found)) => order_to_truth(found.cmp(&expected), op),
        _ => Truth::Unknown,
    }
}

pub fn all(items: &[Truth]) -> Truth {
    if items.contains(&Truth::No) { Truth::No }
    else if items.contains(&Truth::Unknown) { Truth::Unknown }
    else { Truth::Yes }
}

pub fn any(items: &[Truth]) -> Truth {
    if items.contains(&Truth::Yes) { Truth::Yes }
    else if items.contains(&Truth::Unknown) { Truth::Unknown }
    else { Truth::No }
}

pub fn not(item: Truth) -> Truth {
    match item {
        Truth::Yes => Truth::No,
        Truth::No => Truth::Yes,
        Truth::Unknown => Truth::Unknown,
    }
}

pub fn decide(applicable: Truth, excepted: Truth, required: Truth) -> Decision {
    match applicable {
        Truth::No => Decision::NotApplicable,
        Truth::Unknown => Decision::InsufficientFacts,
        Truth::Yes => match excepted {
            Truth::Yes => Decision::Excepted,
            Truth::Unknown => Decision::InsufficientFacts,
            Truth::No => match required {
                Truth::Yes => Decision::Satisfied,
                Truth::No => Decision::Violated,
                Truth::Unknown => Decision::InsufficientFacts,
            },
        },
    }
}


// The predicate for a prohibition denotes a forbidden action, not a required one.
pub fn decide_prohibition(applicable: Truth, excepted: Truth, forbidden: Truth) -> Decision {
    match decide(applicable, excepted, not(forbidden)) {
        Decision::Satisfied => Decision::Satisfied,
        Decision::Violated => Decision::Violated,
        other => other,
    }
}

// A permission is NOT an obligation. Failure to establish permission is not
// automatically a violation of any code provision.
pub fn decide_permission(applicable: Truth, excepted: Truth, allowed: Truth) -> Decision {
    match applicable {
        Truth::No => Decision::NotApplicable,
        Truth::Unknown => Decision::InsufficientFacts,
        Truth::Yes => match excepted {
            Truth::Yes => Decision::PermissionNotEstablished,
            Truth::Unknown => Decision::InsufficientFacts,
            Truth::No => match allowed {
                Truth::Yes => Decision::Permitted,
                Truth::No => Decision::PermissionNotEstablished,
                Truth::Unknown => Decision::InsufficientFacts,
            },
        },
    }
}


// Summary of a *selected* source scope. No variant means "code compliant".
// A single satisfied predicate never establishes provision or edition coverage.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum EvidenceStatus {
    IncompleteCoverage,
    PredicateViolationObserved,
    PredicateEvidenceOnly,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct OpenQuestion {
    pub proposal_id: &'static str,
    pub source_object_id: &'static str,
    pub source_locator: &'static str,
    pub reason: &'static str,
    pub dependencies: &'static [&'static str],
}

#[derive(Debug)]
pub struct EvidenceReport {
    pub status: EvidenceStatus,
    pub publication_id: &'static str,
    pub package_id: &'static str,
    pub source_artifact_sha256: &'static str,
    pub selected_passages: usize,
    pub source_package_objects: usize,
    pub admitted_proposals: usize,
    pub unresolved_proposals: usize,
    pub rejected_proposals: usize,
    pub findings: Vec<Finding>,
    pub open_questions: &'static [OpenQuestion],
    pub predicate_violations: usize,
    pub predicates_with_missing_facts: usize,
}

pub fn assess_evidence(
    findings: &[Finding],
    unresolved_proposals: usize,
    rejected_proposals: usize,
    package_objects_not_selected: usize,
) -> (EvidenceStatus, usize, usize) {
    let violated = findings.iter().filter(|f| f.decision == Decision::Violated).count();
    let unknown = findings.iter().filter(|f|
        matches!(f.decision, Decision::InsufficientFacts |
                 Decision::Unsupported | Decision::PermissionNotEstablished)
    ).count();
    let missing_scope = unresolved_proposals > 0 || rejected_proposals > 0 ||
        package_objects_not_selected > 0 || unknown > 0;
    let status = if missing_scope {
        EvidenceStatus::IncompleteCoverage
    } else if violated > 0 {
        EvidenceStatus::PredicateViolationObserved
    } else {
        EvidenceStatus::PredicateEvidenceOnly
    };
    (status, violated, unknown)
}
