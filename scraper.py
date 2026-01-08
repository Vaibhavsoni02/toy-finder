import requests
import json
import time
import sys
from typing import List, Dict

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class ElefantScraper:
    def __init__(self):
        self.api_url = "https://server.theelefant.com/main-server/graphql"
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/json",
            "origin": "https://www.theelefant.ai",
            "referer": "https://www.theelefant.ai/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        }
        self.all_toys = []

    def build_query(self, limit: int, skip: int) -> Dict:
        """Build the GraphQL query with pagination parameters"""
        return {
            "operationName": "PincodeToysListing",
            "variables": {
                "where": {
                    "id": "c34fbe5b-4c9c-479d-b182-98be79856cf5"
                },
                "filter": {
                    "ageGroupIds": [],
                    "categoryIds": [],
                    "brandIds": [],
                    "facilitateIds": [],
                    "pincodeId": "07fcc988-5747-44b4-a1fc-35230d96e0c4",
                    "tagIds": [],
                    "limit": limit,
                    "skip": skip,
                    "toyTypes": []
                },
                "sort": {
                    "field": "name",
                    "order": "ASC"
                }
            },
            "query": """query PincodeToysListing($where: LibraryUniqueInput, $sort: LibraryInventorySort, $filter: LibraryInventoryFilter) {
  pincodeToysListing(where: $where, sort: $sort, filter: $filter) {
    count
    data {
      id
      createdAt
      availableStock
      toy {
        id
        name
        price
        shortDescription
        slug
        images {
          url
          key
          __typename
        }
        facilitates {
          id
          image
          isArchived
          name
          __typename
        }
        ageGroup {
          id
          maxAge
          minAge
          __typename
        }
        type
        __typename
      }
      __typename
    }
    __typename
  }
}"""
        }

    def fetch_page(self, limit: int, skip: int) -> Dict:
        """Fetch a single page of toys"""
        query = self.build_query(limit, skip)

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=query,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching page (skip={skip}): {e}")
            return None

    def scrape_all_toys(self, limit: int = 12) -> List[Dict]:
        """Scrape all toys by paginating through the API"""
        print("🎯 Starting toy data extraction...")

        # First request to get total count
        print("📊 Fetching total count...")
        first_page = self.fetch_page(limit, 0)

        if not first_page or 'data' not in first_page:
            print("❌ Failed to fetch initial data")
            return []

        total_count = first_page['data']['pincodeToysListing']['count']
        print(f"✅ Found {total_count} total toys!")

        # Add first page toys
        self.all_toys.extend(first_page['data']['pincodeToysListing']['data'])
        print(f"📦 Fetched toys 1-{min(limit, total_count)}")

        # Calculate number of remaining requests needed
        remaining = total_count - limit
        skip = limit

        # Fetch remaining pages
        while skip < total_count:
            time.sleep(0.5)  # Be polite to the server

            page_data = self.fetch_page(limit, skip)

            if page_data and 'data' in page_data:
                toys_in_page = page_data['data']['pincodeToysListing']['data']
                self.all_toys.extend(toys_in_page)
                end_range = min(skip + limit, total_count)
                print(f"📦 Fetched toys {skip + 1}-{end_range}")
            else:
                print(f"⚠️  Failed to fetch page at skip={skip}")

            skip += limit

        print(f"\n✨ Successfully scraped {len(self.all_toys)} toys!")
        return self.all_toys

    def save_to_json(self, filename: str = "toys_data.json"):
        """Save scraped toys to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_toys, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved all toy data to {filename}")

    def get_statistics(self):
        """Print statistics about the scraped toys"""
        if not self.all_toys:
            print("No toys scraped yet!")
            return

        print("\n" + "="*50)
        print("📊 TOY COLLECTION STATISTICS")
        print("="*50)

        # Total toys
        print(f"Total Toys: {len(self.all_toys)}")

        # Age range statistics
        age_ranges = {}
        for item in self.all_toys:
            toy = item.get('toy', {})
            age_group = toy.get('ageGroup', {})
            if age_group:
                min_age = age_group.get('minAge', 'N/A')
                max_age = age_group.get('maxAge', 'N/A')
                age_key = f"{min_age}-{max_age} years"
                age_ranges[age_key] = age_ranges.get(age_key, 0) + 1

        print(f"\n📅 Age Groups:")
        for age_range, count in sorted(age_ranges.items()):
            print(f"  {age_range}: {count} toys")

        # Price statistics
        prices = []
        for item in self.all_toys:
            toy = item.get('toy', {})
            price = toy.get('price')
            if price:
                prices.append(price)

        if prices:
            print(f"\n💰 Price Range:")
            print(f"  Minimum: ₹{min(prices)}")
            print(f"  Maximum: ₹{max(prices)}")
            print(f"  Average: ₹{sum(prices)/len(prices):.2f}")

        # Available toys
        available = sum(1 for item in self.all_toys if item.get('availableStock', 0) > 0)
        print(f"\n📦 Availability:")
        print(f"  Available: {available} toys")
        print(f"  Out of Stock: {len(self.all_toys) - available} toys")

        print("="*50 + "\n")

if __name__ == "__main__":
    scraper = ElefantScraper()

    # Scrape all toys
    toys = scraper.scrape_all_toys(limit=12)

    # Save to JSON
    if toys:
        scraper.save_to_json("toys_data.json")
        scraper.get_statistics()
    else:
        print("❌ No toys were scraped!")
