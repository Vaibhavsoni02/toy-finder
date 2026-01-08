import streamlit as st
import sqlite3
from typing import List, Dict, Optional
import sys

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

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stats-badge {
        background: rgba(255,255,255,0.2);
        padding: 5px 15px;
        border-radius: 20px;
        color: white;
        font-weight: 500;
    }
    /* Make containers look like cards */
    .element-container {
        background: white;
        border-radius: 8px;
        padding: 5px;
    }
    /* Style images */
    img {
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_connection():
    conn = sqlite3.connect('toys.db', check_same_thread=False)
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

        # Fetch images
        cursor.execute("SELECT url FROM images WHERE toy_id = ?", (toy_dict['id'],))
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

# Main app
def main():
    conn = get_connection()

    # Header
    st.markdown("<h1 style='text-align: center; color: white;'>🎁 Toy Finder</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: white; font-size: 1.2em;'>Find the Perfect Toy for Your Daughter <span class='stats-badge'>586 unique toys</span></p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")

        # Age filter
        age = st.number_input("👶 Child's Age (years)", min_value=0.0, max_value=12.0, step=0.5, value=None, placeholder="e.g., 2.5")

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

        # Search
        search_text = st.text_input("🔍 Search Keywords", placeholder="e.g., puzzle, educational")

        # Sort
        sort_by = st.selectbox(
            "📊 Sort By",
            ["Price: Low to High", "Price: High to Low", "Name: A to Z", "Name: Z to A"]
        )

        # Search button
        search_clicked = st.button("🎯 Find Toys", use_container_width=True)

        # Reset button
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.rerun()

    # Main content
    if search_clicked or 'searched' in st.session_state:
        st.session_state['searched'] = True

        # Filter toys
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

        # Display count
        st.markdown(f"<h3 style='color: white;'>Found {len(toys)} toys</h3>", unsafe_allow_html=True)

        if toys:
            # Display toys in 3 columns
            cols = st.columns(3)

            for idx, toy in enumerate(toys):
                col = cols[idx % 3]

                with col:
                    # Container for each toy
                    with st.container():
                        # Display image first
                        if toy.get('images') and len(toy['images']) > 0:
                            try:
                                st.image(toy['images'][0]['url'], use_container_width=True)
                            except Exception as e:
                                st.write("🖼️ Image unavailable")

                        # Toy details
                        st.markdown(f"**{toy['name']}**")
                        st.markdown(f"<h3 style='color: #667eea; margin: 5px 0;'>₹{toy['price']}</h3>", unsafe_allow_html=True)

                        # Age and type badges
                        age_badge = f"👶 {toy.get('min_age_years', 0):.1f}-{toy.get('max_age_years', 0):.1f} years"
                        type_badge = f" • {toy['type'].replace('_', ' ')}" if toy.get('type') else ""
                        st.caption(age_badge + type_badge)

                        # Description
                        if toy.get('short_description'):
                            desc = toy['short_description'][:120] + '...' if len(toy['short_description']) > 120 else toy['short_description']
                            st.write(desc)

                        # View details link
                        if toy.get('slug'):
                            st.markdown(f"[View Details →](https://www.theelefant.ai/toy/{toy['slug']})")

                        st.divider()
        else:
            st.warning("😔 No toys found. Try adjusting your filters!")
    else:
        st.info("👈 Use the filters on the left and click 'Find Toys' to see all 586 toys!")

if __name__ == "__main__":
    main()
