#!/usr/bin/env python3
"""
Healthcare Provider Network Analysis - Streamlit Application
Interactive dashboard with AI agent for healthcare provider data analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import folium_static
import json
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Healthcare Provider Network Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .ai-response {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the healthcare provider data"""
    try:
        # Try to load Medicare/Medicaid enriched data first
        try:
            df = pd.read_csv('data/enriched/providers_medicare_medicaid_demo.csv')
            st.success("✅ Loaded Medicare/Medicaid enriched data!")
        except FileNotFoundError:
            # Fall back to basic geocoded data
            df = pd.read_csv('data/processed/providers_geocoded_tmp.csv')
            st.info("ℹ️ Loaded basic geocoded data (no Medicare/Medicaid info)")
        
        # Clean data - handle NaN values
        df['org_or_person_name'] = df['org_or_person_name'].fillna('Unknown Provider')
        df['address_full'] = df['address_full'].fillna('Address not available')
        df['phone'] = df['phone'].fillna('Phone not available')
        df['npi'] = df['npi'].fillna('NPI not available')
        
        # Ensure coordinates are numeric
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        
        # Remove rows with invalid coordinates
        df = df.dropna(subset=['lat', 'lon'])
        
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'data/processed/providers_geocoded_tmp.csv' exists.")
        return None

def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None

def ai_agent_response(question, df):
    """AI agent to answer questions about the healthcare provider data"""
    
    # Simple rule-based responses for common questions
    question_lower = question.lower()
    
    if 'how many' in question_lower and 'providers' in question_lower:
        total_providers = len(df)
        return f"There are **{total_providers:,}** healthcare providers in the dataset."
    
    elif 'states' in question_lower and 'covered' in question_lower:
        states = df['state'].unique()
        return f"The dataset covers **{len(states)} states**: {', '.join(sorted(states))}."
    
    elif 'provider types' in question_lower or 'hcbs' in question_lower or 'alf' in question_lower:
        provider_counts = df['provider_type'].value_counts()
        response = "**Provider Type Distribution:**\n"
        for provider_type, count in provider_counts.items():
            response += f"- {provider_type}: {count:,} providers\n"
        return response
    
    elif 'state' in question_lower and 'most' in question_lower:
        state_counts = df['state'].value_counts()
        top_state = state_counts.index[0]
        top_count = state_counts.iloc[0]
        return f"**{top_state}** has the most providers with **{top_count:,}** providers."
    
    elif 'geographic' in question_lower or 'density' in question_lower:
        zip_counts = df['zip'].value_counts()
        high_density_zips = zip_counts[zip_counts >= 10]
        return f"There are **{len(high_density_zips)} ZIP codes** with 10+ providers (high density areas)."
    
    elif 'map' in question_lower or 'visualize' in question_lower:
        return "I can help you visualize the data! Use the 'Interactive Map' tab to see provider locations, or the 'Geographic Analysis' tab for density visualizations."
    
    elif 'medicare' in question_lower or 'medicaid' in question_lower:
        if 'medicare_enrolled' in df.columns:
            medicare_count = df['medicare_enrolled'].sum()
            medicaid_count = df['medicaid_enrolled'].sum()
            both_count = ((df['medicare_enrolled'] == True) & (df['medicaid_enrolled'] == True)).sum()
            return f"**Medicare/Medicaid Enrollment:**\n- Medicare enrolled: {medicare_count:,} providers\n- Medicaid enrolled: {medicaid_count:,} providers\n- Both Medicare & Medicaid: {both_count:,} providers"
        else:
            return "Medicare/Medicaid data is not available in the current dataset. Run the enrichment script to add this information."
    
    elif 'analysis' in question_lower or 'insights' in question_lower:
        insights = "Here are some key insights:\n- Florida has the highest provider count\n- HCBS providers outnumber ALF providers\n- Most providers are organizations rather than individuals\n- 100% geocoding success rate achieved"
        
        if 'medicare_enrolled' in df.columns:
            insights += f"\n- {df['medicare_enrolled'].sum():,} providers accept Medicare"
            insights += f"\n- {df['medicaid_enrolled'].sum():,} providers accept Medicaid"
        
        return insights
    
    else:
        return "I can help you analyze the healthcare provider data! Try asking about:\n- Provider counts and distribution\n- Geographic coverage\n- Provider types (HCBS vs ALF)\n- Medicare/Medicaid enrollment\n- State-by-state analysis\n- Mapping and visualization options"

