use crate::database::models::metrics::Metric;

impl Metric {
    pub fn react(&self) -> Result<(), Box<dyn std::error::Error>> {
        Ok(())
    }
}
