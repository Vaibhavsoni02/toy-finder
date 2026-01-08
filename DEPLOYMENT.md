# 🚀 Deployment Guide

## Run with Streamlit Locally

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd toy-database
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the Streamlit app**
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Run with Flask (Alternative)

```bash
python web_app.py
```

Access at `http://localhost:5000`

## Deploy to Streamlit Cloud

1. **Push to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `streamlit_app.py`
   - Click "Deploy"

## Deploy to Heroku (Flask)

1. **Create a Procfile**
```
web: python web_app.py
```

2. **Deploy**
```bash
heroku create your-app-name
git push heroku main
```

## Deploy to Railway

1. Go to https://railway.app
2. Connect your GitHub repository
3. Railway will auto-detect and deploy

## Environment Requirements

- Python 3.8+
- SQLite database (included: `toys.db`)
- All dependencies in `requirements.txt`

## Files Included

- ✅ `toys.db` - SQLite database with 586 toys
- ✅ `toys_data.json` - Raw scraped data
- ✅ `streamlit_app.py` - Streamlit web interface
- ✅ `web_app.py` - Flask web interface
- ✅ All supporting Python files

## Notes

- The database is already populated and ready to use
- No API keys required
- No additional setup needed
- Just install dependencies and run!
