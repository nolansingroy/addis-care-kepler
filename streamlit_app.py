#!/usr/bin/env python3
"""
Healthcare Provider Network Analysis - Streamlit Application
Interactive dashboard with AI agent for healthcare provider data analysis
Deployment-ready version for Streamlit Cloud
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
    page_title="Addis Care: Medicaid Crisis Analysis",
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
            try:
                df = pd.read_csv('data/processed/providers_geocoded_tmp.csv')
                st.info("ℹ️ Loaded basic geocoded data (no Medicare/Medicaid info)")
            except FileNotFoundError:
                # Create sample data for demonstration
                st.warning("⚠️ No data files found. Using sample data for demonstration.")
                df = create_sample_data()
        
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
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create sample data for demonstration when real data is not available"""
    np.random.seed(42)
    
    # Sample states and cities
    states = ['CA', 'TX', 'FL', 'NY', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
    cities = ['Los Angeles', 'Houston', 'Miami', 'New York', 'Chicago', 'Philadelphia', 'Columbus', 'Atlanta', 'Charlotte', 'Detroit']
    
    # Create sample data
    n_samples = 1000
    data = {
        'npi': [f'{np.random.randint(1000000000, 9999999999)}' for _ in range(n_samples)],
        'org_or_person_name': [f'Sample Provider {i+1}' for i in range(n_samples)],
        'provider_type': np.random.choice(['HCBS', 'ALF'], n_samples, p=[0.8, 0.2]),
        'state': np.random.choice(states, n_samples),
        'city': np.random.choice(cities, n_samples),
        'zip': [f'{np.random.randint(10000, 99999)}' for _ in range(n_samples)],
        'address_full': [f'{np.random.randint(100, 9999)} Main St, {city}, {state} {np.random.randint(10000, 99999)}' 
                        for city, state in zip(np.random.choice(cities, n_samples), np.random.choice(states, n_samples))],
        'phone': [f'({np.random.randint(100, 999)}) {np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}' for _ in range(n_samples)],
        'lat': np.random.uniform(25, 50, n_samples),
        'lon': np.random.uniform(-125, -65, n_samples),
        'entity_type': np.random.choice([1, 2], n_samples, p=[0.3, 0.7])
    }
    
    # Add Medicare/Medicaid columns if they don't exist
    data['medicare_enrolled'] = np.random.choice([True, False], n_samples, p=[0.7, 0.3])
    data['medicaid_enrolled'] = np.random.choice([True, False], n_samples, p=[0.8, 0.2])
    
    return pd.DataFrame(data)

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
            return "Medicare/Medicaid data is not available in the current dataset."
    
    elif 'medicaid crisis' in question_lower or 'high risk' in question_lower:
        return """**Medicaid Crisis Analysis:**
        
Based on our analysis of 82,608 providers across 10 states:

**Key Findings:**
- **12 million people** at risk of losing Medicaid access
- **1,861 high-risk ZIP codes** identified
- **$4.6B total market potential** for Addis Care solutions

**High-Risk Areas:**
- HCBS-dominant areas (>70% HCBS providers)
- High provider density areas (>100 total providers)
- ALF-heavy areas (>50% ALF providers)

**Top Critical Risk ZIP Codes:**
1. ZIP 77036 (TX): 13 ALFs, 453 HCBS (466 total)
2. ZIP 91411 (CA): 6 ALFs, 290 HCBS (296 total)
3. ZIP 77407 (TX): 17 ALFs, 277 HCBS (294 total)"""
    
    elif 'addis care' in question_lower:
        return """**Addis Care Value Proposition:**

**For Both ALF and HCBS Providers:**

1. **Staff Training & Retention**: AI-driven training for 82,608 facilities
2. **Documentation & Compliance**: Streamlined operations for all facilities
3. **Family Communication**: Real-time communication and coordination
4. **Care Quality Improvement**: AI-driven insights and personalized care plans

**Revenue Model:**
- **$125 per resident/client per month** for both ALF and HCBS
- **Year 1**: $22.9M (0.5% adoption)
- **Year 2**: $91.5M (2.0% adoption)
- **Year 3**: $457.5M (10.0% adoption)
- **Total Market**: $4.6B annual revenue potential"""
    
    elif 'analysis' in question_lower or 'insights' in question_lower:
        insights = "Here are some key insights:\n- Florida has the highest provider count\n- HCBS providers outnumber ALF providers\n- Most providers are organizations rather than individuals"
        
        if 'medicare_enrolled' in df.columns:
            insights += f"\n- {df['medicare_enrolled'].sum():,} providers accept Medicare"
            insights += f"\n- {df['medicaid_enrolled'].sum():,} providers accept Medicaid"
        
        return insights
    
    else:
        return "I can help you analyze the healthcare provider data! Try asking about:\n- Provider counts and distribution\n- Geographic analysis\n- Medicare/Medicaid enrollment\n- Medicaid crisis analysis\n- Addis Care opportunities"

def main():
    """Main application function"""
    initialize_session_state()
    
    # Load data
    df = load_data()
    if df is None:
        st.error("Failed to load data. Please check your data files.")
        return
    
    # Main header
    st.markdown('<h1 class="main-header">🏥 Addis Care: Medicaid Crisis Analysis</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Dashboard", "Interactive Map", "Geographic Analysis", "AI Agent", "Data Explorer", "Medicaid Crisis Analysis"]
    )
    
    if page == "Dashboard":
        show_dashboard(df)
    elif page == "Interactive Map":
        show_interactive_map(df)
    elif page == "Geographic Analysis":
        show_geographic_analysis(df)
    elif page == "AI Agent":
        show_ai_agent(df)
    elif page == "Data Explorer":
        show_data_explorer(df)
    elif page == "Medicaid Crisis Analysis":
        show_medicaid_crisis_analysis(df)

def show_dashboard(df):
    """Show the main dashboard"""
    st.header("📊 Dashboard Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Providers", f"{len(df):,}")
    
    with col2:
        hcbs_count = len(df[df['provider_type'] == 'HCBS'])
        st.metric("HCBS Providers", f"{hcbs_count:,}")
    
    with col3:
        alf_count = len(df[df['provider_type'] == 'ALF'])
        st.metric("ALF Providers", f"{alf_count:,}")
    
    with col4:
        states_covered = len(df['state'].unique())
        st.metric("States Covered", states_covered)
    
    # Provider type distribution
    st.subheader("Provider Type Distribution")
    provider_counts = df['provider_type'].value_counts()
    fig = px.pie(values=provider_counts.values, names=provider_counts.index, title="Provider Types")
    st.plotly_chart(fig, use_container_width=True)
    
    # State distribution
    st.subheader("Provider Distribution by State")
    state_counts = df['state'].value_counts().head(10)
    fig = px.bar(x=state_counts.index, y=state_counts.values, title="Top 10 States by Provider Count")
    st.plotly_chart(fig, use_container_width=True)

def show_interactive_map(df):
    """Show interactive map"""
    st.header("🗺️ Interactive Map")
    
    # Create map
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=4)
    
    # Add markers
    for idx, row in df.head(1000).iterrows():  # Limit to 1000 points for performance
        popup_text = f"""
        <b>{row['org_or_person_name']}</b><br>
        Type: {row['provider_type']}<br>
        Address: {row['address_full']}<br>
        Phone: {row['phone']}<br>
        NPI: {row['npi']}
        """
        
        color = 'red' if row['provider_type'] == 'HCBS' else 'blue'
        folium.Marker(
            [row['lat'], row['lon']],
            popup=popup_text,
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    
    folium_static(m)

def show_geographic_analysis(df):
    """Show geographic analysis"""
    st.header("📈 Geographic Analysis")
    
    # Provider density by state
    st.subheader("Provider Density by State")
    state_density = df['state'].value_counts()
    fig = px.choropleth(
        locations=state_density.index,
        locationmode="USA-states",
        z=state_density.values,
        scope="usa",
        title="Provider Density by State"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ZIP code analysis
    st.subheader("Top ZIP Codes by Provider Count")
    zip_counts = df['zip'].value_counts().head(20)
    fig = px.bar(x=zip_counts.index, y=zip_counts.values, title="Top 20 ZIP Codes")
    st.plotly_chart(fig, use_container_width=True)

def show_ai_agent(df):
    """Show AI agent interface"""
    st.header("🤖 AI Agent")
    st.write("Ask me anything about the healthcare provider data!")
    
    # Chat interface
    user_question = st.text_input("Your question:", placeholder="e.g., How many providers are in California?")
    
    if st.button("Ask AI Agent"):
        if user_question:
            response = ai_agent_response(user_question, df)
            st.markdown(f'<div class="ai-response">{response}</div>', unsafe_allow_html=True)
            
            # Add to chat history
            st.session_state.chat_history.append({"question": user_question, "response": response})
    
    # Show chat history
    if st.session_state.chat_history:
        st.subheader("Chat History")
        for i, chat in enumerate(st.session_state.chat_history):
            with st.expander(f"Q: {chat['question']}"):
                st.write(chat['response'])

def show_data_explorer(df):
    """Show data explorer"""
    st.header("🔍 Data Explorer")
    
    # Filters
    st.subheader("Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        selected_states = st.multiselect("Select States:", df['state'].unique())
        selected_types = st.multiselect("Select Provider Types:", df['provider_type'].unique())
    
    with col2:
        search_term = st.text_input("Search Provider Name:")
        min_lat, max_lat = st.slider("Latitude Range:", float(df['lat'].min()), float(df['lat'].max()), 
                                    (float(df['lat'].min()), float(df['lat'].max())))
    
    # Apply filters
    filtered_df = df.copy()
    if selected_states:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
    if selected_types:
        filtered_df = filtered_df[filtered_df['provider_type'].isin(selected_types)]
    if search_term:
        filtered_df = filtered_df[filtered_df['org_or_person_name'].str.contains(search_term, case=False, na=False)]
    filtered_df = filtered_df[(filtered_df['lat'] >= min_lat) & (filtered_df['lat'] <= max_lat)]
    
    # Show results
    st.subheader(f"Results ({len(filtered_df):,} providers)")
    st.dataframe(filtered_df.head(100))

def show_medicaid_crisis_analysis(df):
    """Show Medicaid crisis analysis"""
    st.header("🚨 Medicaid Crisis Analysis")
    
    st.markdown("""
    ## **Key Findings**
    
    - **12 million people** at risk of losing Medicaid access
    - **82,608 providers** across 10 states facing policy changes
    - **1,861 high-risk ZIP codes** identified
    - **$4.6B total market potential** for Addis Care solutions
    """)
    
    # High-risk areas simulation
    st.subheader("High-Risk Areas Identified")
    
    # Simulate high-risk areas based on provider density
    zip_counts = df['zip'].value_counts()
    high_risk_zips = zip_counts[zip_counts >= 10].head(10)
    
    risk_data = []
    for zip_code, count in high_risk_zips.items():
        zip_df = df[df['zip'] == zip_code]
        hcbs_count = len(zip_df[zip_df['provider_type'] == 'HCBS'])
        alf_count = len(zip_df[zip_df['provider_type'] == 'ALF'])
        hcbs_percentage = (hcbs_count / count) * 100
        
        risk_level = "CRITICAL" if hcbs_percentage >= 70 else "HIGH" if hcbs_percentage >= 50 else "MODERATE"
        risk_data.append({
            "ZIP": zip_code,
            "Total Providers": count,
            "HCBS": hcbs_count,
            "ALF": alf_count,
            "HCBS %": f"{hcbs_percentage:.1f}%",
            "Risk Level": risk_level
        })
    
    risk_df = pd.DataFrame(risk_data)
    st.dataframe(risk_df)
    
    # Revenue projections
    st.subheader("Revenue Projections")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Year 1 Revenue", "$22.9M", "0.5% adoption")
    
    with col2:
        st.metric("Year 2 Revenue", "$91.5M", "2.0% adoption")
    
    with col3:
        st.metric("Year 3 Revenue", "$457.5M", "10.0% adoption")
    
    st.markdown("""
    ## **Addis Care Value Proposition**
    
    **For Both ALF and HCBS Providers:**
    
    1. **Staff Training & Retention**: AI-driven training for 82,608 facilities
    2. **Documentation & Compliance**: Streamlined operations for all facilities
    3. **Family Communication**: Real-time communication and coordination
    4. **Care Quality Improvement**: AI-driven insights and personalized care plans
    """)

if __name__ == "__main__":
    main()
