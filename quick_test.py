"""
Quick test to verify the agent works before building full test suite.
"""

import json
import os
from dotenv import load_dotenv
from src.graph import EcommerceAgent

# Load environment variables
load_dotenv()

def test_basic_functionality():
    """Test basic agent functionality."""
    
    print("🧪 Quick Agent Test")
    print("=" * 30)
    
    # Check API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY not found!")
        print("Please:")
        print("1. Copy .env.example to .env")
        print("2. Add your Gemini API key to .env")
        return False
    
    try:
        # Create agent
        print("🤖 Creating agent...")
        agent = EcommerceAgent()
        print("✅ Agent created successfully!")
        
        # Test simple product query
        print("\n🛍️  Testing product search...")
        test_input = "wedding dress under $120"
        
        result = agent.process_message(test_input)
        
        print("\n📋 Results:")
        print(f"Intent: {result['json_trace'].get('intent', 'Unknown')}")
        print(f"Tools called: {result['json_trace'].get('tools_called', [])}")
        print(f"Evidence count: {len(result['json_trace'].get('evidence', []))}")
        
        print(f"\n💬 Response preview:")
        print(result['final_message'][:200] + "..." if len(result['final_message']) > 200 else result['final_message'])
        
        print("\n✅ Basic test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    
    if success:
        print("\n🎉 Ready for full testing!")
        print("Next step: Run the complete test suite")
    else:
        print("\n🔧 Please fix the issues above before proceeding")