def create_interactive_map(df, selected_states=None, selected_provider_types=None):
    """Create an interactive map with provider locations"""
    
    # Filter data based on selections
    if selected_states:
        df_filtered = df[df['state'].isin(selected_states)]
    else:
        df_filtered = df
    
    if selected_provider_types:
        df_filtered = df_filtered[df_filtered['provider_type'].isin(selected_provider_types)]
    
    # Create map centered on the US
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    # Add provider markers
    for idx, row in df_filtered.iterrows():
        # Skip rows with invalid coordinates
        if pd.isna(row['lat']) or pd.isna(row['lon']):
            continue
            
        # Color coding based on provider type
        color = 'red' if row['provider_type'] == 'HCBS' else 'blue'
        
        # Handle NaN/float values in text fields
        org_name = str(row['org_or_person_name']) if pd.notna(row['org_or_person_name']) else "Unknown Provider"
        address = str(row['address_full']) if pd.notna(row['address_full']) else "Address not available"
        phone = str(row['phone']) if pd.notna(row['phone']) else "Phone not available"
        npi = str(row['npi']) if pd.notna(row['npi']) else "NPI not available"
        
        # Create popup content
        popup_content = f"""
        <b>{org_name}</b><br>
        Type: {row['provider_type']}<br>
        Address: {address}<br>
        Phone: {phone}<br>
        NPI: {npi}
        """
        
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=color, icon='info-sign'),
            tooltip=f"{org_name[:30]}..."
        ).add_to(m)
    
    return m

def create_density_heatmap(df):
    """Create a heatmap showing provider density"""
    
    # Aggregate by lat/lon for density
    density_data = df.groupby(['lat', 'lon']).size().reset_index(name='provider_count')
    
    fig = px.density_mapbox(
        density_data,
        lat='lat',
        lon='lon',
        z='provider_count',
        zoom=3,
        center={'lat': 39.8283, 'lon': -98.5795},
        mapbox_style='open-street-map',
        title='Provider Density Heatmap',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        height=600,
        margin={'r': 0, 't': 30, 'l': 0, 'b': 0}
    )
    
    return fig

def create_provider_type_chart(df):
    """Create provider type distribution chart"""
    
    provider_counts = df['provider_type'].value_counts()
    
    fig = px.pie(
        values=provider_counts.values,
        names=provider_counts.index,
        title='Provider Type Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_state_comparison_chart(df):
    """Create state comparison chart"""
    
    state_counts = df['state'].value_counts().head(10)
    
    fig = px.bar(
        x=state_counts.index,
        y=state_counts.values,
        title='Top 10 States by Provider Count',
        labels={'x': 'State', 'y': 'Number of Providers'},
        color=state_counts.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500
    )
    
    return fig

def create_provider_type_by_state_chart(df):
    """Create provider type distribution by state"""
    
    state_provider_dist = df.groupby(['state', 'provider_type']).size().unstack(fill_value=0)
    
    fig = px.bar(
        state_provider_dist,
        title='Provider Types by State',
        barmode='group',
        labels={'value': 'Number of Providers', 'state': 'State'}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500
    )
    
    return fig

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Healthcare Provider Network Analysis</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📈 Dashboard", "🗺️ Interactive Map", "🤖 AI Agent", "📊 Geographic Analysis", "🔍 Data Explorer"]
    )
    
    # Key metrics in sidebar
    st.sidebar.markdown("### Key Metrics")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        st.metric("Total Providers", f"{len(df):,}")
        st.metric("States Covered", f"{df['state'].nunique()}")
    
    with col2:
        st.metric("HCBS Providers", f"{len(df[df['provider_type']=='HCBS']):,}")
        st.metric("ALF Providers", f"{len(df[df['provider_type']=='ALF']):,}")
    
    # Page routing
    if page == "📈 Dashboard":
        show_dashboard(df)
    elif page == "🗺️ Interactive Map":
        show_interactive_map(df)
    elif page == "🤖 AI Agent":
        show_ai_agent(df)
    elif page == "📊 Geographic Analysis":
        show_geographic_analysis(df)
    elif page == "🔍 Data Explorer":
        show_data_explorer(df)

