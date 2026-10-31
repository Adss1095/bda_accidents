"""Pandas mirror of the Spark/Hive logic, used by the Streamlit dashboard."""
import pandas as pd

REQUIRED = ["accident_id", "accident_date", "accident_time", "district",
            "severity", "weather_condition", "road_surface", "vehicle_type"]


def clean(df: pd.DataFrame):
    """Same rules as spark/spark_analysis.py. Returns (clean_df, report dict)."""
    rep = {"raw_rows": len(df)}
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df = df[REQUIRED]
    before = len(df)
    df = df.drop_duplicates()
    rep["duplicates_removed"] = before - len(df)
    for c in ["district", "severity", "weather_condition", "road_surface", "vehicle_type"]:
        df[c] = df[c].astype("string").str.strip().str.title()
    before = len(df)
    df = df.dropna(subset=["district", "severity"])
    rep["null_rows_removed"] = before - len(df)
    dt = pd.to_datetime(df["accident_date"].astype(str) + " " + df["accident_time"].astype(str),
                        errors="coerce")
    before = len(df)
    df = df.assign(timestamp=dt).dropna(subset=["timestamp"])
    rep["invalid_datetime_removed"] = before - len(df)
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.day_name()
    rep["clean_rows"] = len(df)
    return df.reset_index(drop=True), rep


def count_by(df, col, order=None):
    s = df.groupby(col).size().rename("accident_count").reset_index()
    if order:
        s[col] = pd.Categorical(s[col], categories=order, ordered=True)
        return s.sort_values(col).reset_index(drop=True)
    return s.sort_values("accident_count", ascending=False).reset_index(drop=True)


def severity_share(df, by):
    t = pd.crosstab(df[by], df["severity"])
    return (t.div(t.sum(axis=1), axis=0) * 100).round(1)
