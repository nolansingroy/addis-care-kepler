# Streamlit Application Deployment Guide

## 🚀 Healthcare Provider Network Analysis - Streamlit App

This guide provides step-by-step instructions for deploying the Healthcare Provider Network Analysis Streamlit application.

## 📋 Prerequisites

### Required Software
- **Python 3.8+**
- **pip** (Python package installer)
- **Git** (for version control)

### Data Requirements
- Ensure `data/processed/providers_geocoded_tmp.csv` exists in the project directory

## 🛠️ Local Development Setup

### 1. Clone and Setup Repository
```bash
# Clone the repository
git clone [your-repository-url]
cd healthcare-provider-analysis

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application Locally
```bash
# Start the Streamlit app
streamlit run app.py

# The app will open in your browser at http://localhost:8501
```

## 🌐 Cloud Deployment Options

### Option 1: Streamlit Cloud (Recommended)

#### Step 1: Prepare Repository
1. **Push to GitHub**: Ensure your repository is on GitHub
2. **Check File Structure**: Verify all files are in the correct locations
3. **Update Requirements**: Ensure `requirements.txt` includes all dependencies

#### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository and branch
5. Set the main file path to `app.py`
6. Click "Deploy"

#### Step 3: Configure Environment
- **App URL**: Your app will be available at `https://your-app-name.streamlit.app`
- **Auto-deploy**: Changes to your main branch will automatically deploy
- **Logs**: Monitor deployment and runtime logs in the Streamlit Cloud dashboard

### Option 2: Heroku Deployment

#### Step 1: Create Heroku App
```bash
# Install Heroku CLI
# Create new Heroku app
heroku create your-app-name

# Add buildpacks
heroku buildpacks:add heroku/python
```

#### Step 2: Create Procfile
Create a file named `Procfile` (no extension) in your root directory:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

#### Step 3: Deploy
```bash
# Add all files to git
git add .
git commit -m "Deploy to Heroku"

# Deploy to Heroku
git push heroku main
```

### Option 3: AWS/GCP/Azure Deployment

#### Docker Deployment
1. **Create Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Build and Deploy**:
```bash
# Build Docker image
docker build -t healthcare-provider-app .

# Run locally
docker run -p 8501:8501 healthcare-provider-app

# Deploy to cloud platform of choice
```

## 📊 Application Features

### 🏠 Dashboard
- **Key Metrics**: Total providers, states covered, provider types
- **Interactive Charts**: Provider distribution, state comparisons
- **Real-time Data**: Live updates from the dataset

### 🗺️ Interactive Map
- **Provider Locations**: All 82,608 providers mapped
- **Color Coding**: Red (HCBS) vs Blue (ALF) providers
- **Filtering**: By state and provider type
- **Popups**: Detailed provider information

### 🤖 AI Agent
- **Natural Language Queries**: Ask questions in plain English
- **Smart Responses**: Context-aware answers about the data
- **Chat History**: Persistent conversation tracking
- **Suggested Questions**: Quick access to common queries

### 📊 Geographic Analysis
- **Density Heatmaps**: Provider concentration visualization
- **ZIP Code Analysis**: High and low density areas
- **State Statistics**: Geographic distribution metrics

### 🔍 Data Explorer
- **Interactive Filtering**: Filter by state and provider type
- **Data Table**: Browse and search provider records
- **Export Functionality**: Download filtered datasets

## 🔧 Configuration Options

### Environment Variables
```bash
# Optional: Set custom configuration
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
```

### Custom Styling
The app includes custom CSS for professional styling:
- **Color Scheme**: Healthcare-themed blue and red
- **Responsive Design**: Works on desktop and mobile
- **Professional Layout**: Clean, modern interface

## 📈 Performance Optimization

### Data Caching
- **Streamlit Cache**: Automatic caching of data loading
- **Efficient Queries**: Optimized database operations
- **Lazy Loading**: Load data only when needed

### Memory Management
- **Pandas Optimization**: Efficient data handling
- **Chart Rendering**: Optimized Plotly visualizations
- **Map Performance**: Efficient Folium map rendering

## 🔒 Security Considerations

### Data Privacy
- **No Sensitive Data**: Only public provider information
- **Secure Deployment**: HTTPS encryption
- **Access Control**: Configure as needed for your use case

### API Security
- **Rate Limiting**: Implement if using external APIs
- **Input Validation**: Sanitize user inputs
- **Error Handling**: Graceful error management

## 🐛 Troubleshooting

### Common Issues

#### 1. Data File Not Found
```bash
# Ensure data file exists
ls -la data/processed/providers_geocoded_tmp.csv

# Check file permissions
chmod 644 data/processed/providers_geocoded_tmp.csv
```

#### 2. Dependencies Issues
```bash
# Update pip
pip install --upgrade pip

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### 3. Port Conflicts
```bash
# Use different port
streamlit run app.py --server.port=8502
```

#### 4. Memory Issues
```bash
# Increase memory limit
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
```

### Debug Mode
```bash
# Run in debug mode
streamlit run app.py --logger.level=debug
```

## 📞 Support

### Getting Help
1. **Check Logs**: Review Streamlit Cloud or local logs
2. **Documentation**: Refer to Streamlit documentation
3. **Community**: Post issues on GitHub or Streamlit forums

### Monitoring
- **Health Checks**: Monitor application health
- **Performance**: Track response times and memory usage
- **User Analytics**: Monitor usage patterns (if enabled)

## 🚀 Next Steps

### Enhancements
1. **Advanced AI**: Integrate with OpenAI GPT or similar
2. **Real-time Data**: Connect to live data sources
3. **User Authentication**: Add login functionality
4. **Advanced Analytics**: Add predictive modeling
5. **Mobile App**: Create mobile-friendly version

### Scaling
1. **Load Balancing**: For high-traffic deployments
2. **Database Integration**: For larger datasets
3. **Caching Layer**: Redis for improved performance
4. **CDN**: For static asset delivery

---

**Your Streamlit app is now ready for deployment! Choose the deployment option that best fits your needs and start sharing your healthcare provider analysis with the world.**
