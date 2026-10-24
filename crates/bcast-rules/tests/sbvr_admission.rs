use bcast_rules::compile_combined;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs;
use std::process::Command;

fn sha(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }
fn addr(prefix: &str, payload: Value) -> String {
    format!("{prefix}:sha256:{}", sha(&serde_json::to_vec(&payload).unwrap()))
}

fn batch() -> Value {
    let publication = json!({"namespace":"study.example","family":"fictional-electrical","edition":"2017"});
    let publication_id = addr("bcastpub", publication.clone());
    let pkg = format!("bcastpkg:sha256:{}", "e".repeat(64));
    let source_id = addr("bcastobj", json!({
        "publication_id":publication_id,"kind":"section","locator":"210.19(A)(3)"
    }));
    let next_source_id = addr("bcastobj",json!({
        "publication_id":publication_id,"kind":"section","locator":"210.19(A)(4)"
    }));
    let artifact = sha(b"synthetic PDF bytes");
    let mut passages = Vec::new();
    for (object,locator,page,bbox,text) in [
        (&source_id,"210.19(A)(3)",65_u32,[36000_u32,289000,285000,360000],"synthetic threshold passage"),
        (&next_source_id,"210.19(A)(4)",65_u32,[36000_u32,528000,285000,578000],"synthetic unsupported passage")
    ] {
        let digest = sha(text.as_bytes());
        let id = addr("bcastpassage",json!({
            "artifact_sha256": artifact, "source_object_id":object,
            "pdf_page":page,"bbox_millipoints":bbox,"text_sha256":digest
        }));
        passages.push(json!({
            "passage_id":id,"kind":"section","locator":locator,"source_object_id":object,
            "pdf_page":page,"bbox_millipoints":bbox,"text":text,"text_sha256":digest
        }));
    }
    let first_id = passages[0]["passage_id"].clone();
    let second_id = passages[1]["passage_id"].clone();
    let baseline = json!({
        "schema_version":"bcast.rule_ir/0.1.0",
        "editions":[{
            "publication": {
                "namespace":"study.example","family":"fictional-electrical","edition":"2017",
                "publication_id":publication_id
            },
            "package_id":pkg,
            "rules":[{
                "id":"baseline", "source":{"object_id":source_id,"locator":"210.19(A)(3)","text_sha256":sha(b"synthetic threshold passage")},
                "review":{"reviewer":"test reviewer","review_ref":"test:baseline"},
                "must":{"fact":"baseline.enabled","op":"eq","value":{"bool":true}}
            }],
            "unsupported":[]
        }]
    });
    json!({
        "schema_version":"bcast.sbvr_proposal_batch/0.1.0",
        "baseline":baseline,
        "source":{
            "namespace":"study.example","family":"fictional-electrical","edition":"2017",
            "publication_id":publication_id,"package_id":pkg,"artifact_sha256":artifact,
            "media_type":"application/pdf"
        },
        "passages":passages,
        "proposals":[
            {"proposal_id":"new-threshold","passage_id":first_id,"modality":"obligation","disposition":"admitted",
             "condition":{"fact":"household","op":"eq","value":{"bool":true}},
             "exception":{"fact":"exemption","op":"eq","value":{"bool":true}},
             "predicate":{"fact":"branch.rating","op":"ge","value":{"quantity":{"decimal":"40","unit":"A"}}},
             "dependencies":[{"locator":"210.19(A)(3)","resolved":true}],
             "review":{"reviewer":"synthetic tester","review_ref":"test:threshold"}},
            {"proposal_id":"new-permission","passage_id":first_id,"modality":"permission","disposition":"admitted",
             "predicate":{"fact":"alternate.allowed","op":"eq","value":{"bool":true}},
             "dependencies":[],"review":{"reviewer":"synthetic tester","review_ref":"test:permission"}},
            {"proposal_id":"needs-definition","passage_id":second_id,"modality":"prohibition","disposition":"unresolved",
             "dependencies":[{"locator":"Article 100","resolved":false}],"reason":"term not interpreted"}
        ],
        "accounting":{"extracted_passages":2,"classified_passages":2,"proposals":3,"admitted":2,"unresolved":1,"rejected":0}
    })
}

#[test]
fn combined_compilation_is_deterministic_and_omits_protected_text() {
    let first = batch();
    let output = compile_combined(&first.to_string()).unwrap();
    assert_eq!(output, compile_combined(&first.to_string()).unwrap());
    assert!(output.contains("pub fn evaluate_combined"));
    assert!(output.contains("pub fn evaluate_sbvr"));
    assert!(output.contains("pub fn decide_permission"));
    assert!(output.contains("SBVR_PASSAGE_COUNT: usize = 2"));
    assert!(output.contains("SBVR_ADMITTED_COUNT: usize = 2"));
    assert!(output.contains("SBVR_UNRESOLVED_COUNT: usize = 1"));
    assert!(output.contains("SBVR_REJECTED_COUNT: usize = 0"));
    assert!(!output.contains("synthetic threshold passage"));
    assert!(!output.contains("synthetic unsupported passage"));
}

