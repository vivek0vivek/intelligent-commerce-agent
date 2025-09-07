"""
Prompt management for the e-commerce agent.
"""

from pathlib import Path


def load_system_prompt() -> str:
    """Load the main system prompt from markdown file."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "system.md"
    with open(prompt_path, 'r') as f:
        return f.read()


def create_user_prompt(user_input: str, context: dict = None) -> str:
    """
    Create a formatted prompt for the LLM with user input and any context.
    
    Args:
        user_input: The user's message
        context: Optional context (tool results, state, etc.)
    
    Returns:
        Formatted prompt string
    """
    prompt_parts = []
    
    # Add context if provided
    if context:
        prompt_parts.append("CONTEXT:")
        for key, value in context.items():
            prompt_parts.append(f"{key}: {value}")
        prompt_parts.append("")
    
    # Add user input
    prompt_parts.append("USER MESSAGE:")
    prompt_parts.append(user_input)
    prompt_parts.append("")
    
    # Add instruction for JSON trace
    prompt_parts.append("INSTRUCTIONS:")
    prompt_parts.append("1. Follow the system prompt guidelines exactly")
    prompt_parts.append("2. Use the appropriate tools based on the user's intent")
    prompt_parts.append("3. ALWAYS respond with the required JSON trace format")
    prompt_parts.append("4. Include a customer-friendly final_message")
    
    return "\n".join(prompt_parts)


def create_router_prompt(user_input: str) -> str:
    """Create prompt specifically for the router node."""
    return f"""
Classify the user's intent based on their message.

USER MESSAGE: {user_input}

Classify this into exactly one category:
- "product_assist" - User wants help finding, comparing, or learning about products
- "order_help" - User wants to lookup, modify, or cancel an existing order  
- "other" - Everything else (general questions, complaints, requests outside scope)

Respond with just the intent category, nothing else.
"""


def create_tool_selector_prompt(user_input: str, intent: str) -> str:
    """Create prompt for tool selection based on intent."""
    return f"""
Based on the user's message and intent, determine which tools to call.

USER MESSAGE: {user_input}
INTENT: {intent}

Available tools:
- product_search(query, price_max, tags) - Search for products
- size_recommender(user_inputs) - Recommend M vs L sizing
- eta(zip_code) - Calculate shipping time
- order_lookup(order_id, email) - Find order details
- order_cancel(order_id, timestamp) - Cancel order with policy check

For product_assist: Usually need product_search, often size_recommender and eta
For order_help: Usually need order_lookup, sometimes order_cancel
For other: Usually no tools needed

Return a JSON list of tools to call: ["tool1", "tool2"]
"""


# Test the prompt loader
if __name__ == "__main__":
    print("🧪 Testing Prompt Loader...")
    
    system_prompt = load_system_prompt()
    print(f"✅ System prompt loaded: {len(system_prompt)} characters")
    
    user_prompt = create_user_prompt("I need a wedding dress under $100")
    print(f"✅ User prompt created: {len(user_prompt)} characters")
    
    router_prompt = create_router_prompt("Cancel my order A1001")
    print(f"✅ Router prompt created: {len(router_prompt)} characters")
    
    print("\n📝 Sample system prompt preview:")
    print(system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt)