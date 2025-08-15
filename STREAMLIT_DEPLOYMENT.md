# **Streamlit Cloud Deployment Guide**

## **🚀 Deploy to Streamlit Cloud**

This guide will help you deploy your Addis Care Medicaid Crisis Analysis app to Streamlit Cloud for free hosting.

## **📋 Prerequisites**

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Streamlit Cloud Account** - Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Repository Structure** - Ensure your files are properly organized

## **📁 Required Files**

Make sure these files are in your GitHub repository:

```
kelper/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── .gitignore               # Git ignore rules
└── data/                    # Data files (optional for demo)
```

## **🔧 Deployment Steps**

### **Step 1: Prepare Your Repository**

1. **Push to GitHub** - Ensure your code is pushed to a public GitHub repository
2. **Check File Structure** - Verify all required files are present
3. **Test Locally** - Run `streamlit run streamlit_app.py` locally first

### **Step 2: Deploy to Streamlit Cloud**

1. **Go to Streamlit Cloud** - Visit [share.streamlit.io](https://share.streamlit.io)
2. **Sign In** - Use your GitHub account to sign in
3. **New App** - Click "New app"
4. **Repository Settings**:
   - **Repository**: Select your GitHub repository
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `streamlit_app.py`
   - **App URL**: Choose a custom URL (optional)

### **Step 3: Configure App Settings**

1. **Advanced Settings** (if needed):
   - **Python version**: 3.9 or higher
   - **Memory**: Default (1GB should be sufficient)
   - **Timeout**: Default (30 seconds)

2. **Environment Variables** (if needed):
   - Add any API keys or configuration variables
   - For this app, no environment variables are required

### **Step 4: Deploy**

1. **Click "Deploy"** - Streamlit Cloud will build and deploy your app
2. **Wait for Build** - This usually takes 2-5 minutes
3. **Access Your App** - Your app will be available at the provided URL

## **✅ Deployment Checklist**

- [ ] Repository is public on GitHub
- [ ] `streamlit_app.py` is the main file
- [ ] `requirements.txt` includes all dependencies
- [ ] App runs locally without errors
- [ ] No large data files (>100MB) in repository
- [ ] No sensitive information in code

## **🔍 Troubleshooting**

### **Common Issues**

1. **Import Errors**
   - Check `requirements.txt` includes all packages
   - Ensure package versions are compatible

2. **Data File Not Found**
   - The app will use sample data if real data is not available
   - Check file paths in `streamlit_app.py`

3. **Memory Issues**
   - Reduce data size or optimize code
   - Use data sampling for large datasets

4. **Build Failures**
   - Check Streamlit Cloud logs for error messages
   - Verify Python version compatibility

### **Performance Optimization**

1. **Data Loading**
   - Use `@st.cache_data` for expensive operations
   - Load only necessary data columns
   - Implement data sampling for large datasets

2. **Visualizations**
   - Limit map markers to reasonable numbers
   - Use efficient plotting libraries
   - Cache expensive computations

## **🌐 App Features**

Your deployed app will include:

- **📊 Dashboard** - Key metrics and visualizations
- **🗺️ Interactive Map** - Provider locations
- **📈 Geographic Analysis** - Density and distribution
- **🤖 AI Agent** - Natural language queries
- **🔍 Data Explorer** - Filter and search data
- **🚨 Medicaid Crisis Analysis** - Risk assessment

## **🔗 Sharing Your App**

Once deployed, you can:

1. **Share the URL** - Anyone can access your app
2. **Embed in Websites** - Use iframe embedding
3. **Custom Domain** - Set up custom domain (paid feature)
4. **Team Access** - Invite team members (paid feature)

## **📈 Monitoring**

Streamlit Cloud provides:

- **Usage Analytics** - Track app usage
- **Performance Metrics** - Monitor app performance
- **Error Logs** - Debug issues
- **Deployment History** - Track changes

## **🔄 Updates**

To update your app:

1. **Push Changes** - Update your GitHub repository
2. **Auto-Deploy** - Streamlit Cloud automatically redeploys
3. **Manual Deploy** - Or trigger manual deployment from dashboard

## **💡 Best Practices**

1. **Keep Dependencies Minimal** - Only include necessary packages
2. **Optimize Data Loading** - Use caching and efficient data structures
3. **Handle Errors Gracefully** - Provide fallbacks for missing data
4. **Test Thoroughly** - Test locally before deploying
5. **Document Your App** - Include clear instructions for users

## **🎯 Next Steps**

After deployment:

1. **Test All Features** - Ensure everything works as expected
2. **Share with Stakeholders** - Get feedback from users
3. **Monitor Usage** - Track how people use your app
4. **Iterate and Improve** - Make updates based on feedback

---

**Your Addis Care Medicaid Crisis Analysis app will be live and accessible to anyone with the URL!**
