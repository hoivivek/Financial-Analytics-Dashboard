import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import requests

# Page config
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon=":material/analytics:",
    layout="wide"
)

# Initialize session state
st.session_state.setdefault("df", None)
st.session_state.setdefault("data_source", None)
st.session_state.setdefault("ticker_data", {})

# Cache yfinance data
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_yfinance_data(ticker: str, period: str = "1mo") -> pd.DataFrame:
    """Fetch stock data from yfinance."""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Cache API data
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_api_data(url: str) -> pd.DataFrame:
    """Fetch data from custom API endpoint."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Try to convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            st.error("API response format not supported")
            return None
        
        return df
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return None

def validate_dataframe(df: pd.DataFrame) -> bool:
    """Validate that DataFrame has data for visualization."""
    if df is None or df.empty:
        st.warning("No data available to display.", icon=":material/warning:")
        return False
    return True

# Sidebar
with st.sidebar:
    st.header(":material/settings: Data Source")
    
    data_source = st.radio(
        "Select data source:",
        ["yFinance", "API Link", "CSV Upload"],
        key="data_source_selector"
    )
    
    st.divider()
    
    # yFinance input
    if data_source == "yFinance":
        st.subheader(":material/show_chart: Stock Data")
        
        ticker = st.text_input(
            "Enter ticker symbol:",
            value="AAPL",
            help="Examples: AAPL, GOOGL, MSFT, TSLA",
            key="ticker_input"
        )
        
        period = st.selectbox(
            "Time period:",
            ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
            index=2,
            key="period_select"
        )
        
        if st.button(":material/refresh: Fetch Data", use_container_width=True):
            with st.spinner(f"Fetching {ticker} data..."):
                df = fetch_yfinance_data(ticker.upper(), period)
                if df is not None and not df.empty:
                    st.session_state.df = df
                    st.session_state.data_source = "yFinance"
                    st.session_state.ticker_data = {
                        "ticker": ticker.upper(),
                        "period": period
                    }
                    st.success(f"Loaded {len(df)} records")
    
    # API Link input
    elif data_source == "API Link":
        st.subheader(":material/link: API Data")
        
        api_url = st.text_input(
            "Enter API URL:",
            placeholder="https://api.example.com/data",
            help="Must return JSON data",
            key="api_url_input"
        )
        
        if st.button(":material/cloud_download: Fetch Data", use_container_width=True):
            if api_url:
                with st.spinner("Fetching API data..."):
                    df = fetch_api_data(api_url)
                    if df is not None and not df.empty:
                        st.session_state.df = df
                        st.session_state.data_source = "API"
                        st.success(f"Loaded {len(df)} records")
            else:
                st.warning("Please enter an API URL")
    
    # CSV Upload
    else:
        st.subheader(":material/upload_file: Upload CSV")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            help="Upload a CSV file for analysis",
            key="csv_uploader"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.df = df
                st.session_state.data_source = "CSV"
                st.success(f"Loaded {len(df)} rows from {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error loading file: {e}")

# Main content
st.title(":material/analytics: Financial Dashboard")

# Check if data is loaded
if st.session_state.df is not None and validate_dataframe(st.session_state.df):
    df = st.session_state.df
    
    # Display data source info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.session_state.data_source == "yFinance":
            ticker_info = st.session_state.ticker_data
            st.info(
                f":material/show_chart: **{ticker_info.get('ticker', 'N/A')}** | "
                f"Period: {ticker_info.get('period', 'N/A')} | "
                f"{len(df)} records",
                icon=":material/info:"
            )
        else:
            st.info(
                f":material/database: **{st.session_state.data_source}** | "
                f"{len(df)} records",
                icon=":material/info:"
            )
    
    with col2:
        st.metric("Rows", f"{len(df):,}")
    with col3:
        st.metric("Columns", len(df.columns))
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs([
        ":material/table_chart: Data",
        ":material/bar_chart: Charts",
        ":material/query_stats: Statistics"
    ])
    
    with tab1:
        st.subheader("Dataset Preview")
        
        # Column selector
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "Select columns to display:",
            all_columns,
            default=all_columns[:min(10, len(all_columns))],
            key="column_selector"
        )
        
        if selected_columns:
            st.dataframe(
                df[selected_columns],
                use_container_width=True,
                height=400
            )
            
            # Download button
            csv = df[selected_columns].to_csv(index=False)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            st.download_button(
                label=":material/download: Download CSV",
                data=csv,
                file_name=f"export_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("Please select at least one column to display")
    
    with tab2:
        st.subheader("Visualizations")
        
        # Detect numeric and datetime columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # For yFinance data, create price chart
        if st.session_state.data_source == "yFinance" and 'Close' in df.columns:
            st.markdown("#### Stock Price Over Time")
            
            fig = go.Figure()
            
            # Add candlestick if OHLC data available
            if all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
                fig.add_trace(go.Candlestick(
                    x=df['Date'],
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='OHLC'
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=df['Date'],
                    y=df['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='#00BFC4', width=2)
                ))
            
            fig.update_layout(
                margin=dict(t=20, l=0, r=0, b=0),
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            if 'Volume' in df.columns:
                st.markdown("#### Trading Volume")
                fig_vol = px.bar(
                    df, x='Date', y='Volume',
                    color_discrete_sequence=['#F8766D']
                )
                fig_vol.update_layout(
                    margin=dict(t=20, l=0, r=0, b=0),
                    showlegend=False,
                    height=250
                )
                st.plotly_chart(fig_vol, use_container_width=True)
        
        # Generic chart builder for other data sources
        else:
            if numeric_cols:
                col1, col2 = st.columns(2)
                
                with col1:
                    chart_type = st.selectbox(
                        "Chart type:",
                        ["Line", "Bar", "Scatter", "Area"],
                        key="chart_type"
                    )
                
                with col2:
                    y_column = st.selectbox(
                        "Y-axis column:",
                        numeric_cols,
                        key="y_axis"
                    )
                
                # X-axis selection
                x_options = datetime_cols + numeric_cols + df.select_dtypes(include=['object']).columns.tolist()
                x_column = st.selectbox(
                    "X-axis column:",
                    x_options,
                    key="x_axis"
                )
                
                # Color by column (optional)
                color_options = ["None"] + df.select_dtypes(include=['object']).columns.tolist()
                color_by = st.selectbox(
                    "Color by (optional):",
                    color_options,
                    key="color_by"
                )
                
                # Create chart
                try:
                    if chart_type == "Line":
                        fig = px.line(
                            df, x=x_column, y=y_column,
                            color=None if color_by == "None" else color_by
                        )
                    elif chart_type == "Bar":
                        fig = px.bar(
                            df, x=x_column, y=y_column,
                            color=None if color_by == "None" else color_by
                        )
                    elif chart_type == "Scatter":
                        fig = px.scatter(
                            df, x=x_column, y=y_column,
                            color=None if color_by == "None" else color_by
                        )
                    else:  # Area
                        fig = px.area(
                            df, x=x_column, y=y_column,
                            color=None if color_by == "None" else color_by
                        )
                    
                    fig.update_layout(
                        margin=dict(t=20, l=0, r=0, b=0),
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                except Exception as e:
                    st.error(f"Error creating chart: {e}")
            else:
                st.info("No numeric columns available for visualization")
    
    with tab3:
        st.subheader("Statistical Summary")
        
        if numeric_cols:
            # Summary statistics
            st.markdown("#### Descriptive Statistics")
            summary_df = df[numeric_cols].describe()
            st.dataframe(summary_df, use_container_width=True)
            
            # Distribution plots
            st.markdown("#### Distributions")
            selected_col = st.selectbox(
                "Select column for distribution:",
                numeric_cols,
                key="dist_column"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_hist = px.histogram(
                    df, x=selected_col,
                    nbins=30,
                    title="Histogram",
                    color_discrete_sequence=['#7CAE00']
                )
                fig_hist.update_layout(
                    margin=dict(t=40, l=0, r=0, b=0),
                    showlegend=False
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                fig_box = px.box(
                    df, y=selected_col,
                    title="Box Plot",
                    color_discrete_sequence=['#C77CFF']
                )
                fig_box.update_layout(
                    margin=dict(t=40, l=0, r=0, b=0),
                    showlegend=False
                )
                st.plotly_chart(fig_box, use_container_width=True)
            
            # Correlation matrix
            if len(numeric_cols) > 1:
                st.markdown("#### Correlation Matrix")
                corr_matrix = df[numeric_cols].corr()
                
                fig_corr = px.imshow(
                    corr_matrix,
                    text_auto='.2f',
                    color_continuous_scale='RdBu_r',
                    aspect="auto"
                )
                fig_corr.update_layout(
                    margin=dict(t=20, l=0, r=0, b=0),
                    height=500
                )
                st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("No numeric columns available for statistics")

else:
    # Welcome screen
    st.markdown("""
    ## Welcome to the Financial Dashboard! 👋
    
    Get started by selecting a data source from the sidebar:
    
    - **:material/show_chart: yFinance**: Fetch real-time stock market data
    - **:material/link: API Link**: Connect to any JSON API endpoint
    - **:material/upload_file: CSV Upload**: Upload your own data files
    
    Once loaded, you'll be able to:
    - View and filter your data
    - Create interactive visualizations
    - Analyze statistical distributions
    - Export processed data
    """)
    
    # Example data section
    with st.expander(":material/lightbulb: See examples", expanded=False):
        st.markdown("""
        ### Example Queries
        
        **yFinance tickers:**
        - `AAPL` - Apple Inc.
        - `GOOGL` - Alphabet Inc.
        - `MSFT` - Microsoft Corporation
        - `TSLA` - Tesla Inc.
        - `^GSPC` - S&P 500 Index
        
        **Sample API endpoints:**
        - Financial data APIs (Alpha Vantage, Polygon.io)
        - Weather data (OpenWeatherMap)
        - Public datasets (data.gov)
        
        **CSV format:**
        - First row should contain column headers
        - Numeric data for charts and statistics
        - Date columns for time series analysis
        """)
