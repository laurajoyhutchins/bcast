// Generated rule sets use this source-independent evaluation kernel.
// No source text, legal authority, or edition selection is inferred here.
use std::cmp::Ordering;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Truth {
    Yes,
    No,
    Unknown,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Decision {
    Satisfied,
    Violated,
    NotApplicable,
    Excepted,
    InsufficientFacts,
    Unsupported,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Value<'a> {
    Bool(bool),
    Text(&'a str),
    // Fixed-point decimal. No binary floating-point rounding.
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

// Missing, conflicting, and duplicate facts are all unknown, never false.
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
    let yes = match op {
        Op::Eq => found == Ordering::Equal,
        Op::Ne => found != Ordering::Equal,
        Op::Lt => found == Ordering::Less,
        Op::Le => found != Ordering::Greater,
        Op::Gt => found == Ordering::Greater,
        Op::Ge => found != Ordering::Less,
    };
    if yes { Truth::Yes } else { Truth::No }
}

fn compare_fixed(a: i128, a_scale: u32, b: i128, b_scale: u32) -> Option<Ordering> {
    if a_scale > 18 || b_scale > 18 { return None; }
    let aa = a.checked_mul(10_i128.checked_pow(b_scale)?)?;
    let bb = b.checked_mul(10_i128.checked_pow(a_scale)?)?;
    Some(aa.cmp(&bb))
}

pub fn number(facts: &[Fact<'_>], key: &str, op: Op, n: i128, scale: u32, unit: &str) -> Truth {
    match lookup(facts, key) {
        Some(Value::Quantity { mantissa, scale: got_scale, unit: got_unit }) if got_unit == unit => {
            match compare_fixed(mantissa, got_scale, n, scale) {
                Some(order) => order_to_truth(order, op),
                None => Truth::Unknown,
            }
        }
        _ => Truth::Unknown,
    }
}

pub fn text(facts: &[Fact<'_>], key: &str, op: Op, expected: &str) -> Truth {
    match lookup(facts, key) {
        Some(Value::Text(got)) => order_to_truth(got.cmp(expected), op),
        _ => Truth::Unknown,
    }
}

pub fn boolean(facts: &[Fact<'_>], key: &str, op: Op, expected: bool) -> Truth {
    match lookup(facts, key) {
        Some(Value::Bool(got)) => order_to_truth(got.cmp(&expected), op),
        _ => Truth::Unknown,
    }
}

pub fn all(items: &[Truth]) -> Truth {
    if items.iter().any(|v| *v == Truth::No) { Truth::No }
    else if items.iter().any(|v| *v == Truth::Unknown) { Truth::Unknown }
    else { Truth::Yes }
}

pub fn any(items: &[Truth]) -> Truth {
    if items.iter().any(|v| *v == Truth::Yes) { Truth::Yes }
    else if items.iter().any(|v| *v == Truth::Unknown) { Truth::Unknown }
    else { Truth::No }
}

pub fn not(item: Truth) -> Truth {
    match item { Truth::Yes => Truth::No, Truth::No => Truth::Yes, Truth::Unknown => Truth::Unknown }
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