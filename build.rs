cat > build.rs << 'ENDBUILD'
// build.rs — ISST-TOFT Sovereign Inference Backend
use std::path::PathBuf;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("cargo:rerun-if-changed=proto/isst_toft.proto");

    let proto_dir = PathBuf::from("proto");

    tonic_build::configure()
        .build_server(true)
        .build_client(true)
        .compile(&[proto_dir.join("isst_toft.proto")], &[proto_dir])?;

    println!("cargo:warning=ISST-TOFT gRPC codegen complete");
    Ok(())
}
ENDBUILD