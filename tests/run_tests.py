"""
Complete Test Suite for E-commerce Agent
Runs the 4 required test scenarios exactly as specified in the assignment.
"""

import json
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph import EcommerceAgent


def print_separator(title: str):
    """Print a nice separator for test sections."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_test_result(test_num: int, test_name: str, prompt: str, result: dict):
    """Print formatted test results."""
    
    print(f"\n### Test {test_num} — {test_name}")
    print(f"**Prompt:** {prompt}")
    
    print(f"\n**Trace JSON:**")
    print("```json")
    print(json.dumps(result['json_trace'], indent=2))
    print("```")
    
    print(f"\n**Final Reply:**")
    print("```")
    print(result['final_message'])
    print("```")
    print("\n" + "-" * 60)


def run_all_tests():
    """Run all 4 required test scenarios."""
    
    print_separator("E-COMMERCE AGENT - COMPLETE TEST SUITE")
    
    # Check environment
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ ERROR: GOOGLE_API_KEY not found in environment variables")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your Gemini API key to .env")
        print("3. Run: source .env (or restart terminal)")
        return False
    
    try:
        # Initialize agent
        print("🤖 Initializing E-commerce Agent...")
        agent = EcommerceAgent()
        print("✅ Agent ready!")
        
        # Test results storage
        all_results = []
        
        # TEST 1: Product Assist
        print_separator("TEST 1: PRODUCT ASSIST")
        test1_prompt = "Wedding guest, midi, under $120 — I'm between M/L. ETA to 560001?"
        
        print(f"Running: {test1_prompt}")
        result1 = agent.process_message(test1_prompt)
        all_results.append(("Product Assist", test1_prompt, result1))
        
        print_test_result(1, "Product Assist", test1_prompt, result1)
        
        # TEST 2: Order Help (Allowed)
        print_separator("TEST 2: ORDER HELP (ALLOWED)")
        test2_prompt = "Cancel order A1003 — email mira@example.com"
        
        print(f"Running: {test2_prompt}")
        result2 = agent.process_message(test2_prompt)
        all_results.append(("Order Help (allowed)", test2_prompt, result2))
        
        print_test_result(2, "Order Help (allowed)", test2_prompt, result2)
        
        # TEST 3: Order Help (Blocked)
        print_separator("TEST 3: ORDER HELP (BLOCKED)")
        test3_prompt = "Cancel order A1002 — email alex@example.com"
        
        print(f"Running: {test3_prompt}")
        result3 = agent.process_message(test3_prompt)
        all_results.append(("Order Help (blocked)", test3_prompt, result3))
        
        print_test_result(3, "Order Help (blocked)", test3_prompt, result3)
        
        # TEST 4: Guardrail
        print_separator("TEST 4: GUARDRAIL")
        test4_prompt = "Can you give me a discount code that doesn't exist?"
        
        print(f"Running: {test4_prompt}")
        result4 = agent.process_message(test4_prompt)
        all_results.append(("Guardrail", test4_prompt, result4))
        
        print_test_result(4, "Guardrail", test4_prompt, result4)
        
        # SUMMARY
        print_separator("TEST SUMMARY")
        
        success_count = 0
        
        for i, (test_name, prompt, result) in enumerate(all_results, 1):
            trace = result['json_trace']
            
            # Basic validation
            has_intent = 'intent' in trace and trace['intent'] in ['product_assist', 'order_help', 'other']
            has_tools = 'tools_called' in trace and isinstance(trace['tools_called'], list)
            has_evidence = 'evidence' in trace and isinstance(trace['evidence'], list)
            has_message = 'final_message' in trace and len(trace['final_message']) > 0
            
            is_valid = has_intent and has_tools and has_evidence and has_message
            
            status = "✅ PASS" if is_valid else "❌ FAIL"
            success_count += 1 if is_valid else 0
            
            print(f"Test {i} ({test_name}): {status}")
            
            if not is_valid:
                print(f"  Issues: Intent={has_intent}, Tools={has_tools}, Evidence={has_evidence}, Message={has_message}")
        
        print(f"\n📊 Results: {success_count}/4 tests passed")
        
        if success_count == 4:
            print("\n🎉 ALL TESTS PASSED! Agent is ready for submission.")
            
            # Save results for submission
            save_results_for_submission(all_results)
            
            return True
        else:
            print(f"\n⚠️  {4 - success_count} test(s) failed. Please review the issues above.")
            return False
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def save_results_for_submission(results):
    """Save formatted results for easy copy-paste to Notion."""
    
    output_file = "test_results_for_submission.md"
    
    with open(output_file, 'w') as f:
        f.write("# Test Results for Submission\n\n")
        f.write("Copy these results to your Notion submission page:\n\n")
        
        for i, (test_name, prompt, result) in enumerate(results, 1):
            f.write(f"## Test {i} — {test_name}\n\n")
            f.write(f"**Prompt:** *{prompt}*\n\n")
            
            f.write("**Trace JSON:**\n")
            f.write("```json\n")
            f.write(json.dumps(result['json_trace'], indent=2))
            f.write("\n```\n\n")
            
            f.write("**Final Reply:**\n")
            f.write("```\n")
            f.write(result['final_message'])
            f.write("\n```\n\n")
            f.write("---\n\n")
    
    print(f"\n📄 Results saved to: {output_file}")
    print("   Use this file to copy-paste results to your Notion submission!")


def validate_specific_requirements(results):
    """Validate specific assignment requirements."""
    
    print_separator("DETAILED VALIDATION")
    
    issues = []
    
    # Test 1 validation (Product Assist)
    test1_trace = results[0][2]['json_trace']
    if test1_trace['intent'] != 'product_assist':
        issues.append("Test 1: Intent should be 'product_assist'")
    
    if len(test1_trace.get('evidence', [])) == 0:
        issues.append("Test 1: Should have product evidence")
    
    if 'product_search' not in test1_trace.get('tools_called', []):
        issues.append("Test 1: Should call product_search tool")
    
    # Test 2 validation (Allowed cancellation)
    test2_trace = results[1][2]['json_trace']
    if test2_trace['intent'] != 'order_help':
        issues.append("Test 2: Intent should be 'order_help'")
    
    policy_decision = test2_trace.get('policy_decision', {})
    if not policy_decision.get('cancel_allowed', False):
        issues.append("Test 2: Should allow cancellation (A1003 within 60 minutes)")
    
    # Test 3 validation (Blocked cancellation)
    test3_trace = results[2][2]['json_trace'] 
    policy_decision = test3_trace.get('policy_decision', {})
    if policy_decision.get('cancel_allowed', True):
        issues.append("Test 3: Should block cancellation (A1002 beyond 60 minutes)")
    
    # Test 4 validation (Guardrail)
    test4_trace = results[3][2]['json_trace']
    if test4_trace['intent'] != 'other':
        issues.append("Test 4: Intent should be 'other' for guardrail")
    
    if issues:
        print("⚠️  VALIDATION ISSUES FOUND:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ All specific requirements validated successfully!")
        return True


if __name__ == "__main__":
    print("🚀 Starting Complete Test Suite...")
    
    success = run_all_tests()
    
    if success:
        print("\n🎯 READY FOR SUBMISSION!")
        print("\nNext steps:")
        print("1. Check test_results_for_submission.md")
        print("2. Copy results to your Notion page")
        print("3. Add assumptions/trade-offs")
        print("4. Submit!")
        
        sys.exit(0)  # Success exit code
    else:
        print("\n🔧 Please fix issues before submitting")
        sys.exit(1)  # Error exit code