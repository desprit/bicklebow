use crate::database::models::metrics::Metric;

impl Metric {
    pub fn apply_is_signal_logic(&self) -> Result<(), Box<dyn std::error::Error>> {
        Ok(())
    }
}
