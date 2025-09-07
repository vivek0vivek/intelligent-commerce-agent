"""
Debug script to test product search function
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.tools import product_search, load_products

def debug_product_search():
    print("🔍 Debugging Product Search...")
    
    # Test data loading
    print("\n1. Testing data loading:")
    products = load_products()
    print(f"   Loaded {len(products)} products")
    for p in products:
        print(f"   - {p['id']}: {p['title']} (${p['price']}) tags: {p['tags']}")
    
    # Test search function
    print(f"\n2. Testing search: query='wedding', price_max=120")
    results = product_search("wedding", 120)
    print(f"   Found {len(results)} results:")
    for r in results:
        print(f"   - {r['id']}: {r['title']} (${r['price']})")
    
    # Test different variations
    print(f"\n3. Testing variations:")
    
    test_cases = [
        ("wedding", 120),
        ("Wedding", 120),
        ("midi", 120),
        ("dress", 200),
    ]
    
    for query, price_max in test_cases:
        results = product_search(query, price_max)
        print(f"   query='{query}', price_max={price_max} → {len(results)} results")

if __name__ == "__main__":
    debug_product_search()