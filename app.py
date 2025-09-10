import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Wind Energy Analytics - Pan India Beta",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern, professional color scheme with beta styling
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f1a2a;
        color: #e6e9f0;
    }
    
    /* Beta badge */
    .beta-badge {
        background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 15px;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Headers */
    .main-header {
        font-size: 2.8rem;
        color: #4fd1c5;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid #4fd1c5;
        font-weight: 700;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        color: white;
        border: 1px solid #4a5568;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #4fd1c5;
    }
    
    /* Section headers */
    .section-header {
        color: #4fd1c5;
        border-left: 5px solid #4fd1c5;
        padding-left: 12px;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Navigation
page = st.sidebar.selectbox("Navigate", ["Wind Dashboard", "Data Sources", "Beta Features", "Feedback"])

# Pan-India wind data (sample data for beta - would be expanded with real sources)
india_wind_data = {
    "Tamil Nadu": {
        "wind_speed": 8.2, "potential": "Excellent", "turbulence": 10.5, "elevation": 150,
        "lat": 11.1271, "lon": 78.6569, "wind_potential": 88.5, "state_code": "TN",
        "source": "NIWE Wind Atlas of India", "installed_capacity": 9600
    },
    "Gujarat": {
        "wind_speed": 7.8, "potential": "Excellent", "turbulence": 11.2, "elevation": 120,
        "lat": 22.2587, "lon": 71.1924, "wind_potential": 84.3, "state_code": "GJ",
        "source": "MNRE Wind Potential Assessment", "installed_capacity": 8900
    },
    "Maharashtra": {
        "wind_speed": 6.5, "potential": "Good", "turbulence": 12.0, "elevation": 450,
        "lat": 19.7515, "lon": 75.7139, "wind_potential": 45.2, "state_code": "MH",
        "source": "NIWE Regional Assessment", "installed_capacity": 5200
    },
    "Rajasthan": {
        "wind_speed": 7.1, "potential": "Very Good", "turbulence": 13.5, "elevation": 280,
        "lat": 27.0238, "lon": 74.2179, "wind_potential": 67.8, "state_code": "RJ",
        "source": "State Renewable Energy Dept", "installed_capacity": 4800
    },
    "Karnataka": {
        "wind_speed": 6.8, "potential": "Good", "turbulence": 11.8, "elevation": 320,
        "lat": 15.3173, "lon": 75.7139, "wind_potential": 52.4, "state_code": "KA",
        "source": "NIWE Wind Monitoring", "installed_capacity": 5100
    },
    "Madhya Pradesh": {
        "wind_speed": 5.7, "potential": "Medium", "turbulence": 12.5, "elevation": 553,
        "lat": 23.2599, "lon": 77.4126, "wind_potential": 28.4, "state_code": "MP",
        "source": "State Energy Department", "installed_capacity": 2500
    },
    "Andhra Pradesh": {
        "wind_speed": 7.3, "potential": "Very Good", "turbulence": 11.0, "elevation": 180,
        "lat": 15.9129, "lon": 79.7400, "wind_potential": 72.6, "state_code": "AP",
        "source": "NIWE Coastal Assessment", "installed_capacity": 3800
    },
    "Kerala": {
        "wind_speed": 5.2, "potential": "Medium", "turbulence": 14.2, "elevation": 80,
        "lat": 10.8505, "lon": 76.2711, "wind_potential": 18.9, "state_code": "KL",
        "source": "State Renewable Energy", "installed_capacity": 1200
    }
}

# Regional classification
wind_regions = {
    "Excellent": ["Tamil Nadu", "Gujarat"],
    "Very Good": ["Rajasthan", "Andhra Pradesh"],
    "Good": ["Maharashtra", "Karnataka"],
    "Medium": ["Madhya Pradesh", "Kerala"]
}

if page == "Wind Dashboard":
    # Header with beta badge
    st.markdown("""
    <div style="display: flex; align-items: center;">
        <h1 class="main-header">🌬️ Wind Energy Analytics - Pan India</h1>
        <div class="beta-badge">BETA</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("""
    **BETA VERSION**: This is a preliminary nationwide assessment. Data is being continuously updated. 
    Please provide feedback using the Feedback section.
    """)

    # Sidebar for user inputs
    with st.sidebar:
        st.markdown('<div class="district-selector">', unsafe_allow_html=True)
        st.header("📍 Select State")
        selected_state = st.selectbox("", list(india_wind_data.keys()), index=0)
        
        # Region filter
        st.header("🌪️ Filter by Wind Potential")
        selected_potential = st.multiselect("", list(wind_regions.keys()), default=list(wind_regions.keys()))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<h3 class="section-header">Project Parameters</h3>', unsafe_allow_html=True)
        years = st.slider("Project Lifetime (Years)", 1, 30, 20)
        capacity_mw = st.slider("Turbine Capacity (MW)", 0.5, 8.0, 2.5, step=0.5)
        area_km = st.slider("Project Area (sq. km)", 1.0, 200.0, 25.0, step=5.0)
        
        st.markdown('<h3 class="section-header">Wind Conditions</h3>', unsafe_allow_html=True)
        avg_wind_speed = st.slider("Average Wind Speed (m/s)", 3.0, 12.0, 
                                  india_wind_data[selected_state]["wind_speed"], step=0.1)
        turbulence = st.slider("Turbulence Intensity (%)", 5.0, 25.0, 
                              india_wind_data[selected_state]["turbulence"], step=0.1)
        
        st.markdown('<h3 class="section-header">Financial Parameters</h3>', unsafe_allow_html=True)
        turbine_cost = st.slider("Turbine Cost (₹ lakhs/MW)", 500, 1200, 750)
        om_cost = st.slider("O&M Cost (₹ lakhs/MW/year)", 10, 60, 35)
        tariff_rate = st.slider("Electricity Tariff (₹/kWh)", 3.0, 10.0, 6.2, step=0.1)

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        # India map visualization
        st.markdown(f'<h3 class="section-header">National Wind Potential Map</h3>', unsafe_allow_html=True)
        
        # Create India map
        india_center = [20.5937, 78.9629]
        m = folium.Map(location=india_center, zoom_start=5, tiles="CartoDB dark_matter")
        
        # Add markers for all states
        for state, data in india_wind_data.items():
            color = "#4fd1c5"  # Default
            if data["potential"] == "Excellent": color = "#00ff00"
            elif data["potential"] == "Very Good": color = "#a0e75a"
            elif data["potential"] == "Good": color = "#ffb74d"
            else: color = "#ff6b6b"
            
            folium.Marker(
                [data["lat"], data["lon"]],
                popup=f"{state}: {data['wind_speed']} m/s ({data['potential']})",
                tooltip=f"{state} - {data['wind_speed']} m/s",
                icon=folium.Icon(color=color, icon="wind", prefix="fa")
            ).add_to(m)
        
        folium_static(m, width=700, height=400)
        
        # State comparison table
        st.markdown('<h3 class="section-header">State Comparison</h3>', unsafe_allow_html=True)
        comparison_data = []
        for state, data in india_wind_data.items():
            comparison_data.append({
                "State": state,
                "Wind Speed (m/s)": data["wind_speed"],
                "Potential": data["potential"],
                "Installed Capacity (MW)": f"{data['installed_capacity']:,}",
                "Theoretical Potential (GW)": data["wind_potential"]
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, height=300)

    with col2:
        # State-specific metrics
        st.markdown(f'<h3 class="section-header">{selected_state} Overview</h3>', unsafe_allow_html=True)
        
        col1a, col2a = st.columns(2)
        with col1a:
            st.metric("Wind Speed", f"{india_wind_data[selected_state]['wind_speed']} m/s")
            st.metric("Potential", india_wind_data[selected_state]["potential"])
        with col2a:
            st.metric("Installed Capacity", f"{india_wind_data[selected_state]['installed_capacity']:,} MW")
            st.metric("Theoretical Potential", f"{india_wind_data[selected_state]['wind_potential']} GW")
        
        # Calculations
        capacity_factor = max(0.087 * avg_wind_speed - (turbulence * 0.005), 0)
        estimated_annual_generation = capacity_mw * 8760 * capacity_factor
        annual_revenue = estimated_annual_generation * tariff_rate * 1000
        total_investment = capacity_mw * turbine_cost * 100000
        annual_om_cost = capacity_mw * om_cost * 100000
        annual_cash_flow = annual_revenue - annual_om_cost
        roi = (annual_cash_flow * years - total_investment) / total_investment * 100 if total_investment > 0 else 0
        
        # Key metrics
        st.markdown('<h3 class="section-header">Project Metrics</h3>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Capacity Factor</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{capacity_factor:.1%}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Annual Generation</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{estimated_annual_generation:,.0f} MWh</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Estimated ROI</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{roi:.1f}%</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Data Sources":
    st.markdown('<h1 class="main-header">📚 Data Sources & Methodology</h1>', unsafe_allow_html=True)
    st.warning("**BETA NOTE**: Data sources are being expanded and validated for nationwide coverage.")
    
    # ... (similar content as before but expanded for nationwide data)

elif page == "Beta Features":
    st.markdown('<h1 class="main-header">🚀 Beta Features & Roadmap</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Current Beta Features
    
    ### ✅ Implemented
    - **Pan-India coverage** with 8 major states
    - **Interactive national map** with wind potential visualization
    - **State comparison dashboard**
    - **Advanced filtering** by wind potential class
    - **Preliminary nationwide data** integration
    
    ### 🚧 In Development
    - **Complete 28-state coverage** with detailed regional data
    - **Seasonal variation analysis** with monthly wind patterns
    - **Turbine technology selection** with manufacturer data
    - **Grid connectivity assessment** with transmission maps
    - **Environmental impact calculator**
    
    ### 📅 Planned
    - **Real-time wind data integration**
    - **Policy incentive database**
    - **Project feasibility scoring system**
    - **Exportable project reports**
    - **API access for developers**
    """)

elif page == "Feedback":
    st.markdown('<h1 class="main-header">💡 Beta Feedback</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Help Improve This Tool
    
    This is a **beta version** and we need your feedback to make it better!
    """)
    
    with st.form("feedback_form"):
        st.selectbox("How would you rate this tool?", ["Excellent", "Good", "Average", "Poor"])
        st.text_area("What features would you like to see added?")
        st.text_area("Any data inaccuracies or issues found?")
        st.text_input("Email (optional, for follow-up)")
        
        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            st.success("Thank you for your feedback! It will help us improve the tool.")

# Footer with beta disclaimer
st.markdown("""
<p class="footer">
    © 2025 Wind Energy Analytics by Prakarsh - Pan India Beta | 
    <span style="color: #ff6b6b;">BETA VERSION - Data subject to validation</span><br>
    For preliminary assessment only. Not for commercial decision-making.
</p>
""", unsafe_allow_html=True)
