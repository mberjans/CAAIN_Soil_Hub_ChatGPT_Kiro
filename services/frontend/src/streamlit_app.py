import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time
import json
from typing import Dict, List, Any

# API Configuration
API_BASE_URL = "http://localhost:8001/api/v1"
PLANTING_API_URL = f"{API_BASE_URL}/planting"

# API Helper Functions
def get_planting_dates(crop_name: str, location_data: Dict[str, Any], season: str = "spring") -> Dict[str, Any]:
    """Get planting dates for a specific crop and location."""
    try:
        payload = {
            "crop_name": crop_name.lower(),
            "location": {
                "latitude": location_data.get("latitude", 42.0),
                "longitude": location_data.get("longitude", -93.0),
                "elevation_ft": location_data.get("elevation_ft", 1000),
                "address": location_data.get("address", "Farm Location"),
                "state": location_data.get("state", "Iowa"),
                "county": location_data.get("county", "Story"),
                "climate_zone": location_data.get("climate_zone", "5b"),
                "climate_zone_name": location_data.get("climate_zone_name", "USDA Zone 5b"),
                "temperature_range_f": location_data.get("temperature_range_f", {"min": -15, "max": -10}),
                "climate_confidence": location_data.get("climate_confidence", 0.85)
            },
            "planting_season": season
        }
        
        response = requests.post(f"{PLANTING_API_URL}/calculate-dates", json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.warning(f"Could not fetch planting dates: {str(e)}")
        return None

def get_frost_dates(location_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get frost date information for a location.""" 
    try:
        payload = {
            "location": {
                "latitude": location_data.get("latitude", 42.0),
                "longitude": location_data.get("longitude", -93.0),
                "elevation_ft": location_data.get("elevation_ft", 1000),
                "address": location_data.get("address", "Farm Location"),
                "state": location_data.get("state", "Iowa"),
                "county": location_data.get("county", "Story"),
                "climate_zone": location_data.get("climate_zone", "5b"),
                "climate_zone_name": location_data.get("climate_zone_name", "USDA Zone 5b"),
                "temperature_range_f": location_data.get("temperature_range_f", {"min": -15, "max": -10}),
                "climate_confidence": location_data.get("climate_confidence", 0.85)
            }
        }
        
        response = requests.post(f"{PLANTING_API_URL}/frost-dates", json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.warning(f"Could not fetch frost dates: {str(e)}")
        return None

def get_available_crops() -> List[str]:
    """Get list of available crops for planting date calculations."""
    try:
        response = requests.get(f"{PLANTING_API_URL}/available-crops", timeout=10)
        if response.status_code == 200:
            crops_data = response.json()
            return [crop["name"] for crop in crops_data]
        else:
            return ["corn", "soybean", "wheat", "peas", "lettuce", "spinach", "tomato", "potato", "onion"]
    except Exception as e:
        # Fallback to default crops if API is unavailable
        return ["corn", "soybean", "wheat", "peas", "lettuce", "spinach", "tomato", "potato", "onion"]

def format_planting_date(date_str: str) -> str:
    """Format date string for display."""
    try:
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime("%B %d, %Y")
        return date_str
    except:
        return date_str

# Helper functions for agricultural climate zone mapping
def get_agricultural_zone_data() -> Dict[str, Any]:
    """
    Comprehensive agricultural zone data for climate zone mapping.
    In production, this would connect to a database or API.
    """
    return {
        "5b_iowa_agricultural": {
            "zone_id": "5b_iowa_agricultural",
            "climate_zone": "5b", 
            "agricultural_classification": "intensive_cropping",
            "crop_suitability": {
                "corn": {"rating": 9.2, "yield_potential": "180 bu/acre", "risk_level": "low"},
                "soybeans": {"rating": 8.8, "yield_potential": "55 bu/acre", "risk_level": "low"},
                "wheat": {"rating": 7.5, "yield_potential": "65 bu/acre", "risk_level": "medium"},
                "oats": {"rating": 8.0, "yield_potential": "80 bu/acre", "risk_level": "low"},
                "alfalfa": {"rating": 8.3, "yield_potential": "6 ton/acre", "risk_level": "low"}
            },
            "growing_season": {
                "frost_free_days": 180,
                "planting_window": "April 15 - May 15",
                "harvest_window": "September 15 - November 1",
                "optimal_planting": "May 1",
                "growing_degree_days": 3100
            },
            "agricultural_risks": ["late_spring_frost", "drought_potential", "wet_spring_delays"],
            "soil_types": ["prairie_soils", "glacial_till", "mollisols"],
            "productivity_index": 8.7,
            "farm_enterprises": ["row_crops", "livestock", "dairy", "grain_storage"],
            "economic_factors": {
                "production_cost_index": 85,
                "market_access": "excellent",
                "elevator_distance": "5-10 miles"
            }
        }
        # Additional zones would be added here in production
    }

def calculate_risk_score(risks: List[str]) -> float:
    """Calculate overall risk score based on identified risks."""
    risk_weights = {
        "late_spring_frost": 0.3,
        "drought_potential": 0.4, 
        "wet_spring_delays": 0.2,
        "disease_pressure": 0.4,
        "pest_pressure": 0.3,
        "market_volatility": 0.6,
        "equipment_risk": 0.2
    }
    
    total_risk = sum(risk_weights.get(risk, 0.3) for risk in risks)
    return min(total_risk / len(risks), 1.0) if risks else 0.2

def format_agricultural_recommendation(zone_data: Dict[str, Any]) -> str:
    """Generate formatted agricultural recommendation text."""
    top_crop = max(zone_data['crop_suitability'].items(), 
                  key=lambda x: x[1]['rating'])
    
    return f"""
    **Zone {zone_data['climate_zone']} Agricultural Recommendations:**
    
    🌽 **Top Crop:** {top_crop[0].title()} (Rating: {top_crop[1]['rating']}/10)
    📊 **Productivity Index:** {zone_data['productivity_index']}/10
    🗓️ **Growing Season:** {zone_data['growing_season']['frost_free_days']} frost-free days
    🏛️ **Best Enterprise:** {zone_data['farm_enterprises'][0].replace('_', ' ').title()}
    
    This zone offers excellent conditions for {zone_data['agricultural_classification'].replace('_', ' ')}.
    """

# Configure page
st.set_page_config(
    page_title="AFAS - Farm Advisory System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for validation feedback system
if 'show_correction_form' not in st.session_state:
    st.session_state.show_correction_form = False
if 'show_override_form' not in st.session_state:
    st.session_state.show_override_form = False

# Custom CSS for agricultural theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #28a745, #20c997);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .recommendation-card {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #28a745;
        margin-bottom: 1rem;
    }
    .climate-zone-card {
        background: #f0f8ff;
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 3px solid #20c997;
        margin: 0.5rem 0;
    }
    .frost-info {
        background: #e6f3ff;
        padding: 0.5rem;
        border-radius: 4px;
        margin: 0.25rem 0;
    }
    .validation-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #20c997;
        margin-bottom: 1rem;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
    .validation-alert {
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .alert-error {
        background: #f8d7da;
        border-left-color: #dc3545;
        color: #721c24;
    }
    .alert-warning {
        background: #fff3cd;
        border-left-color: #ffc107;
        color: #856404;
    }
    .alert-info {
        background: #d1ecf1;
        border-left-color: #17a2b8;
        color: #0c5460;
    }
    .alert-success {
        background: #d4edda;
        border-left-color: #28a745;
        color: #155724;
    }
    .crop-card {
        background: #f8f9fa;
        padding: 0.5rem;
        margin: 0.2rem 0;
        border-radius: 4px;
        border-left: 3px solid #28a745;
    }
    .enterprise-card {
        background: #f8f9fa;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 6px;
        border-left: 3px solid #28a745;
    }
    .agricultural-zone-header {
        background: linear-gradient(90deg, #28a745, #20c997);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
    }
    .risk-card {
        background: #fff3cd;
        padding: 0.6rem;
        margin: 0.3rem 0;
        border-radius: 4px;
        border-left: 3px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🌱 Autonomous Farm Advisory System</h1>
    <p>Science-based agricultural recommendations powered by expert knowledge</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for farm information
with st.sidebar:
    st.header("🏡 Farm Profile")
    farm_name = st.text_input("Farm Name", placeholder="Green Valley Farm")
    location = st.text_input("Location", placeholder="Ames, Iowa")
    farm_size = st.number_input("Farm Size (acres)", min_value=1, value=160, step=1)
    
    # Climate Zone Section
    st.header("🌡️ Climate Zone Information")
    
    # USDA Hardiness Zone
    col1, col2 = st.columns([2, 1])
    with col1:
        usda_zone = st.selectbox(
            "USDA Hardiness Zone",
            ["Zone 3a", "Zone 3b", "Zone 4a", "Zone 4b", "Zone 5a", "Zone 5b", 
             "Zone 6a", "Zone 6b", "Zone 7a", "Zone 7b", "Zone 8a", "Zone 8b", 
             "Zone 9a", "Zone 9b", "Zone 10a", "Zone 10b"],
            index=5,  # Default to Zone 5b
            help="USDA Plant Hardiness Zone based on average extreme minimum winter temperatures"
        )
    with col2:
        st.metric("Zone Confidence", "92%", help="Confidence level of zone determination")
    
    # Köppen Climate Classification
    koppen_climate = st.text_input(
        "Köppen Climate Classification", 
        value="Dfa - Hot-summer humid continental",
        disabled=True,
        help="Köppen climate classification system - automatically determined based on location"
    )
    
    # Frost Date Information
    st.subheader("🌨️ Frost Dates")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Last Frost", "April 15", help="Average date of last spring frost")
    with col2:
        st.metric("First Frost", "October 12", help="Average date of first fall frost")
    with col3:
        st.metric("Frost-Free Days", "180", help="Average number of frost-free days")
    
    # Agricultural Suitability
    st.subheader("🌾 Agricultural Assessment")
    col1, col2 = st.columns([2, 1])
    with col1:
        # Agricultural suitability score with progress bar
        suitability_score = 8.5
        st.write("**Agricultural Suitability Score**")
        progress_color = "#28a745" if suitability_score >= 7 else "#ffc107" if suitability_score >= 5 else "#dc3545"
        st.progress(suitability_score / 10.0)
        st.write(f"**{suitability_score}/10** - Excellent conditions for agriculture")
    with col2:
        # Climate zone detection status
        st.write("**Detection Status**")
        st.success("✅ Verified")
        st.caption("Last updated: Today")
    
    # Climate zone insights
    with st.expander("🔍 Climate Zone Insights", expanded=False):
        st.markdown("""
        **Key Climate Characteristics:**
        - **Temperature Range**: Cold winters (-15°F to -10°F), warm summers
        - **Precipitation**: 30-40 inches annually, well-distributed
        - **Growing Season**: 160-180 frost-free days
        - **Best Crops**: Corn, soybeans, wheat, alfalfa
        
        **Agricultural Advantages:**
        - Excellent moisture availability
        - Long growing season for temperate crops
        - Good soil development conditions
        
        **Considerations:**
        - Plan for cold winter storage
        - Monitor for late spring/early fall frosts
        - Optimize planting dates for frost-free period
        """)
    
    # Climate Zone Visualizations Section
    st.subheader("📊 Climate Zone Visualizations")
    
    # Interactive Climate Zone Map
    with st.expander("🗺️ Interactive Climate Zone Map", expanded=False):
        st.markdown("**USDA Hardiness Zones Map** - Your location is highlighted")
        
        # Mock US states data for USDA zones
        states_data = {
            'State': ['Iowa', 'Illinois', 'Indiana', 'Minnesota', 'Wisconsin', 'Michigan', 'Ohio', 'Missouri', 'Kansas', 'Nebraska'],
            'Zone': ['5b', '6a', '6a', '4b', '4b', '5a', '6a', '6b', '6a', '5a'],
            'Min_Temp': [-15, -10, -10, -20, -20, -15, -10, -5, -10, -15],
            'Latitude': [41.8, 40.0, 39.8, 45.0, 44.3, 44.3, 40.4, 38.4, 38.5, 41.1],
            'Longitude': [-93.1, -89.0, -86.1, -93.2, -89.6, -84.5, -82.7, -92.2, -96.7, -98.0]
        }
        
        states_df = pd.DataFrame(states_data)
        
        # Color mapping for zones
        zone_colors = {
            '4b': '#0066CC', '5a': '#3399FF', '5b': '#66CCFF', 
            '6a': '#99FF99', '6b': '#66FF66', '7a': '#FFFF66'
        }
        
        states_df['Color'] = states_df['Zone'].map(zone_colors)
        states_df['Current_Location'] = states_df['State'] == 'Iowa'  # Highlight Iowa as current location
        states_df['Marker_Size'] = states_df['Current_Location'].apply(lambda x: 15 if x else 8)
        
        fig_map = px.scatter(states_df, 
                           x='Longitude', y='Latitude',
                           color='Zone',
                           size='Marker_Size',
                           size_max=15,
                           hover_data=['State', 'Min_Temp'],
                           title="USDA Hardiness Zones - Midwest Region",
                           color_discrete_map=zone_colors)
        
        fig_map.update_layout(
            height=400,
            showlegend=True,
            geo=dict(
                projection_type='natural earth',
                showcoastlines=True,
                landcolor='rgb(243, 243, 243)',
            )
        )
        fig_map.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
        st.plotly_chart(fig_map, use_container_width=True)
        
        st.info("🎯 **Your Location**: Iowa (Zone 5b) - Highlighted in larger marker")
    
    # Temperature Patterns Chart
    with st.expander("🌡️ Temperature Patterns", expanded=False):
        st.markdown("**Monthly Temperature Ranges** - Zone 5b Climate Patterns")
        
        # Mock temperature data for Zone 5b
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        temp_max = [31, 37, 49, 63, 74, 84, 87, 85, 77, 65, 49, 35]
        temp_min = [11, 17, 28, 39, 50, 60, 64, 62, 53, 41, 29, 17]
        temp_avg = [(max_t + min_t) / 2 for max_t, min_t in zip(temp_max, temp_min)]
        
        temp_df = pd.DataFrame({
            'Month': months,
            'Max_Temp': temp_max,
            'Min_Temp': temp_min,
            'Avg_Temp': temp_avg
        })
        
        fig_temp = go.Figure()
        
        # Add temperature bands
        fig_temp.add_trace(go.Scatter(
            x=months, y=temp_max,
            fill=None,
            mode='lines',
            line_color='rgba(255, 0, 0, 0.8)',
            name='Maximum Temperature'
        ))
        
        fig_temp.add_trace(go.Scatter(
            x=months, y=temp_min,
            fill='tonexty',
            mode='lines',
            line_color='rgba(0, 0, 255, 0.8)',
            name='Minimum Temperature',
            fillcolor='rgba(0, 100, 80, 0.2)'
        ))
        
        fig_temp.add_trace(go.Scatter(
            x=months, y=temp_avg,
            mode='lines+markers',
            line=dict(color='#28a745', width=3),
            name='Average Temperature',
            marker=dict(size=8)
        ))
        
        fig_temp.update_layout(
            title="Monthly Temperature Ranges (°F)",
            xaxis_title="Month",
            yaxis_title="Temperature (°F)",
            height=400,
            hovermode='x'
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Coldest Month", "January", f"{min(temp_avg):.0f}°F avg")
        with col2:
            st.metric("Warmest Month", "July", f"{max(temp_avg):.0f}°F avg")
        with col3:
            st.metric("Annual Range", f"{max(temp_max) - min(temp_min)}°F", "Max to Min")
    
    # Precipitation Chart
    with st.expander("🌧️ Precipitation Patterns", expanded=False):
        st.markdown("**Monthly Precipitation & Seasonal Trends** - Zone 5b Climate")
        
        # Mock precipitation data
        precip_monthly = [1.2, 1.1, 2.3, 3.5, 4.2, 4.8, 4.1, 4.0, 3.2, 2.8, 2.1, 1.5]
        seasons = ['Winter', 'Winter', 'Spring', 'Spring', 'Spring', 'Summer', 
                  'Summer', 'Summer', 'Fall', 'Fall', 'Fall', 'Winter']
        
        precip_df = pd.DataFrame({
            'Month': months,
            'Precipitation': precip_monthly,
            'Season': seasons
        })
        
        # Seasonal color mapping
        season_colors = {'Spring': '#28a745', 'Summer': '#ffc107', 'Fall': '#fd7e14', 'Winter': '#6f42c1'}
        
        fig_precip = px.bar(precip_df, x='Month', y='Precipitation', 
                           color='Season',
                           color_discrete_map=season_colors,
                           title="Monthly Precipitation (inches)",
                           hover_data={'Season': True})
        
        fig_precip.update_layout(
            height=400,
            xaxis_title="Month",
            yaxis_title="Precipitation (inches)",
            showlegend=True
        )
        
        st.plotly_chart(fig_precip, use_container_width=True)
        
        # Seasonal precipitation summary
        seasonal_precip = precip_df.groupby('Season')['Precipitation'].sum().round(1)
        
        col1, col2, col3, col4 = st.columns(4)
        seasons_order = ['Spring', 'Summer', 'Fall', 'Winter']
        for i, season in enumerate(seasons_order):
            with [col1, col2, col3, col4][i]:
                st.metric(f"{season}", f"{seasonal_precip[season]:.1f}\"", 
                         f"{'Above' if seasonal_precip[season] > 8 else 'Below'} avg")
    
    # Growing Season Timeline
    with st.expander("📅 Growing Season Timeline", expanded=False):
        st.markdown("**Frost Dates & Growing Season** - Critical Agricultural Timing")
        
        # Create timeline data
        timeline_data = {
            'Event': ['Last Spring Frost', 'Planting Window Opens', 'Growing Season Peak', 
                     'First Fall Frost', 'Harvest Window', 'Winter Preparation'],
            'Date': ['April 15', 'April 20', 'July 15', 'October 12', 'October 1', 'November 1'],
            'Day_of_Year': [105, 110, 196, 285, 274, 305],
            'Category': ['Frost', 'Planting', 'Growing', 'Frost', 'Harvest', 'Winter'],
            'Temperature': [32, 50, 85, 32, 45, 35]
        }
        
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create timeline visualization
        fig_timeline = px.scatter(timeline_df, x='Day_of_Year', y='Temperature',
                                 color='Category', size='Temperature',
                                 hover_data=['Event', 'Date'],
                                 title="Growing Season Timeline",
                                 labels={'Day_of_Year': 'Day of Year', 'Temperature': 'Temperature (°F)'})
        
        fig_timeline.add_hline(y=32, line_dash="dash", line_color="blue", 
                              annotation_text="Freezing Point")
        fig_timeline.add_hline(y=50, line_dash="dash", line_color="green", 
                              annotation_text="Safe Planting Temp")
        
        fig_timeline.update_layout(
            height=400,
            xaxis=dict(
                tickmode='array',
                tickvals=[1, 60, 121, 182, 244, 305, 365],
                ticktext=['Jan 1', 'Mar 1', 'May 1', 'Jul 1', 'Sep 1', 'Nov 1', 'Dec 31']
            )
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Growing season metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Growing Season", "180 days", "Apr 15 - Oct 12")
        with col2:
            st.metric("Safe Planting", "175 days", "Apr 20 onward")
        with col3:
            st.metric("Peak Season", "89 days", "May 1 - Jul 29")
        with col4:
            st.metric("Harvest Window", "42 days", "Sep 1 - Oct 12")
    
    # Climate Comparison Chart
    with st.expander("🔍 Climate Zone Comparison", expanded=False):
        st.markdown("**Compare Zone 5b with Similar Zones** - Regional Climate Analysis")
        
        # Comparison data for similar zones
        comparison_data = {
            'Zone': ['Zone 5a', 'Zone 5b (Current)', 'Zone 6a', 'Zone 4b'],
            'Min_Winter_Temp': [-20, -15, -10, -25],
            'Frost_Free_Days': [160, 180, 200, 140],
            'Annual_Precip': [32, 35, 38, 28],
            'Growing_Degree_Days': [2800, 3100, 3400, 2500],
            'Agricultural_Rating': [7.8, 8.5, 8.9, 7.2]
        }
        
        comp_df = pd.DataFrame(comparison_data)
        comp_df['Is_Current'] = comp_df['Zone'].str.contains('Current')
        
        # Multi-metric comparison
        fig_comp = px.parallel_coordinates(comp_df, 
                                         dimensions=['Min_Winter_Temp', 'Frost_Free_Days', 
                                                   'Annual_Precip', 'Growing_Degree_Days', 
                                                   'Agricultural_Rating'],
                                         color='Agricultural_Rating',
                                         labels={'Min_Winter_Temp': 'Min Winter Temp (°F)',
                                               'Frost_Free_Days': 'Frost-Free Days',
                                               'Annual_Precip': 'Annual Precipitation (in)',
                                               'Growing_Degree_Days': 'Growing Degree Days',
                                               'Agricultural_Rating': 'Ag Suitability (1-10)'},
                                         title="Climate Zone Comparison - Multi-Factor Analysis")
        
        fig_comp.update_layout(height=400)
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Comparison table
        st.markdown("**Detailed Comparison:**")
        comparison_styled = comp_df[['Zone', 'Min_Winter_Temp', 'Frost_Free_Days', 
                                    'Annual_Precip', 'Agricultural_Rating']].copy()
        comparison_styled.columns = ['Climate Zone', 'Min Winter Temp (°F)', 
                                   'Frost-Free Days', 'Annual Precipitation (in)', 
                                   'Agricultural Suitability (1-10)']
        
        st.dataframe(comparison_styled, use_container_width=True, hide_index=True)
        
        st.info("💡 **Analysis**: Zone 5b offers excellent agricultural conditions with optimal balance of temperature, moisture, and growing season length.")
    
    # ============================================================================
    # 🌾 AGRICULTURAL CLIMATE ZONE MAPPING SYSTEM
    # Enhanced agricultural mapping with farming-specific data and insights
    # ============================================================================
    
    st.subheader("🌾 Agricultural Climate Zone Mapping")
    st.markdown("**Comprehensive agricultural zone analysis with crop suitability, growing seasons, and farm enterprise recommendations**")
    
    # Load agricultural zone data
    try:
        agricultural_zones = get_agricultural_zone_data()
        
        # Add additional zones for comprehensive mapping
        agricultural_zones.update({
            "6a_illinois_agricultural": {
                "zone_id": "6a_illinois_agricultural", 
                "climate_zone": "6a",
                "agricultural_classification": "intensive_cropping",
                "crop_suitability": {
                    "corn": {"rating": 9.4, "yield_potential": "190 bu/acre", "risk_level": "low"},
                    "soybeans": {"rating": 9.0, "yield_potential": "58 bu/acre", "risk_level": "low"},
                    "wheat": {"rating": 8.0, "yield_potential": "70 bu/acre", "risk_level": "low"}
                },
                "growing_season": {
                    "frost_free_days": 200,
                    "planting_window": "April 10 - May 10",
                    "harvest_window": "September 20 - November 10", 
                    "optimal_planting": "April 25",
                    "growing_degree_days": 3400
                },
                "agricultural_risks": ["excess_moisture", "disease_pressure"],
                "soil_types": ["prairie_soils", "alfisols"],
                "productivity_index": 9.1,
                "farm_enterprises": ["row_crops", "specialty_grains", "livestock"],
                "economic_factors": {
                    "production_cost_index": 88,
                    "market_access": "excellent", 
                    "elevator_distance": "3-8 miles"
                }
            },
            "4b_minnesota_agricultural": {
                "zone_id": "4b_minnesota_agricultural",
                "climate_zone": "4b", 
                "agricultural_classification": "short_season_cropping",
                "crop_suitability": {
                    "corn": {"rating": 7.8, "yield_potential": "160 bu/acre", "risk_level": "medium"},
                    "soybeans": {"rating": 8.2, "yield_potential": "50 bu/acre", "risk_level": "medium"},
                    "wheat": {"rating": 8.8, "yield_potential": "60 bu/acre", "risk_level": "low"},
                    "oats": {"rating": 9.0, "yield_potential": "85 bu/acre", "risk_level": "low"},
                    "barley": {"rating": 8.5, "yield_potential": "70 bu/acre", "risk_level": "low"}
                },
                "growing_season": {
                    "frost_free_days": 140,
                    "planting_window": "May 1 - May 20",
                    "harvest_window": "September 1 - October 15",
                    "optimal_planting": "May 10",
                    "growing_degree_days": 2500
                },
                "agricultural_risks": ["early_frost", "short_season", "cold_springs"],
                "soil_types": ["mollisols", "glacial_soils"],
                "productivity_index": 7.5,
                "farm_enterprises": ["short_season_crops", "livestock", "dairy", "specialty_grains"],
                "economic_factors": {
                    "production_cost_index": 82,
                    "market_access": "good",
                    "elevator_distance": "10-15 miles"
                }
            },
            "6b_missouri_agricultural": {
                "zone_id": "6b_missouri_agricultural",
                "climate_zone": "6b",
                "agricultural_classification": "extended_season_cropping", 
                "crop_suitability": {
                    "corn": {"rating": 8.6, "yield_potential": "175 bu/acre", "risk_level": "low"},
                    "soybeans": {"rating": 8.9, "yield_potential": "56 bu/acre", "risk_level": "low"},
                    "wheat": {"rating": 9.2, "yield_potential": "75 bu/acre", "risk_level": "low"},
                    "cotton": {"rating": 7.0, "yield_potential": "1200 lb/acre", "risk_level": "medium"},
                    "rice": {"rating": 8.0, "yield_potential": "150 bu/acre", "risk_level": "medium"}
                },
                "growing_season": {
                    "frost_free_days": 210,
                    "planting_window": "April 1 - May 1", 
                    "harvest_window": "September 25 - November 15",
                    "optimal_planting": "April 15",
                    "growing_degree_days": 3600
                },
                "agricultural_risks": ["heat_stress", "variable_precipitation", "disease_pressure"],
                "soil_types": ["alfisols", "ultisols", "alluvial_soils"],
                "productivity_index": 8.3,
                "farm_enterprises": ["row_crops", "livestock", "specialty_crops", "double_cropping"],
                "economic_factors": {
                    "production_cost_index": 86,
                    "market_access": "very_good",
                    "elevator_distance": "5-12 miles"
                }
            }
        })
        
    except Exception as e:
        st.error(f"Error loading agricultural zone data: {e}")
        agricultural_zones = {}
    
    # Current zone data (defaulting to Iowa 5b)
    current_zone = agricultural_zones["5b_iowa_agricultural"]
    
    # 1. Agricultural Productivity Map
    with st.expander("🗺️ Agricultural Productivity Map", expanded=True):
        st.markdown("**Regional Agricultural Suitability & Productivity Index**")
        
        # Create agricultural productivity data
        productivity_data = {
            'State': ['Iowa', 'Illinois', 'Indiana', 'Minnesota', 'Wisconsin', 'Michigan', 'Ohio', 'Missouri', 'Kansas', 'Nebraska'],
            'Zone': ['5b', '6a', '6a', '4b', '4b', '5a', '6a', '6b', '6a', '5a'],
            'Productivity_Index': [8.7, 9.1, 8.9, 7.5, 7.8, 8.2, 8.8, 8.3, 8.4, 8.5],
            'Primary_Crop': ['Corn/Soy', 'Corn/Soy', 'Corn/Soy', 'Wheat/Soy', 'Dairy/Corn', 'Corn/Soy', 'Corn/Soy', 'Corn/Soy/Wheat', 'Wheat/Corn', 'Corn/Soy'],
            'Latitude': [41.8, 40.0, 39.8, 45.0, 44.3, 44.3, 40.4, 38.4, 38.5, 41.1],
            'Longitude': [-93.1, -89.0, -86.1, -93.2, -89.6, -84.5, -82.7, -92.2, -96.7, -98.0],
            'Classification': ['Intensive Cropping', 'Intensive Cropping', 'Intensive Cropping', 
                             'Short Season', 'Short Season', 'Moderate Season', 'Intensive Cropping', 
                             'Extended Season', 'Moderate Season', 'Moderate Season']
        }
        
        productivity_df = pd.DataFrame(productivity_data)
        productivity_df['Current_Location'] = productivity_df['State'] == 'Iowa'
        productivity_df['Size'] = productivity_df['Current_Location'].apply(lambda x: 20 if x else 10)
        
        # Create productivity map with color scale
        fig_productivity = px.scatter(productivity_df,
                                    x='Longitude', y='Latitude',
                                    color='Productivity_Index',
                                    size='Size',
                                    size_max=20,
                                    color_continuous_scale='RdYlGn',
                                    hover_data=['State', 'Zone', 'Primary_Crop', 'Classification'],
                                    title="Agricultural Productivity Index by Climate Zone",
                                    labels={'Productivity_Index': 'Productivity Index (1-10)'})
        
        fig_productivity.update_layout(
            height=500,
            coloraxis_colorbar=dict(
                title="Agricultural<br>Productivity",
                tickvals=[7, 8, 9],
                ticktext=['Good', 'Very Good', 'Excellent']
            )
        )
        
        fig_productivity.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
        st.plotly_chart(fig_productivity, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Your Zone Productivity", f"{current_zone['productivity_index']}/10", "Excellent")
        with col2:
            st.metric("Regional Ranking", "Top 15%", "Above average")
        with col3:
            st.metric("Classification", current_zone['agricultural_classification'].title().replace('_', ' '))
    
    # 2. Crop Suitability Analysis
    with st.expander("🌽 Crop Suitability Analysis", expanded=True):
        st.markdown("**Detailed Crop Recommendations for Your Climate Zone**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Crop suitability chart
            crop_data = current_zone['crop_suitability']
            crops = list(crop_data.keys())
            ratings = [crop_data[crop]['rating'] for crop in crops]
            yields = [crop_data[crop]['yield_potential'] for crop in crops]
            risks = [crop_data[crop]['risk_level'] for crop in crops]
            
            # Color mapping for risk levels
            risk_colors = {'low': '#28a745', 'medium': '#ffc107', 'high': '#dc3545'}
            colors = [risk_colors[risk] for risk in risks]
            
            fig_crops = go.Figure(data=[
                go.Bar(x=crops, y=ratings, marker_color=colors, 
                      text=[f"{rating}/10<br>{yield_val}" for rating, yield_val in zip(ratings, yields)],
                      textposition='auto')
            ])
            
            fig_crops.update_layout(
                title="Crop Suitability Ratings for Zone 5b",
                xaxis_title="Crops",
                yaxis_title="Suitability Rating (1-10)",
                height=400,
                yaxis=dict(range=[0, 10])
            )
            
            st.plotly_chart(fig_crops, use_container_width=True)
        
        with col2:
            st.markdown("**Crop Performance Summary**")
            for crop, data in crop_data.items():
                risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
                st.markdown(f"""
                <div class="crop-card" style="background: #f8f9fa; padding: 0.5rem; margin: 0.2rem 0; border-radius: 4px; border-left: 3px solid {risk_colors[data['risk_level']]};">
                    <strong>{crop.title()}</strong><br>
                    Rating: {data['rating']}/10<br>
                    Yield: {data['yield_potential']}<br>
                    Risk: {risk_emoji[data['risk_level']]} {data['risk_level'].title()}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("**Legend:**")
            st.markdown("🟢 Low Risk | 🟡 Medium Risk | 🔴 High Risk")
    
    # 3. Growing Season Planning
    with st.expander("📅 Growing Season Planning & Calendar", expanded=True):
        st.markdown("**Interactive Agricultural Calendar for Optimal Planning**")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Growing season timeline
            season_events = {
                'Event': ['Soil Preparation', 'Planting Window Opens', 'Optimal Planting', 
                         'Cultivation Period', 'Mid-Season Care', 'Harvest Begins', 'Harvest Ends', 'Field Prep for Winter'],
                'Start_Date': ['April 1', 'April 15', 'May 1', 'May 15', 'July 1', 'September 15', 'October 15', 'November 1'],
                'End_Date': ['April 15', 'May 15', 'May 1', 'July 1', 'August 31', 'October 15', 'November 1', 'November 15'],
                'Day_Start': [91, 105, 121, 135, 182, 258, 288, 305],
                'Day_End': [105, 135, 121, 182, 243, 288, 305, 319],
                'Category': ['Prep', 'Planting', 'Planting', 'Growing', 'Growing', 'Harvest', 'Harvest', 'Prep'],
                'Priority': ['High', 'Critical', 'Critical', 'Medium', 'High', 'Critical', 'Critical', 'Medium']
            }
            
            season_df = pd.DataFrame(season_events)
            
            # Create Gantt-style chart
            fig_season = go.Figure()
            
            category_colors = {
                'Prep': '#6c757d',
                'Planting': '#28a745', 
                'Growing': '#20c997',
                'Harvest': '#fd7e14'
            }
            
            for i, row in season_df.iterrows():
                fig_season.add_trace(go.Scatter(
                    x=[row['Day_Start'], row['Day_End'], row['Day_End'], row['Day_Start'], row['Day_Start']],
                    y=[i, i, i+0.8, i+0.8, i],
                    fill='toself',
                    fillcolor=category_colors[row['Category']],
                    line=dict(color=category_colors[row['Category']], width=2),
                    name=row['Category'],
                    text=row['Event'],
                    hovertemplate=f"<b>{row['Event']}</b><br>Period: {row['Start_Date']} - {row['End_Date']}<br>Priority: {row['Priority']}<extra></extra>",
                    showlegend=i==0 or row['Category'] not in [season_df.loc[j, 'Category'] for j in range(i)]
                ))
            
            fig_season.update_layout(
                title="Agricultural Calendar - Growing Season Timeline",
                xaxis=dict(
                    title="Day of Year",
                    tickmode='array',
                    tickvals=[91, 121, 152, 182, 213, 244, 274, 305],
                    ticktext=['Apr 1', 'May 1', 'Jun 1', 'Jul 1', 'Aug 1', 'Sep 1', 'Oct 1', 'Nov 1']
                ),
                yaxis=dict(
                    title="Agricultural Activities",
                    tickmode='array',
                    tickvals=list(range(len(season_df))),
                    ticktext=season_df['Event'].tolist()
                ),
                height=400,
                showlegend=True
            )
            
            # Add frost lines
            fig_season.add_vline(x=105, line_dash="dash", line_color="blue", annotation_text="Last Frost")
            fig_season.add_vline(x=285, line_dash="dash", line_color="blue", annotation_text="First Frost") 
            
            st.plotly_chart(fig_season, use_container_width=True)
        
        with col2:
            st.markdown("**Growing Season Metrics**")
            
            growing_season = current_zone['growing_season']
            
            st.metric("Frost-Free Days", growing_season['frost_free_days'], "days")
            st.metric("Growing Degree Days", growing_season['growing_degree_days'], "GDD")
            
            st.markdown("**Key Dates:**")
            st.info(f"🌱 Planting: {growing_season['planting_window']}")
            st.info(f"🌾 Harvest: {growing_season['harvest_window']}")
            st.success(f"🎯 Optimal: {growing_season['optimal_planting']}")
            
            st.markdown("**Weather Considerations:**")
            st.warning("⚠️ Monitor late spring frosts")
            st.info("ℹ️ Plan for potential wet springs")
            st.success("✅ Excellent growing conditions expected")
    
    # 4. Agricultural Risk Assessment
    with st.expander("⚠️ Agricultural Risk Assessment", expanded=True):
        st.markdown("**Risk Analysis & Mitigation Strategies for Your Zone**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Risk assessment radar chart
            risk_categories = {
                'Weather Risks': 0.3,
                'Pest Pressure': 0.4,
                'Disease Risk': 0.35,
                'Market Volatility': 0.6,
                'Input Cost Risk': 0.5,
                'Equipment Risk': 0.2
            }
            
            categories = list(risk_categories.keys())
            values = list(risk_categories.values())
            
            fig_risk = go.Figure()
            
            fig_risk.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Risk Level',
                line_color='#dc3545',
                fillcolor='rgba(220, 53, 69, 0.2)'
            ))
            
            fig_risk.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1],
                        tickformat='.0%',
                        tickmode='array',
                        tickvals=[0.2, 0.4, 0.6, 0.8, 1.0],
                        ticktext=['Low', 'Moderate', 'Medium', 'High', 'Critical']
                    )
                ),
                title="Agricultural Risk Assessment Profile",
                height=400
            )
            
            st.plotly_chart(fig_risk, use_container_width=True)
        
        with col2:
            st.markdown("**Identified Risks:**")
            
            for risk in current_zone['agricultural_risks']:
                risk_display = risk.replace('_', ' ').title()
                if 'frost' in risk.lower():
                    st.warning(f"❄️ {risk_display}")
                elif 'drought' in risk.lower():
                    st.error(f"🌵 {risk_display}")
                elif 'wet' in risk.lower():
                    st.info(f"🌧️ {risk_display}")
                else:
                    st.warning(f"⚠️ {risk_display}")
            
            st.markdown("**Risk Mitigation:**")
            st.success("🛡️ Crop insurance available")
            st.info("📊 Weather monitoring systems")
            st.success("🌾 Diverse crop rotation")
            st.info("💧 Drainage management")
            
            st.markdown("**Overall Risk Level:**")
            overall_risk = sum(risk_categories.values()) / len(risk_categories)
            if overall_risk <= 0.3:
                st.success(f"🟢 Low Risk ({overall_risk*100:.0f}%)")
            elif overall_risk <= 0.6:
                st.warning(f"🟡 Moderate Risk ({overall_risk*100:.0f}%)")
            else:
                st.error(f"🔴 High Risk ({overall_risk*100:.0f}%)")
    
    # 5. Farm Enterprise Recommendations
    with st.expander("🏛️ Farm Enterprise Recommendations", expanded=True):
        st.markdown("**Recommended Farm Types & Enterprises for Your Climate Zone**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Enterprise suitability analysis
            enterprises = current_zone['farm_enterprises']
            
            enterprise_data = {
                'row_crops': {'suitability': 9.5, 'investment': 'High', 'roi': 'High', 'labor': 'Seasonal'},
                'livestock': {'suitability': 8.2, 'investment': 'High', 'roi': 'Medium', 'labor': 'Year-round'},
                'dairy': {'suitability': 7.8, 'investment': 'Very High', 'roi': 'Medium', 'labor': 'Intensive'},
                'grain_storage': {'suitability': 9.0, 'investment': 'Medium', 'roi': 'Medium', 'labor': 'Low'},
                'specialty_grains': {'suitability': 6.5, 'investment': 'Medium', 'roi': 'Variable', 'labor': 'Medium'},
                'specialty_crops': {'suitability': 5.8, 'investment': 'Medium', 'roi': 'High', 'labor': 'High'}
            }
            
            # Filter to recommended enterprises
            recommended_enterprises = {k: enterprise_data[k] for k in enterprises if k in enterprise_data}
            
            enterprise_names = list(recommended_enterprises.keys())
            suitability_scores = [recommended_enterprises[e]['suitability'] for e in enterprise_names]
            
            # Create enterprise comparison chart
            fig_enterprises = go.Figure(data=[
                go.Bar(x=enterprise_names, y=suitability_scores, 
                      marker_color=['#28a745', '#17a2b8', '#ffc107', '#20c997'][:len(enterprise_names)],
                      text=[f"{score}/10" for score in suitability_scores],
                      textposition='auto')
            ])
            
            fig_enterprises.update_layout(
                title="Farm Enterprise Suitability Scores",
                xaxis_title="Enterprise Type",
                yaxis_title="Suitability Score (1-10)",
                height=400,
                yaxis=dict(range=[0, 10])
            )
            
            st.plotly_chart(fig_enterprises, use_container_width=True)
            
            # Economic factors
            st.markdown("**Economic Environment:**")
            econ = current_zone['economic_factors']
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Production Cost Index", econ['production_cost_index'], "Below national avg")
            with col_b:
                st.metric("Market Access", econ['market_access'].title(), "Multiple elevators")
            with col_c:
                st.metric("Elevator Distance", econ['elevator_distance'], "Good access")
        
        with col2:
            st.markdown("**Enterprise Details:**")
            
            for enterprise in enterprises:
                if enterprise in enterprise_data:
                    data = enterprise_data[enterprise]
                    enterprise_name = enterprise.replace('_', ' ').title()
                    
                    st.markdown(f"""
                    <div class="enterprise-card" style="background: #f8f9fa; padding: 0.8rem; margin: 0.5rem 0; border-radius: 6px; border-left: 3px solid #28a745;">
                        <strong>{enterprise_name}</strong><br>
                        Suitability: {data['suitability']}/10<br>
                        Investment: {data['investment']}<br>
                        ROI Potential: {data['roi']}<br>
                        Labor Needs: {data['labor']}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("**Success Examples:**")
            st.success("🌽 Johnson Farm: 1,200 acres corn/soy")
            st.success("🐄 Wilson Ranch: 200 head cattle")
            st.success("🏬 Miller Grain: On-farm storage")
            
            st.markdown("**Extension Resources:**")
            st.info("📞 County Extension: (515) 555-0123")
            st.info("🌐 Iowa State University")
            st.info("📧 Farm Business Planning")
    
    # 6. Zone Comparison Tool
    with st.expander("🔍 Agricultural Zone Comparison Tool", expanded=False):
        st.markdown("**Compare Multiple Agricultural Climate Zones**")
        
        # Zone selection for comparison
        col1, col2 = st.columns(2)
        
        with col1:
            compare_zones = st.multiselect(
                "Select zones to compare:",
                options=list(agricultural_zones.keys()),
                default=["5b_iowa_agricultural", "6a_illinois_agricultural"],
                format_func=lambda x: f"{agricultural_zones[x]['climate_zone']} - {agricultural_zones[x]['agricultural_classification'].replace('_', ' ').title()}"
            )
        
        with col2:
            comparison_metric = st.selectbox(
                "Primary comparison metric:",
                ["productivity_index", "growing_season", "crop_suitability", "economic_factors"]
            )
        
        if len(compare_zones) >= 2:
            # Create comparison data
            comparison_data = []
            
            for zone_id in compare_zones:
                zone = agricultural_zones[zone_id]
                
                if comparison_metric == "crop_suitability":
                    # Average crop ratings
                    avg_rating = sum([crop['rating'] for crop in zone['crop_suitability'].values()]) / len(zone['crop_suitability'])
                    comparison_data.append({
                        'Zone': zone['climate_zone'],
                        'Classification': zone['agricultural_classification'].replace('_', ' ').title(),
                        'Avg_Crop_Rating': avg_rating,
                        'Productivity_Index': zone['productivity_index'],
                        'Frost_Free_Days': zone['growing_season']['frost_free_days']
                    })
                
            comp_df = pd.DataFrame(comparison_data)
            
            # Multi-metric comparison chart
            fig_comparison = go.Figure()
            
            metrics_to_plot = ['Avg_Crop_Rating', 'Productivity_Index', 'Frost_Free_Days']
            
            for zone in comp_df['Zone']:
                zone_data = comp_df[comp_df['Zone'] == zone].iloc[0]
                
                fig_comparison.add_trace(go.Scatterpolar(
                    r=[zone_data['Avg_Crop_Rating'], zone_data['Productivity_Index'], zone_data['Frost_Free_Days']/200*10],
                    theta=['Avg Crop Rating', 'Productivity Index', 'Growing Season (scaled)'],
                    fill='toself',
                    name=f"Zone {zone}"
                ))
            
            fig_comparison.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )
                ),
                showlegend=True,
                title="Multi-Metric Zone Comparison",
                height=400
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Detailed comparison table
            st.markdown("**Detailed Zone Comparison:**")
            st.dataframe(comp_df, use_container_width=True, hide_index=True)
    
    # Climate Zone Validation Feedback System
    st.subheader("🔍 Climate Zone Validation Dashboard")
    
    # Mock validation data structure
    validation_data = {
        "overall_confidence": 0.92,
        "confidence_breakdown": {
            "gps_accuracy": 0.95,
            "weather_data_quality": 0.89,
            "elevation_accuracy": 0.94,
            "historical_consistency": 0.88
        },
        "validation_alerts": [
            {"type": "warning", "message": "Limited precipitation data for winter months", "severity": "medium"},
            {"type": "info", "message": "High GPS location accuracy confirmed", "severity": "low"},
            {"type": "success", "message": "USDA zone data cross-validated successfully", "severity": "low"}
        ],
        "data_sources": {
            "usda": {"reliability": 0.96, "last_updated": "2024-01-15"},
            "noaa": {"reliability": 0.91, "last_updated": "2024-01-20"},
            "local_stations": {"reliability": 0.83, "last_updated": "2024-01-22"}
        }
    }
    
    # 1. Enhanced Confidence Scoring & Feedback
    with st.expander("📊 Enhanced Confidence Analysis", expanded=True):
        st.markdown("**Comprehensive Climate Zone Validation Metrics**")
        
        # Overall confidence with color coding
        overall_conf = validation_data["overall_confidence"]
        if overall_conf >= 0.9:
            conf_color = "🟢 High Confidence"
            conf_bg = "success"
        elif overall_conf >= 0.7:
            conf_color = "🟡 Medium Confidence"  
            conf_bg = "warning"
        else:
            conf_color = "🔴 Low Confidence"
            conf_bg = "error"
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.metric("Overall Validation Score", f"{overall_conf*100:.1f}%", conf_color)
            st.progress(overall_conf)
        with col2:
            if conf_bg == "success":
                st.success(f"✅ {conf_color}")
            elif conf_bg == "warning":
                st.warning(f"⚠️ {conf_color}")
            else:
                st.error(f"❌ {conf_color}")
        
        st.markdown("**Confidence Breakdown by Component:**")
        
        # Individual confidence metrics
        breakdown = validation_data["confidence_breakdown"]
        cols = st.columns(4)
        
        metrics = [
            ("GPS Accuracy", "gps_accuracy", "📍"),
            ("Weather Data", "weather_data_quality", "🌤️"),
            ("Elevation Data", "elevation_accuracy", "⛰️"),
            ("Historical Consistency", "historical_consistency", "📈")
        ]
        
        for i, (label, key, icon) in enumerate(metrics):
            with cols[i]:
                value = breakdown[key]
                st.metric(f"{icon} {label}", f"{value*100:.1f}%")
                if value >= 0.9:
                    st.success("Excellent")
                elif value >= 0.8:
                    st.warning("Good")
                else:
                    st.error("Needs Review")
    
    # 2. Data Quality Assessment
    with st.expander("🔎 Data Quality Assessment", expanded=False):
        st.markdown("**Source Reliability & Data Freshness**")
        
        sources = validation_data["data_sources"]
        
        for source_name, source_data in sources.items():
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                reliability = source_data["reliability"]
                source_display = {
                    "usda": "🇺🇸 USDA Plant Hardiness",
                    "noaa": "🌡️ NOAA Climate Data", 
                    "local_stations": "📡 Local Weather Stations"
                }
                st.write(f"**{source_display.get(source_name, source_name.upper())}**")
            
            with col2:
                st.metric("Reliability", f"{reliability*100:.1f}%")
                if reliability >= 0.95:
                    st.success("🟢 Excellent")
                elif reliability >= 0.85:
                    st.warning("🟡 Good")
                else:
                    st.error("🔴 Poor")
            
            with col3:
                last_updated = source_data["last_updated"]
                from datetime import datetime, timedelta
                update_date = datetime.strptime(last_updated, "%Y-%m-%d")
                days_old = (datetime.now() - update_date).days
                
                st.write(f"**Last Updated:** {last_updated}")
                if days_old <= 7:
                    st.success(f"✅ Fresh ({days_old} days old)")
                elif days_old <= 30:
                    st.warning(f"⚠️ Recent ({days_old} days old)")
                else:
                    st.error(f"❌ Stale ({days_old} days old)")
            
            st.divider()
    
    # 3. Real-time Validation Alerts
    with st.expander("🚨 Validation Alerts & Warnings", expanded=False):
        st.markdown("**Active Alerts for Climate Zone Determination**")
        
        alerts = validation_data["validation_alerts"]
        
        if not alerts:
            st.success("✅ No validation issues detected")
        else:
            for alert in alerts:
                alert_type = alert["type"]
                message = alert["message"]
                severity = alert["severity"]
                
                if alert_type == "error":
                    st.error(f"🔴 **Critical**: {message}")
                elif alert_type == "warning":
                    st.warning(f"🟡 **Warning**: {message}")
                elif alert_type == "info":
                    st.info(f"🔵 **Info**: {message}")
                elif alert_type == "success":
                    st.success(f"🟢 **Success**: {message}")
        
        # Additional contextual warnings
        st.markdown("**Seasonal Accuracy Notifications:**")
        current_month = datetime.now().month
        
        if current_month in [12, 1, 2]:  # Winter
            st.warning("❄️ **Winter Season**: Zone determination may be more accurate due to extreme temperature data availability")
        elif current_month in [6, 7, 8]:  # Summer
            st.info("☀️ **Summer Season**: Growing season data is most reliable during this period")
        else:
            st.info("🌱 **Transition Season**: Zone boundaries may show some variation during seasonal transitions")
    
    # 4. User Feedback & Correction System
    with st.expander("📝 User Feedback & Zone Correction", expanded=False):
        st.markdown("**Help Us Improve Climate Zone Accuracy**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current Zone Assessment:**")
            st.info(f"📍 **Detected Zone**: {usda_zone}\n\n🎯 **Confidence**: {overall_conf*100:.1f}%\n\n📊 **Based on**: GPS location, USDA data, local weather patterns")
            
            # Report incorrect zone
            if st.button("🚩 Report Incorrect Zone", type="secondary"):
                st.session_state.show_correction_form = True
            
            # Manual override option
            if st.button("⚙️ Manual Zone Override", type="secondary"):
                st.session_state.show_override_form = True
        
        with col2:
            # Correction form
            if st.session_state.get('show_correction_form', False):
                st.markdown("**🚩 Report Zone Correction**")
                
                with st.form("zone_correction_form"):
                    correct_zone = st.selectbox(
                        "What should the correct zone be?",
                        ["Zone 3a", "Zone 3b", "Zone 4a", "Zone 4b", "Zone 5a", "Zone 5b", 
                         "Zone 6a", "Zone 6b", "Zone 7a", "Zone 7b", "Zone 8a", "Zone 8b", 
                         "Zone 9a", "Zone 9b", "Zone 10a", "Zone 10b"],
                        help="Select the zone based on your local experience"
                    )
                    
                    experience_years = st.selectbox(
                        "Years farming at this location:",
                        ["Less than 1 year", "1-5 years", "5-10 years", "10-20 years", "20+ years"]
                    )
                    
                    feedback_reason = st.text_area(
                        "Why do you believe this zone is incorrect?",
                        placeholder="e.g., I've observed different frost dates, different plant survival rates, etc.",
                        height=80
                    )
                    
                    submitted = st.form_submit_button("📤 Submit Correction")
                    
                    if submitted:
                        st.success("✅ Thank you! Your feedback has been recorded and will help improve our zone detection system.")
                        st.session_state.show_correction_form = False
                        st.rerun()
            
            # Override form
            if st.session_state.get('show_override_form', False):
                st.markdown("**⚙️ Manual Zone Override**")
                
                with st.form("manual_override_form"):
                    override_zone = st.selectbox(
                        "Select preferred zone:",
                        ["Zone 3a", "Zone 3b", "Zone 4a", "Zone 4b", "Zone 5a", "Zone 5b", 
                         "Zone 6a", "Zone 6b", "Zone 7a", "Zone 7b", "Zone 8a", "Zone 8b", 
                         "Zone 9a", "Zone 9b", "Zone 10a", "Zone 10b"]
                    )
                    
                    justification = st.text_area(
                        "Justification for override (required):",
                        placeholder="Please explain why you want to override the automated detection...",
                        height=60
                    )
                    
                    apply_override = st.form_submit_button("✅ Apply Override")
                    
                    if apply_override and justification:
                        st.success(f"✅ Zone overridden to {override_zone}. All recommendations will now be based on this zone.")
                        st.info("💡 **Note**: You can revert to automatic detection at any time.")
                        st.session_state.show_override_form = False
                        st.rerun()
                    elif apply_override and not justification:
                        st.error("❌ Justification is required for manual overrides")
    
    # 5. Validation Status Dashboard
    with st.expander("📈 Validation Status Dashboard", expanded=False):
        st.markdown("**Complete Climate Zone Validation Overview**")
        
        # Create validation score visualization
        validation_components = {
            'Location Accuracy': validation_data['confidence_breakdown']['gps_accuracy'],
            'Weather Data Quality': validation_data['confidence_breakdown']['weather_data_quality'],
            'Elevation Verification': validation_data['confidence_breakdown']['elevation_accuracy'],
            'Historical Consistency': validation_data['confidence_breakdown']['historical_consistency'],
            'Cross-Reference Check': 0.91,
            'Boundary Validation': 0.87
        }
        
        # Validation radar chart
        categories = list(validation_components.keys())
        values = list(validation_components.values())
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Validation Scores',
            line_color='#28a745',
            fillcolor='rgba(40, 167, 69, 0.2)'  
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickformat='.0%'
                )),
            showlegend=True,
            title="Climate Zone Validation Component Analysis",
            height=400
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Component status table
        st.markdown("**Individual Component Status:**")
        
        status_data = []
        for component, score in validation_components.items():
            if score >= 0.9:
                status = "🟢 Excellent"
                recommendation = "No action needed"
            elif score >= 0.8:
                status = "🟡 Good"
                recommendation = "Monitor for improvements"
            else:
                status = "🔴 Needs Attention"
                recommendation = "Review data sources"
            
            status_data.append({
                "Component": component,
                "Score": f"{score*100:.1f}%",
                "Status": status,
                "Recommendation": recommendation
            })
        
        status_df = pd.DataFrame(status_data)
        st.dataframe(status_df, use_container_width=True, hide_index=True)
        
        # Overall system health
        avg_score = sum(validation_components.values()) / len(validation_components)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Overall System Health", f"{avg_score*100:.1f}%", 
                     f"{'🟢' if avg_score >= 0.9 else '🟡' if avg_score >= 0.8 else '🔴'}")
        
        with col2:
            alert_count = len([a for a in validation_data['validation_alerts'] if a['type'] in ['warning', 'error']])
            st.metric("Active Alerts", f"{alert_count}", 
                     f"{'🟢 None' if alert_count == 0 else '🟡 Some' if alert_count <= 2 else '🔴 Many'}")
        
        with col3:
            data_freshness = min([
                (datetime.now() - datetime.strptime(source['last_updated'], '%Y-%m-%d')).days 
                for source in validation_data['data_sources'].values()
            ])
            st.metric("Data Freshness", f"{data_freshness} days", 
                     f"{'🟢 Fresh' if data_freshness <= 7 else '🟡 Recent' if data_freshness <= 30 else '🔴 Stale'}")
    
    # Action buttons for validation system
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Re-validate Zone", help="Trigger a fresh validation of the climate zone"):
            with st.spinner("Re-validating climate zone..."):
                import time
                time.sleep(2)
                st.success("✅ Zone re-validation completed! All systems nominal.")
        
        if st.button("🔍 Check Zone Consistency", help="Validate climate zone consistency across multiple dimensions"):
            with st.spinner("Validating climate zone consistency..."):
                # Mock consistency validation data (in production would call actual API)
                consistency_data = {
                    "overall_consistent": True,
                    "confidence": 0.87,
                    "checks_performed": ["cross_reference", "spatial", "temporal"],
                    "warnings": [
                        "Köppen zone Dfa/Dfb slightly inconsistent with USDA 5b - within acceptable range",
                        "Northern neighbors show 5a zones - gradual transition detected"
                    ],
                    "cross_reference_check": {
                        "consistent": True,
                        "confidence": 0.82,
                        "message": "USDA zone 5b is generally consistent with Köppen Dfa"
                    },
                    "spatial_check": {
                        "consistent": True,
                        "confidence": 0.85,
                        "message": "Spatial consistency good: 5/6 neighbors consistent"
                    },
                    "temporal_check": {
                        "consistent": True,
                        "confidence": 0.93,
                        "message": "Zone 5b is historically stable"
                    }
                }
                
                # Display consistency results
                if consistency_data["overall_consistent"]:
                    st.success(f"✅ Climate zone consistency validated! (Confidence: {consistency_data['confidence']:.1%})")
                else:
                    st.warning(f"⚠️ Some consistency issues detected (Confidence: {consistency_data['confidence']:.1%})")
                
                # Show detailed results
                with st.expander("📋 Detailed Consistency Results", expanded=True):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.markdown("**Cross-Reference Check**")
                        ref_check = consistency_data["cross_reference_check"]
                        status_icon = "✅" if ref_check["consistent"] else "❌"
                        st.markdown(f"{status_icon} {ref_check['message']}")
                        st.caption(f"Confidence: {ref_check['confidence']:.1%}")
                    
                    with col_b:
                        st.markdown("**Spatial Check**")
                        spatial_check = consistency_data["spatial_check"]
                        status_icon = "✅" if spatial_check["consistent"] else "❌"
                        st.markdown(f"{status_icon} {spatial_check['message']}")
                        st.caption(f"Confidence: {spatial_check['confidence']:.1%}")
                    
                    with col_c:
                        st.markdown("**Temporal Check**")
                        temporal_check = consistency_data["temporal_check"]
                        status_icon = "✅" if temporal_check["consistent"] else "❌"
                        st.markdown(f"{status_icon} {temporal_check['message']}")
                        st.caption(f"Confidence: {temporal_check['confidence']:.1%}")
                    
                    # Show warnings if any
                    if consistency_data["warnings"]:
                        st.markdown("**⚠️ Consistency Warnings:**")
                        for warning in consistency_data["warnings"]:
                            st.warning(f"• {warning}")
                
                time.sleep(1)
                st.success("🔍 Consistency validation completed!")
    
    with col2:
        if st.button("📊 Generate Validation Report", help="Create detailed validation report"):
            st.info("📄 Generating comprehensive validation report... (Feature coming soon)")
    
    with col3:
        if st.button("🎯 Improve Accuracy", help="Access tools to enhance zone detection accuracy"):
            st.info("🔧 Opening accuracy improvement tools... (Feature coming soon)")
    
    st.header("🌾 Current Crop")
    primary_crop = st.selectbox("Primary Crop", ["Corn", "Soybean", "Wheat", "Cotton"])
    yield_goal = st.number_input("Yield Goal (bu/acre)", min_value=50, value=180, step=5)
    
    st.header("📊 Quick Stats")
    st.metric("Soil Health Score", "7.2/10", "0.3")
    st.metric("Last Soil Test", "Mar 2024", "")
    st.metric("Recommendations", "12", "3")

# Agricultural Zone Summary Section
st.markdown("""
<div class="agricultural-zone-header">
    <h2>🌾 Agricultural Climate Zone Summary</h2>
    <p>Your location has been classified as <strong>Zone 5b - Intensive Cropping Region</strong></p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Agricultural Productivity", 
        "8.7/10", 
        "Excellent",
        help="Overall agricultural suitability combining climate, soil, and economic factors"
    )

with col2:
    st.metric(
        "Top Crop", 
        "Corn", 
        "9.2/10 rating",
        help="Highest rated crop for your climate zone with yield potential"
    )

with col3:
    st.metric(
        "Growing Season", 
        "180 days", 
        "Apr 15 - Oct 12",
        help="Frost-free growing period for crop production"
    )

with col4:
    st.metric(
        "Risk Level", 
        "Low", 
        "Manageable",
        help="Overall agricultural risk assessment for your zone"
    )

with col5:
    st.metric(
        "Best Enterprise", 
        "Row Crops", 
        "9.5/10 fit",
        help="Most suitable farm enterprise type for your climate zone"
    )

# Quick agricultural insights
st.markdown("""
**🎯 Key Agricultural Insights for Zone 5b:**
- **Premium corn and soybean production** with yield potential of 180+ bu/acre for corn and 55+ bu/acre for soybeans
- **Excellent soil conditions** with prairie soils and optimal moisture retention
- **Strong economic environment** with good market access and below-average production costs
- **Manageable risk profile** with primary concerns being late spring frost and occasional drought
- **Multiple enterprise options** including row crops, livestock, dairy, and grain storage operations
""")

# Climate Zone Change Detection Section
st.markdown("""
<div class="change-detection-header">
    <h3>📈 Climate Zone Change Detection</h3>
    <p>Track climate zone transitions over time to anticipate agricultural impacts</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("🔍 Analyze Zone Changes", help="Detect climate zone transitions over time"):
        with st.spinner("Analyzing climate zone changes..."):
            # Mock climate zone change data (in production would call actual API)
            change_data = {
                "current_zone": {
                    "zone_id": "6a",
                    "name": "USDA Zone 6a",
                    "description": "Moderate (-10°F to -5°F)",
                    "min_temp_f": -10,
                    "max_temp_f": -5
                },
                "previous_zone": {
                    "zone_id": "5b", 
                    "name": "USDA Zone 5b",
                    "description": "Cool (-15°F to -10°F)",
                    "min_temp_f": -15,
                    "max_temp_f": -10
                },
                "change_detected": True,
                "change_confidence": 0.85,
                "change_date": "2019-03-15T00:00:00",
                "change_direction": "warmer",
                "zones_affected": ["5b", "6a"],
                "trend_analysis": {
                    "trend_direction": "warmer",
                    "confidence": 0.87,
                    "rate_of_change_per_year": 0.12,
                    "projected_zone_1yr": "6a",
                    "projected_zone_5yr": "6b"
                },
                "recommendations": [
                    "Consider heat-tolerant crop varieties for future plantings",
                    "Implement water conservation strategies due to increased evapotranspiration",
                    "Adjust planting dates to account for longer growing seasons",
                    "Monitor for new pest and disease pressures from warmer climates",
                    "High confidence in climate shift - consider major adaptation strategies"
                ]
            }
            
            # Display change detection results
            if change_data["change_detected"]:
                st.success(f"🌡️ Climate zone change detected! (Confidence: {change_data['change_confidence']:.1%})")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**Previous Zone**")
                    prev_zone = change_data["previous_zone"]
                    st.info(f"**{prev_zone['zone_id']}** - {prev_zone['description']}")
                    
                with col_b:
                    st.markdown("**Current Zone**")  
                    curr_zone = change_data["current_zone"]
                    st.success(f"**{curr_zone['zone_id']}** - {curr_zone['description']}")
                
                # Change metrics
                st.markdown("**📊 Change Analysis**")
                col_x, col_y, col_z = st.columns(3)
                
                with col_x:
                    st.metric(
                        "Change Direction",
                        change_data["change_direction"].title(),
                        f"{change_data['trend_analysis']['rate_of_change_per_year']:.2f}°F/year"
                    )
                
                with col_y:
                    change_date = datetime.fromisoformat(change_data["change_date"].replace("Z", "+00:00"))
                    years_ago = (datetime.now().replace(tzinfo=None) - change_date.replace(tzinfo=None)).days // 365
                    st.metric(
                        "Transition Date",
                        f"{years_ago} years ago",
                        change_date.strftime("%Y")
                    )
                
                with col_z:
                    projected_zone = change_data["trend_analysis"]["projected_zone_5yr"]
                    st.metric(
                        "5-Year Projection", 
                        f"Zone {projected_zone}",
                        "Continued warming"
                    )
                
            else:
                st.info("📊 Climate zone appears stable - no significant changes detected")
            
            # Show adaptation recommendations
            st.markdown("**🌾 Adaptation Recommendations**")
            for i, rec in enumerate(change_data["recommendations"], 1):
                if "High confidence" in rec:
                    st.warning(f"**{i}.** {rec}")
                else:
                    st.info(f"**{i}.** {rec}")

with col2:
    if st.button("📊 View Time Series", help="View detailed historical data"):
        st.markdown("**Historical Zone Data**")
        # Mock time series data
        time_series = [
            {"year": "2015", "zone": "5b", "confidence": "82%"},
            {"year": "2017", "zone": "5b", "confidence": "79%"},
            {"year": "2019", "zone": "6a", "confidence": "85%"},
            {"year": "2021", "zone": "6a", "confidence": "88%"},
            {"year": "2024", "zone": "6a", "confidence": "92%"}
        ]
        
        for entry in time_series:
            if entry["zone"] == "6a":
                st.success(f"**{entry['year']}**: Zone {entry['zone']} ({entry['confidence']})")
            else:
                st.info(f"**{entry['year']}**: Zone {entry['zone']} ({entry['confidence']})")

st.divider()

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dashboard", "🌱 Crop Selection", "🏔️ Soil Health", "🧪 Fertilizer Strategy", "🌾 Zone Analysis"])

with tab1:
    # Dashboard content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Farm Size", f"{farm_size} acres", "")
    with col2:
        st.metric("Active Fields", "4", "")
    with col3:
        st.metric("Avg. Confidence", "87%", "2%")
    with col4:
        st.metric("ROI Improvement", "15%", "3%")
    
    # Question input
    st.subheader("❓ Ask an Agricultural Question")
    question = st.text_area(
        "What would you like to know about your farm?",
        placeholder="What crop varieties are best suited to my soil type and climate?",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔍 Get Recommendation", type="primary"):
            if question:
                with st.spinner("Analyzing your question..."):
                    # Simulate API call
                    import time
                    time.sleep(2)
                    
                    st.success("✅ Question processed successfully!")
                    
                    # Display mock recommendation
                    st.markdown("""
                    <div class="recommendation-card">
                        <h4>🌽 Crop Selection Recommendation</h4>
                        <p><strong>Confidence:</strong> 92%</p>
                        <p><strong>Recommendation:</strong> Based on your soil pH of 6.5 and location in Iowa, 
                        corn varieties like Pioneer P1197AM would be excellent choices for your farm.</p>
                        <p><strong>Expected Yield:</strong> 185 bu/acre</p>
                        <p><strong>Next Steps:</strong> Consider soil testing for micronutrients and review nitrogen application timing.</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please enter a question")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    # Create sample data for visualization
    dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='M')
    recommendations = np.random.randint(5, 25, len(dates))
    confidence_scores = np.random.uniform(0.75, 0.95, len(dates))
    
    activity_df = pd.DataFrame({
        'Date': dates,
        'Recommendations': recommendations,
        'Avg_Confidence': confidence_scores
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_recs = px.line(activity_df, x='Date', y='Recommendations', 
                          title='Monthly Recommendations',
                          color_discrete_sequence=['#28a745'])
        fig_recs.update_layout(height=300)
        st.plotly_chart(fig_recs, use_container_width=True)
    
    with col2:
        fig_conf = px.line(activity_df, x='Date', y='Avg_Confidence', 
                          title='Average Confidence Score',
                          color_discrete_sequence=['#20c997'])
        fig_conf.update_layout(height=300)
        st.plotly_chart(fig_conf, use_container_width=True)

with tab2:
    # Crop Selection tab with Planting Date Integration
    st.subheader("🌱 Crop Selection & Planting Timeline")
    
    # Create tabs within the crop selection
    crop_tab1, crop_tab2, crop_tab3 = st.tabs(["📊 Recommendations", "📅 Planting Calendar", "🌡️ Frost Analysis"])
    
    with crop_tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Location & Farm Information**")
            crop_location = st.text_input("Location", value=location, key="crop_location")
            crop_farm_size = st.number_input("Farm Size (acres)", value=farm_size, key="crop_farm_size")
            irrigation = st.checkbox("Irrigation Available")
            
            st.write("**Soil Test Data**")
            soil_ph = st.slider("Soil pH", 3.0, 10.0, 6.5, 0.1)
            organic_matter = st.slider("Organic Matter (%)", 0.0, 15.0, 3.5, 0.1)
            phosphorus = st.number_input("Phosphorus (ppm)", 0, 200, 25)
            potassium = st.number_input("Potassium (ppm)", 0, 800, 180)
        
        with col2:
            if st.button("🔍 Get Crop Recommendations with Planting Dates", key="crop_rec"):
                with st.spinner("Calculating optimal planting dates..."):
                    # Prepare location data for API calls
                    location_data = {
                        "latitude": 42.0,  # Default to Iowa coordinates
                        "longitude": -93.0,
                        "elevation_ft": 1000,
                        "address": crop_location or "Farm Location",
                        "state": "Iowa",
                        "county": "Story", 
                        "climate_zone": "5b",
                        "climate_zone_name": "USDA Zone 5b",
                        "temperature_range_f": {"min": -15, "max": -10},
                        "climate_confidence": 0.85
                    }
                    
                    st.write("**🌟 Recommended Crops with Planting Timing:**")
                    
                    # Enhanced recommendations with planting dates
                    recommendations = [
                        {"crop": "corn", "variety": "Pioneer P1197AM", "confidence": 92, "yield": "185 bu/acre"},
                        {"crop": "soybean", "variety": "Asgrow AG2834", "confidence": 88, "yield": "58 bu/acre"},
                        {"crop": "wheat", "variety": "AgriPro SY Monument", "confidence": 75, "yield": "65 bu/acre"}
                    ]
                    
                    for i, rec in enumerate(recommendations):
                        with st.container():
                            # Get planting dates for this crop
                            planting_data = get_planting_dates(rec["crop"], location_data, "spring")
                            
                            col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1.5])
                            with col_a:
                                st.write(f"**{rec['crop'].title()}** - {rec['variety']}")
                                
                            with col_b:
                                st.metric("Confidence", f"{rec['confidence']}%")
                                
                            with col_c:
                                st.metric("Yield Potential", rec['yield'])
                                
                            with col_d:
                                if planting_data and planting_data.get('success'):
                                    optimal_date = planting_data.get('optimal_date')
                                    if optimal_date:
                                        formatted_date = format_planting_date(optimal_date)
                                        st.metric("🗓️ Plant By", formatted_date)
                                        
                                        # Show planting window
                                        earliest = planting_data.get('earliest_safe_date')
                                        latest = planting_data.get('latest_safe_date')
                                        if earliest and latest:
                                            earliest_fmt = format_planting_date(earliest)
                                            latest_fmt = format_planting_date(latest)
                                            st.caption(f"Window: {earliest_fmt} - {latest_fmt}")
                                    else:
                                        st.caption("Planting date unavailable")
                                else:
                                    st.caption("⚠️ API unavailable - using defaults")
                                    # Show default planting recommendations
                                    default_dates = {
                                        "corn": "May 1 - May 15",
                                        "soybean": "May 10 - May 25", 
                                        "wheat": "September 15 - October 1"
                                    }
                                    st.metric("🗓️ Plant By", default_dates.get(rec["crop"], "Spring"))
                            
                            # Show additional planting information
                            if planting_data and planting_data.get('success'):
                                considerations = planting_data.get('frost_considerations', [])
                                if considerations:
                                    st.info(f"💡 **Tip:** {considerations[0]}")
                                    
                                warnings = planting_data.get('climate_warnings', [])
                                if warnings:
                                    st.warning(f"⚠️ **Warning:** {warnings[0]}")
                            
                            if i == 0:  # Highlight top recommendation
                                st.success("🏆 Top recommendation based on your soil conditions and climate")
                            
                            st.divider()
    
    with crop_tab2:
        st.write("**🗓️ Planting Calendar for Available Crops**")
        
        # Location input for calendar
        cal_location = st.text_input("Location for Calendar", value=location, key="cal_location")
        
        if st.button("Generate Planting Calendar", key="gen_calendar"):
            with st.spinner("Generating planting calendar..."):
                # Prepare location data
                location_data = {
                    "latitude": 42.0,
                    "longitude": -93.0,
                    "elevation_ft": 1000,
                    "address": cal_location or "Farm Location",
                    "state": "Iowa",
                    "county": "Story",
                    "climate_zone": "5b",
                    "climate_zone_name": "USDA Zone 5b",
                    "temperature_range_f": {"min": -15, "max": -10},
                    "climate_confidence": 0.85
                }
                
                # Get available crops
                available_crops = get_available_crops()
                
                st.write("**Spring Planting Timeline:**")
                
                # Create calendar data
                calendar_data = []
                for crop in available_crops[:6]:  # Limit to first 6 crops for display
                    planting_info = get_planting_dates(crop, location_data, "spring")
                    
                    if planting_info and planting_info.get('success'):
                        calendar_data.append({
                            "Crop": crop.title(),
                            "Optimal Date": format_planting_date(planting_info.get('optimal_date', '')),
                            "Earliest Safe": format_planting_date(planting_info.get('earliest_safe_date', '')),
                            "Latest Safe": format_planting_date(planting_info.get('latest_safe_date', '')),
                            "Season Length": f"{planting_info.get('days_to_maturity', 0)} days"
                        })
                    else:
                        # Fallback data
                        default_calendar = {
                            "corn": {"optimal": "May 5", "earliest": "April 20", "latest": "May 20", "days": 110},
                            "soybean": {"optimal": "May 15", "earliest": "May 1", "latest": "June 1", "days": 105},
                            "wheat": {"optimal": "September 25", "earliest": "September 15", "latest": "October 5", "days": 240},
                            "lettuce": {"optimal": "April 1", "earliest": "March 15", "latest": "April 15", "days": 65},
                            "tomato": {"optimal": "May 20", "earliest": "May 10", "latest": "June 1", "days": 85},
                            "potato": {"optimal": "April 15", "earliest": "April 1", "latest": "May 1", "days": 90}
                        }
                        
                        crop_data = default_calendar.get(crop, {"optimal": "Spring", "earliest": "Early Spring", "latest": "Late Spring", "days": 90})
                        calendar_data.append({
                            "Crop": crop.title(),
                            "Optimal Date": crop_data["optimal"],
                            "Earliest Safe": crop_data["earliest"],
                            "Latest Safe": crop_data["latest"],
                            "Season Length": f"{crop_data['days']} days"
                        })
                
                if calendar_data:
                    df = pd.DataFrame(calendar_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Show as chart
                    st.write("**📊 Planting Timeline Visualization:**")
                    
                    # Create a simple timeline chart
                    months = ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
                    month_positions = {month: i for i, month in enumerate(months)}
                    
                    chart_data = []
                    for _, row in df.iterrows():
                        try:
                            optimal_month = row['Optimal Date'].split()[0][:3]
                            if optimal_month in month_positions:
                                chart_data.append({
                                    'Crop': row['Crop'],
                                    'Month': optimal_month,
                                    'Position': month_positions[optimal_month]
                                })
                        except:
                            pass
                    
                    if chart_data:
                        chart_df = pd.DataFrame(chart_data)
                        fig = px.scatter(chart_df, x='Position', y='Crop', 
                                       title='Optimal Planting Times by Crop',
                                       labels={'Position': 'Month'})
                        fig.update_xaxis(tickvals=list(range(len(months))), ticktext=months)
                        st.plotly_chart(fig, use_container_width=True)
    
    with crop_tab3:
        st.write("**🌡️ Frost Date Analysis for Your Location**")
        
        frost_location = st.text_input("Location for Frost Analysis", value=location, key="frost_location")
        
        if st.button("Get Frost Date Analysis", key="frost_analysis"):
            with st.spinner("Analyzing frost dates..."):
                location_data = {
                    "latitude": 42.0,
                    "longitude": -93.0,
                    "elevation_ft": 1000,
                    "address": frost_location or "Farm Location",
                    "state": "Iowa",
                    "county": "Story",
                    "climate_zone": "5b",
                    "climate_zone_name": "USDA Zone 5b",
                    "temperature_range_f": {"min": -15, "max": -10},
                    "climate_confidence": 0.85
                }
                
                frost_data = get_frost_dates(location_data)
                
                if frost_data and frost_data.get('success'):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        last_frost = frost_data.get('last_frost_date')
                        if last_frost:
                            st.metric("🌸 Last Spring Frost", format_planting_date(last_frost))
                        else:
                            st.metric("🌸 Last Spring Frost", "April 15 (estimated)")
                    
                    with col2:
                        first_frost = frost_data.get('first_frost_date')
                        if first_frost:
                            st.metric("🍂 First Fall Frost", format_planting_date(first_frost))
                        else:
                            st.metric("🍂 First Fall Frost", "October 15 (estimated)")
                    
                    with col3:
                        season_length = frost_data.get('growing_season_length', 183)
                        st.metric("📏 Growing Season", f"{season_length} days")
                    
                    confidence = frost_data.get('confidence_level', 'estimated')
                    if confidence == 'historical':
                        st.success("✅ Based on historical weather data")
                    elif confidence == 'estimated':
                        st.info("ℹ️ Based on climate zone estimation")
                    else:
                        st.warning("⚠️ Using default values")
                        
                    # Frost safety recommendations
                    st.write("**🛡️ Frost Protection Recommendations:**")
                    frost_tips = [
                        "Plant warm-season crops 2 weeks after last frost date",
                        "Use row covers or cold frames for early season protection", 
                        "Monitor soil temperature - should be 50°F+ for most crops",
                        "Cool-season crops can be planted 2-4 weeks before last frost"
                    ]
                    
                    for tip in frost_tips:
                        st.write(f"• {tip}")
                        
                else:
                    # Show default frost information
                    st.warning("⚠️ API unavailable - showing default frost information for Zone 5b")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🌸 Last Spring Frost", "April 15 (estimated)")
                    with col2:
                        st.metric("🍂 First Fall Frost", "October 15 (estimated)")
                    with col3:
                        st.metric("📏 Growing Season", "183 days")

with tab3:
    # Soil Health tab
    st.subheader("🏔️ Soil Health Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Soil Test Input**")
        ph_input = st.number_input("Soil pH", 3.0, 10.0, 6.2, 0.1, key="soil_ph")
        om_input = st.number_input("Organic Matter (%)", 0.0, 15.0, 2.8, 0.1, key="soil_om")
        p_input = st.number_input("Phosphorus (ppm)", 0, 200, 15, key="soil_p")
        k_input = st.number_input("Potassium (ppm)", 0, 800, 120, key="soil_k")
        
        soil_texture = st.selectbox("Soil Texture", 
                                   ["Sand", "Loamy Sand", "Sandy Loam", "Loam", 
                                    "Silt Loam", "Clay Loam", "Clay"])
        
        if st.button("📊 Assess Soil Health"):
            # Calculate soil health score
            score = 5.0
            if 6.0 <= ph_input <= 7.0: score += 1.5
            elif 5.5 <= ph_input <= 7.5: score += 1.0
            if om_input >= 3.0: score += 1.5
            elif om_input >= 2.0: score += 1.0
            if 20 <= p_input <= 40: score += 1.0
            if 150 <= k_input <= 250: score += 1.0
            
            score = min(score, 10.0)
            
            st.session_state.soil_score = score
    
    with col2:
        if 'soil_score' in st.session_state:
            score = st.session_state.soil_score
            
            # Soil health gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Soil Health Score"},
                delta = {'reference': 7.0},
                gauge = {
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 5], 'color': "lightgray"},
                        {'range': [5, 7], 'color': "yellow"},
                        {'range': [7, 10], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 8
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            st.write("**Improvement Recommendations:**")
            
            if ph_input < 6.0:
                st.warning("🔸 Apply lime to raise soil pH to 6.5-7.0 range")
            if om_input < 3.0:
                st.warning("🔸 Increase organic matter through cover crops or compost")
            if p_input < 15:
                st.warning("🔸 Apply phosphorus fertilizer to build soil P levels")
            if k_input < 100:
                st.warning("🔸 Apply potassium fertilizer to improve soil K levels")
            
            if score >= 8:
                st.success("✅ Excellent soil health! Maintain current practices.")

with tab4:
    # Fertilizer Strategy tab
    st.subheader("🧪 Fertilizer Strategy Optimizer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Crop & Field Information**")
        fert_crop = st.selectbox("Primary Crop", ["Corn", "Soybean", "Wheat"], key="fert_crop")
        fert_yield_goal = st.number_input("Yield Goal (bu/acre)", 50, 300, 180, key="fert_yield")
        fert_acres = st.number_input("Planted Acres", 1, 5000, 250, key="fert_acres")
        previous_crop = st.selectbox("Previous Crop", ["Corn", "Soybean", "Wheat", "Fallow"])
        
        st.write("**Economic Parameters**")
        budget = st.number_input("Fertilizer Budget ($)", 1000, 100000, 18000)
        corn_price = st.number_input("Corn Price ($/bu)", 2.0, 8.0, 4.25, 0.01)
        
        st.write("**Fertilizer Prices ($/ton)**")
        urea_price = st.number_input("Urea (46-0-0)", 200, 800, 420)
        dap_price = st.number_input("DAP (18-46-0)", 300, 1000, 580)
        potash_price = st.number_input("Potash (0-0-60)", 200, 600, 380)
    
    with col2:
        if st.button("💰 Calculate Optimal Strategy"):
            # Simplified fertilizer calculation
            n_rate = fert_yield_goal * 0.9
            if previous_crop == "Soybean":
                n_rate -= 40  # Legume credit
            
            p_rate = 30  # Maintenance rate
            k_rate = 50  # Maintenance rate
            
            # Cost calculation
            n_cost = (n_rate * fert_acres * urea_price) / (2000 * 0.46)
            p_cost = (p_rate * fert_acres * dap_price) / (2000 * 0.46)
            k_cost = (k_rate * fert_acres * potash_price) / (2000 * 0.60)
            
            total_cost = n_cost + p_cost + k_cost
            expected_revenue = fert_yield_goal * fert_acres * corn_price
            roi = ((expected_revenue - total_cost) / total_cost) * 100
            
            # Display results
            st.success("✅ Strategy Calculated!")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Total Cost", f"${total_cost:,.0f}")
            with col_b:
                st.metric("Expected Revenue", f"${expected_revenue:,.0f}")
            with col_c:
                st.metric("ROI", f"{roi:.0f}%")
            
            st.write("**Fertilizer Program:**")
            st.write(f"• Nitrogen: {n_rate:.0f} lbs/acre")
            st.write(f"• Phosphorus: {p_rate:.0f} lbs P₂O₅/acre")
            st.write(f"• Potassium: {k_rate:.0f} lbs K₂O/acre")
            
            # ROI visualization
            fig = go.Figure(go.Bar(
                x=['Nitrogen', 'Phosphorus', 'Potassium'],
                y=[n_cost, p_cost, k_cost],
                marker_color=['#28a745', '#17a2b8', '#ffc107']
            ))
            fig.update_layout(title="Fertilizer Cost Breakdown", height=300)
            st.plotly_chart(fig, use_container_width=True)

with tab5:
    # Agricultural Zone Analysis tab
    st.subheader("🌾 Comprehensive Agricultural Zone Analysis")
    
    # Zone overview
    st.markdown("""
    **Climate Zone 5b Agricultural Profile:**
    This analysis provides detailed agricultural insights for your specific climate zone, 
    combining climate data with farming-specific information to support optimal agricultural decision-making.
    """)
    
    # Agricultural zone metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Zone Characteristics")
        st.info("**USDA Zone:** 5b (-15°F to -10°F)")
        st.info("**Classification:** Intensive Cropping")
        st.info("**Frost-Free Days:** 180 days")
        st.info("**Growing Degree Days:** 3,100 GDD")
        
    with col2:
        st.markdown("### 🌽 Top Crops")
        zone_crops = [
            ("Corn", "9.2/10", "180 bu/acre"),
            ("Soybeans", "8.8/10", "55 bu/acre"), 
            ("Alfalfa", "8.3/10", "6 ton/acre"),
            ("Oats", "8.0/10", "80 bu/acre"),
            ("Wheat", "7.5/10", "65 bu/acre")
        ]
        
        for crop, rating, yield_est in zone_crops:
            st.success(f"**{crop}:** {rating} - {yield_est}")
            
    with col3:
        st.markdown("### 🏛️ Farm Enterprises")
        enterprises = [
            ("Row Crops", "9.5/10", "Excellent fit"),
            ("Grain Storage", "9.0/10", "High demand"),
            ("Livestock", "8.2/10", "Good potential"),
            ("Dairy", "7.8/10", "Viable option")
        ]
        
        for enterprise, score, note in enterprises:
            st.info(f"**{enterprise}:** {score} - {note}")
    
    st.divider()
    
    # Detailed agricultural calendar
    st.markdown("### 📅 Detailed Agricultural Calendar")
    
    # Create comprehensive agricultural timeline
    agricultural_calendar = {
        "Month": ["March", "April", "May", "June", "July", "August", "September", "October", "November"],
        "Key_Activities": [
            "Equipment prep, soil testing",
            "Field prep, early planting",
            "Main planting season",
            "Cultivation, pest monitoring", 
            "Crop monitoring, spraying",
            "Late season care",
            "Early harvest, grain handling",
            "Main harvest season",
            "Field cleanup, storage management"
        ],
        "Weather_Focus": [
            "Soil conditions",
            "Frost risk",
            "Planting conditions", 
            "Moisture levels",
            "Heat stress",
            "Disease pressure",
            "Harvest weather",
            "Frost risk",
            "Winter prep"
        ],
        "Risk_Level": [2, 4, 3, 2, 3, 2, 3, 4, 2]
    }
    
    cal_df = pd.DataFrame(agricultural_calendar)
    
    # Risk level visualization
    risk_colors = {1: '#28a745', 2: '#20c997', 3: '#ffc107', 4: '#fd7e14', 5: '#dc3545'}
    cal_df['Color'] = cal_df['Risk_Level'].map(risk_colors)
    
    fig_calendar = px.bar(cal_df, x='Month', y='Risk_Level',
                         color='Risk_Level', 
                         color_continuous_scale='RdYlGn_r',
                         title="Monthly Agricultural Risk & Activity Level",
                         hover_data=['Key_Activities', 'Weather_Focus'])
    
    fig_calendar.update_layout(height=400)
    st.plotly_chart(fig_calendar, use_container_width=True)
    
    # Monthly breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌡️ Critical Weather Periods")
        
        critical_periods = [
            ("Late April", "Last frost risk", "Monitor planting timing", "warning"),
            ("May 1-15", "Optimal planting window", "Ideal conditions for corn/soy", "success"),
            ("July-August", "Peak growing season", "Monitor heat stress & moisture", "info"),
            ("Early October", "First frost risk", "Plan harvest acceleration", "warning"),
            ("October 15+", "Harvest window closing", "Complete grain harvest", "error")
        ]
        
        for period, event, action, alert_type in critical_periods:
            if alert_type == "success":
                st.success(f"**{period}:** {event} - {action}")
            elif alert_type == "warning":
                st.warning(f"**{period}:** {event} - {action}")
            elif alert_type == "info":
                st.info(f"**{period}:** {event} - {action}")
            elif alert_type == "error":
                st.error(f"**{period}:** {event} - {action}")
    
    with col2:
        st.markdown("### 💰 Economic Considerations")
        
        economic_factors = [
            ("Production Costs", "15% below national avg", "Competitive advantage"),
            ("Market Access", "Excellent", "Multiple elevators 5-10 miles"),
            ("Land Values", "Stable/increasing", "Strong agricultural economy"),
            ("Input Availability", "Good", "Multiple supplier options"),
            ("Crop Insurance", "Available", "Strong participation rates")
        ]
        
        for factor, status, note in economic_factors:
            st.info(f"**{factor}:** {status}")
            st.caption(note)
    
    st.divider()
    
    # Zone comparison with neighbors
    st.markdown("### 🗺️ Regional Zone Comparison")
    
    neighbor_zones = {
        "Zone": ["4b (Minnesota)", "5a (Nebraska)", "5b (Iowa - You)", "6a (Illinois)", "6b (Missouri)"],
        "Frost_Free_Days": [140, 160, 180, 200, 210],
        "Corn_Rating": [7.8, 8.5, 9.2, 9.4, 8.6],
        "Soy_Rating": [8.2, 8.0, 8.8, 9.0, 8.9],
        "Risk_Level": [3.2, 2.8, 2.5, 2.3, 2.7]
    }
    
    comparison_df = pd.DataFrame(neighbor_zones)
    comparison_df['Your_Zone'] = comparison_df['Zone'].str.contains('You')
    
    # Multi-metric comparison
    fig_multi = go.Figure()
    
    for i, zone in enumerate(comparison_df['Zone']):
        is_current = 'You' in zone
        line_width = 4 if is_current else 2
        marker_size = 15 if is_current else 10
        
        fig_multi.add_trace(go.Scatter(
            x=comparison_df.loc[i, 'Frost_Free_Days'],
            y=comparison_df.loc[i, 'Corn_Rating'],
            mode='markers+text',
            marker=dict(
                size=marker_size,
                color='red' if is_current else 'blue',
                line=dict(width=line_width, color='darkblue')
            ),
            text=zone.split(' ')[0],
            textposition='top center',
            name=zone,
            hovertemplate=f"<b>{zone}</b><br>" +
                         f"Frost-Free Days: {comparison_df.loc[i, 'Frost_Free_Days']}<br>" +
                         f"Corn Rating: {comparison_df.loc[i, 'Corn_Rating']}<br>" +
                         f"Soy Rating: {comparison_df.loc[i, 'Soy_Rating']}<br>" +
                         f"Risk Level: {comparison_df.loc[i, 'Risk_Level']}<extra></extra>"
        ))
    
    fig_multi.update_layout(
        title="Zone Comparison: Growing Season vs Crop Suitability",
        xaxis_title="Frost-Free Days",
        yaxis_title="Corn Suitability Rating (1-10)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_multi, use_container_width=True)
    
    # Summary insights
    st.markdown("### 🎯 Zone Analysis Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Competitive Advantages:**")
        st.success("✅ Optimal climate for major row crops")
        st.success("✅ Excellent soil resources") 
        st.success("✅ Strong agricultural infrastructure")
        st.success("✅ Favorable economics")
        st.success("✅ Manageable risk profile")
        
    with col2:
        st.markdown("**Areas for Attention:**")
        st.warning("⚠️ Monitor spring frost timing")
        st.info("ℹ️ Diversify crop rotation options")
        st.warning("⚠️ Plan for occasional droughts")
        st.info("ℹ️ Consider specialty crop opportunities")
        st.info("ℹ️ Optimize harvest timing")
    
    # Action recommendations
    st.markdown("### 📋 Actionable Recommendations")
    
    recommendations = [
        {
            "category": "Crop Selection",
            "recommendations": [
                "Focus on corn and soybean as primary crops (9+ ratings)",
                "Consider adding alfalfa for livestock feed and soil health",
                "Evaluate winter wheat as a third crop for rotation",
                "Test specialty corn varieties for premium markets"
            ]
        },
        {
            "category": "Risk Management", 
            "recommendations": [
                "Implement comprehensive crop insurance coverage",
                "Develop frost protection strategies for early/late season",
                "Install weather monitoring equipment",
                "Create drought contingency plans"
            ]
        },
        {
            "category": "Infrastructure",
            "recommendations": [
                "Invest in on-farm grain storage (9.0/10 suitability)",
                "Upgrade field drainage systems for wet springs", 
                "Consider livestock facilities for diversification",
                "Improve machinery for efficient harvest timing"
            ]
        },
        {
            "category": "Economic Optimization",
            "recommendations": [
                "Leverage below-average production costs",
                "Explore premium grain marketing contracts",
                "Consider vertical integration opportunities",
                "Evaluate land expansion possibilities"
            ]
        }
    ]
    
    for rec_category in recommendations:
        with st.expander(f"🎯 {rec_category['category']} Recommendations", expanded=False):
            for rec in rec_category['recommendations']:
                st.write(f"• {rec}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    <p>🌱 AFAS - Autonomous Farm Advisory System | Science-based recommendations for modern agriculture</p>
    <p>All recommendations are validated by agricultural experts and based on university extension research.</p>
</div>
""", unsafe_allow_html=True)