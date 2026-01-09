import streamlit as st
import sqlite3
from typing import List, Dict, Optional
import sys
import pandas as pd

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Page config
st.set_page_config(
    page_title="Toy Finder - TheElefant.ai",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, clean design
st.markdown("""
    <style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Clean card styling */
    .toy-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .toy-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }

    /* Image styling */
    .toy-image {
        border-radius: 8px;
        width: 100%;
        object-fit: cover;
        aspect-ratio: 1;
    }

    /* Price styling */
    .price-tag {
        color: #667eea;
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0;
    }

    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        margin: 4px 4px 4px 0;
        background: #f0f0f0;
    }

    .age-badge {
        background: #e3f2fd;
        color: #1976d2;
    }

    .type-badge {
        background: #f3e5f5;
        color: #7b1fa2;
    }

    /* List view styling */
    .list-item {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .list-item img {
        width: 100px;
        height: 100px;
        object-fit: cover;
        border-radius: 8px;
    }

    /* Stats badge */
    .stats-badge {
        background: rgba(255,255,255,0.2);
        padding: 5px 15px;
        border-radius: 20px;
        color: white;
        font-weight: 500;
    }

    /* Remove streamlit branding padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255,255,255,0.1);
        padding: 8px;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.2);
        color: white;
        border-radius: 6px;
        padding: 8px 16px;
    }

    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_connection():
    conn = sqlite3.connect('toys_new.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_toy_types(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT type FROM toys WHERE type IS NOT NULL ORDER BY type")
    return [row['type'] for row in cursor.fetchall()]

def get_price_range(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(price) as min_price, MAX(price) as max_price FROM toys WHERE price IS NOT NULL")
    result = cursor.fetchone()
    return (int(result['min_price']), int(result['max_price']))

def filter_toys(conn, age: Optional[float] = None, min_price: Optional[int] = None,
                max_price: Optional[int] = None, search_text: Optional[str] = None,
                toy_type: Optional[str] = None) -> List[Dict]:
    cursor = conn.cursor()

    query = """
        SELECT DISTINCT t.*,
               GROUP_CONCAT(DISTINCT f.name) as features
        FROM toys t
        LEFT JOIN toy_facilitates tf ON t.id = tf.toy_id
        LEFT JOIN facilitates f ON tf.facilitate_id = f.id
        WHERE 1=1
    """
    params = []

    # Age filter
    if age is not None:
        age_months = int(age * 12)
        query += " AND t.min_age <= ? AND t.max_age >= ?"
        params.extend([age_months, age_months])

    # Price filter
    if min_price is not None:
        query += " AND t.price >= ?"
        params.append(min_price)

    if max_price is not None:
        query += " AND t.price <= ?"
        params.append(max_price)

    # Search text filter
    if search_text:
        query += " AND (t.name LIKE ? OR t.short_description LIKE ?)"
        search_param = f"%{search_text}%"
        params.extend([search_param, search_param])

    # Toy type filter
    if toy_type and toy_type != "All Types":
        query += " AND t.type = ?"
        params.append(toy_type)

    query += " GROUP BY t.id ORDER BY t.price ASC"

    cursor.execute(query, params)
    results = cursor.fetchall()

    # Convert to list of dictionaries
    toys = []
    for row in results:
        toy_dict = dict(row)

        # Fetch images (prefer local_path over url)
        cursor.execute("SELECT url, local_path FROM images WHERE toy_id = ?", (toy_dict['id'],))
        toy_dict['images'] = [dict(img) for img in cursor.fetchall()]

        # Convert age to years
        if toy_dict.get('min_age'):
            toy_dict['min_age_years'] = toy_dict['min_age'] / 12
        if toy_dict.get('max_age'):
            toy_dict['max_age_years'] = toy_dict['max_age'] / 12

        toys.append(toy_dict)

    return toys

def sort_toys(toys: List[Dict], sort_by: str) -> List[Dict]:
    if sort_by == "Price: Low to High":
        return sorted(toys, key=lambda x: x.get('price', 0))
    elif sort_by == "Price: High to Low":
        return sorted(toys, key=lambda x: x.get('price', 0), reverse=True)
    elif sort_by == "Name: A to Z":
        return sorted(toys, key=lambda x: x.get('name', '').lower())
    elif sort_by == "Name: Z to A":
        return sorted(toys, key=lambda x: x.get('name', '').lower(), reverse=True)
    return toys

def render_toy_image(toy):
    """Render toy image with fallback"""
    if toy.get('images') and len(toy['images']) > 0:
        image = toy['images'][0]
        local_path = image.get('local_path', '')

        try:
            if local_path and local_path.strip():
                return local_path
            elif image.get('url'):
                return image['url']
        except:
            pass
    return None

def render_grid_view(toys):
    """Render toys in grid layout (3 columns)"""
    cols = st.columns(3)

    for idx, toy in enumerate(toys):
        with cols[idx % 3]:
            # Clean card container
            with st.container():
                # Image
                img_src = render_toy_image(toy)
                if img_src:
                    try:
                        st.image(img_src, use_column_width=True)
                    except:
                        st.info("🖼️ Image unavailable")

                # Title
                st.markdown(f"**{toy['name']}**")

                # Price
                st.markdown(f"<div class='price-tag'>₹{toy['price']}</div>", unsafe_allow_html=True)

                # Badges
                age_text = f"{toy.get('min_age_years', 0):.1f}-{toy.get('max_age_years', 0):.1f} yrs"
                type_text = toy['type'].replace('_', ' ').title() if toy.get('type') else ""

                badge_html = f"<span class='badge age-badge'>👶 {age_text}</span>"
                if type_text:
                    badge_html += f"<span class='badge type-badge'>{type_text}</span>"
                st.markdown(badge_html, unsafe_allow_html=True)

                # Description (shortened)
                if toy.get('short_description'):
                    desc = toy['short_description'][:100] + '...' if len(toy['short_description']) > 100 else toy['short_description']
                    st.caption(desc)

                # Link
                if toy.get('slug'):
                    st.markdown(f"[View Details →](https://www.theelefant.ai/toy/{toy['slug']})")

                st.divider()

def render_list_view(toys):
    """Render toys in list layout"""
    for toy in toys:
        col1, col2 = st.columns([1, 3])

        with col1:
            img_src = render_toy_image(toy)
            if img_src:
                try:
                    st.image(img_src, use_column_width=True)
                except:
                    st.info("🖼️ No image")

        with col2:
            st.markdown(f"### {toy['name']}")
            st.markdown(f"<div class='price-tag'>₹{toy['price']}</div>", unsafe_allow_html=True)

            # Badges
            age_text = f"{toy.get('min_age_years', 0):.1f}-{toy.get('max_age_years', 0):.1f} years"
            type_text = toy['type'].replace('_', ' ').title() if toy.get('type') else ""

            badge_html = f"<span class='badge age-badge'>👶 {age_text}</span>"
            if type_text:
                badge_html += f"<span class='badge type-badge'>{type_text}</span>"
            st.markdown(badge_html, unsafe_allow_html=True)

            # Description
            if toy.get('short_description'):
                st.write(toy['short_description'])

            # Link
            if toy.get('slug'):
                st.markdown(f"[View on TheElefant.ai →](https://www.theelefant.ai/toy/{toy['slug']})")

        st.divider()

def render_table_view(toys):
    """Render toys in table format"""
    table_data = []
    for toy in toys:
        age_range = f"{toy.get('min_age_years', 0):.1f}-{toy.get('max_age_years', 0):.1f}"
        toy_type = toy['type'].replace('_', ' ').title() if toy.get('type') else "N/A"

        table_data.append({
            "Name": toy['name'],
            "Price (₹)": f"₹{toy['price']}",
            "Age (years)": age_range,
            "Type": toy_type,
            "Link": f"https://www.theelefant.ai/toy/{toy['slug']}" if toy.get('slug') else ""
        })

    df = pd.DataFrame(table_data)

    # Display as interactive table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn("View Details")
        }
    )

# Main app
def main():
    conn = get_connection()

    # Header
    st.markdown("<h1 style='text-align: center; color: white;'>🎁 Toy Finder</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: white; font-size: 1.2em;'>Find the Perfect Toy for Your Daughter</p>", unsafe_allow_html=True)

    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters & Sorting")

        # Search
        search_text = st.text_input("🔍 Search", placeholder="Search by name or description...")

        # Age filter
        age = st.number_input(
            "👶 Child's Age (years)",
            min_value=0.0,
            max_value=12.0,
            step=0.5,
            value=None,
            placeholder="Optional"
        )

        # Price range
        st.subheader("💰 Budget")
        min_price_range, max_price_range = get_price_range(conn)
        price_range = st.slider(
            "Price Range (₹)",
            min_value=min_price_range,
            max_value=max_price_range,
            value=(min_price_range, max_price_range)
        )

        # Toy type
        toy_types = ["All Types"] + get_toy_types(conn)
        toy_type = st.selectbox("🎲 Toy Type", toy_types)

        # Sort
        sort_by = st.selectbox(
            "📊 Sort By",
            ["Price: Low to High", "Price: High to Low", "Name: A to Z", "Name: Z to A"]
        )

        st.divider()

        # Reset button
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.rerun()

    # Auto-fetch toys (no need to click a button)
    toys = filter_toys(
        conn,
        age=age if age else None,
        min_price=price_range[0],
        max_price=price_range[1],
        search_text=search_text if search_text else None,
        toy_type=toy_type if toy_type != "All Types" else None
    )

    # Sort toys
    toys = sort_toys(toys, sort_by)

    # Results header with count
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<h3 style='color: white;'>Found {len(toys)} toys</h3>", unsafe_allow_html=True)
    with col2:
        # View mode selector
        view_mode = st.selectbox(
            "View Mode",
            ["🎴 Grid", "📋 List", "📊 Table"],
            label_visibility="collapsed"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Display toys
    if toys:
        if view_mode == "🎴 Grid":
            render_grid_view(toys)
        elif view_mode == "📋 List":
            render_list_view(toys)
        else:  # Table
            render_table_view(toys)
    else:
        st.warning("😔 No toys found. Try adjusting your filters!")

if __name__ == "__main__":
    main()
