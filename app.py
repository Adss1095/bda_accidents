"""ROADSAFE ANALYTICS - US Road Accident Intelligence Dashboard (Streamlit)."""
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="RoadSafe Analytics", page_icon="🚦", layout="wide")

RED, BG, CARD, BORDER, MUTED = "#ef4444", "#0b0f19", "#111827", "#1f2937", "#94a3b8"
SEV_COLORS = {1: "#22c55e", 2: "#eab308", 3: "#f97316", 4: "#ef4444"}

st.markdown(f"""
<style>
.stApp {{ background:{BG}; color:#e5e7eb; }}
header[data-testid="stHeader"] {{ background:transparent; }}
section[data-testid="stSidebar"] {{ background:#0f172a; border-right:1px solid {BORDER}; }}
.block-container {{ padding-top:1.5rem; max-width:1400px; }}
.brand {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:.4rem; }}
.brand h1 {{ font-size:1.9rem; letter-spacing:.18em; margin:0; color:#fff; font-weight:800; }}
.brand h1 span {{ color:{RED}; }}
.sub {{ color:{MUTED}; font-size:1rem; margin-bottom:1.2rem; }}
.live {{ border:1px solid {RED}55; background:{RED}1a; color:{RED}; padding:.3rem .9rem;
        border-radius:999px; font-size:.75rem; font-weight:700; letter-spacing:.12em; }}
.live::before {{ content:""; display:inline-block; width:8px; height:8px; border-radius:50%;
        background:{RED}; margin-right:8px; animation:pulse 1.4s infinite; }}
@keyframes pulse {{ 0%{{box-shadow:0 0 0 0 {RED}aa}} 70%{{box-shadow:0 0 0 8px transparent}} 100%{{box-shadow:0 0 0 0 transparent}} }}
.sec {{ font-size:1.25rem; font-weight:700; color:#fff; margin:1.4rem 0 .1rem; }}
.secsub {{ color:{MUTED}; font-size:.85rem; margin-bottom:.7rem; }}
.kpi {{ background:{CARD}; border:1px solid {BORDER}; border-top:3px solid {RED};
        border-radius:12px; padding:1rem 1.2rem; height:100%; }}
.kpi .l {{ color:{MUTED}; font-size:.75rem; text-transform:uppercase; letter-spacing:.1em; }}
.kpi .v {{ color:#fff; font-size:2rem; font-weight:800; line-height:1.2; }}
.kpi .s {{ color:#64748b; font-size:.78rem; }}
.card {{ background:{CARD}; border:1px solid {BORDER}; border-radius:12px; padding:1rem 1.2rem .4rem; }}
.card h4 {{ margin:0; color:#fff; font-size:1rem; }}
.card p {{ margin:0 0 .5rem; color:{MUTED}; font-size:.78rem; }}
.note {{ color:#64748b; font-size:.78rem; margin-top:.4rem; }}
</style>""", unsafe_allow_html=True)

# ------------------------------------------------------------------ data
CITIES = [  # (city, state, lat, lng, weight)
 ("Los Angeles","CA",34.05,-118.24,10),("San Francisco","CA",37.77,-122.42,4),("San Diego","CA",32.72,-117.16,4),
 ("Sacramento","CA",38.58,-121.49,3),("Houston","TX",29.76,-95.37,6),("Dallas","TX",32.78,-96.80,6),
 ("Austin","TX",30.27,-97.74,3),("San Antonio","TX",29.42,-98.49,3),("Miami","FL",25.76,-80.19,6),
 ("Orlando","FL",28.54,-81.38,4),("Tampa","FL",27.95,-82.46,3),("Jacksonville","FL",30.33,-81.66,2),
 ("New York","NY",40.71,-74.01,5),("Buffalo","NY",42.89,-78.88,1.5),("Philadelphia","PA",39.95,-75.17,3),
 ("Pittsburgh","PA",40.44,-80.0,2),("Chicago","IL",41.88,-87.63,5),("Atlanta","GA",33.75,-84.39,4),
 ("Charlotte","NC",35.23,-80.84,3),("Raleigh","NC",35.78,-78.64,2),("Columbus","OH",39.96,-83.0,2.5),
 ("Cleveland","OH",41.50,-81.69,2),("Detroit","MI",42.33,-83.05,3),("Seattle","WA",47.61,-122.33,3.5),
 ("Portland","OR",45.52,-122.68,2.5),("Phoenix","AZ",33.45,-112.07,4),("Denver","CO",39.74,-104.99,3),
 ("Minneapolis","MN",44.98,-93.27,2.5),("St. Louis","MO",38.63,-90.2,2),("Nashville","TN",36.16,-86.78,2.5),
 ("Baltimore","MD",39.29,-76.61,2.5),("Richmond","VA",37.54,-77.44,2),("Boston","MA",42.36,-71.06,2.5),
 ("Salt Lake City","UT",40.76,-111.89,2),("Las Vegas","NV",36.17,-115.14,2.5),("New Orleans","LA",29.95,-90.07,2),
 ("Indianapolis","IN",39.77,-86.16,2),("Kansas City","MO",39.1,-94.58,1.8),("Oklahoma City","OK",35.47,-97.52,1.8),
 ("Louisville","KY",38.25,-85.76,1.5),
]
WEATHER = ["Clear","Fair","Cloudy","Mostly Cloudy","Partly Cloudy","Overcast","Light Rain","Rain",
           "Heavy Rain","Fog","Snow","Haze","Thunderstorm"]
