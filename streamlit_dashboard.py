import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
import json

# Page configuration
st.set_page_config(
    page_title="J&J Deutschlandticket Adoption Analysis",
    page_icon="🎫",
    layout="wide"
)

# Custom CSS for compact layout
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        color: white;
        background-color: #0066cc;
        border-radius: 5px;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;
    }
    h1 {
        font-size: 1.8rem !important;
        margin-bottom: 0.5rem !important;
    }
    .stMetric {
        background-color: white;
        padding: 0.5rem;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    commute_df = pd.read_csv('data/synthetic_employees_with_optimal_commutes.csv')
    hvv_stations = pd.read_csv('data/hvv_stations_filtered.csv')
    with open('data/jj_office_snapped.json', 'r') as f:
        office_data = json.load(f)
    return commute_df, hvv_stations, office_data

commute_df, hvv_stations, office_data = load_data()

# Sidebar - Filters
st.sidebar.header("🎛️ Filters")

# Commute time filter
commute_min, commute_max = st.sidebar.slider(
    "Commute Time (minutes)",
    min_value=0,
    max_value=120,
    value=(0, 120),
    help="Filter employees by commute time range"
)

# Adoption score filter
adoption_min, adoption_max = st.sidebar.slider(
    "Adoption Score",
    min_value=0,
    max_value=100,
    value=(0, 100),
    help="Filter employees by adoption score range"
)

# Distance filter
distance_min, distance_max = st.sidebar.slider(
    "Distance from Office (km)",
    min_value=0,
    max_value=70,
    value=(0, 70),
    help="Filter employees by distance from office"
)

# Cost scenario
scenario = st.sidebar.selectbox(
    "Cost Scenario",
    ['Company Pays Full', '50% Subsidy', 'Employee Pays Full'],
    help="Select cost scenario for analysis"
)

# Apply filters
filtered_df = commute_df.copy()
filtered_df = filtered_df[
    (filtered_df['total_commute_min'].between(commute_min, commute_max)) |
    (filtered_df['total_commute_min'].isna())
]
filtered_df = filtered_df[
    (filtered_df[f'adoption_score_{scenario}'].between(adoption_min, adoption_max)) |
    (filtered_df[f'adoption_score_{scenario}'].isna())
]

# Calculate distance from office (using car distance as proxy)
filtered_df['distance_km'] = filtered_df['car_distance_m'] / 1000
filtered_df = filtered_df[
    (filtered_df['distance_km'].between(distance_min, distance_max)) |
    (filtered_df['distance_km'].isna())
]

# Compact Header
st.title("🎫 J&J Deutschlandticket Analysis")
st.markdown("<br>", unsafe_allow_html=True)

# Compact Key Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Employees", len(filtered_df))
with col2:
    high_adoption = filtered_df[filtered_df[f'adoption_score_{scenario}'] >= 70]
    st.metric("High Adoption", len(high_adoption))
with col3:
    avg_commute = filtered_df['total_commute_min'].mean()
    st.metric("Avg Commute", f"{avg_commute:.0f}m" if pd.notna(avg_commute) else "N/A")
with col4:
    avg_savings = filtered_df['monthly_driving_cost'].mean() - 63
    st.metric("Avg Savings", f"€{avg_savings:.0f}" if pd.notna(avg_savings) else "N/A")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Interactive Map", "📊 Analytics", "👥 Employee Explorer", "🔄 Scenario Comparison"])

# Tab 1: Interactive Map
with tab1:
    st.subheader("Interactive Commute Map")
    
    # Initialize layer selection state
    if 'show_office' not in st.session_state:
        st.session_state.show_office = True
    if 'show_employees' not in st.session_state:
        st.session_state.show_employees = True
    if 'show_stations' not in st.session_state:
        st.session_state.show_stations = True
    
    # Layer checkboxes
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.show_office = st.checkbox("Show Office", st.session_state.show_office)
    with col2:
        st.session_state.show_employees = st.checkbox("Show Employees", st.session_state.show_employees)
    with col3:
        st.session_state.show_stations = st.checkbox("Show HVV Stations", st.session_state.show_stations)
    
    # Create folium map
    office_location = [office_data['snapped_latitude'], office_data['snapped_longitude']]
    m = folium.Map(
        location=office_location,
        zoom_start=10,
        tiles='CartoDB Positron',
        control_scale=True
    )
    
    # Add office as a separate layer (if selected)
    if st.session_state.show_office:
        office_layer = folium.FeatureGroup(name='J&J Office')
        folium.Marker(
            location=office_location,
            icon=folium.Icon(icon='building', color='red', prefix='fa'),
            popup='<b>Johnson & Johnson Medical GmbH</b><br>Robert-Koch-Straße 1, 22851 Norderstedt',
            tooltip='J&J Office'
        ).add_to(office_layer)
        office_layer.add_to(m)
    
    # Add employees as a separate layer (if selected)
    if st.session_state.show_employees:
        employee_layer = folium.FeatureGroup(name='Employee Locations')
        def get_commute_color(commute_time):
            if pd.isna(commute_time):
                return 'gray'
            elif commute_time < 30:
                return 'green'
            elif commute_time < 45:
                return 'blue'
            elif commute_time < 60:
                return 'orange'
            else:
                return 'red'
        
        for idx, row in filtered_df.iterrows():
            if pd.notna(row['snapped_latitude']) and pd.notna(row['snapped_longitude']):
                color = get_commute_color(row['total_commute_min'])
                folium.CircleMarker(
                    location=[row['snapped_latitude'], row['snapped_longitude']],
                    radius=5,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    popup=f"""
                    <b>Employee: {row['employee_id']}</b><br>
                    Commute Time: {f"{row['total_commute_min']:.1f} min" if pd.notna(row['total_commute_min']) else "No route"}<br>
                    Adoption Score: {f"{row[f'adoption_score_{scenario}']:.1f}/100" if pd.notna(row[f'adoption_score_{scenario}']) else "N/A"}
                    """,
                    tooltip=row['employee_id']
                ).add_to(employee_layer)
        employee_layer.add_to(m)
    
    # Add HVV stations as a separate layer (if selected)
    if st.session_state.show_stations:
        stations_layer = folium.FeatureGroup(name='HVV Stations')
        stations_subset = hvv_stations.sample(min(1000, len(hvv_stations)))
        for idx, row in stations_subset.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=2,
                color='darkblue',
                fill=True,
                fillColor='lightblue',
                fillOpacity=0.4,
                tooltip=row['name']
            ).add_to(stations_layer)
        stations_layer.add_to(m)
    
    folium_static(m, width=1200, height=400)
    
    st.caption("Legend: 🟢 <30min | 🔵 30-45min | 🟠 45-60min | 🔴 >60min | ⚫ No route")

