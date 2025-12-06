# src/train_baseline.py
from app import get_data
from features.engineering import add_basic_features
from models.baseline import train_baseline
import pandas as pd

def main(symbol="AAPL", minutes=600):
    df = get_data(symbol, minutes)
    feats = add_basic_features(df)
    model, metrics, holdout = train_baseline(feats)
    idx, y_true, y_pred = holdout

    print(f"Trained on {symbol} with {len(feats)} rows")
    print("Metrics:", metrics)
    # Show last few predictions side-by-side
    out = pd.DataFrame({"y_true": y_true, "y_pred": y_pred}, index=idx).tail(10)
    print("\nLast predictions:")
    print(out)

if __name__ == "__main__":
    main()