WEATHER_P = np.array([22,18,12,9,8,6,6,4,1.5,3,3,3,2.5]); WEATHER_P = WEATHER_P / WEATHER_P.sum()


@st.cache_data(show_spinner=False)
def demo_data(n=60000):
    """Synthetic data shaped like the US Accidents dataset. NOT real statistics."""
    rng = np.random.default_rng(7)
    w = np.array([c[4] for c in CITIES], float); w /= w.sum()
    idx = rng.choice(len(CITIES), n, p=w)
    lat = np.array([CITIES[i][2] for i in idx]) + rng.normal(0, .18, n)
    lng = np.array([CITIES[i][3] for i in idx]) + rng.normal(0, .22, n)
    hp = np.array([1,.8,.7,.7,1,2,4.5,7,6,4,3.5,3.8,4.2,4,4.3,5.5,7.5,8,6,4,3,2.2,1.6,1.2]); hp /= hp.sum()
    ts = (pd.Timestamp("2021-01-01") + pd.to_timedelta(rng.integers(0, 365*3, n), "D")
          + pd.to_timedelta(rng.choice(24, n, p=hp), "h") + pd.to_timedelta(rng.integers(0, 60, n), "m"))
    wx = rng.choice(WEATHER, n, p=WEATHER_P)
    bad = np.isin(wx, ["Heavy Rain", "Snow", "Fog", "Thunderstorm"])
    sev = np.where(rng.random(n) < .55 + 0, 2, rng.choice([1, 3, 4], n, p=[.1, .75, .15]))
    sev = np.where(bad & (rng.random(n) < .18), 3, sev)
    return pd.DataFrame({"severity": sev, "state": [CITIES[i][1] for i in idx], "weather": wx,
                         "start_time": ts, "lat": lat, "lng": lng})


@st.cache_data(show_spinner="Reading & cleaning file...")
def load_upload(file):
    """Accepts the Kaggle 'US Accidents' CSV (Severity, State, Weather_Condition, Start_Time, Start_Lat, Start_Lng)."""
    head = pd.read_csv(file, nrows=0); file.seek(0)
    low = {c.lower(): c for c in head.columns}
    need = {"severity": "severity", "state": "state", "weather_condition": "weather",
            "start_time": "start_time", "start_lat": "lat", "start_lng": "lng"}
    miss = [k for k in need if k not in low]
    if miss:
        raise ValueError(f"Missing columns: {miss}")
    df = pd.read_csv(file, usecols=[low[k] for k in need]).rename(columns={low[k]: v for k, v in need.items()})
    df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce", format="mixed")
    df["severity"] = pd.to_numeric(df["severity"], errors="coerce")
    df = df.dropna(subset=["severity", "state", "start_time"]).copy()
    df["severity"] = df["severity"].astype(int)
    df["weather"] = df["weather"].fillna("Unknown")
    return df


def section(title, sub):
    st.markdown(f'<div class="sec">{title}</div><div class="secsub">{sub}</div>', unsafe_allow_html=True)


def kpi(col, label, value, sub):
    col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div>'
                 f'<div class="s">{sub}</div></div>', unsafe_allow_html=True)


VL = {"background": "transparent", "view": {"stroke": None},
      "axis": {"labelColor": MUTED, "titleColor": MUTED, "gridColor": "#1e293b", "domainColor": "#334155", "tickColor": "#334155"},
      "legend": {"labelColor": "#cbd5e1", "titleColor": MUTED}}


def chart(df, spec, height=300):
    spec = {**spec, "height": height, "config": VL}
    st.vega_lite_chart(df, spec, use_container_width=True)


