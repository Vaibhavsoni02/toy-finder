"""
Scrape toy data and immediately download images before URLs expire
"""
import requests
import json
import time
import os
from pathlib import Path
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Create images directory
images_dir = Path("toy_images")
images_dir.mkdir(exist_ok=True)

class ToyScraperWithImages:
    def __init__(self):
        self.api_url = "https://server.theelefant.com/main-server/graphql"
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/json",
            "origin": "https://www.theelefant.ai",
            "referer": "https://www.theelefant.ai/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.all_toys = []
        self.downloaded_images = 0
        self.failed_images = 0

    def build_query(self, limit: int, skip: int):
        return {
            "operationName": "PincodeToysListing",
            "variables": {
                "where": {"id": "c34fbe5b-4c9c-479d-b182-98be79856cf5"},
                "filter": {
                    "ageGroupIds": [], "categoryIds": [], "brandIds": [],
                    "facilitateIds": [],
                    "pincodeId": "07fcc988-5747-44b4-a1fc-35230d96e0c4",
                    "tagIds": [], "limit": limit, "skip": skip, "toyTypes": []
                },
                "sort": {"field": "name", "order": "ASC"}
            },
            "query": """query PincodeToysListing($where: LibraryUniqueInput, $sort: LibraryInventorySort, $filter: LibraryInventoryFilter) {
  pincodeToysListing(where: $where, sort: $sort, filter: $filter) {
    count
    data {
      id
      toy {
        id
        name
        slug
        images {
          url
          key
        }
      }
    }
  }
}"""
        }

    def download_image(self, url, toy_id, img_index):
        """Download a single image"""
        filename = f"{toy_id}_{img_index}.jpg"
        filepath = images_dir / filename

        # Skip if exists
        if filepath.exists():
            return str(filepath)

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                self.downloaded_images += 1
                return str(filepath)
            else:
                self.failed_images += 1
                return None
        except Exception as e:
            self.failed_images += 1
            print(f"Error downloading: {e}")
            return None

    def scrape_and_download(self, limit=12):
        print("🎯 Scraping toys and downloading images...")
        print("=" * 60)

        # First request
        page = self.fetch_page(limit, 0)
        if not page or 'data' not in page:
            print("❌ Failed to fetch data")
            return []

        total_count = page['data']['pincodeToysListing']['count']
        print(f"✅ Found {total_count} total toys\n")

        # Process first page
        self.process_page(page, 1, limit, total_count)

        # Fetch remaining pages
        skip = limit
        page_num = 2
        while skip < total_count:
            time.sleep(0.5)
            page = self.fetch_page(limit, skip)

            if page and 'data' in page:
                self.process_page(page, page_num, limit, total_count)
                page_num += 1

            skip += limit

        print(f"\n✨ Scraping complete!")
        print(f"📦 Total toys: {len(self.all_toys)}")
        print(f"📷 Images downloaded: {self.downloaded_images}")
        print(f"❌ Failed images: {self.failed_images}")

        return self.all_toys

    def process_page(self, page_data, page_num, limit, total):
        """Process a page and download images immediately"""
        toys = page_data['data']['pincodeToysListing']['data']

        for item in toys:
            toy = item.get('toy', {})
            if not toy:
                continue

            # Download images immediately
            local_images = []
            for idx, image in enumerate(toy.get('images', [])):
                url = image.get('url')
                if url:
                    local_path = self.download_image(url, toy['id'], idx)
                    if local_path:
                        local_images.append({
                            'url': url,  # Keep original
                            'local_path': local_path,
                            'key': image.get('key')
                        })

            # Update toy with local paths
            toy['images'] = local_images
            self.all_toys.append(item)

        end_idx = min(page_num * limit, total)
        print(f"📦 Page {page_num}: Processed toys {(page_num-1)*limit + 1}-{end_idx} | Images: {self.downloaded_images}")

    def fetch_page(self, limit, skip):
        query = self.build_query(limit, skip)
        try:
            response = requests.post(self.api_url, headers=self.headers, json=query, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None

    def save_to_json(self, filename="toys_with_local_images.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_toys, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved to {filename}")

if __name__ == "__main__":
    scraper = ToyScraperWithImages()
    toys = scraper.scrape_and_download(limit=12)

    if toys:
        scraper.save_to_json()
        print("\n✅ Data saved with local image paths!")
    else:
        print("❌ No toys scraped!")
