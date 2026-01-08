from flask import Flask, render_template, request, jsonify
from database import ToyFilter
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

app = Flask(__name__)
toy_filter = ToyFilter()
toy_filter.connect()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/features')
def get_features():
    """Get all available features"""
    features = toy_filter.get_available_features()
    return jsonify(features)

@app.route('/api/price-range')
def get_price_range():
    """Get price range"""
    min_price, max_price = toy_filter.get_price_range()
    return jsonify({'min': min_price, 'max': max_price})

@app.route('/api/age-ranges')
def get_age_ranges():
    """Get all age ranges"""
    age_ranges = toy_filter.get_age_ranges()
    return jsonify(age_ranges)

@app.route('/api/toy-types')
def get_toy_types():
    """Get all toy types"""
    toy_types = toy_filter.get_toy_types()
    return jsonify(toy_types)

@app.route('/api/search', methods=['POST'])
def search_toys():
    """Search toys based on filters"""
    data = request.json

    age_years = data.get('age')
    age_months = int(float(age_years) * 12) if age_years else None

    min_price = data.get('min_price')
    max_price = data.get('max_price')
    search_text = data.get('search_text')
    toy_type = data.get('toy_type')
    sort_by = data.get('sort_by', 'price_asc')

    toys = toy_filter.filter_toys(
        min_age=age_months,
        max_age=age_months,
        min_price=min_price,
        max_price=max_price,
        search_text=search_text,
        toy_type=toy_type,
        features=None,
        limit=None
    )

    # Format toys for JSON
    result = []
    for toy in toys:
        toy_dict = dict(toy)
        # Convert age from months to years for display
        if toy_dict.get('min_age'):
            toy_dict['min_age_years'] = toy_dict['min_age'] / 12
        if toy_dict.get('max_age'):
            toy_dict['max_age_years'] = toy_dict['max_age'] / 12

        result.append(toy_dict)

    # Sort results
    if sort_by == 'price_asc':
        result.sort(key=lambda x: x.get('price', 0))
    elif sort_by == 'price_desc':
        result.sort(key=lambda x: x.get('price', 0), reverse=True)
    elif sort_by == 'name_asc':
        result.sort(key=lambda x: x.get('name', '').lower())
    elif sort_by == 'name_desc':
        result.sort(key=lambda x: x.get('name', '').lower(), reverse=True)

    return jsonify({
        'count': len(result),
        'toys': result
    })

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🌐 Starting Toy Finder Web Application")
    print("="*80)
    print("\n🚀 Server starting at http://localhost:5000")
    print("📱 Open this URL in your web browser")
    print("\n💡 Press Ctrl+C to stop the server")
    print("="*80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
