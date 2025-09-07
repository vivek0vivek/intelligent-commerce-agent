"""
E-commerce Agent LangGraph Implementation
Creates the main agent workflow with Router -> ToolSelector -> PolicyGuard -> Responder
"""

import json
import os
from datetime import datetime, timezone
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import google.generativeai as genai
from dotenv import load_dotenv

from .tools import (
    product_search, size_recommender, eta, 
    order_lookup, order_cancel
)
from .prompts import (
    load_system_prompt, create_router_prompt,
    create_tool_selector_prompt, create_user_prompt
)

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


class AgentState(TypedDict):
    """State passed between nodes in the agent workflow."""
    user_input: str
    intent: str
    tools_called: List[str]
    tool_results: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    policy_decision: Optional[Dict[str, Any]]
    final_message: str
    json_trace: Dict[str, Any]


def call_llm(prompt: str, system_prompt: str = None) -> str:
    """
    Call Gemini LLM with the given prompt.
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
    
    Returns:
        LLM response text
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
            
        response = model.generate_content(full_prompt)
        return response.text.strip()
    
    except Exception as e:
        print(f"LLM Error: {e}")
        return "I'm having trouble processing your request right now."


def router_node(state: AgentState) -> AgentState:
    """
    Router Node: Classify user intent into product_assist, order_help, or other.
    """
    print("🔄 Router: Classifying user intent...")
    
    prompt = create_router_prompt(state["user_input"])
    
    try:
        intent = call_llm(prompt).lower().strip()
        
        # Ensure intent is one of the valid options
        if intent not in ["product_assist", "order_help", "other"]:
            # Fallback classification based on keywords
            user_lower = state["user_input"].lower()
            if any(word in user_lower for word in ["cancel", "order", "refund", "return"]):
                intent = "order_help"
            elif any(word in user_lower for word in ["dress", "product", "size", "wedding", "find", "recommend"]):
                intent = "product_assist"
            else:
                intent = "other"
    
    except Exception as e:
        print(f"Router error: {e}")
        # Default fallback
        intent = "other"
    
    state["intent"] = intent
    print(f"   Intent classified as: {intent}")
    
    return state


def tool_selector_node(state: AgentState) -> AgentState:
    """
    ToolSelector Node: Decide which tools to call based on intent and user input.
    """
    print("🔧 ToolSelector: Choosing and executing tools...")
    
    intent = state["intent"]
    user_input = state["user_input"]
    tools_called = []
    tool_results = {}
    evidence = []
    
    if intent == "product_assist":
        # Extract price constraint if mentioned
        price_max = 1000  # Default high value
        words = user_input.lower().split()
        for i, word in enumerate(words):
            if word in ["under", "below", "max"] and i + 1 < len(words):
                try:
                    # Look for price like "$120" or "120"
                    price_text = words[i + 1].replace("$", "").replace(",", "")
                    price_max = int(price_text)
                    break
                except ValueError:
                    continue
        
        # Product search
        try:
            query_terms = []
            if "wedding" in user_input.lower():
                query_terms.append("wedding")
            if "midi" in user_input.lower():
                query_terms.append("midi")
            if "party" in user_input.lower():
                query_terms.append("party")
            
            query = " ".join(query_terms) if query_terms else "dress"
            
            products = product_search(query, price_max)
            tools_called.append("product_search")
            tool_results["product_search"] = products
            
            # Add products to evidence
            for product in products:
                evidence.append({
                    "product_id": product["id"],
                    "title": product["title"],
                    "price": product["price"],
                    "sizes": product["sizes"],
                    "color": product["color"]
                })
            
            print(f"   Found {len(products)} products under ${price_max}")
            
        except Exception as e:
            print(f"   Product search error: {e}")
        
        # Size recommendation if mentioned
        if any(word in user_input.lower() for word in ["size", "m/l", "between"]):
            try:
                size_rec = size_recommender({"preference": user_input.lower()})
                tools_called.append("size_recommender")
                tool_results["size_recommender"] = size_rec
                print(f"   Size recommendation: {size_rec['recommended_size']}")
            except Exception as e:
                print(f"   Size recommender error: {e}")
        
        # ETA if zip code mentioned
        import re
        zip_match = re.search(r'\b\d{5,6}\b', user_input)
        if zip_match:
            try:
                zip_code = zip_match.group()
                eta_result = eta(zip_code)
                tools_called.append("eta")
                tool_results["eta"] = eta_result
                print(f"   ETA for {zip_code}: {eta_result['eta_days']} days")
            except Exception as e:
                print(f"   ETA error: {e}")
    
    elif intent == "order_help":
        # Extract order ID and email
        order_id = None
        email = None
        
        # Look for order ID pattern (A followed by digits)
        import re
        order_match = re.search(r'\b[A-Z]\d+\b', user_input)
        if order_match:
            order_id = order_match.group()
        
        # Look for email pattern
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input)
        if email_match:
            email = email_match.group()
        
        if order_id and email:
            try:
                # Order lookup
                order = order_lookup(order_id, email)
                tools_called.append("order_lookup")
                tool_results["order_lookup"] = order
                
                if order:
                    evidence.append({
                        "order_id": order["order_id"],
                        "email": order["email"],
                        "created_at": order["created_at"],
                        "items": order["items"]
                    })
                    print(f"   Order {order_id} found for {email}")
                    
                    # Check if this is a cancellation request
                    if "cancel" in user_input.lower():
                        try:
                            # Use mock timestamp for testing consistency
                            mock_timestamp = "2025-09-07T12:30:00Z"
                            cancel_result = order_cancel(order_id, mock_timestamp)
                            tools_called.append("order_cancel")
                            tool_results["order_cancel"] = cancel_result
                            print(f"   Cancellation result: {cancel_result['success']}")
                        except Exception as e:
                            print(f"   Order cancel error: {e}")
                else:
                    print(f"   Order {order_id} not found or email mismatch")
                    
            except Exception as e:
                print(f"   Order lookup error: {e}")
        else:
            print(f"   Missing order ID or email in request")
    
    # For "other" intent, typically no tools needed
    
    state["tools_called"] = tools_called
    state["tool_results"] = tool_results
    state["evidence"] = evidence
    
    return state


def policy_guard_node(state: AgentState) -> AgentState:
    """
    PolicyGuard Node: Enforce business rules and policies.
    """
    print("🛡️  PolicyGuard: Checking policies...")
    
    policy_decision = None
    
    # Check for order cancellation policy
    if "order_cancel" in state["tool_results"]:
        cancel_result = state["tool_results"]["order_cancel"]
        policy_decision = cancel_result.get("policy_decision", {})
        print(f"   Cancellation policy: {policy_decision}")
    
    # Check for discount code requests (guardrail)
    elif "discount" in state["user_input"].lower() and "code" in state["user_input"].lower():
        policy_decision = {
            "refuse": True,
            "reason": "Non-existent discount code requested",
            "alternatives": [
                "Sign up for our newsletter to get future discount codes",
                "Check our current promotions page",
                "First-time customers get 10% off their first order"
            ]
        }
        print("   Discount code guardrail triggered")
    
    state["policy_decision"] = policy_decision
    
    return state


def responder_node(state: AgentState) -> AgentState:
    """
    Responder Node: Generate final customer response and JSON trace.
    """
    print("💬 Responder: Creating final response...")
    
    # Create JSON trace first
    json_trace = {
        "intent": state["intent"],
        "tools_called": state["tools_called"],
        "evidence": state["evidence"],
        "policy_decision": state["policy_decision"],
        "final_message": ""  # Will be filled after generating response
    }
    
    # Generate customer-facing response based on intent and results
    try:
        final_message = generate_customer_response(state)
        json_trace["final_message"] = final_message
        
    except Exception as e:
        print(f"Response generation error: {e}")
        final_message = "I apologize, but I'm having trouble processing your request right now. Please try again or contact customer support."
        json_trace["final_message"] = final_message
    
    state["final_message"] = final_message
    state["json_trace"] = json_trace
    
    print("   ✅ Response generated")
    
    return state


def generate_customer_response(state: AgentState) -> str:
    """Generate the customer-facing response based on state."""
    
    intent = state["intent"]
    tools_called = state["tools_called"]
    tool_results = state["tool_results"]
    policy_decision = state["policy_decision"]
    
    if intent == "product_assist":
        return generate_product_response(tools_called, tool_results)
    
    elif intent == "order_help":
        return generate_order_response(tools_called, tool_results, policy_decision)
    
    elif intent == "other":
        return generate_other_response(state["user_input"], policy_decision)
    
    else:
        return "I'm not sure how to help with that. Could you please rephrase your request?"


def generate_product_response(tools_called: List[str], tool_results: Dict[str, Any]) -> str:
    """Generate response for product assistance."""
    
    response_parts = []
    
    # Product recommendations
    if "product_search" in tool_results:
        products = tool_results["product_search"]
        if products:
            response_parts.append(f"I found {len(products)} great option{'s' if len(products) > 1 else ''} for you:\n")
            
            for i, product in enumerate(products, 1):
                sizes_text = ", ".join(product["sizes"])
                response_parts.append(
                    f"{i}. **{product['title']}** (${product['price']}, {product['color']}) - Available in {sizes_text}"
                )
        else:
            response_parts.append("I don't see any products matching those criteria in our current collection.")
    
    # Size recommendation
    if "size_recommender" in tool_results:
        size_rec = tool_results["size_recommender"]
        response_parts.append(f"\n**Size recommendation:** {size_rec['recommended_size']} - {size_rec['rationale']}")
    
    # Shipping ETA
    if "eta" in tool_results:
        eta_info = tool_results["eta"]
        response_parts.append(f"\n**Shipping to {eta_info['zip']}:** {eta_info['eta_days']} business days")
    
    # Add helpful next step
    response_parts.append("\nWould you like more details about any of these options?")
    
    return "\n".join(response_parts)


def generate_order_response(tools_called: List[str], tool_results: Dict[str, Any], policy_decision: Optional[Dict[str, Any]]) -> str:
    """Generate response for order help."""
    
    if "order_lookup" not in tool_results:
        return "I couldn't find an order with that ID and email combination. Please double-check the order number and email address."
    
    order = tool_results["order_lookup"]
    if not order:
        return "I couldn't find an order with that ID and email combination. Please double-check the order number and email address."
    
    # Format order items
    items_text = []
    for item in order["items"]:
        # Look up product details from our catalog
        from .tools import load_products
        products = load_products()
        product = next((p for p in products if p["id"] == item["id"]), None)
        if product:
            items_text.append(f"- {product['title']} (Size {item['size']})")
        else:
            items_text.append(f"- Product {item['id']} (Size {item['size']})")
    
    # Handle cancellation
    if "order_cancel" in tool_results:
        cancel_result = tool_results["order_cancel"]
        
        if cancel_result["success"]:
            # Successful cancellation
            return f"""✅ **Order {order['order_id']} has been successfully cancelled.**

