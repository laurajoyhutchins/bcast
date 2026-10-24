//! Proposal admission and source-pinned composition, not legal interpretation.
//! SBVR-inspired modalities are explicitly NOT an OMG SBVR-XMI interchange claim.
use super::*;
use serde::Deserialize;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};

pub const PROPOSAL_CONTRACT: &str = "bcast.sbvr_proposal_batch/0.1.0";

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ProposalBatch {
    schema_version: String,
    baseline: Value,
    source: BatchSource,
    passages: Vec<Passage>,
    proposals: Vec<Proposal>,
    accounting: Accounting,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct BatchSource {
    namespace: String,
    family: String,
    edition: String,
    revision: Option<String>,
    publication_id: String,
    package_id: String,
    artifact_sha256: String,
    media_type: String,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Passage {
    passage_id: String,
    kind: String,
    locator: String,
    source_object_id: String,
    pdf_page: u32,
    bbox_millipoints: [u32; 4],
    text: String,
    text_sha256: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "snake_case")]
enum Modality { Obligation, Prohibition, Permission }

#[derive(Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum Disposition { Admitted, Unresolved, Rejected }

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Dependency {
    locator: String,
    resolved: bool,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Proposal {
    proposal_id: String,
    passage_id: String,
    modality: Modality,
    disposition: Disposition,
    condition: Option<Expr>,
    exception: Option<Expr>,
    predicate: Option<Expr>,
    dependencies: Vec<Dependency>,
    review: Option<Review>,
    reason: Option<String>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Accounting {
    extracted_passages: usize,
    classified_passages: usize,
    proposals: usize,
    admitted: usize,
    unresolved: usize,
    rejected: usize,
}

fn digest(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn hash_json(value: Value) -> Result<String, CompileError> {
    let bytes = serde_json::to_vec(&value).map_err(|e| fail(e.to_string()))?;
    Ok(digest(&bytes))
}

fn canonical_publication(source: &BatchSource) -> Result<String, CompileError> {
    let mut v = json!({"namespace":source.namespace,"family":source.family,"edition":source.edition});
    if let Some(revision) = &source.revision {
        v["revision"] = json!(revision);
    }
    Ok(format!("bcastpub:sha256:{}", hash_json(v)?))
}

fn canonical_object(source: &BatchSource, p: &Passage) -> Result<String, CompileError> {
    Ok(format!("bcastobj:sha256:{}", hash_json(json!({
        "publication_id":source.publication_id,"kind":p.kind,"locator":p.locator
    }))?))
}

fn canonical_passage_id(source: &BatchSource, p: &Passage) -> Result<String, CompileError> {
    Ok(format!("bcastpassage:sha256:{}", hash_json(json!({
        "artifact_sha256":source.artifact_sha256,
        "source_object_id":p.source_object_id,
        "pdf_page":p.pdf_page,
        "bbox_millipoints":p.bbox_millipoints,
        "text_sha256":p.text_sha256
    }))?))
}

fn checked_batch_source(source: &BatchSource) -> Result<(), CompileError> {
    checked_namespace(&source.namespace)?;
    checked_family(&source.family)?;
    checked_text(&source.edition, "source.edition")?;
    if let Some(s) = &source.revision { checked_text(s, "source.revision")?; }
    if source.media_type != "application/pdf" { return Err(fail("source.media_type must be application/pdf")); }
    if !is_digest(&source.artifact_sha256) { return Err(fail("invalid source artifact SHA-256")); }
    checked_id(&source.publication_id, "bcastpub")?;
    checked_id(&source.package_id, "bcastpkg")?;
    if canonical_publication(source)? != source.publication_id {
        return Err(fail("source publication ID does not match canonical BCAST publication identity"));
    }
    Ok(())
}

fn check_passage(source: &BatchSource, p: &Passage) -> Result<(), CompileError> {
    if p.kind != "section" && p.kind != "subsection" && p.kind != "paragraph" {
        return Err(fail("source passage kind unsupported"));
    }
    checked_text(&p.locator, "passage.locator")?;
    checked_id(&p.source_object_id, "bcastobj")?;
    if canonical_object(source, p)? != p.source_object_id {
        return Err(fail("source object ID does not match BCAST coordinates"));
    }
    if p.pdf_page == 0 ||
       p.bbox_millipoints[0] >= p.bbox_millipoints[2] ||
       p.bbox_millipoints[1] >= p.bbox_millipoints[3] {
        return Err(fail("invalid page or bounded rectangle"));
    }
    if p.text.is_empty() || p.text.len() > 8192 {
        return Err(fail("passage text must be bounded to 8192 UTF-8 bytes"));
    }
    if digest(p.text.as_bytes()) != p.text_sha256 {
        return Err(fail("passage text SHA-256 mismatch"));
    }
    if canonical_passage_id(source, p)? != p.passage_id {
        return Err(fail("passage identity mismatch"));
    }
    Ok(())
}

fn count_proposals(doc: &ProposalBatch) -> Result<BTreeMap<String, Vec<&Proposal>>, CompileError> {
    let mut result: BTreeMap<String, Vec<&Proposal>> = BTreeMap::new();
    let mut ids = BTreeSet::new();
    for proposal in &doc.proposals {
        checked_text(&proposal.proposal_id, "proposal_id")?;
        if !ids.insert(&proposal.proposal_id) {
            return Err(fail("duplicate proposal ID"));
        }
        if !doc.passages.iter().any(|p| p.passage_id == proposal.passage_id) {
            return Err(fail("orphan proposal without extracted passage"));
        }
        let mut dependency_ids = BTreeSet::new();
        for dep in &proposal.dependencies {
            checked_text(&dep.locator, "dependency.locator")?;
            if !dependency_ids.insert(dep.locator.as_str()) {
                return Err(fail("duplicate unresolved/resolved dependency locator"));
            }
        }
        // Validate ALL supplied semantic expressions, even those not admitted.
        // An unresolved candidate must not become a hiding place for malformed
        // operands and operator/unit mismatches.
        if let Some(condition) = &proposal.condition { emit_expr(condition, 0)?; }
        if let Some(exception) = &proposal.exception { emit_expr(exception, 0)?; }
        if let Some(predicate) = &proposal.predicate { emit_expr(predicate, 0)?; }
        if proposal.disposition == Disposition::Admitted {
            if proposal.predicate.is_none() || proposal.reason.is_some() ||
                proposal.dependencies.iter().any(|d| !d.resolved) {
                return Err(fail("admitted proposal requires predicate and resolved dependencies"));
            }
            let review = proposal.review.as_ref().ok_or_else(|| fail("admitted proposal missing review"))?;
            checked_text(&review.reviewer, "review.reviewer")?;
            checked_text(&review.review_ref, "review.review_ref")?;
        } else {
            if proposal.predicate.is_some() || proposal.review.is_some() {
                return Err(fail("unadmitted proposal cannot carry an executable predicate/review"));
            }
            checked_text(proposal.reason.as_deref().ok_or_else(|| fail("unadmitted proposal missing reason"))?, "reason")?;
        }
        result.entry(proposal.passage_id.clone()).or_default().push(proposal);
    }
    Ok(result)
}

fn proposal_expr(p: &Proposal, source: &Passage) -> Result<String, CompileError> {
    let condition = p.condition.as_ref().map_or(Ok("Truth::Yes".to_owned()), |v| emit_expr(v, 0))?;
    let exception = p.exception.as_ref().map_or(Ok("Truth::No".to_owned()), |v| emit_expr(v, 0))?;
    let predicate = emit_expr(p.predicate.as_ref().ok_or_else(|| fail("missing predicate"))?, 0)?;
    let decision = match p.modality {
        Modality::Obligation => "decide",
        Modality::Prohibition => "decide_prohibition",
        Modality::Permission => "decide_permission",
    };
    let review = p.review.as_ref().ok_or_else(|| fail("missing review"))?;
    Ok(format!(
        "            Finding {{ rule_id: {}, source_object_id: {}, source_locator: {}, source_text_sha256: {}, review_ref: {}, reason: \"\", decision: {decision}({condition}, {exception}, {predicate}) }}",
        literal(&p.proposal_id), literal(&source.source_object_id), literal(&source.locator),
        literal(&source.text_sha256), literal(&review.review_ref)
    ))
}

/// Validate a fully accounted extraction batch and append admitted predicates
/// to the existing generated Rust. No source text enters the generated code.
/// Both successful admission and evaluation remain distinct from code compliance.
pub fn compile_combined(input: &str) -> Result<String, CompileError> {
    if input.len() > MAX_BYTES { return Err(fail("input exceeds 4 MB")); }
    let doc: ProposalBatch = serde_json::from_str(input)
        .map_err(|e| fail(format!("invalid proposal batch: {e}")))?;
    if doc.schema_version != PROPOSAL_CONTRACT { return Err(fail("unsupported proposal schema_version")); }
    checked_batch_source(&doc.source)?;
    limited_len(doc.passages.len(), "passages", false)?;
    limited_len(doc.proposals.len(), "proposals", false)?;

    let mut passage_map = BTreeMap::new();
    let mut coordinates = BTreeSet::new();
    for passage in &doc.passages {
        check_passage(&doc.source, passage)?;
        if passage_map.insert(passage.passage_id.clone(), passage).is_some() {
            return Err(fail("duplicate source passage identity"));
        }
        if !coordinates.insert((passage.source_object_id.clone(), passage.pdf_page, passage.bbox_millipoints)) {
            return Err(fail("duplicate source page/object/rectangle"));
        }
    }

    let classes = count_proposals(&doc)?;
    if classes.len() != passage_map.len() ||
       passage_map.keys().any(|k| !classes.contains_key(k)) {
        return Err(fail("unclassified source passages in extraction batch"));
    }
    let actual_admitted = doc.proposals.iter().filter(|p| p.disposition == Disposition::Admitted).count();
    let actual_unresolved = doc.proposals.iter().filter(|p| p.disposition == Disposition::Unresolved).count();
    let actual_rejected = doc.proposals.iter().filter(|p| p.disposition == Disposition::Rejected).count();
    let counts = &doc.accounting;
    if counts.extracted_passages != doc.passages.len() ||
       counts.classified_passages != classes.len() ||
       counts.proposals != doc.proposals.len() ||
       counts.admitted != actual_admitted ||
       counts.unresolved != actual_unresolved ||
       counts.rejected != actual_rejected ||
       counts.admitted + counts.unresolved + counts.rejected != counts.proposals {
        return Err(fail("batch accounting does not balance"));
    }

    let baseline_text = serde_json::to_string(&doc.baseline).map_err(|e| fail(e.to_string()))?;
    let generated = compile(&baseline_text)?;
    let baselines = doc.baseline["editions"].as_array().ok_or_else(|| fail("baseline editions missing"))?;
    let same_edition = baselines.iter().any(|edition| {
        edition["publication"]["namespace"] == doc.source.namespace &&
        edition["publication"]["family"] == doc.source.family &&
        edition["publication"]["edition"] == doc.source.edition &&
        edition["publication"]["revision"].as_str().unwrap_or("") == doc.source.revision.as_deref().unwrap_or("") &&
        edition["publication"]["publication_id"] == doc.source.publication_id &&
        edition["package_id"] == doc.source.package_id
    });
    if !same_edition {
        return Err(fail("proposal source edition and package absent from validated baseline"));
    }

    let mut expressions = Vec::new();
    let mut known_baseline_ids = BTreeSet::new();
    for edition in baselines {
        if edition["publication"]["publication_id"] == doc.source.publication_id {
            if let Some(rules) = edition["rules"].as_array() {
                for rule in rules {
                    if let Some(id) = rule["id"].as_str() { known_baseline_ids.insert(id); }
                    if let (Some(object), Some(digest)) = (
                        rule["source"]["object_id"].as_str(),
                        rule["source"]["text_sha256"].as_str(),
                    ) {
                        for passage in doc.passages.iter().filter(|p| p.source_object_id == object) {
                            if passage.text_sha256 != digest {
                                return Err(fail("baseline and extracted passage text SHA-256 disagree"));
                            }
                        }
                    }
                }
            }
        }
    }
    let mut sorted = doc.proposals.iter().filter(|p| p.disposition == Disposition::Admitted).collect::<Vec<_>>();
    sorted.sort_by(|a,b| a.proposal_id.cmp(&b.proposal_id));
    for proposal in sorted {
        if known_baseline_ids.contains(proposal.proposal_id.as_str()) {
            return Err(fail("admitted proposal duplicates baseline rule ID"));
        }
        let passage = passage_map.get(&proposal.passage_id).ok_or_else(|| fail("missing passage"))?;
        expressions.push(proposal_expr(proposal, passage)?);
    }

    let source = &doc.source;
    let revision = source.revision.as_deref().unwrap_or("");
    let arm = format!(
        "        ({}, {}, {}, {}) => Some(vec![\n{}\n        ]),",
        literal(&source.namespace), literal(&source.family), literal(&source.edition),
        literal(revision), expressions.join(",\n")
    );

    Ok(format!(
        "{generated}\n\
         // Source-pinned OMG SBVR-inspired proposals: admitted predicates only.\n\
         pub const SBVR_PROPOSAL_CONTRACT: &str = \"bcast.sbvr_proposal_batch/0.1.0\";\n\
         pub const SBVR_ARTIFACT_SHA256: &str = {};\n\
         pub const SBVR_PASSAGE_COUNT: usize = {};\n\
         pub const SBVR_PROPOSAL_COUNT: usize = {};\n\
         pub const SBVR_ADMITTED_COUNT: usize = {};\n\
         pub const SBVR_UNRESOLVED_COUNT: usize = {};\n\
         pub const SBVR_REJECTED_COUNT: usize = {};\n\
         pub fn evaluate_sbvr(namespace: &str, family: &str, edition: &str, revision: &str, facts: &[Fact<'_>]) -> Option<Vec<Finding>> {{\n\
             match (namespace, family, edition, revision) {{\n{arm}\n        _ => None,\n    }}\n}}\n\
         pub fn evaluate_combined(namespace: &str, family: &str, edition: &str, revision: &str, facts: &[Fact<'_>]) -> Option<Vec<Finding>> {{\n\
             let baseline = evaluate(namespace, family, edition, revision, facts);\n\
             let proposals = evaluate_sbvr(namespace, family, edition, revision, facts);\n\
             match (baseline, proposals) {{\n\
                 (None, None) => None,\n\
                 (Some(mut a), Some(b)) => {{ a.extend(b); Some(a) }},\n\
                 (Some(a), None) => Some(a),\n\
                 (None, Some(b)) => Some(b),\n\
             }}\n\
         }}\n",
        literal(&source.artifact_sha256),
        doc.passages.len(), doc.proposals.len(), actual_admitted, actual_unresolved, actual_rejected
    ))
}
