import sqlite3
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('toys.db')
cursor = conn.cursor()

# Search for the tunnel toy
cursor.execute("SELECT * FROM toys WHERE LOWER(name) LIKE '%tunnel%'")
toy = cursor.fetchone()

if toy:
    print("=" * 60)
    print("3 WAY ACTIVITY TUNNEL - TOY DETAILS")
    print("=" * 60)
    print(f"Name: {toy[1]}")
    print(f"Type: {toy[5]} (BIG_TOY category)")
    print(f"Price: ₹{toy[2]}")
    print(f"Age Range: {toy[6]//12}-{toy[7]//12} years ({toy[6]}-{toy[7]} months)")
    print(f"Description: {toy[3] if toy[3] else 'N/A'}")
    print(f"Link: https://www.theelefant.ai/toy/{toy[4]}")

    # Get images
    cursor.execute("SELECT url FROM images WHERE toy_id = ?", (toy[0],))
    images = cursor.fetchall()
    if images:
        print(f"\nImages: {len(images)} available")
        print(f"First image: {images[0][0]}")

    print("\n" + "=" * 60)
    print("This toy is categorized as 'BIG_TOY' in the database")
    print("You can filter by 'BIG_TOY' type in the web app!")
    print("=" * 60)

conn.close()
