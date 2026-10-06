use isst_toft_mesh::tordial_client::{RouteBurstRequest, TelemetryVector, TordialMeshClient};
use std::time::{Instant, SystemTime, UNIX_EPOCH};
use tokio::sync::mpsc;
use tokio_stream::wrappers::ReceiverStream;
use tokio_stream::StreamExt;

fn percentile(sorted: &[f64], pct: f64) -> f64 {
    if sorted.is_empty() {
        return 0.0;
    }
    let idx = ((pct / 100.0) * (sorted.len() - 1) as f64).round() as usize;
    sorted[idx]
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let endpoint = "http://127.0.0.1:50055".to_string();
    const ITERATIONS: usize = 1000;

    println!("==========================================================");
    println!("⚡ RUST TONIC STREAMING BENCHMARK: StreamRouteBursts");
    println!("   Target Endpoint : {}", endpoint);
    println!("   Sample Size     : {} frames", ITERATIONS);
    println!("==========================================================");

    let mut client = TordialMeshClient::connect(endpoint).await?;

    // Warmup unary call
    let warmup_tel = [4.0, 3.0, 0.01, 0.02, 3.5, 0.98, 0.2, 0.002];
    for _ in 0..5 {
        let _ = client.route_burst("WARMUP", 500, warmup_tel).await?;
    }

    let (tx, rx) = mpsc::channel::<RouteBurstRequest>(512);
    let request_stream = ReceiverStream::new(rx);

    let mut response_stream = client.stream_route_bursts(request_stream).await?;

    let t0 = Instant::now();
    let mut latencies_us = Vec::with_capacity(ITERATIONS);

    let producer_handle = tokio::spawn(async move {
        for i in 0..ITERATIONS {
            let now = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_millis();

            let req = RouteBurstRequest {
                origin_node_id: format!("RUST-EDGE-{:04}", i),
                budget_sats: 500,
                payload_digest: format!("bench_digest_{}", i),
                timestamp_epoch_ms: now as i64,
                telemetry: Some(TelemetryVector {
                    latency_ms: 4.0 + ((i % 50) as f64) * 0.01,
                    queue_depth: 3.0,
                    thermal_headroom: 0.01,
                    battery_reserve: 0.02,
                    packet_loss_rate: 3.5,
                    bandwidth_capacity: 0.98,
                    memory_pressure: 0.2,
                    compute_load: 0.002,
                }),
            };
            if tx.send(req).await.is_err() {
                break;
            }
        }
        drop(tx);
    });

    let mut frame_start = Instant::now();
    let mut received = 0;

    while let Some(res) = response_stream.next().await {
        let _resp = res?;
        let elapsed = frame_start.elapsed().as_secs_f64() * 1_000_000.0;
        latencies_us.push(elapsed);
        received += 1;
        frame_start = Instant::now();

        if received % 200 == 0 {
            println!("   -> Processed {} / {} frames...", received, ITERATIONS);
        }

        if received == ITERATIONS {
            break;
        }
    }

    let total_elapsed = t0.elapsed();
    let _ = producer_handle.await;

    latencies_us.sort_by(|a, b| a.partial_cmp(b).unwrap());

    let throughput = (received as f64) / total_elapsed.as_secs_f64();
    let p50 = percentile(&latencies_us, 50.0);
    let p95 = percentile(&latencies_us, 95.0);
    let p99 = percentile(&latencies_us, 99.0);

    println!("\n| Client / Transport           | Throughput (ops/s) | p50 (µs) | p95 (µs) | p99 (µs) | Total Elapsed (ms) |");
    println!("|------------------------------|--------------------|----------|----------|----------|--------------------|");
    println!(
        "| Rust Tonic Duplex Stream     | {:>18.1} | {:>8.2} | {:>8.2} | {:>8.2} | {:>18.2} |",
        throughput,
        p50,
        p95,
        p99,
        total_elapsed.as_secs_f64() * 1000.0
    );
    println!("==========================================================\n");

    Ok(())
}
