"""
Debug test for product search in agent workflow
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph import EcommerceAgent

def test_product_search_in_agent():
    print("🔍 Testing product search in agent workflow...")
    
    agent = EcommerceAgent()
    
    # Test the exact prompt from Test 1
    test_prompt = "Wedding guest, midi, under $120 — I'm between M/L. ETA to 560001?"
    
    print(f"Input: {test_prompt}")
    
    result = agent.process_message(test_prompt)
    
    print(f"\nResults:")
    print(f"Intent: {result['json_trace']['intent']}")
    print(f"Tools called: {result['json_trace']['tools_called']}")
    print(f"Evidence count: {len(result['json_trace']['evidence'])}")
    
    if result['json_trace']['evidence']:
        print(f"Evidence found:")
        for i, evidence in enumerate(result['json_trace']['evidence']):
            print(f"  {i+1}. {evidence}")
    else:
        print("No evidence found - this is the issue!")
    
    print(f"\nFinal message preview:")
    print(result['final_message'][:200] + "...")

if __name__ == "__main__":
    test_product_search_in_agent()