
# Error Metrics

Error metrics summarize how well the model fits the historical data.  Lumen provides four standard metrics:

- Mean Absolute Error (MAE),
- Root Mean Squared Error (RMSE),
- Mean Absolute Percentage Error (RASE), and 
- Symmetric Meam Absolute Squared Error (SMAPE).

These metrics provide complementary perspectives on model accuracy and help compare performance across datasets.

## Mean Absolute Error (MAE)

MAE measures the average magnitude of errors:

$$
MAE = \frac{1}{n} \sum^n_{t = 1} |y_t - \hat{y}_t |
$$

MAE is easy to understand, robust to outliers, and good for comparing models on the same dataset.

## Root Mean Sqaured Error (RMSE)

RMSE penalizes large errors more than MAE:

$$
RMSE = \sqrt{ \frac{1}{n} \sum^n_{t = 1} (y_t - \hat{y}_t)}
$$

RMSE is sensitive to large deviations, useful when big misses matter, and RMSE > MAE indicates the presence of large errors.

## Mean Absolute Percentage Error (MAPE)

MAPE measures error as a percentage of the actual value:

$$
MAPE = \frac{100}{n} \sum^n_{t = 1} | \frac{y_t - \hat{y}_t}{y_t} |
$$

MAPE is scale-free, easy to communicate, but can be unstable when actual values are near zero.

## Symmetric Mean Absolute Percentage Error (SMAPE)

SMAPE avoids some of MAPE's pitfalls:

$$
SMAPE = \frac{100}{n} \sum^n_{t = 1} \frac{|y_t - \hat{y}_t|}{(|y_t| + |\hat{y}_t|) / 2}
$$

SMAPE is symmetric between actual and forecast and more stable when values approach zero.  It is useful for comparing across datasets.