# Tab 2: Analytics
with tab2:
    st.subheader("Analytics Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Commute time distribution
        fig_commute = px.histogram(
            filtered_df, 
            x='total_commute_min',
            title='Commute Time Distribution',
            labels={'total_commute_min': 'Commute Time (minutes)'},
            color_discrete_sequence=['#0066cc']
        )
        st.plotly_chart(fig_commute, use_container_width=True)
    
    with col2:
        # Adoption score distribution
        fig_adoption = px.histogram(
            filtered_df,
            x=f'adoption_score_{scenario}',
            title=f'Adoption Score Distribution ({scenario})',
            labels={f'adoption_score_{scenario}': 'Adoption Score'},
            color_discrete_sequence=['#00cc66']
        )
        st.plotly_chart(fig_adoption, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Transport attractiveness vs Adoption score
        fig_scatter = px.scatter(
            filtered_df,
            x='transport_attractiveness',
            y=f'adoption_score_{scenario}',
            title='Transport vs Adoption Score',
            labels={
                'transport_attractiveness': 'Transport Attractiveness',
                f'adoption_score_{scenario}': 'Adoption Score'
            },
            color='total_commute_min',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col4:
        # Distance vs Commute time
        fig_distance = px.scatter(
            filtered_df,
            x='distance_km',
            y='total_commute_min',
            title='Distance vs Commute Time',
            labels={
                'distance_km': 'Distance from Office (km)',
                'total_commute_min': 'Commute Time (minutes)'
            },
            color=f'adoption_score_{scenario}',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_distance, use_container_width=True)

# Tab 3: Employee Explorer
with tab3:
    st.subheader("Employee Explorer")
    
    # Searchable data table
    search = st.text_input("Search employees by ID or name", "")
    
    if search:
        display_df = filtered_df[
            filtered_df['employee_id'].str.contains(search, case=False) |
            filtered_df['name'].str.contains(search, case=False)
        ]
    else:
        display_df = filtered_df
    
    # Select columns to display
    display_cols = [
        'employee_id', 'name', 'total_commute_min', 
        f'adoption_score_{scenario}', 'transport_attractiveness',
        'distance_km', 'monthly_driving_cost'
    ]
    
    st.dataframe(
        display_df[display_cols].head(100),
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = display_df[display_cols].to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name='filtered_employees.csv',
        mime='text/csv'
    )

# Tab 4: Scenario Comparison
with tab4:
    st.subheader("Cost Scenario Comparison")
    
    # Calculate metrics for each scenario
    scenarios = ['Company Pays Full', '50% Subsidy', 'Employee Pays Full']
    scenario_metrics = []
    
    for scen in scenarios:
        high_adoption = len(filtered_df[filtered_df[f'adoption_score_{scen}'] >= 70])
        avg_adoption = filtered_df[f'adoption_score_{scen}'].mean()
        scenario_metrics.append({
            'Scenario': scen,
            'High Adoption (%)': f"{high_adoption/len(filtered_df)*100:.1f}%",
            'Avg Adoption Score': f"{avg_adoption:.1f}" if pd.notna(avg_adoption) else "N/A"
        })
    
    scenario_df = pd.DataFrame(scenario_metrics)
    st.dataframe(scenario_df, use_container_width=True, hide_index=True)
    
    # Financial analysis
    st.subheader("Financial Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_driving_cost = filtered_df['monthly_driving_cost'].sum()
        st.metric("Total Monthly Driving Cost", f"€{total_driving_cost:,.0f}")
    
    with col2:
        total_ticket_cost = 63 * len(filtered_df)  # Deutschlandticket cost
        st.metric("Total Monthly Ticket Cost", f"€{total_ticket_cost:,.0f}")
    
    with col3:
        total_savings = total_driving_cost - total_ticket_cost
        st.metric("Total Monthly Savings", f"€{total_savings:,.0f}")

# Footer
st.markdown("---")
st.caption("J&J Deutschlandticket Adoption Analysis Dashboard | Powered by Streamlit")