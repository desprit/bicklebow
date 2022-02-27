#![allow(dead_code)]

#[macro_use]
extern crate lazy_static;

mod config;
mod database;
mod filters;
mod reactions;
mod rules;
mod sources;

use database::models::SourceData;
use sources::sources::{Source, TinkoffMarketNewsSource, TinkoffMarketValuesSource};

struct Pipeline {
    pub sources: Vec<Box<dyn Source>>,
}

/// `Pipeline` defines steps the data pass:
///  - pull data from the Source (e.g. broker API)
///  - save data to the local database
///  - apply logic to find if data should be treated as a signal
///  - apply filters to drop signals that we are not interested in
///  - emit reaction (e.g. send alert message or maybe trigger broker API)
impl Pipeline {
    fn new(sources: Vec<Box<dyn Source>>) -> Self {
        Pipeline { sources }
    }
    fn run(self) -> ! {
        loop {
            self.sources
                .iter()
                .flat_map(|x| x.read())
                .filter(|x| x.save().is_ok())
                .filter(|x| x.apply_is_signal_logic().is_ok())
                .filter(|x| match x {
                    SourceData::Metric { is_signal, .. } => *is_signal,
                    SourceData::News { is_signal, .. } => *is_signal,
                })
                .filter(|x| x.apply_filters().is_ok())
                .map(|x| x.react())
                .for_each(drop)
        }
    }
}

fn main() {
    Pipeline::new(vec![
        Box::new(TinkoffMarketNewsSource {}),
        Box::new(TinkoffMarketValuesSource {}),
    ])
    .run();
}
