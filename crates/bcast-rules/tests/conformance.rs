use bcast_rules::compile;
use serde_json::{json, Value};
use std::fs;
use std::process::Command;

const FIXTURE: &str = include_str!("../../../examples/synthetic/reviewed-rules.json");
const SMOKE: &str = include_str!("../../../tests/rust_codegen_smoke.rs");

fn parsed() -> Value {
    serde_json::from_str(FIXTURE).expect("checked synthetic fixture")
}

fn must_fail(doc: Value) {
    assert!(compile(&doc.to_string()).is_err(), "unreviewed/invalid IR was accepted");
}

#[test]
fn multiple_codes_editions_and_deterministic_output() {
    let generated = compile(FIXTURE).unwrap();
    let mut swapped = parsed();
    swapped["editions"].as_array_mut().unwrap().reverse();
    assert_eq!(generated, compile(&swapped.to_string()).unwrap());
    assert!(generated.contains("synthetic-building-code"));
    assert!(generated.contains("synthetic-fire-code"));
    assert!(generated.contains("Decision::Unsupported"));
    assert!(generated.contains("edition: \"2027\""));
    assert_eq!(generated.matches("Edition { namespace:").count(), 3);
}

#[test]
fn rejects_unknown_fields_unreviewed_rules_bad_values_and_edition_aliasing() {
    let mut doc = parsed();
    doc["editions"][0]["rules"][0].as_object_mut().unwrap().remove("review");
    must_fail(doc);

    let mut doc = parsed();
    doc["editions"][0]["rules"][0]["must"]["value"]["quantity"]["decimal"] = json!("NaN");
    must_fail(doc);

    let mut doc = parsed();
    doc["editions"][0]["rules"][0]["must"]["value"]["quantity"]["unit"] = json!("");
    must_fail(doc);
    let mut doc = parsed();
    doc["editions"][0]["rules"][0]["must"]["value"]["quantity"]["unit"] = json!("mysteryUnit");
    must_fail(doc);

    let mut doc = parsed();
    doc["editions"][0]["rules"][0]["must"]["op"] = json!("inferred");
    must_fail(doc);

    let mut doc = parsed();
    doc["editions"][0]["rules"][0]["new_legal_text"] = json!("restricted");
    must_fail(doc);

    let mut doc = parsed();
    let duplicated = doc["editions"][0].clone();
    doc["editions"].as_array_mut().unwrap().push(duplicated);
    must_fail(doc);

    let mut doc = parsed();
    doc["editions"][0]["unsupported"][0]["source"]["object_id"] =
        doc["editions"][0]["rules"][0]["source"]["object_id"].clone();
    must_fail(doc);
}

#[test]
fn rejects_noncanonical_decimals_and_invalid_expression_forms() {
    for bad in ["01", "1.", "1e2", "1.0000000", "", "+4", "NaN"] {
        let mut doc = parsed();
        doc["editions"][0]["rules"][0]["must"]["value"]["quantity"]["decimal"] = json!(bad);
        must_fail(doc);
    }

    let mut doc = parsed();
    doc["editions"][0]["rules"][0]["must"] = json!({"all": []});
    must_fail(doc);

    let mut doc = parsed();
    doc["editions"][0]["rules"][0]["must"] = json!({"not": {"not": {"oops": true}}});
    must_fail(doc);

    let mut doc = parsed();
    doc["editions"][0]["rules"][0]["must"] = json!({"fact": "x", "op": "gt", "value": {"text": "a"}});
    must_fail(doc);
}

#[test]
fn generated_rust_executes_original_behavioral_conformance() {
    let dir = std::env::temp_dir().join(format!("bcast-native-{}", std::process::id()));
    fs::create_dir_all(&dir).unwrap();
    let source = dir.join("generated_rule_tests.rs");
    let binary = dir.join("generated_rule_tests");
    fs::write(&source, format!("{}\n{SMOKE}", compile(FIXTURE).unwrap())).unwrap();
    let compiled = Command::new("rustc")
        .args(["--edition=2021", "--test"])
        .arg(&source)
        .arg("-o")
        .arg(&binary)
        .output()
        .unwrap();
    assert!(compiled.status.success(), "{}", String::from_utf8_lossy(&compiled.stderr));
    let executed = Command::new(&binary).output().unwrap();
    assert!(executed.status.success(), "{}", String::from_utf8_lossy(&executed.stderr));
    fs::remove_dir_all(dir).unwrap();
}
