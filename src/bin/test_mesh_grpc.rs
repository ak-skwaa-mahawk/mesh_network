use isst_toft_mesh::tordial_client::TordialMeshClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let endpoint = "http://127.0.0.1:50055".to_string();
    println!("[*] Connecting Rust tonic client to {}...", endpoint);

    let mut client = TordialMeshClient::connect(endpoint).await?;

    // Calibrated nominal 8D vector
    let telemetry = [4.0, 3.0, 0.01, 0.02, 3.5, 0.98, 0.2, 0.002];

    let t0 = std::time::Instant::now();
    let resp = client.route_burst("ISST-TOFT-RUST-01", 500, telemetry).await?;
    let elapsed = t0.elapsed();

    let decision = resp.decision.unwrap();
    println!("\n[+] Received RouteBurstResponse from Tordial-GS (Rust Client):");
    println!("    Node ID         : {}", resp.node_id);
    println!("    Budget Sats     : {}", resp.budget_sats);
    println!("    Dispatch Status : {}", decision.status);
    println!("    Root Index      : #{}", decision.selected_root_index);
    println!("    Dispatch Weight : {:.4}", decision.dispatch_weight);
    println!("    Mass Norm       : {:.4}", decision.mass_norm);
    println!("    Phase Drift     : {:.4}", decision.phase_drift);
    println!("    Round-trip Time : {:.2?}", elapsed);

    Ok(())
}