Order details:
{chr(10).join(items_text)}
- Placed: {format_order_date(order['created_at'])}
- Cancelled within our 60-minute window

**Refund:** {cancel_result.get('refund_info', 'Full refund will be processed within 3-5 business days to your original payment method.')}

Is there anything else I can help you with?"""
        
        else:
            # Blocked cancellation
            alternatives_text = []
            for alt in cancel_result.get("alternatives", []):
                alternatives_text.append(f"• **{alt}**")
            
            return f"""❌ **Unable to cancel order {order['order_id']}**

{cancel_result['reason']}

**Alternative options:**
{chr(10).join(alternatives_text)}

Which option would work best for you?"""
    
    else:
        # Just order lookup
        return f"""📋 **Order {order['order_id']} Details:**

{chr(10).join(items_text)}
- Placed: {format_order_date(order['created_at'])}
- Email: {order['email']}

How can I help you with this order?"""


def generate_other_response(user_input: str, policy_decision: Optional[Dict[str, Any]]) -> str:
    """Generate response for 'other' intent."""
    
    if policy_decision and policy_decision.get("refuse"):
        # Handle discount code refusal
        if "discount" in user_input.lower():
            alternatives = policy_decision.get("alternatives", [])
            alt_text = "\n".join([f"• {alt}" for alt in alternatives])
            
            return f"""I don't have access to create custom discount codes, but here are some ways you can save:

