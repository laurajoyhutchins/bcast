use std::env;
use std::fs;
use std::process::ExitCode;

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        eprintln!("usage: bcast-rust <reviewed-rules.json> <generated.rs>");
        return ExitCode::FAILURE;
    }
    match run(&args[1], &args[2]) {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("ERROR: {e}");
            ExitCode::FAILURE
        }
    }
}

fn run(input: &str, output: &str) -> Result<(), Box<dyn std::error::Error>> {
    if fs::metadata(input)?.len() > bcast_rules::MAX_BYTES as u64 {
        return Err("input exceeds 4 MB".into());
    }
    let document = fs::read_to_string(input)?;
    let contract: serde_json::Value = serde_json::from_str(&document)?;
    let generated = if contract["schema_version"] == bcast_rules::PROPOSAL_CONTRACT {
        bcast_rules::compile_combined(&document)?
    } else {
        bcast_rules::compile(&document)?
    };
    fs::write(output, generated)?;
    Ok(())
}