# ------------------------------------------------------------------ header
st.markdown('<div class="brand"><h1>ROAD<span>SAFE</span> ANALYTICS</h1><div class="live">LIVE ANALYTICS</div></div>'
            '<div class="sub">US Road Accident Intelligence Dashboard</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Data source")
    up = st.file_uploader("Upload US Accidents CSV", type="csv",
                          help="Needs: Severity, State, Weather_Condition, Start_Time, Start_Lat, Start_Lng")
if up is not None:
    try:
        data = load_upload(up)
    except Exception as e:
        st.error(f"Could not read file: {e}"); st.stop()
    demo = False
else:
    data, demo = demo_data(), True

with st.sidebar:
    st.markdown("### Filters")
    years = sorted(data["start_time"].dt.year.unique())
    yr = st.select_slider("Year range", options=years, value=(years[0], years[-1])) if len(years) > 1 else (years[0], years[0])
    sevs = st.multiselect("Severity", [1, 2, 3, 4], default=[1, 2, 3, 4])
    states = sorted(data["state"].unique())
    sel_states = st.multiselect("State", states, default=states)
    st.markdown("### Map")
    mode = st.radio("Map style", ["Red points", "Heatmap"], horizontal=True)
    max_pts = st.slider("Max points drawn", 5000, 100000, 40000, 5000)

f = data[data["start_time"].dt.year.between(*yr) & data["severity"].isin(sevs) & data["state"].isin(sel_states)]
if f.empty:
    st.info("No records match the current filters."); st.stop()

if demo:
    st.warning("Showing a **synthetic demo dataset** (not real statistics). Upload the US Accidents CSV in the sidebar to analyse real data.")

# ------------------------------------------------------------------ overview
section("Overview", "Historical accident data")
c1, c2, c3, c4 = st.columns(4)
kpi(c1, "Total accidents", f"{len(f):,}", "Dataset records")
kpi(c2, "States covered", f["state"].nunique(), "Unique states")
kpi(c3, "Average severity", f"{f['severity'].mean():.2f}", "Severity score (1–4)")
kpi(c4, "Weather conditions", f["weather"].nunique(), "Conditions recorded")

# ------------------------------------------------------------------ severity + hourly
a, b = st.columns(2)
with a:
    section("Accidents by severity", "Severity 1–4 · Distribution")
    s = f["severity"].value_counts().rename_axis("severity").reset_index(name="count")
    s["severity"] = s["severity"].astype(str)
    s["share"] = (s["count"] / s["count"].sum() * 100).round(1)
    chart(s, {"mark": {"type": "arc", "innerRadius": 70, "stroke": BG},
              "encoding": {"theta": {"field": "count", "type": "quantitative"},
                           "color": {"field": "severity", "type": "nominal", "title": "Severity",
                                     "scale": {"domain": ["1", "2", "3", "4"], "range": list(SEV_COLORS.values())}},
                           "tooltip": [{"field": "severity"}, {"field": "count", "format": ","}, {"field": "share", "title": "%"}]}}, 320)
with b:
    section("Hourly trends", "Accidents by hour")
    h = f["start_time"].dt.hour.value_counts().sort_index().rename_axis("hour").reset_index(name="count")
    chart(h, {"mark": {"type": "bar", "color": RED, "cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3},
              "encoding": {"x": {"field": "hour", "type": "ordinal", "title": "Hour of day", "axis": {"labelAngle": 0}},
                           "y": {"field": "count", "type": "quantitative", "title": None},
                           "tooltip": [{"field": "hour"}, {"field": "count", "format": ","}]}}, 320)

# ------------------------------------------------------------------ weather + state
a, b = st.columns(2)
with a:
    section("Weather analysis", "Weather conditions")
    w = f["weather"].value_counts().head(10).rename_axis("weather").reset_index(name="count")
    chart(w, {"mark": {"type": "bar", "color": "#f97316", "cornerRadiusEnd": 3},
              "encoding": {"y": {"field": "weather", "type": "nominal", "sort": "-x", "title": None},
                           "x": {"field": "count", "type": "quantitative", "title": "Accidents"},
                           "tooltip": [{"field": "weather"}, {"field": "count", "format": ","}]}}, 340)
with b:
    section("State-wise accident distribution", "Top 15 states by accident count")
    st_ = f["state"].value_counts().head(15).rename_axis("state").reset_index(name="count")
    chart(st_, {"mark": {"type": "bar", "color": RED, "cornerRadiusEnd": 3},
                "encoding": {"y": {"field": "state", "type": "nominal", "sort": "-x", "title": None},
                             "x": {"field": "count", "type": "quantitative", "title": "Accidents"},
                             "tooltip": [{"field": "state"}, {"field": "count", "format": ","}]}}, 340)

# ------------------------------------------------------------------ map
section("US accident map", "Every recorded accident location highlighted in red")
m = f.dropna(subset=["lat", "lng"])
sampled = len(m) > max_pts
if sampled:
    m = m.sample(max_pts, random_state=1)
m = m[["lat", "lng", "severity"]].rename(columns={"lng": "lon"})
if mode == "Heatmap":
    layer = pdk.Layer("HeatmapLayer", data=m, get_position="[lon, lat]", radius_pixels=28, intensity=1.4, threshold=0.05,
                      color_range=[[127, 29, 29, 40], [185, 28, 28, 120], [220, 38, 38, 180], [239, 68, 68, 220], [254, 202, 202, 255]])
else:
    layer = pdk.Layer("ScatterplotLayer", data=m, get_position="[lon, lat]", get_fill_color=[239, 68, 68, 150],
                      get_radius=1, radius_min_pixels=2, radius_max_pixels=5, pickable=True)
view = pdk.ViewState(latitude=38.5, longitude=-96, zoom=3.3, pitch=0)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, map_style="dark",
                         tooltip={"text": "Severity {severity}"}), use_container_width=True, height=560)
st.markdown(f'<div class="note">Showing {len(m):,} of {len(f):,} accidents'
            f'{" (random sample for performance)" if sampled else ""}.'
            f'{" Demo coordinates are synthetic clusters around major US cities." if demo else ""}</div>', unsafe_allow_html=True)

with st.expander("Data table"):
    st.dataframe(f.head(1000), use_container_width=True)