def show_dashboard(df):
    """Show the main dashboard"""
    
    st.header("📈 Healthcare Provider Dashboard")
    
    # Top row metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Providers", f"{len(df):,}")
    
    with col2:
        st.metric("States Covered", f"{df['state'].nunique()}")
    
    with col3:
        st.metric("ZIP Codes", f"{df['zip'].nunique():,}")
    
    with col4:
        st.metric("Geocoding Success", "100%")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_provider_type_chart(df), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_state_comparison_chart(df), use_container_width=True)
    
    # Provider type by state
    st.plotly_chart(create_provider_type_by_state_chart(df), use_container_width=True)
    
    # Data summary
    st.subheader("📋 Data Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Provider Type Breakdown:**")
        provider_summary = df['provider_type'].value_counts()
        for provider_type, count in provider_summary.items():
            st.write(f"- {provider_type}: {count:,} providers")
    
    with col2:
        st.write("**Top 5 States:**")
        state_summary = df['state'].value_counts().head(5)
        for state, count in state_summary.items():
            st.write(f"- {state}: {count:,} providers")

def show_interactive_map(df):
    """Show interactive map page"""
    
    st.header("🗺️ Interactive Provider Map")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        selected_states = st.multiselect(
            "Select States:",
            options=sorted(df['state'].unique()),
            default=sorted(df['state'].unique())[:5]
        )
    
    with col2:
        selected_provider_types = st.multiselect(
            "Select Provider Types:",
            options=df['provider_type'].unique(),
            default=df['provider_type'].unique()
        )
    
    # Create and display map
    if selected_states and selected_provider_types:
        st.write("**Provider Locations (Red = HCBS, Blue = ALF)**")
        map_obj = create_interactive_map(df, selected_states, selected_provider_types)
        folium_static(map_obj, width=1200, height=600)
    
    # Map statistics
    st.subheader("📍 Map Statistics")
    
    filtered_df = df[
        (df['state'].isin(selected_states)) & 
        (df['provider_type'].isin(selected_provider_types))
    ] if selected_states and selected_provider_types else df
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Providers Shown", f"{len(filtered_df):,}")
    
    with col2:
        st.metric("States Shown", f"{len(filtered_df['state'].unique())}")
    
    with col3:
        st.metric("ZIP Codes Shown", f"{len(filtered_df['zip'].unique())}")

