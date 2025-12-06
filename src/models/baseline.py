# src/models/baseline.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

FEATURES_DEFAULT = [
    "return_1", "ma_5", "ma_10", "ma_20", "rsi_5", "rsi_10", "rsi_20", "volatility_10"
]

def train_baseline(df: pd.DataFrame, features=FEATURES_DEFAULT):
    df = df.dropna()
    X = df[features]
    y = df["target_next_close"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, shuffle=False  # time-order split
    )
    model = LinearRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    return model, {"MAE": mae, "RMSE": rmse}, (X_test.index, y_test, preds)
