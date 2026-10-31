"""Generate a SYNTHETIC road-accident dataset (for demo only, not real statistics)."""
import numpy as np, pandas as pd

rng = np.random.default_rng(42)
N = 50_000
districts = ["Bengaluru Urban", "Mysuru", "Tumakuru", "Belagavi", "Mangaluru",
             "Hubballi-Dharwad", "Ballari", "Kalaburagi", "Shivamogga", "Hassan"]
d_w = np.array([22, 9, 10, 9, 8, 9, 7, 7, 8, 11], float); d_w /= d_w.sum()
weather = ["Clear", "Rain", "Fog", "Overcast", "Storm"]
w_w = [0.60, 0.20, 0.08, 0.10, 0.02]
surface = ["Dry", "Wet", "Muddy", "Oily/Slippery"]
s_w = [0.68, 0.24, 0.05, 0.03]
vehicles = ["Two-wheeler", "Car", "Truck", "Bus", "Auto-rickshaw", "Pedestrian involved"]
v_w = [0.38, 0.24, 0.14, 0.07, 0.10, 0.07]
hour_w = np.array([1,1,1,1,1.5,2.5,4,6,7,5,4,4,4.5,4,4,4.5,5.5,7,8,7,5,3.5,2.5,1.5], float)
hour_w /= hour_w.sum()

start = pd.Timestamp("2021-01-01")
days = rng.integers(0, 365 * 4, N)
hours = rng.choice(24, N, p=hour_w)
mins = rng.integers(0, 60, N)
dt = start + pd.to_timedelta(days, "D") + pd.to_timedelta(hours, "h") + pd.to_timedelta(mins, "m")

w = rng.choice(weather, N, p=w_w)
surf = np.where((w == "Rain") | (w == "Storm"),
                rng.choice(surface, N, p=[0.1, 0.8, 0.07, 0.03]),
                rng.choice(surface, N, p=[0.82, 0.08, 0.06, 0.04]))
# severity probabilities depend slightly on conditions
p_fatal = 0.05 + 0.03 * np.isin(w, ["Fog", "Storm"]) + 0.02 * ((hours < 5) | (hours > 21))
p_serious = 0.25 + 0.05 * (surf == "Wet")
u = rng.random(N)
sev = np.where(u < p_fatal, "Fatal", np.where(u < p_fatal + p_serious, "Serious", "Slight"))

df = pd.DataFrame({
    "accident_id": [f"ACC{i:06d}" for i in range(N)],
    "accident_date": dt.strftime("%Y-%m-%d"),
    "accident_time": dt.strftime("%H:%M"),
    "district": rng.choice(districts, N, p=d_w),
    "severity": sev,
    "weather_condition": w,
    "road_surface": surf,
    "vehicle_type": rng.choice(vehicles, N, p=v_w),
})
# inject a few duplicates / nulls to demonstrate cleaning
df = pd.concat([df, df.sample(300, random_state=1)], ignore_index=True)
df.loc[df.sample(150, random_state=2).index, "district"] = None
df.to_csv("data/accidents_sample.csv", index=False)
print(df.shape)
