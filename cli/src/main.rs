use bicklebow::database::models::markets;
use bicklebow::sources::sources::MetricsSource;
use bicklebow_lib as bicklebow;

#[tokio::main]
async fn main() -> Result<(), ()> {
    let fn_name = std::env::args().nth(1).expect("No function name provided");
    match fn_name.as_str() {
        "init-db" => {
            bicklebow::database::utils::setup_db().unwrap();
        }
        "drop-db" => {
            bicklebow::database::utils::teardown_db().unwrap();
        }
        "fill-db" => {
            bicklebow::sources::utils::init_markets().await.unwrap();
        }
        "fill-checklist" => {}
        "fill-metrics" => {
            let markets: Vec<markets::Market> =
                bicklebow::sources::tinkoff::get_portfolio_markets()
                    .await
                    .unwrap()
                    .into_iter()
                    .filter_map(|m| markets::Market::try_from(m).ok())
                    .collect();
            let source = Box::new(bicklebow::sources::tinkoff::TinkoffMetricsSource {});
            let metrics = source.read(markets).await.unwrap();
            for metric in metrics {
                metric.save().ok();
            }
        }
        _ => (),
    }
    Ok(())
}
