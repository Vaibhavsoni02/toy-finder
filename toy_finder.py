import sys
from database import ToyFilter
from typing import Optional, List

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class ToyFinder:
    def __init__(self):
        self.filter = ToyFilter()
        self.filter.connect()

    def display_toy(self, toy: dict, index: int):
        """Display a single toy in a formatted way"""
        print(f"\n{'='*80}")
        print(f"🎁 #{index}. {toy['name']}")
        print(f"{'='*80}")
        print(f"💰 Price: ₹{toy['price']}")
        print(f"👶 Age Range: {toy['min_age']//12}-{toy['max_age']//12} years ({toy['min_age']}-{toy['max_age']} months)")

        if toy['short_description']:
            print(f"📝 Description: {toy['short_description']}")

        if toy.get('features'):
            features = toy['features'].split(',')
            if features and features[0]:
                print(f"✨ Features: {', '.join(features)}")

        if toy.get('images'):
            print(f"🖼️  Images: {len(toy['images'])} available")
            if toy['images']:
                print(f"   View: {toy['images'][0]['url']}")

        if toy.get('slug'):
            print(f"🔗 URL: https://www.theelefant.ai/toy/{toy['slug']}")

    def search_by_age(self, age_years: float):
        """Search toys suitable for a specific age"""
        age_months = int(age_years * 12)
        print(f"\n🔍 Searching for toys suitable for {age_years} year old child...")

        toys = self.filter.filter_toys(min_age=age_months, max_age=age_months)

        if not toys:
            print("❌ No toys found for this age range.")
            return []

        print(f"\n✅ Found {len(toys)} toys suitable for this age!")
        return toys

    def search_by_criteria(self,
                          age_years: Optional[float] = None,
                          min_price: Optional[float] = None,
                          max_price: Optional[float] = None,
                          search_text: Optional[str] = None,
                          features: Optional[List[str]] = None,
                          limit: int = 20):
        """Search toys with multiple criteria"""
        print("\n🔍 Searching for toys with your criteria...")

        age_months = int(age_years * 12) if age_years else None

        toys = self.filter.filter_toys(
            min_age=age_months,
            max_age=age_months,
            min_price=min_price,
            max_price=max_price,
            search_text=search_text,
            features=features,
            limit=limit
        )

        if not toys:
            print("❌ No toys found matching your criteria.")
            return []

        print(f"\n✅ Found {len(toys)} toys!")
        return toys

    def interactive_search(self):
        """Interactive search interface"""
        print("\n" + "="*80)
        print("🎯 TOY FINDER - Find the Perfect Toy for Your Daughter!")
        print("="*80)

        # Get daughter's age
        while True:
            try:
                age_input = input("\n👶 How old is your daughter? (in years, e.g., 2.5): ")
                age_years = float(age_input)
                if age_years < 0 or age_years > 12:
                    print("⚠️  Please enter an age between 0 and 12 years.")
                    continue
                break
            except ValueError:
                print("⚠️  Please enter a valid number.")

        # Get price range
        print("\n💰 What's your budget?")
        min_price, max_price = self.filter.get_price_range()
        print(f"   Available price range: ₹{min_price} - ₹{max_price}")

        budget_min = None
        budget_max = None

        budget_input = input(f"   Enter max budget (press Enter for no limit): ").strip()
        if budget_input:
            try:
                budget_max = float(budget_input)
            except ValueError:
                print("⚠️  Invalid budget, ignoring price filter.")

        # Get search keywords
        search_text = input("\n🔍 Any keywords to search for? (e.g., 'puzzle', 'educational', press Enter to skip): ").strip()
        if not search_text:
            search_text = None

        # Get features
        print("\n✨ Available features:")
        available_features = self.filter.get_available_features()
        for i, feature in enumerate(available_features[:20], 1):  # Show first 20
            print(f"   {i}. {feature}")

        if len(available_features) > 20:
            print(f"   ... and {len(available_features) - 20} more")

        feature_input = input("\n   Enter feature numbers (comma-separated, or press Enter to skip): ").strip()
        selected_features = None
        if feature_input:
            try:
                indices = [int(x.strip()) - 1 for x in feature_input.split(',')]
                selected_features = [available_features[i] for i in indices if 0 <= i < len(available_features)]
            except (ValueError, IndexError):
                print("⚠️  Invalid feature selection, skipping feature filter.")

        # Perform search
        toys = self.search_by_criteria(
            age_years=age_years,
            min_price=budget_min,
            max_price=budget_max,
            search_text=search_text,
            features=selected_features,
            limit=50
        )

        # Display results
        if toys:
            for i, toy in enumerate(toys, 1):
                self.display_toy(toy, i)

            print(f"\n{'='*80}")
            print(f"📊 Total: {len(toys)} toys found")
            print(f"{'='*80}")

        return toys

    def quick_search(self):
        """Quick search with just age"""
        print("\n" + "="*80)
        print("⚡ QUICK SEARCH - Enter your daughter's age")
        print("="*80)

        while True:
            try:
                age_input = input("\n👶 Age in years (e.g., 2.5): ")
                age_years = float(age_input)
                if age_years < 0 or age_years > 12:
                    print("⚠️  Please enter an age between 0 and 12 years.")
                    continue
                break
            except ValueError:
                print("⚠️  Please enter a valid number.")

        toys = self.search_by_age(age_years)

        # Display top 10 results
        display_count = min(10, len(toys))
        for i in range(display_count):
            self.display_toy(toys[i], i + 1)

        if len(toys) > 10:
            print(f"\n... and {len(toys) - 10} more toys available!")
            show_all = input("\nShow all results? (y/n): ").strip().lower()
            if show_all == 'y':
                for i in range(10, len(toys)):
                    self.display_toy(toys[i], i + 1)

        print(f"\n{'='*80}")
        print(f"📊 Total: {len(toys)} toys found")
        print(f"{'='*80}")

        return toys

    def main_menu(self):
        """Main menu interface"""
        while True:
            print("\n" + "="*80)
            print("🎯 TOY FINDER - Main Menu")
            print("="*80)
            print("1. ⚡ Quick Search (by age only)")
            print("2. 🔍 Advanced Search (with filters)")
            print("3. 📊 Browse All Features")
            print("4. 📈 Show Statistics")
            print("5. 🚪 Exit")
            print("="*80)

            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == '1':
                self.quick_search()
            elif choice == '2':
                self.interactive_search()
            elif choice == '3':
                self.show_features()
            elif choice == '4':
                self.show_statistics()
            elif choice == '5':
                print("\n👋 Thank you for using Toy Finder! Happy toy shopping!")
                break
            else:
                print("⚠️  Invalid choice, please try again.")

    def show_features(self):
        """Show all available features"""
        print("\n" + "="*80)
        print("✨ ALL AVAILABLE FEATURES")
        print("="*80)
        features = self.filter.get_available_features()
        for i, feature in enumerate(features, 1):
            print(f"{i:3d}. {feature}")
        print(f"\n📊 Total: {len(features)} features")

    def show_statistics(self):
        """Show database statistics"""
        print("\n" + "="*80)
        print("📈 DATABASE STATISTICS")
        print("="*80)

        # Age ranges
        age_ranges = self.filter.get_age_ranges()
        print(f"\n👶 Age Ranges Available:")
        age_range_summary = {}
        for ar in age_ranges:
            key = f"{ar['min_age']//12}-{ar['max_age']//12} years"
            age_range_summary[key] = age_range_summary.get(key, 0) + 1

        for age_range, count in sorted(age_range_summary.items()):
            print(f"   {age_range}: {count} toys")

        # Price range
        min_price, max_price = self.filter.get_price_range()
        print(f"\n💰 Price Range: ₹{min_price} - ₹{max_price}")

        # Toy types
        toy_types = self.filter.get_toy_types()
        print(f"\n🎲 Toy Types: {len(toy_types)} types")
        for toy_type in toy_types:
            print(f"   - {toy_type}")

        # Features
        features = self.filter.get_available_features()
        print(f"\n✨ Features: {len(features)} unique features")

    def close(self):
        """Close database connection"""
        self.filter.close()

def main():
    """Main entry point"""
    finder = ToyFinder()

    try:
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == 'quick':
                finder.quick_search()
            else:
                try:
                    age = float(sys.argv[1])
                    toys = finder.search_by_age(age)
                    for i, toy in enumerate(toys[:10], 1):
                        finder.display_toy(toy, i)
                except ValueError:
                    print("Usage: python toy_finder.py [age_in_years|quick]")
        else:
            # Interactive mode
            finder.main_menu()
    finally:
        finder.close()

if __name__ == "__main__":
    main()
