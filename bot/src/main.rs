use bicklebow::sources::ggdrive::GoogleDriveMarketsSource;
use bicklebow::sources::tinkoff::{TinkoffMarketsSource, TinkoffMetricsSource};
use bicklebow_lib as bicklebow;

#[tokio::main]
async fn main() -> Result<(), ()> {
    bicklebow::Pipeline::new(
        vec![
            Box::new(TinkoffMarketsSource {}),
            Box::new(GoogleDriveMarketsSource {}),
        ],
        Box::new(TinkoffMetricsSource {}),
    )
    .run()
    .await;
    Ok(())
}
