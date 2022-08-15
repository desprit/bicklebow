#![allow(dead_code)]

#[macro_use]
extern crate lazy_static;

mod config;
pub mod database;
mod filters;
mod reactions;
mod rules;
pub mod sources;

use database::models::markets;
use database::models::metrics;
use sources::sources::{MarketsSource, MetricsSource};

pub struct Pipeline {
    pub market_sources: Vec<Box<dyn MarketsSource>>,
    pub metric_source: Box<dyn MetricsSource>,
}

/// `Pipeline` defines steps the data pass:
///  - pull data from the Source (e.g. broker API)
///  - save data to the local database
///  - apply logic to find if data should be treated as a signal
///  - apply filters to drop signals that we are not interested in
///  - emit reaction (e.g. send alert message or maybe trigger broker API)
impl Pipeline {
    pub fn new(
        market_sources: Vec<Box<dyn MarketsSource>>,
        metric_source: Box<dyn MetricsSource>,
    ) -> Self {
        Pipeline {
            market_sources,
            metric_source,
        }
    }
    pub async fn run(&self) -> () {
        let mut markets: Vec<markets::Market> = vec![];
        for market_source in &self.market_sources {
            markets.append(
                &mut market_source
                    .read()
                    .await
                    .map_err(|_| -> Vec<markets::Market> { vec![] })
                    .unwrap(),
            );
        }
        dbg!(
            "Markets to work with: {}",
            markets.iter().map(|x| &x.ticker).collect::<Vec<&String>>()
        );
        self.metric_source
            .read(markets[..3].to_vec())
            .await
            .map_err(|_| -> Vec<metrics::Metric> { vec![] })
            .unwrap()
            .into_iter()
            .filter(|x| x.save().is_ok())
            .filter(|x| x.apply_is_signal_logic().is_ok())
            .filter(|x| x.is_signal)
            .filter(|x| x.apply_filters().is_ok())
            .map(|x| x.react())
            .for_each(drop)
    }
}
