"""
Merge complete toy data from toys_data.json with local image paths from toys_with_local_images.json
"""
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("📖 Loading complete toy data...")
with open('toys_data.json', 'r', encoding='utf-8') as f:
    complete_data = json.load(f)

print("📖 Loading local image paths...")
with open('toys_with_local_images.json', 'r', encoding='utf-8') as f:
    local_images_data = json.load(f)

# Create a mapping of toy_id -> local images
print("🔗 Creating toy ID to local images mapping...")
toy_images_map = {}
for entry in local_images_data:
    toy = entry.get('toy', {})
    toy_id = toy.get('id')
    if toy_id and toy.get('images'):
        toy_images_map[toy_id] = toy['images']

print(f"   Found local images for {len(toy_images_map)} toys")

# Update complete data with local image paths
print("✨ Merging data...")
updated_count = 0
for entry in complete_data:
    toy = entry.get('toy', {})
    toy_id = toy.get('id')

    if toy_id and toy_id in toy_images_map:
        # Replace images with local versions
        toy['images'] = toy_images_map[toy_id]
        updated_count += 1

print(f"   Updated {updated_count} toys with local image paths")

# Save merged data
output_file = 'toys_complete_with_local_images.json'
print(f"💾 Saving to {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(complete_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Successfully merged data!")
print(f"   Total entries: {len(complete_data)}")
print(f"   Toys with local images: {updated_count}")
print(f"   Output: {output_file}")
