use crate::database::models::SourceData;

impl SourceData {
    pub fn apply_filters(&self) -> Result<(), Box<dyn std::error::Error>> {
        Ok(())
    }
}
