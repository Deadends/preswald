import pandas as pd
import plotly.express as px
import preswald

def air_quality_dashboard():
    df = preswald.get_df("sample_csv")
    df['date'] = pd.to_datetime(df['date'])
    df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')

    numeric_cols = ["aqi", "pm2_5", "pm10", "no2", "o3", "hospital_admissions"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 1. Average AQI by City
    avg_aqi = (
        df.groupby("city", as_index=False)["aqi"]
          .mean()
          .sort_values("aqi", ascending=False)
    )
    fig_aqi_bar = px.bar(avg_aqi, x="city", y="aqi", title="Average AQI by City", labels={"aqi": "Avg AQI"})

    # 2a. AQI Over Time
    avg_trend = df.groupby("date_str", as_index=False)["aqi"].mean().iloc[::10]
    fig_avg_trend = px.line(avg_trend, x="date_str", y="aqi", title="Average AQI Over Time (All Cities)")

    # 2b. Top 5 AQI Cities
    top5_cities = avg_aqi["city"].head(5).tolist()
    df_top5 = df[df["city"].isin(top5_cities)]
    df_top5 = df_top5.groupby(["city", "date_str"], as_index=False)["aqi"].mean()
    df_top5 = df_top5.groupby("city").apply(lambda x: x.iloc[::10, :]).reset_index(drop=True)
    fig_top5_trend = px.line(df_top5.sort_values("date_str"), x="date_str", y="aqi", color="city", title="Top 5 Cities AQI Over Time")

    # 3. Pollutant Heatmap
    pollutant_means = df.groupby("city")[["pm2_5", "pm10", "no2", "o3"]].mean().round(2)
    fig_pollut_heatmap = px.imshow(pollutant_means, x=pollutant_means.columns, y=pollutant_means.index,
                                   labels=dict(x="Pollutant", y="City", color="Avg Level"),
                                   title="Average Pollutant Levels by City")

    # 4. Hospital Admissions
    df_sampled = df.iloc[::50]
    fig_admissions = px.scatter(df_sampled, x="aqi", y="hospital_admissions", color="city", title="Admissions vs AQI")

    # Render UI
    preswald.sidebar("Navigation", items=["Overview", "Trends", "Pollutants", "Health Impact"])
    preswald.text("# Air Quality & Health Dashboard")
    preswald.text("## 1. Average AQI by City")
    preswald.plotly(fig_aqi_bar)
    preswald.text("## 2a. Average AQI Over Time (All Cities)")
    preswald.plotly(fig_avg_trend)
    preswald.text("## 2b. AQI Over Time for Top 5 Highest-AQI Cities")
    preswald.plotly(fig_top5_trend)
    preswald.text("## 3. Average Pollutant Levels by City")
    preswald.plotly(fig_pollut_heatmap)
    preswald.text("## 4. Hospital Admissions vs. AQI")
    preswald.plotly(fig_admissions)

air_quality_dashboard()
