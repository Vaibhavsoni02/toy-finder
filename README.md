# 🎁 Toy Finder - TheElefant.ai Toy Database & Filter System

A complete toy scraping and filtering system for finding the perfect toy for your daughter from TheElefant.ai's catalogue.

## 📊 What This System Does

1. **Scrapes** all toys from TheElefant.ai using their GraphQL API
2. **Downloads** 1,508 toy images locally for reliable offline access
3. **Stores** 434 unique toys with images in a local SQLite database
4. **Filters** toys by age, price, type, and keywords
5. **Provides** both CLI and Web interfaces with sorting

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Scrape Toy Data & Images (Already Done!)

**Toy data and images have been downloaded:**
- **434 unique toys** with complete information
- **1,508 images** downloaded locally (572MB in `toy_images/` directory)
- **Images stored permanently** - no more expiring CDN URLs!
- Age ranges: 0-12 years
- Price range: ₹195 - ₹5,499

Files included:
- `toys_complete_with_local_images.json` - Full toy data with local image paths
- `toys_new.db` - SQLite database with local image references
- `toy_images/` - All downloaded toy images

To re-scrape fresh data with images:
```bash
python scrape_and_download.py  # Scrapes and downloads images immediately
python merge_data_with_local_images.py  # Merges with complete data
python migrate_to_local_images.py  # Updates database
```

### 3. Database Setup (Already Done!)

The database `toys_new.db` includes:
- Full toy details (name, price, age, description, type)
- Local image paths that work offline
- No more expired CDN URLs!

### 4. Use the Toy Finder

#### Option A: Streamlit Web App (Recommended) 🌟

```bash
streamlit run streamlit_app.py
```

Opens automatically at: **http://localhost:8501**

Features:
- 🎨 Beautiful, modern Streamlit interface
- 👶 Filter by child's age
- 💰 Price range sliders
- 🎲 Filter by toy type (TOY/BOOK/BIG_TOY)
- 🔍 Search by keywords
- 📊 Sort by price or name
- 📱 Responsive design
- 🚀 Easy to deploy on Streamlit Cloud

#### Option B: Flask Web Interface

```bash
python web_app.py
```

Access at: **http://localhost:5000**

#### Option C: Command Line Interface

**Interactive Menu:**
```bash
python toy_finder.py
```

**Quick Search (by age only):**
```bash
python toy_finder.py quick
```

**Direct Age Search:**
```bash
python toy_finder.py 3.5
```
This will show all toys suitable for a 3.5 year old.

## 🌐 Deploy to Streamlit Cloud

1. **Push to GitHub** (see instructions below)
2. Go to https://streamlit.io/cloud
3. Sign in with GitHub
4. Click "New app"
5. Select this repository
6. Set main file: `streamlit_app.py`
7. Click "Deploy"

Done! Your app will be live in minutes. See [DEPLOYMENT.md](DEPLOYMENT.md) for more options.

## 📁 Project Files

- **streamlit_app.py** - Streamlit web interface (recommended)
- **web_app.py** - Flask web application
- **scraper.py** - Scrapes toy data from TheElefant.ai API
- **database.py** - Database setup and filter logic
- **toy_finder.py** - CLI interface for finding toys
- **templates/index.html** - Flask web interface template
- **toys_data.json** - Raw scraped data (669 entries)
- **toys.db** - SQLite database with 586 unique toys

## 🎯 How the Scraping Works

The original API had a limit of 12 toys per request. We bypassed this by:

1. Making an initial request to get the total count (669 toys)
2. Using pagination with the `skip` parameter
3. Making 56 requests with skip values: 0, 12, 24, 36... up to 660
4. Combining all results into a complete dataset

**GraphQL Query Used:**
- Endpoint: `https://server.theelefant.com/main-server/graphql`
- Operation: `PincodeToysListing`
- Parameters: `limit`, `skip`, `pincodeId`, filters, sorting

## 🔍 Available Filters

- **Age**: Filter toys suitable for specific age (in years)
- **Price**: Set min/max budget with range sliders
- **Toy Type**: Filter by TOY (467), BOOK (115), or BIG_TOY (4)
- **Keywords**: Search in toy name and description
- **Sorting**: Sort by price or name (ascending/descending)

## 📊 Database Schema

**Tables:**
1. **toys** - Main toy information (id, name, price, description, age range)
2. **images** - Toy images with URLs
3. **facilitates** - Features/benefits (educational, cognitive, etc.)
4. **toy_facilitates** - Links toys to their features

## 💡 Example Searches

**Find toys for a 3 year old under ₹1000:**
- Age: 3
- Max Price: 1000

**Find educational puzzles:**
- Keywords: "puzzle"
- Features: "Educational", "Cognitive Development"

**Find toys for 2-3 year olds with motor skill development:**
- Age: 2.5
- Features: "Motor Skills"

## 🛠️ Advanced Usage

### Modify the Scraper

Edit `scraper.py` to:
- Change the `limit` parameter (default: 12)
- Add delay between requests (default: 0.5s)
- Filter by different pincodes or libraries

### Extend the Database

Edit `database.py` to:
- Add more filter options
- Create custom queries
- Add sorting options

### Customize Web Interface

Edit `templates/index.html` to:
- Change colors and styling
- Add more filter options
- Modify layout

## 📈 Statistics

- **Total Unique Toys**: 586
- **Total Entries**: 669 (includes duplicates across inventories)
- **Toy Types**:
  - TOY: 467 items
  - BOOK: 115 items
  - BIG_TOY: 4 items
- **Age Groups**:
  - 0-1 years: 21 toys
  - 1-3 years: 277 toys
  - 3-5 years: 218 toys
  - 5-8 years: 62 toys
  - 8-12 years: 91 toys
- **Price Range**: ₹195 - ₹5,499
- **Average Price**: ₹1,004

## 🎉 Success!

You now have:
- ✅ Complete toy database (586 unique toys)
- ✅ Powerful filtering and sorting system
- ✅ Beautiful web interface
- ✅ CLI tool for quick searches
- ✅ All data stored locally for fast access

**Happy toy hunting for your daughter! 🎁**
