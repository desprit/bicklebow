#[derive(Debug)]
pub enum MarketLabel {
    Speculation,
    LongTerm,
    MidTerm,
    ShortTerm,
    TechAnalysis,
    News,
    Meme,
}

#[derive(Debug)]
pub enum MarketCategory {
    Etfs,
    Healthcare,
    BasicMaterials,
    IndustrialGoods,
    It,
    ConsumerGoods,
    CopyTrade,
    Transport,
    Financial,
}

#[derive(Debug)]
pub struct Market {
    pub id: i32,
    pub name: String,
    pub label: String,
    pub risk: i8,
    pub priority: i8,
    pub labels: Vec<MarketLabel>,
    pub category: MarketCategory,
    pub amount: i32,
    pub created_at: String,
}

#[derive(Debug)]
pub enum SourceData {
    News {
        source: String,
        created_at: String,
        is_signal: bool,
        value: String,
        market_id: i32, // TODO: make it Foreign Key in database
    },
    Metric {
        source: String,
        created_at: String,
        is_signal: bool,
        value: i32,
        market_id: i32, // TODO: make it Foreign Key in database
    },
}

#[derive(Debug)]
pub enum Period {
    Hour,
    Day,
    Week,
    Month,
    Current,
}

#[derive(Debug)]
pub struct MarketValue {
    pub market: String,
    pub period: Period,
    pub price: i32,
    pub qty: i32,
}

#[derive(Debug)]
pub struct MarketNews {
    pub market: String,
    pub text: String,
}
