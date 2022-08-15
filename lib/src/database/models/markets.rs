/// Market info received from source external source
#[derive(Debug)]
pub struct SourceMarket {
    pub figi: Option<String>,
    pub ticker: String,
}

/// Market info converted into local format
#[derive(Debug, Clone)]
pub struct Market {
    pub id: Option<i32>,
    pub ticker: String,
    pub label: String,
    pub figi: Option<String>,
    pub risk: i8,
    pub priority: i8,
    pub category: Option<MarketCategory>,
    pub created_at: Option<String>,
}
#[derive(Debug, PartialEq, Clone)]
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
impl std::fmt::Display for MarketCategory {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "{:?}", self)
    }
}
impl std::str::FromStr for MarketCategory {
    type Err = String;

    fn from_str(s: &str) -> Result<MarketCategory, String> {
        match s {
            "Etfs" => Ok(MarketCategory::Etfs),
            "Healthcare" => Ok(MarketCategory::Healthcare),
            "BasicMaterials" => Ok(MarketCategory::BasicMaterials),
            "IndustrialGoods" => Ok(MarketCategory::IndustrialGoods),
            "It" => Ok(MarketCategory::It),
            "ConsumerGoods" => Ok(MarketCategory::ConsumerGoods),
            "CopyTrade" => Ok(MarketCategory::CopyTrade),
            "Transport" => Ok(MarketCategory::Transport),
            "Financial" => Ok(MarketCategory::Financial),
            _ => Err(format!("Couldn't convert {} into MarketCategory", s)),
        }
    }
}
