# 🚀 GitHub Setup & Deployment Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `toy-finder` (or your preferred name)
3. Description: "Toy database and finder for TheElefant.ai - 586 unique toys with filtering and sorting"
4. Choose **Public** (required for free Streamlit deployment)
5. **DON'T** initialize with README (we already have one)
6. Click "Create repository"

## Step 2: Push to GitHub

Run these commands in your terminal:

```bash
cd "C:\Users\netway\claudeprojects\toy database"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/toy-finder.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Sign in with your GitHub account
3. Click "New app"
4. Select:
   - **Repository**: YOUR_USERNAME/toy-finder
   - **Branch**: main
   - **Main file path**: streamlit_app.py
5. Click "Deploy!"

**Done!** Your app will be live at: `https://YOUR_USERNAME-toy-finder.streamlit.app`

## Step 4: Share Your App

Once deployed, you'll get a public URL like:
```
https://your-username-toy-finder.streamlit.app
```

Share this URL with anyone - no login required!

## Troubleshooting

### If deployment fails:

1. **Check requirements.txt** - Make sure all dependencies are listed
2. **Check file paths** - Ensure `toys.db` and `toys_data.json` are committed
3. **Check logs** - Streamlit Cloud shows deployment logs
4. **Python version** - Streamlit Cloud uses Python 3.9-3.11

### If database is missing:

The repository should include:
- ✅ `toys.db` (SQLite database)
- ✅ `toys_data.json` (backup data)

These files are committed to git and will be included in deployment.

## Updating Your App

To push updates:

```bash
git add .
git commit -m "Update description"
git push
```

Streamlit Cloud will automatically redeploy!

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit locally
streamlit run streamlit_app.py

# Run Flask locally
python web_app.py
```

## Repository Size

- Total size: ~50 MB
- Main files:
  - `toys_data.json`: ~45 MB
  - `toys.db`: ~3 MB
  - All Python files: ~100 KB

This is within GitHub's size limits (100 MB per file, 1 GB per repo).
