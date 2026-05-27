import pandas as pd

from hotix.engine.models import IndexRuntime


def _rolling_percentile(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).apply(
        lambda values: float((values <= values[-1]).mean()), raw=True
    )


def compute_index_features(
    index_id: str, date: str, df: pd.DataFrame, features_dsl: dict
) -> IndexRuntime:
    df_slice = df[df["date"] <= date].copy()
    last_row = df_slice.iloc[-1].to_dict()
    runtime = IndexRuntime(
        id=index_id,
        date=date,
        raw=last_row,
        features={},
        states={},
        trace={"features": {}},
    )
    series_map = {column: df_slice[column] for column in df_slice.columns}

    for rule in features_dsl["features"]:
        rule_id = rule["id"]
        output = rule["output"]
        value = None
        output_series = None

        if rule["type"] == "rolling" and rule["method"] == "mean":
            series = series_map[rule["input"][0]]
            if len(series) >= int(rule["window"]):
                output_series = series.rolling(int(rule["window"])).mean()
                value = float(output_series.iloc[-1])
        elif rule_id == "ret_1d":
            close = series_map["close"]
            if len(close) >= 2:
                value = float(close.iloc[-1] / close.iloc[-2] - 1)
                output_series = close / close.shift(1) - 1
        elif rule_id == "ret_5d":
            close = series_map["close"]
            if len(close) >= 6:
                output_series = close / close.shift(5) - 1
                value = float(output_series.iloc[-1])
        elif rule_id == "ret_20d":
            close = series_map["close"]
            if len(close) >= 21:
                output_series = close / close.shift(20) - 1
                value = float(output_series.iloc[-1])
        elif rule_id == "ma_slope_20":
            ma_20 = series_map["ma_20"]
            if len(ma_20.dropna()) >= 6:
                output_series = ma_20 / ma_20.shift(5) - 1
                value = float(output_series.iloc[-1])
        elif rule_id == "distance_to_ma20":
            close = series_map["close"]
            ma_20 = series_map["ma_20"]
            output_series = close / ma_20 - 1
            if pd.notna(output_series.iloc[-1]):
                value = float(output_series.iloc[-1])
        elif rule_id == "price_percentile_120d":
            close = series_map["close"]
            output_series = _rolling_percentile(close, 120)
            if pd.notna(output_series.iloc[-1]):
                value = float(output_series.iloc[-1])
        elif rule_id == "amount_ratio_1_20":
            amount = series_map["amount"]
            amount_ma_20 = series_map["amount_ma_20"]
            output_series = amount / amount_ma_20
            if pd.notna(output_series.iloc[-1]):
                value = float(output_series.iloc[-1])
        elif rule_id == "amount_ratio_5_20":
            amount = series_map["amount"]
            output_series = amount.rolling(5).mean() / amount.rolling(20).mean()
            if pd.notna(output_series.iloc[-1]):
                value = float(output_series.iloc[-1])
        elif rule_id == "amount_percentile_120d":
            amount = series_map["amount"]
            output_series = _rolling_percentile(amount, 120)
            if pd.notna(output_series.iloc[-1]):
                value = float(output_series.iloc[-1])
        elif rule_id == "breadth_ratio":
            adv = series_map["adv"]
            decl = series_map["decl"]
            output_series = adv / (adv + decl + 1e-9)
            value = float(output_series.iloc[-1])
        elif rule_id == "breadth_diff":
            adv = series_map["adv"]
            decl = series_map["decl"]
            output_series = adv - decl
            value = float(output_series.iloc[-1])
        elif rule_id == "true_range":
            high = series_map["high"]
            low = series_map["low"]
            close = series_map["close"]
            output_series = pd.concat(
                [
                    high - low,
                    (high - close.shift(1)).abs(),
                    (low - close.shift(1)).abs(),
                ],
                axis=1,
            ).max(axis=1)
            if pd.notna(output_series.iloc[-1]):
                value = float(output_series.iloc[-1])
        elif rule_id == "atr_pct_14":
            atr_14 = series_map["atr_14"]
            close = series_map["close"]
            output_series = atr_14 / close
            if pd.notna(output_series.iloc[-1]):
                value = float(output_series.iloc[-1])
        elif rule_id == "volatility_percentile_250d":
            atr_pct_14 = series_map["atr_pct_14"]
            output_series = _rolling_percentile(atr_pct_14, 250)
            if pd.notna(output_series.iloc[-1]):
                value = float(output_series.iloc[-1])
        elif rule_id == "breakout_20d":
            close = series_map["close"]
            high = series_map["high"]
            output_series = close > high.shift(1).rolling(20).max()
            if pd.notna(output_series.iloc[-1]):
                value = bool(output_series.iloc[-1])
        elif rule_id == "breakdown_20d":
            close = series_map["close"]
            low = series_map["low"]
            output_series = close < low.shift(1).rolling(20).min()
            if pd.notna(output_series.iloc[-1]):
                value = bool(output_series.iloc[-1])

        runtime.features[output] = value
        runtime.trace["features"][output] = {
            "rule_id": rule_id,
            "inputs": rule.get("input", []),
            "output": value,
        }
        if output_series is None:
            output_series = pd.Series([value] * len(df_slice), index=df_slice.index)
        series_map[output] = output_series

    return runtime
