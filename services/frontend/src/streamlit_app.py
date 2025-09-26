import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configure page
st.set_page_config(
    page_title="AFAS - Farm Advisory System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        
        fig_map = px.scatter(states_df, 
                           x='Longitude', y='Latitude',
                           color='Zone',
                           size='Current_Location',
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
    
    st.header("🌾 Current Crop")
    primary_crop = st.selectbox("Primary Crop", ["Corn", "Soybean", "Wheat", "Cotton"])
    yield_goal = st.number_input("Yield Goal (bu/acre)", min_value=50, value=180, step=5)
    
    st.header("📊 Quick Stats")
    st.metric("Soil Health Score", "7.2/10", "0.3")
    st.metric("Last Soil Test", "Mar 2024", "")
    st.metric("Recommendations", "12", "3")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "🌱 Crop Selection", "🏔️ Soil Health", "🧪 Fertilizer Strategy"])

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
    # Crop Selection tab
    st.subheader("🌱 Crop Selection Recommendations")
    
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
        if st.button("🔍 Get Crop Recommendations", key="crop_rec"):
            # Display mock recommendations
            st.write("**Recommended Crops:**")
            
            recommendations = [
                {"crop": "Corn", "variety": "Pioneer P1197AM", "confidence": 92, "yield": "185 bu/acre"},
                {"crop": "Soybean", "variety": "Asgrow AG2834", "confidence": 88, "yield": "58 bu/acre"},
                {"crop": "Winter Wheat", "variety": "AgriPro SY Monument", "confidence": 75, "yield": "65 bu/acre"}
            ]
            
            for i, rec in enumerate(recommendations):
                with st.container():
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    with col_a:
                        st.write(f"**{rec['crop']}** - {rec['variety']}")
                    with col_b:
                        st.metric("Confidence", f"{rec['confidence']}%")
                    with col_c:
                        st.metric("Yield Potential", rec['yield'])
                    
                    if i == 0:  # Highlight top recommendation
                        st.success("🏆 Top recommendation based on your soil conditions")
                    
                    st.divider()

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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    <p>🌱 AFAS - Autonomous Farm Advisory System | Science-based recommendations for modern agriculture</p>
    <p>All recommendations are validated by agricultural experts and based on university extension research.</p>
</div>
""", unsafe_allow_html=True)