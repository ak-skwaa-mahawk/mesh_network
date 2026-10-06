pub mod tordial {
    tonic::include_proto!("tordial.v1");
}

use tordial::sovereign_mesh_service_client::SovereignMeshServiceClient;
use tordial::{RouteBurstRequest, RouteBurstResponse, TelemetryVector};
use tonic::transport::Channel;

#[derive(Clone)]
pub struct TordialMeshClient {
    client: SovereignMeshServiceClient<Channel>,
}

impl TordialMeshClient {
    pub async fn connect(endpoint: String) -> Result<Self, tonic::transport::Error> {
        let client = SovereignMeshServiceClient::connect(endpoint).await?;
        Ok(Self { client })
    }

    pub async fn route_burst(
        &mut self,
        origin_node_id: &str,
        budget_sats: u64,
        telemetry: [f64; 8],
    ) -> Result<RouteBurstResponse, tonic::Status> {
        let request = tonic::Request::new(RouteBurstRequest {
            origin_node_id: origin_node_id.to_string(),
            budget_sats,
            payload_digest: format!("rust_digest_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis()),
            timestamp_epoch_ms: std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis() as i64,
            telemetry: Some(TelemetryVector {
                latency_ms: telemetry[0],
                queue_depth: telemetry[1],
                thermal_headroom: telemetry[2],
                battery_reserve: telemetry[3],
                packet_loss_rate: telemetry[4],
                bandwidth_capacity: telemetry[5],
                memory_pressure: telemetry[6],
                compute_load: telemetry[7],
            }),
        });

        let response = self.client.route_burst(request).await?;
        Ok(response.into_inner())
    }
}
