"""
Fresh test after restarting Python to clear module cache
"""

# Force reload of modules
import sys
import importlib

# Clear any cached modules
for module_name in list(sys.modules.keys()):
    if module_name.startswith('src'):
        del sys.modules[module_name]

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Now import fresh
from src.tools import product_search
from src.graph import EcommerceAgent

def test_fresh():
    print("🔄 Fresh test after restart...")
    
    # Test product search directly first
    print("\n1. Direct product search test:")
    results = product_search("wedding", 120)
    print(f"   product_search('wedding', 120) → {len(results)} products")
    for r in results:
        print(f"   - {r['id']}: {r['title']} (${r['price']})")
    
    # Test agent
    print("\n2. Agent test:")
    agent = EcommerceAgent()
    result = agent.process_message("Wedding guest, midi, under $120 — I'm between M/L. ETA to 560001?")
    
    print(f"   Evidence count: {len(result['json_trace']['evidence'])}")
    if result['json_trace']['evidence']:
        for evidence in result['json_trace']['evidence']:
            print(f"   - {evidence['product_id']}: {evidence['title']} (${evidence['price']})")
    else:
        print("   No evidence found")

if __name__ == "__main__":
    test_fresh()