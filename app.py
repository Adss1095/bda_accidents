import pandas as pd
import streamlit as st
from analysis import clean, count_by, severity_share

st.set_page_config(page_title="Road Accident Analytics (Hadoop/Hive/Spark)", page_icon="🚦", layout="wide")
st.title("🚦 Big Data Analytics for Road Accident Analysis")
st.caption("HDFS · Hive · Apache Spark  |  Aditi V Bidkar (1MV23AI002) · BCS714D · SMVIT")

# ---------- data source ----------
with st.sidebar:
    st.header("Data source")
    up = st.file_uploader("Upload accident CSV", type="csv",
                          help="Columns: accident_id, accident_date, accident_time, district, "
                               "severity, weather_condition, road_surface, vehicle_type")
    using_sample = up is None


@st.cache_data(show_spinner="Cleaning data...")
def load(file):
    raw = pd.read_csv(file if file is not None else "data/accidents_sample.csv")
    return clean(raw)


try:
    df, rep = load(up)
except Exception as e:
    st.error(f"Could not process file: {e}")
    st.stop()

if using_sample:
    st.warning("Showing a **synthetic demo dataset** (not real accident statistics). "
               "Upload a real CSV in the sidebar to analyse actual data.")

# ---------- filters ----------
with st.sidebar:
    st.header("Filters")
    years = sorted(df["year"].unique())
    yr = st.multiselect("Year", years, default=years)
    sev = st.multiselect("Severity", sorted(df["severity"].unique()), default=sorted(df["severity"].unique()))
    dist = st.multiselect("District", sorted(df["district"].unique()), default=sorted(df["district"].unique()))

f = df[df["year"].isin(yr) & df["severity"].isin(sev) & df["district"].isin(dist)]
if f.empty:
    st.info("No records match the current filters.")
    st.stop()

# ---------- KPIs ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Accidents", f"{len(f):,}")
c2.metric("Districts", f["district"].nunique())
c3.metric("Fatal share", f"{(f['severity'].eq('Fatal').mean()*100):.1f}%")
c4.metric("Peak hour", f"{f['hour'].mode().iat[0]:02d}:00")

tabs = st.tabs(["📍 Location", "🕒 Time", "⚠️ Severity", "🌧️ Weather & Road", "🚗 Vehicles",
                "🧹 Data quality", "🏗️ Architecture & code"])

with tabs[0]:
    d = count_by(f, "district")
    a, b = st.columns([2, 1])
    a.subheader("Accidents by district")
    a.bar_chart(d.set_index("district")["accident_count"])
    b.dataframe(d, hide_index=True, use_container_width=True)
    st.caption("High counts may reflect population, traffic volume or reporting coverage, not just risk.")

with tabs[1]:
    a, b = st.columns(2)
    a.subheader("By hour of day")
    a.bar_chart(count_by(f, "hour", order=list(range(24))).set_index("hour")["accident_count"])
    b.subheader("By month")
    b.bar_chart(count_by(f, "month", order=list(range(1, 13))).set_index("month")["accident_count"])
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    st.subheader("By weekday")
    st.bar_chart(count_by(f, "weekday", order=days).set_index("weekday")["accident_count"])
    st.subheader("Yearly trend")
    st.line_chart(count_by(f, "year", order=sorted(f["year"].unique())).set_index("year")["accident_count"])

with tabs[2]:
    a, b = st.columns(2)
    s = count_by(f, "severity")
    a.subheader("Severity distribution")
    a.bar_chart(s.set_index("severity")["accident_count"])
    b.dataframe(s, hide_index=True, use_container_width=True)
    by = st.selectbox("Severity mix (% within group) by", ["district", "weather_condition", "road_surface", "vehicle_type"])
    mix = severity_share(f, by)
    st.bar_chart(mix)
    st.dataframe(mix, use_container_width=True)

with tabs[3]:
    a, b = st.columns(2)
    a.subheader("By weather")
    a.bar_chart(count_by(f, "weather_condition").set_index("weather_condition")["accident_count"])
    b.subheader("By road surface")
    b.bar_chart(count_by(f, "road_surface").set_index("road_surface")["accident_count"])
    st.subheader("Weather × road surface")
    st.dataframe(pd.crosstab(f["weather_condition"], f["road_surface"]), use_container_width=True)

with tabs[4]:
    v = count_by(f, "vehicle_type")
    st.bar_chart(v.set_index("vehicle_type")["accident_count"])
    st.dataframe(v, hide_index=True, use_container_width=True)

with tabs[5]:
    st.subheader("Cleaning report")
    st.json(rep)
    st.markdown("Rules: drop duplicates → standardise text → drop null district/severity → drop unparsable date/time → derive year, month, hour, weekday.")
    st.download_button("Download cleaned CSV", df.to_csv(index=False), "accidents_clean.csv", "text/csv")

with tabs[6]:
    st.markdown("""
**Pipeline:** Dataset → Cleaning → HDFS → Hive table → HiveQL → Spark DataFrames → Aggregates → Dashboard

| Component | Role |
|---|---|
| HDFS | Stores raw and cleaned accident files |
| Hive | External table + HiveQL aggregations (`hive/queries.hql`) |
| Spark | Cleaning and aggregation at scale (`spark/spark_analysis.py`) |
| Streamlit | Presents the Spark/Hive summary results (this app) |
""")
    st.code(open("hive/queries.hql").read(), language="sql")
    st.code(open("spark/spark_analysis.py").read(), language="python")
    st.caption("This dashboard runs the same logic with pandas so it can be hosted without a Hadoop cluster.")