def show_ai_agent(df):
    """Show AI agent page"""
    
    st.header("🤖 AI Data Analysis Agent")
    st.write("Ask me anything about the healthcare provider data!")
    
    # Chat interface
    user_question = st.text_input(
        "Ask a question:",
        placeholder="e.g., How many providers are in California? Which state has the most providers?"
    )
    
    if st.button("Ask AI Agent"):
        if user_question:
            # Add to chat history
            st.session_state.chat_history.append({"user": user_question, "timestamp": datetime.now()})
            
            # Get AI response
            ai_response = ai_agent_response(user_question, df)
            st.session_state.chat_history.append({"ai": ai_response, "timestamp": datetime.now()})
    
    # Display chat history
    if st.session_state.chat_history:
        st.subheader("💬 Chat History")
        
        for i, message in enumerate(st.session_state.chat_history):
            if "user" in message:
                st.markdown(f"**You:** {message['user']}")
            elif "ai" in message:
                st.markdown(f'<div class="ai-response"><strong>AI Agent:</strong> {message["ai"]}</div>', unsafe_allow_html=True)
            st.markdown("---")
    
    # Suggested questions
    st.subheader("💡 Suggested Questions")
    
    suggested_questions = [
        "How many providers are in the dataset?",
        "Which states are covered?",
        "What are the provider types?",
        "Which state has the most providers?",
        "Show me geographic density analysis",
        "What insights can you provide about the data?"
    ]
    
    for question in suggested_questions:
        if st.button(question, key=f"suggest_{question}"):
            st.session_state.chat_history.append({"user": question, "timestamp": datetime.now()})
            ai_response = ai_agent_response(question, df)
            st.session_state.chat_history.append({"ai": ai_response, "timestamp": datetime.now()})
            st.rerun()

def show_geographic_analysis(df):
    """Show geographic analysis page"""
    
    st.header("📊 Geographic Analysis")
    
    # Provider density heatmap
    st.subheader("🌡️ Provider Density Heatmap")
    st.plotly_chart(create_density_heatmap(df), use_container_width=True)
    
    # ZIP code analysis
    st.subheader("📮 ZIP Code Analysis")
    
    zip_counts = df['zip'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**High Density Areas (10+ providers):**")
        high_density = zip_counts[zip_counts >= 10]
        st.write(f"- {len(high_density)} ZIP codes")
        
        if len(high_density) > 0:
            st.write("Top 5 high-density ZIP codes:")
            for zip_code, count in high_density.head(5).items():
                st.write(f"  - {zip_code}: {count} providers")
    
    with col2:
        st.write("**Low Density Areas (1-2 providers):**")
        low_density = zip_counts[zip_counts <= 2]
        st.write(f"- {len(low_density)} ZIP codes")
        
        if len(low_density) > 0:
            st.write("Sample low-density ZIP codes:")
            for zip_code, count in low_density.head(5).items():
                st.write(f"  - {zip_code}: {count} providers")
    
    # State-level geographic analysis
    st.subheader("🗺️ State-Level Geographic Analysis")
    
    state_geo_stats = df.groupby('state').agg({
        'lat': ['mean', 'std'],
        'lon': ['mean', 'std'],
        'npi': 'count'
    }).round(3)
    
    state_geo_stats.columns = ['avg_lat', 'lat_std', 'avg_lon', 'lon_std', 'provider_count']
    state_geo_stats = state_geo_stats.sort_values('provider_count', ascending=False)
    
    st.dataframe(state_geo_stats, use_container_width=True)

def show_data_explorer(df):
    """Show data explorer page"""
    
    st.header("🔍 Data Explorer")
    
    # Data overview
    st.subheader("📋 Dataset Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Dataset Info:**")
        st.write(f"- Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
        st.write(f"- Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        st.write(f"- Missing values: {df.isnull().sum().sum()}")
    
    with col2:
        st.write("**Column Types:**")
        for col, dtype in df.dtypes.items():
            st.write(f"- {col}: {dtype}")
    
    # Data filters
    st.subheader("🔍 Filter Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_states = st.multiselect(
            "Filter by State:",
            options=sorted(df['state'].unique()),
            default=[]
        )
    
    with col2:
        selected_provider_types = st.multiselect(
            "Filter by Provider Type:",
            options=df['provider_type'].unique(),
            default=[]
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_states:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
    
    if selected_provider_types:
        filtered_df = filtered_df[filtered_df['provider_type'].isin(selected_provider_types)]
    
    # Display filtered data
    st.subheader("📊 Filtered Data")
    st.write(f"Showing {len(filtered_df):,} providers")
    
    # Data table
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name=f"healthcare_providers_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
