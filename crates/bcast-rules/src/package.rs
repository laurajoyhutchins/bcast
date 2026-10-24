//! Canonical BCAST 0.2 source-package admission.
//! The package is a structural source witness, not publication rights or legal assurance.
use super::*;
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

fn object<'a>(value: &'a Value, context: &str) -> Result<&'a serde_json::Map<String, Value>, CompileError> {
    value.as_object().ok_or_else(|| fail(format!("{context}: expected object")))
}

fn required<'a>(value: &'a Value, key: &str) -> Result<&'a str, CompileError> {
    value.get(key).and_then(Value::as_str).ok_or_else(|| fail(format!("missing string {key}")))
}

fn keys(value: &Value, required_keys: &[&str], optional: &[&str], name: &str) -> Result<(), CompileError> {
    let found = object(value, name)?;
    if required_keys.iter().any(|key| !found.contains_key(*key)) {
        return Err(fail(format!("{name}: missing required fields")));
    }
    if found.keys().any(|key| !required_keys.contains(&key.as_str()) && !optional.contains(&key.as_str())) {
        return Err(fail(format!("{name}: unknown field")));
    }
    Ok(())
}

fn verify_publication(package: &Value, source: &BatchSource) -> Result<(), CompileError> {
    let pubn = package.get("publication").ok_or_else(|| fail("missing package publication"))?;
    keys(pubn, &["publication_id","namespace","family","edition"],
         &["revision","title","issuing_body"], "package publication")?;
    for (key, expected) in [
        ("publication_id", source.publication_id.as_str()),
        ("namespace", source.namespace.as_str()),
        ("family", source.family.as_str()),
        ("edition", source.edition.as_str()),
    ] {
        if required(pubn, key)? != expected { return Err(fail(format!("package publication {key} mismatch"))); }
    }
    if pubn.get("revision").and_then(Value::as_str).unwrap_or("") != source.revision.as_deref().unwrap_or("") {
        return Err(fail("package publication revision mismatch"));
    }
    for extra in ["revision", "title", "issuing_body"] {
        if let Some(value) = pubn.get(extra) { checked_text(value.as_str().ok_or_else(|| fail("invalid publication string"))?, extra)?; }
    }
    Ok(())
}

fn verify_object(value: &Value, pub_id: &str, artifact_sha: &str) -> Result<String, CompileError> {
    keys(value, &["object_id","kind","locator","status"],
         &["label","parent_id","content","provenance"], "source package object")?;
    let kind=required(value,"kind")?;
    if !matches!(kind,
      "document"|"chapter"|"appendix"|"section"|"subsection"|"paragraph"|"list_item"|
      "definition_entry"|"table"|"figure"|"note"|"unsupported") {
        return Err(fail("source package object.kind invalid"));
    }
    let locator=required(value,"locator")?;
    checked_text(locator,"package object.locator")?;
    let id=required(value,"object_id")?;
    checked_id(id,"bcastobj")?;
    let expected=format!("bcastobj:sha256:{}",hash_json(json!({
        "publication_id":pub_id,"kind":kind,"locator":locator
    }))?);
    if id != expected { return Err(fail("source package object coordinate/identity mismatch")); }
    if !matches!(required(value,"status")?, "resolved"|"unresolved"|"unsupported") {
        return Err(fail("invalid source package representation status"));
    }
    if let Some(label)=value.get("label") {
        checked_text(label.as_str().ok_or_else(||fail("invalid package label"))?,"label")?;
    }
    if let Some(parent)=value.get("parent_id") {
        checked_id(parent.as_str().ok_or_else(||fail("invalid parent ID"))?,"bcastobj")?;
    }
    if let Some(content)=value.get("content") {
        keys(content,&["media_type","text"],&[],"package content")?;
        if required(content,"media_type")? != "text/plain" {return Err(fail("unsupported package content media type"));}
        if content.get("text").and_then(Value::as_str).is_none() {return Err(fail("invalid package content text"));}
    }
    let provenance=value.get("provenance").ok_or_else(||fail("source object has no provenance"))?;
    keys(provenance,&["citation"],&["source_artifact_sha256"],"source object provenance")?;
    checked_text(required(provenance,"citation")?,"source object citation")?;
    if required(provenance,"source_artifact_sha256")? != artifact_sha {
        return Err(fail("source object provenance PDF digest mismatch"));
    }
    Ok(id.to_owned())
}

pub(super) fn verify_source_package(
    package: &Value, source: &BatchSource, passages: &[Passage],
) -> Result<(), CompileError> {
    keys(package,&["schema_version","package_id","package_version","publication","objects"],&[],"BCAST package")?;
    if required(package,"schema_version")? != "bcast.package/0.2.0" {
        return Err(fail("source package must use bcast.package/0.2.0"));
    }
    checked_text(required(package,"package_version")?,"package version")?;
    verify_publication(package,source)?;
    let objects=package.get("objects").and_then(Value::as_array)
        .ok_or_else(||fail("package objects must be a list"))?;
    limited_len(objects.len(),"source package objects",false)?;
    let mut indexed=BTreeMap::new();
    let mut sorted=Vec::new();
    for item in objects {
        let id=verify_object(item,&source.publication_id,&source.artifact_sha256)?;
        if indexed.insert(id.clone(),item).is_some() {return Err(fail("duplicate package object"));}
        sorted.push(item.clone());
    }
    sorted.sort_by(|a,b| a["object_id"].as_str().cmp(&b["object_id"].as_str()));
    // Follow the canonical BCAST package/0.2 rule: hash sorted materialization
    // without its derived package_id. JSON objects serialize with sorted keys.
    let mut body=package.clone();
    body.as_object_mut().ok_or_else(||fail("invalid package"))?.remove("package_id");
    body["objects"]=Value::Array(sorted);
    let expected=format!("bcastpkg:sha256:{}",hash_json(body)?);
    let actual=required(package,"package_id")?;
    if actual != expected || actual != source.package_id {
        return Err(fail("BCAST package materialization hash does not match source identity"));
    }
    // All extracted source objects must be in this exact package. A digest
    // anchored only in a sibling object or a different edition is insufficient.
    for passage in passages {
        let member=indexed.get(&passage.source_object_id)
            .ok_or_else(||fail("extracted passage not a member of the pinned source package"))?;
        if member["kind"] != passage.kind || member["locator"] != passage.locator {
            return Err(fail("passage member kind/locator mismatch"));
        }
    }
    let mut parent_links=BTreeMap::new();
    for (id,item) in &indexed {
        if let Some(parent)=item.get("parent_id") {
            let parent=parent.as_str().ok_or_else(||fail("invalid parent"))?;
            if !indexed.contains_key(parent) {return Err(fail("package parent missing"));}
            parent_links.insert(id.as_str(),parent);
        }
    }
    for id in indexed.keys() {
        let mut visited=BTreeSet::new();
        let mut current=id.as_str();
        while let Some(parent)=parent_links.get(current) {
            if !visited.insert(current) {return Err(fail("package parent cycle"));}
            current=parent;
        }
    }
    Ok(())
}