#[test]
fn source_anchors_types_dependencies_and_accounting_fail_closed() {
    let cases: Vec<(&str,Box<dyn Fn(&mut Value)>)> = vec![
        ("text drift",Box::new(|d| d["passages"][0]["text"] = json!("changed"))),
        ("object forgery",Box::new(|d| d["passages"][0]["source_object_id"] = json!(format!("bcastobj:sha256:{}", "f".repeat(64))))),
        ("artifact drift",Box::new(|d| d["source"]["artifact_sha256"] = json!("a".repeat(64)))),
        ("page drift",Box::new(|d| d["passages"][0]["pdf_page"] = json!(66))),
        ("duplicate passage",Box::new(|d| {let duplicate=d["passages"][0].clone();d["passages"].as_array_mut().unwrap().push(duplicate);})),
        ("unclassified source",Box::new(|d| {d["proposals"].as_array_mut().unwrap().pop(); d["accounting"]=json!({"extracted_passages":2,"classified_passages":1,"proposals":2,"admitted":2,"unresolved":0,"rejected":0});})),
        ("orphan proposal",Box::new(|d| d["proposals"][0]["passage_id"] = json!(format!("bcastpassage:sha256:{}", "b".repeat(64))))),
        ("accounting fraud",Box::new(|d| d["accounting"]["admitted"] = json!(999))),
        ("unresolved dependency",Box::new(|d| d["proposals"][0]["dependencies"][0]["resolved"] = json!(false))),
        ("missing review",Box::new(|d| {d["proposals"][0].as_object_mut().unwrap().remove("review");})),
        ("wrong operand type",Box::new(|d| d["proposals"][0]["predicate"]["value"] = json!({"text": 12}))),
        ("duplicate proposal",Box::new(|d| d["proposals"][1]["proposal_id"] = json!("new-threshold"))),
        ("invalid unresolved condition",Box::new(|d| d["proposals"][2]["condition"] = json!({"fact":"x","op":"gt","value":{"bool":true}}))),
        ("source/baseline conflict",Box::new(|d| d["baseline"]["editions"][0]["rules"][0]["source"]["text_sha256"] = json!("c".repeat(64)))),
        ("duplicate dependency",Box::new(|d| {
            let item=d["proposals"][0]["dependencies"][0].clone();
            d["proposals"][0]["dependencies"].as_array_mut().unwrap().push(item);
        })),
        ("unreviewed executable",Box::new(|d| d["proposals"][2]["predicate"] = json!({"fact":"x","op":"eq","value":{"bool":true}}))),
        ("unmatched edition",Box::new(|d| d["source"]["edition"] = json!("2020")))
    ];
    for (label,mutate) in cases {
        let mut doc = batch();
        mutate(&mut doc);
        assert!(compile_combined(&doc.to_string()).is_err(), "{label} was admitted");
    }
}

#[test]
fn exact_generated_rust_runs_baseline_and_admitted_predicates() {
    let dir = std::env::temp_dir().join(format!("bcast-sbvr-proof-{}",std::process::id()));
    fs::create_dir_all(&dir).unwrap();
    let source = dir.join("combined.rs");
    let binary = dir.join("combined-tests");
    let tests = r#"
#[cfg(test)]
mod combined_tests {
    use super::*;
    fn f(enabled: bool, rating: i128, allowed: bool) -> Vec<Fact<'static>> {
        vec![
            Fact{name:"baseline.enabled",value:Value::Bool(enabled)},
            Fact{name:"household",value:Value::Bool(true)},
            Fact{name:"exemption",value:Value::Bool(false)},
            Fact{name:"branch.rating",value:Value::Quantity{mantissa:rating,scale:0,unit:"A"}},
            Fact{name:"alternate.allowed",value:Value::Bool(allowed)}
        ]
    }
    #[test]
    fn existing_and_new_rules_coexist() {
        let found=evaluate_combined("study.example","fictional-electrical","2017","",&f(true,40,true)).unwrap();
        assert_eq!(found.len(),3);
        assert_eq!(found[0].decision,Decision::Satisfied);
        assert_eq!(found.iter().find(|x| x.rule_id == "new-threshold").unwrap().decision,Decision::Satisfied);
        assert_eq!(found.iter().find(|x| x.rule_id == "new-permission").unwrap().decision,Decision::Permitted);
        let failed=evaluate_combined("study.example","fictional-electrical","2017","",&f(true,39,false)).unwrap();
        assert_eq!(failed.iter().find(|x| x.rule_id == "new-threshold").unwrap().decision,Decision::Violated);
        assert_eq!(failed.iter().find(|x| x.rule_id == "new-permission").unwrap().decision,Decision::PermissionNotEstablished);
        assert!(evaluate_combined("study.example","fictional-electrical","2020","",&f(true,40,true)).is_none());
    }
}
"#;
    fs::write(&source,format!("{}\n{tests}",compile_combined(&batch().to_string()).unwrap())).unwrap();
    let out=Command::new("rustc").args(["--edition=2021","--test"]).arg(&source).arg("-o").arg(&binary).output().unwrap();
    assert!(out.status.success(),"{}",String::from_utf8_lossy(&out.stderr));
    let out=Command::new(&binary).output().unwrap();
    assert!(out.status.success(),"stdout: {} stderr: {}",String::from_utf8_lossy(&out.stdout),String::from_utf8_lossy(&out.stderr));
    fs::remove_dir_all(&dir).unwrap();
}
