#!/usr/bin/env python3
"""
Streamlit Dashboard for DB-6: Weather Forecasting & Insurance
Interactive query execution, visualization, and analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from pathlib import Path
import json
import os
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title=f"DB-6: Weather Forecasting & Insurance",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .query-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# ENVIRONMENT DETECTION AND CONFIGURATION
# ============================================================================

def detect_environment():
    """Detect execution environment."""
    if os.path.exists('/.dockerenv'):
        return 'docker'
    elif 'google.colab' in str(sys.modules.keys()) or os.path.exists('/content'):
        return 'colab'
    else:
        return 'local'

def find_file_recursively(start_dir: Path, filename: str):
    """Find file recursively."""
    try:
        for path in start_dir.rglob(filename):
            return path
    except:
        pass
    return None

def get_database_config():
    """Get database configuration based on environment."""
    env_type = detect_environment()
    
    if env_type == 'docker':
        return {
            'host': os.getenv('PG_HOST', 'localhost'),
            'port': os.getenv('PG_PORT', '5432'),
            'user': os.getenv('PG_USER', 'postgres'),
            'password': os.getenv('PG_PASSWORD', 'postgres'),
            'database': 'db6'
        }
    elif env_type == 'colab':
        return {
            'host': os.getenv('PG_HOST', 'localhost'),
            'port': os.getenv('PG_PORT', '5432'),
            'user': os.getenv('PG_USER', 'postgres'),
            'password': os.getenv('PG_PASSWORD', ''),
            'database': 'db6'
        }
    else:
        return {
            'host': os.getenv('PG_HOST', 'localhost'),
            'port': os.getenv('PG_PORT', '5432'),
            'user': os.getenv('PG_USER', os.getenv('USER', 'postgres')),
            'password': os.getenv('PG_PASSWORD', ''),
            'database': 'db6'
        }

def find_queries_file():
    """Find queries.json file recursively."""
    search_paths = [
        Path.cwd(),
        Path('/workspace/client/db'),
        Path('/workspace/db'),
        Path('/workspace'),
        Path('/content/drive/MyDrive/db'),
        Path('/content/db'),
        Path('/content'),
        Path.home() / 'Documents' / 'AQ' / 'db',
    ]
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        queries_file = find_file_recursively(search_path, 'queries.json')
        if queries_file:
            db_dir_candidate = queries_file.parent.parent
            if db_dir_candidate.name == 'db-6':
                return queries_file
    
    # Fallback
    return Path('/workspace/client/db/db-6') / 'queries' / 'queries.json'

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

@st.cache_resource
def get_db_connection():
    """Get database connection (cached)."""
    try:
        config = get_database_config()
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# ============================================================================
# QUERY EXECUTION
# ============================================================================

@st.cache_data(ttl=300)
def execute_query(query_sql: str, query_num: int):
    """Execute query and return results."""
    conn = get_db_connection()
    if not conn:
        return None, None
    
    try:
        start_time = datetime.now()
        df = pd.read_sql_query(query_sql, conn)
        execution_time = (datetime.now() - start_time).total_seconds()
        return df, execution_time
    except Exception as e:
        return None, str(e)

# ============================================================================
# LOAD QUERIES
# ============================================================================

@st.cache_data
def load_queries():
    """Load queries from JSON file."""
    queries_file = find_queries_file()
    
    if not queries_file.exists():
        st.error(f"queries.json not found: {queries_file}")
        return []
    
    with open(queries_file) as f:
        queries_data = json.load(f)
    
    return queries_data.get('queries', [])

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    """Main dashboard function."""
    
    # Header
    st.markdown(f'<div class="main-header">DB-6: Weather Forecasting & Insurance</div>', unsafe_allow_html=True)
    
    # Load queries
    queries = load_queries()
    
    if not queries:
        st.error("No queries found. Please ensure queries.json exists.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Dashboard Controls")
        
        # Environment info
        env_type = detect_environment()
        st.info(f"**Environment:** {env_type.upper()}")
        
        # Database connection status
        conn = get_db_connection()
        if conn:
            st.success("✅ Database Connected")
        else:
            st.error("❌ Database Disconnected")
        
        # Statistics
        st.header("📈 Statistics")
        st.metric("Total Queries", 30)
        
        # Query selector
        st.header("🔍 Query Selector")
        query_options = [f"Query {q.get('number')}: {q.get('title', 'N/A')[:50]}" for q in queries]
        selected_query_idx = st.selectbox(
            "Select Query",
            range(len(queries)),
            format_func=lambda x: query_options[x]
        )
        
        # Execution options
        st.header("⚙️ Options")
        auto_refresh = st.checkbox("Auto-refresh (5 min)", value=False)
        show_sql = st.checkbox("Show SQL", value=True)
        show_metadata = st.checkbox("Show Metadata", value=True)
        limit_rows = st.number_input("Row Limit", min_value=100, max_value=10000, value=1000, step=100)
    
    # Main content
    selected_query = queries[selected_query_idx]
    query_num = selected_query.get('number')
    query_title = selected_query.get('title', f'Query {query_num}')
    query_sql = selected_query.get('sql', '')
    query_desc = selected_query.get('description', '')
    query_use_case = selected_query.get('use_case', '')
    query_business_value = selected_query.get('business_value', '')
    
    # Query information
    st.header(f"Query {query_num}: {query_title}")
    
    if show_metadata:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Description:**\n{query_desc[:200]}...")
        with col2:
            st.markdown(f"**Use Case:**\n{query_use_case[:200]}...")
        with col3:
            st.markdown(f"**Business Value:**\n{query_business_value[:200]}...")
    
    if show_sql:
        with st.expander("📝 SQL Query"):
            st.code(query_sql, language='sql')
    
    # Execute query
    if st.button("▶️ Execute Query", type="primary"):
        with st.spinner("Executing query..."):
            df, result = execute_query(query_sql, query_num)
            
            if df is not None:
                st.success(f"✅ Query executed successfully in {result:.3f} seconds")
                
                # Limit rows
                df_display = df.head(limit_rows)
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Rows Returned", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                with col3:
                    st.metric("Execution Time", f"{result:.3f}s")
                with col4:
                    st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
                
                # Data preview
                st.header("📋 Data Preview")
                st.dataframe(df_display, use_container_width=True)
                
                # Visualizations
                st.header("📊 Visualizations")
                
                # Auto-generate visualizations for numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if len(numeric_cols) > 0:
                    # Distribution plots
                    if len(numeric_cols) >= 1:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            selected_col = st.selectbox("Select Column for Distribution", numeric_cols)
                            if selected_col:
                                fig = px.histogram(df, x=selected_col, nbins=30, title=f"Distribution of {selected_col}")
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            if len(numeric_cols) >= 2:
                                selected_col2 = st.selectbox("Select Column for Box Plot", numeric_cols, index=min(1, len(numeric_cols)-1))
                                if selected_col2:
                                    fig = px.box(df, y=selected_col2, title=f"Box Plot of {selected_col2}")
                                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Correlation heatmap
                    if len(numeric_cols) > 1:
                        st.subheader("Correlation Matrix")
                        corr_matrix = df[numeric_cols].corr()
                        fig = px.imshow(
                            corr_matrix,
                            labels=dict(color="Correlation"),
                            x=corr_matrix.columns,
                            y=corr_matrix.columns,
                            color_continuous_scale="RdBu",
                            aspect="auto"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Time series (if date column exists)
                    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
                    if len(date_cols) > 0 and len(numeric_cols) > 0:
                        st.subheader("Time Series Analysis")
                        date_col = st.selectbox("Select Date Column", date_cols)
                        value_col = st.selectbox("Select Value Column", numeric_cols)
                        if date_col and value_col:
                            fig = px.line(df, x=date_col, y=value_col, title=f"{value_col} over Time")
                            st.plotly_chart(fig, use_container_width=True)
                
                # Export options
                st.header("💾 Export Data")
                col1, col2, col3 = st.columns(3)
                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"query_{query_num}_results.csv",
                        mime="text/csv"
                    )
                with col2:
                    json_str = df.to_json(orient='records', indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"query_{query_num}_results.json",
                        mime="application/json"
                    )
                with col3:
                    excel = df.to_excel(index=False)
                    st.download_button(
                        label="📥 Download Excel",
                        data=excel,
                        file_name=f"query_{query_num}_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.error(f"❌ Query execution failed: {result}")
    
    # Query list
    st.header("📚 All Queries")
    
    # Create query cards
    for i, query in enumerate(queries):
        with st.expander(f"Query {query.get('number')}: {query.get('title', 'N/A')}"):
            st.markdown(f"**Description:** {query.get('description', 'N/A')}")
            st.markdown(f"**Use Case:** {query.get('use_case', 'N/A')}")
            st.markdown(f"**Business Value:** {query.get('business_value', 'N/A')}")
            st.markdown(f"**Complexity:** {query.get('complexity', 'N/A')}")
            
            if st.button(f"Execute Query {query.get('number')}", key=f"exec_{i}"):
                st.session_state['selected_query_idx'] = i
                st.rerun()

if __name__ == '__main__':
    main()
