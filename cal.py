import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

# Month mapping fix
MONTH_NAME_TO_NUM = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}

# Page configuration
st.set_page_config(
    page_title="Solar Energy Calculator",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .season-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .formula-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin: 15px 0;
    }
    .stSelectbox label {
        font-weight: bold;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">☀️ Solar Energy Calculator</h1>', unsafe_allow_html=True)

# Seasonal configurations
SEASONS_CONFIG = {
    'winter': {
        'months': ['November', 'December', 'January', 'February'],
        'ranges': {
            'irradiance': (300, 700),
            'humidity': (30, 70),
            'wind_speed': (1, 6),
            'ambient_temperature': (5, 20),
            'tilt_angle': (10, 40),
        },
        'color': '#3498db',
        'icon': '❄️'
    },
    'spring': {
        'months': ['March', 'April', 'May'],
        'ranges': {
            'irradiance': (400, 800),
            'humidity': (40, 80),
            'wind_speed': (2, 8),
            'ambient_temperature': (15, 25),
            'tilt_angle': (15, 35),
        },
        'color': '#2ecc71',
        'icon': '🌸'
    },
    'summer': {
        'months': ['June', 'July', 'August'],
        'ranges': {
            'irradiance': (600, 1000),
            'humidity': (50, 90),
            'wind_speed': (3, 10),
            'ambient_temperature': (25, 40),
            'tilt_angle': (0, 30),
        },
        'color': '#f39c12',
        'icon': '☀️'
    },
    'autumn': {
        'months': ['September', 'October'],
        'ranges': {
            'irradiance': (350, 750),
            'humidity': (35, 75),
            'wind_speed': (2, 7),
            'ambient_temperature': (10, 25),
            'tilt_angle': (20, 45),
        },
        'color': '#e67e22',
        'icon': '🍂'
    }
}

def get_days_in_month(month, year=2024):
    """Get number of days in a month"""
    return calendar.monthrange(year, MONTH_NAME_TO_NUM[month])[1]

def calc_kwh_generalized(irradiance, humidity, wind_speed, ambient_temp, tilt_angle, season='winter'):
    """Generalized kWh calculation with season-specific coefficients"""
    coefficients = {
        'winter': {'irr': 0.18, 'hum': -0.03, 'wind': 0.015, 'temp': 0.08, 'tilt': -0.02},
        'spring': {'irr': 0.20, 'hum': -0.025, 'wind': 0.02, 'temp': 0.06, 'tilt': -0.015},
        'summer': {'irr': 0.22, 'hum': -0.035, 'wind': 0.025, 'temp': 0.04, 'tilt': -0.01},
        'autumn': {'irr': 0.19, 'hum': -0.028, 'wind': 0.018, 'temp': 0.07, 'tilt': -0.018}
    }
    
    coeff = coefficients[season]
    optimal_tilt = 30 if season in ['winter', 'spring'] else 20
    
    return (coeff['irr'] * irradiance +
            coeff['hum'] * humidity +
            coeff['wind'] * wind_speed +
            coeff['temp'] * ambient_temp +
            coeff['tilt'] * abs(tilt_angle - optimal_tilt))

def generate_seasonal_data(season, months, feature_ranges, year=2024):
    """Generate data for a specific season"""
    data = []
    for month in months:
        days = get_days_in_month(month, year)
        for day in range(1, days + 1):
            # Generate random values within ranges
            irr = np.random.uniform(*feature_ranges['irradiance'])
            hum = np.random.uniform(*feature_ranges['humidity'])
            wind = np.random.uniform(*feature_ranges['wind_speed'])
            temp = np.random.uniform(*feature_ranges['ambient_temperature'])
            tilt = np.random.uniform(*feature_ranges['tilt_angle'])
            
            kwh = calc_kwh_generalized(irr, hum, wind, temp, tilt, season)
            
            data.append({
                'date': f"{year}-{MONTH_NAME_TO_NUM[month]:02d}-{day:02d}",
                'irradiance': round(irr, 2),
                'humidity': round(hum, 2),
                'wind_speed': round(wind, 2),
                'ambient_temperature': round(temp, 2),
                'tilt_angle': round(tilt, 2),
                'kwh': round(kwh, 2),
                'season': season,
                'month': month,
                'day': day
            })
    return pd.DataFrame(data)

# SIDEBAR
st.sidebar.header("⚙️ Calculator Settings")
selected_season = st.sidebar.selectbox(
    "Select Season",
    list(SEASONS_CONFIG.keys()),
    format_func=lambda x: f"{SEASONS_CONFIG[x]['icon']} {x.title()}"
)
selected_year = st.sidebar.number_input("Select Year", min_value=2020, max_value=2030, value=2024)
st.sidebar.subheader("🔧 Advanced Settings")
use_custom_params = st.sidebar.checkbox("Use Custom Parameters")

if use_custom_params:
    st.sidebar.write("**Adjust Parameter Ranges:**")
    season_config = SEASONS_CONFIG[selected_season]
    irradiance_range = st.sidebar.slider("Irradiance Range (W/m²)", 0, 1200, season_config['ranges']['irradiance'], 50)
    humidity_range = st.sidebar.slider("Humidity Range (%)", 0, 100, season_config['ranges']['humidity'], 5)
    wind_range = st.sidebar.slider("Wind Speed Range (m/s)", 0, 15, season_config['ranges']['wind_speed'], 1)
    temp_range = st.sidebar.slider("Temperature Range (°C)", -10, 50, season_config['ranges']['ambient_temperature'], 5)
    tilt_range = st.sidebar.slider("Tilt Angle Range (degrees)", 0, 60, season_config['ranges']['tilt_angle'], 5)
    SEASONS_CONFIG[selected_season]['ranges'] = {
        'irradiance': irradiance_range,
        'humidity': humidity_range,
        'wind_speed': wind_range,
        'ambient_temperature': temp_range,
        'tilt_angle': tilt_range
    }

# DISPLAY SEASON INFO
season_info = SEASONS_CONFIG[selected_season]
st.markdown(f"""
<div class="season-card">
    <h2>{season_info['icon']} {selected_season.title()} Season Analysis</h2>
    <p><strong>Months:</strong> {', '.join(season_info['months'])}</p>
    <p><strong>Year:</strong> {selected_year}</p>
</div>
""", unsafe_allow_html=True)

# GENERATE BUTTON
if st.button("🔄 Generate Solar Data", type="primary"):
    with st.spinner("Generating solar energy data..."):
        df_season = generate_seasonal_data(
            selected_season,
            season_info['months'],
            season_info['ranges'],
            selected_year
        )
        st.session_state.solar_data = df_season
        st.session_state.current_season = selected_season

# DATA DISPLAY
if 'solar_data' in st.session_state:
    df = st.session_state.solar_data
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='metric-card'><h3>Total Energy</h3><h2>{df['kwh'].sum():.1f} kWh</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-card'><h3>Average Daily</h3><h2>{df['kwh'].mean():.1f} kWh</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-card'><h3>Peak Day</h3><h2>{df['kwh'].max():.1f} kWh</h2></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='metric-card'><h3>Total Days</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)

    st.subheader("📅 Monthly Breakdown")
    monthly_stats = df.groupby('month').agg({
        'kwh': ['sum', 'mean', 'max', 'min', 'count']
    }).round(2)
    monthly_stats.columns = ['Total kWh', 'Avg kWh', 'Max kWh', 'Min kWh', 'Days']
    st.dataframe(monthly_stats, use_container_width=True)

    st.subheader("📈 Energy Production Analysis")
    fig_timeseries = px.line(df, x='date', y='kwh',
        title=f'{selected_season.title()} Season - Daily Energy Production',
        color_discrete_sequence=[season_info['color']])
    fig_timeseries.update_layout(xaxis_title="Date", yaxis_title="Energy (kWh)", hovermode='x unified')
    st.plotly_chart(fig_timeseries, use_container_width=True)

    st.subheader("🔥 Parameter Correlation Analysis")
    correlation_data = df[['irradiance', 'humidity', 'wind_speed', 'ambient_temperature', 'tilt_angle', 'kwh']].corr()
    fig_heatmap = px.imshow(correlation_data, title="Parameter Correlation Matrix", color_continuous_scale='RdBu')
    st.plotly_chart(fig_heatmap, use_container_width=True)

    col1, col2 = st.columns(2)
    fig_hist = px.histogram(df, x='kwh', nbins=30, title="Energy Production Distribution", color_discrete_sequence=[season_info['color']])
    fig_box = px.box(df, x='month', y='kwh', title="Monthly Energy Production Variation", color_discrete_sequence=[season_info['color']])
    col1.plotly_chart(fig_hist, use_container_width=True)
    col2.plotly_chart(fig_box, use_container_width=True)

    st.subheader("🎯 Parameter Impact Analysis")
    params = ['irradiance', 'humidity', 'wind_speed', 'ambient_temperature', 'tilt_angle']
    for i, param in enumerate(params):
        if i % 2 == 0: cols = st.columns(2)
        with cols[i % 2]:
            fig = px.scatter(df, x=param, y='kwh', title=f'Energy vs {param.title()}', color='month', size='kwh', hover_data=['date'])
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("📝 Calculation Formula")
    st.markdown(f"""
    <div class="formula-card">
        <h4>Energy Calculation Formula for {selected_season.title()} Season:</h4>
        <ul>
            <li><strong>Irradiance coefficient</strong> × Irradiance</li>
            <li><strong>+ Humidity coefficient</strong> × Humidity</li>
            <li><strong>+ Wind coefficient</strong> × Wind Speed</li>
            <li><strong>+ Temperature coefficient</strong> × Temperature</li>
            <li><strong>+ Tilt coefficient</strong> × |Tilt - Optimal Tilt|</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("💾 Download Data")
    st.download_button("📥 Download CSV", df.to_csv(index=False), file_name=f'solar_energy_{selected_season}_{selected_year}.csv', mime='text/csv')
else:
    st.info("👆 Click 'Generate Solar Data' to start analyzing solar energy production!")
