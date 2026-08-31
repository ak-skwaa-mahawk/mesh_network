pub mod intent_engine;
pub mod intent_tracker;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_intent_engine_init() {
        let engine = intent_engine::IntentEngine::new();
        assert!(!engine.get_all_bands().is_empty());
    }
}