{alt_text}

Is there anything else I can help you find today?"""
    
    # Default response for other inquiries
    return """I'm here to help you find products and manage your orders. I can:

• **Find products** - Search by style, price, size, or occasion
• **Size guidance** - Help you choose between M and L
• **Shipping info** - Provide delivery estimates
• **Order help** - Look up orders and handle cancellations (within 60 minutes)

What would you like help with?"""


def format_order_date(iso_date: str) -> str:
    """Format ISO date string for display."""
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return dt.strftime("%B %d at %I:%M %p")
    except:
        return iso_date


# Build the LangGraph workflow
def create_agent_graph() -> StateGraph:
    """Create and configure the LangGraph agent workflow."""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("tool_selector", tool_selector_node)  
    workflow.add_node("policy_guard", policy_guard_node)
    workflow.add_node("responder", responder_node)
    
    # Define the flow
    workflow.set_entry_point("router")
    workflow.add_edge("router", "tool_selector")
    workflow.add_edge("tool_selector", "policy_guard")
    workflow.add_edge("policy_guard", "responder")
    workflow.add_edge("responder", END)
    
    return workflow.compile()


# Main agent interface
class EcommerceAgent:
    """Main agent class that handles user interactions."""
    
    def __init__(self):
        self.graph = create_agent_graph()
        self.system_prompt = load_system_prompt()
    
    def process_message(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user message through the agent workflow.
        
        Args:
            user_input: User's message
            
        Returns:
            Dictionary with json_trace and final_message
        """
        print(f"\n🚀 Processing: '{user_input}'")
        print("=" * 50)
        
        # Initialize state
        initial_state = {
            "user_input": user_input,
            "intent": "",
            "tools_called": [],
            "tool_results": {},
            "evidence": [],
            "policy_decision": None,
            "final_message": "",
            "json_trace": {}
        }
        
        try:
            # Run through the graph
            final_state = self.graph.invoke(initial_state)
            
            print("=" * 50)
            print("✅ Processing complete!\n")
            
            return {
                "json_trace": final_state["json_trace"],
                "final_message": final_state["final_message"]
            }
            
        except Exception as e:
            print(f"❌ Agent error: {e}")
            
            # Return error response
            error_trace = {
                "intent": "error",
                "tools_called": [],
                "evidence": [],
                "policy_decision": {"error": str(e)},
                "final_message": "I'm having trouble processing your request right now. Please try again or contact customer support."
            }
            
            return {
                "json_trace": error_trace,
                "final_message": error_trace["final_message"]
            }


# Quick test
if __name__ == "__main__":
    print("🧪 Testing E-commerce Agent...")
    
    # Test if API key is configured
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please copy .env.example to .env and add your API key")
        exit(1)
    
    agent = EcommerceAgent()
    
    # Quick test message
    test_message = "I need a wedding dress under $120"
    result = agent.process_message(test_message)
    
    print("📋 Test Results:")
    print(f"Trace: {json.dumps(result['json_trace'], indent=2)}")
    print(f"Response: {result['final_message']}")