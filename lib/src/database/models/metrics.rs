/// Market metric received from source external source
#[derive(Debug)]
pub struct SourceMetric {
    pub source: String,
    pub market: String,
    pub period: Period,
    pub price: f64,
    pub volume: u64,
    pub datetime: String,
}
#[derive(Debug, Clone, Copy)]
pub enum Period {
    Hour,
    Day,
    Week,
    Month,
    Current,
}

/// Market metric converted into local format
#[derive(Debug, Clone)]
pub struct Metric {
    pub id: Option<i32>,
    pub source: String,
    pub is_signal: bool,
    pub price: f64,
    pub volume: u64,
    pub market_id: Option<i32>, // TODO: make it Foreign Key in database
    pub datetime: String,
    pub created_at: Option<String>,
}
