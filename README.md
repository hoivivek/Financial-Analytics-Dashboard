# Financial Analytics Dashboard

**A multi-source financial dashboard that visualizes data from yFinance, custom APIs, and CSV uploads with interactive charts and statistics.**

## Features

- **Multiple Data Sources**:
  - 📈 Real-time stock data from yFinance (AAPL, GOOGL, TSLA, etc.)
  - 🔗 Custom API endpoint integration (JSON responses)
  - 📁 CSV file uploads for custom datasets

- **Interactive Visualizations**:
  - Candlestick charts for stock price data
  - Volume analysis for trading data
  - Custom chart builder (Line, Bar, Scatter, Area)
  - Distribution plots (Histograms, Box plots)
  - Correlation matrix heatmaps

- **Data Analysis**:
  - Descriptive statistics
  - Column filtering and selection
  - Data export to CSV
  - Statistical summaries

## Run Locally

```bash
# Clone the repo
git clone [repo-url]
cd financial-dashboard

# Install dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Deploy!

No secrets required - the app works out of the box with public data sources.

## Usage Examples

### yFinance Stock Data
1. Select "yFinance" from the sidebar
2. Enter a ticker symbol (e.g., `AAPL`, `TSLA`, `^GSPC`)
3. Choose a time period (1 day to max)
4. Click "Fetch Data"
5. Explore candlestick charts, volume analysis, and statistics

### API Data
1. Select "API Link" from the sidebar
2. Enter a JSON API endpoint URL
3. Click "Fetch Data"
4. Use the chart builder to create custom visualizations

### CSV Upload
1. Select "CSV Upload" from the sidebar
2. Upload your CSV file
3. Explore data with the interactive chart builder
4. Analyze distributions and correlations

## Data Format Requirements

**CSV Files:**
- First row must contain column headers
- Include numeric columns for charts and statistics
- Date columns (optional) for time series analysis

**API Endpoints:**
- Must return JSON data
- Can be a JSON object or array
- Automatically converted to DataFrame

## Technology Stack

- **Streamlit** - Interactive web framework
- **Plotly** - Interactive visualizations
- **yFinance** - Stock market data
- **Pandas** - Data manipulation
- **Requests** - API integration

---

Built with [Streamlit](https://streamlit.io)
