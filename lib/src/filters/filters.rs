use crate::database::models::metrics::Metric;

impl Metric {
    pub fn apply_filters(&self) -> Result<(), Box<dyn std::error::Error>> {
        Ok(())
    }
}
