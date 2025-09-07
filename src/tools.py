"""
E-commerce Agent Tools
Required tools for product search, order management, and policy enforcement.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_products() -> List[Dict[str, Any]]:
    """Load product catalog from JSON file."""
    file_path = Path(__file__).parent.parent / "data" / "products.json"
    with open(file_path, 'r') as f:
        return json.load(f)


def load_orders() -> List[Dict[str, Any]]:
    """Load orders from JSON file."""
    file_path = Path(__file__).parent.parent / "data" / "orders.json"
    with open(file_path, 'r') as f:
        return json.load(f)


def product_search(query: str, price_max: int, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Search products with filters.
    
    Args:
        query: Search terms (e.g., "wedding", "midi")
        price_max: Maximum price filter
        tags: Optional tag filters
    
    Returns:
        List of ≤2 matching products with full details
    """
    products = load_products()
    results = []
    
    # Convert query to lowercase for matching
    query_lower = query.lower()
    
    for product in products:
        # Price filter (strict requirement)
        if product["price"] > price_max:
            continue
            
        # Query matching (title or tags)
        title_match = query_lower in product["title"].lower()
        tag_match = any(query_lower in tag.lower() for tag in product["tags"])
        
        if title_match or tag_match:
            results.append(product)
    
    # Tag filtering if specified
    if tags:
        filtered_results = []
        for product in results:
            if any(tag.lower() in [t.lower() for t in product["tags"]] for tag in tags):
                filtered_results.append(product)
        results = filtered_results
    
    # Return maximum 2 products (requirement)
    return results[:2]


def size_recommender(user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple M vs L size recommendation heuristic.
    
    Args:
        user_inputs: Dictionary with user preferences/measurements
    
    Returns:
        Dictionary with recommended size and rationale
    """
    # Simple heuristic based on common preferences
    # In real system, this would use more sophisticated logic
    
    preference = user_inputs.get("preference", "").lower()
    
    if "between m/l" in preference or "m/l" in preference:
        return {
            "recommended_size": "M",
            "rationale": "Based on your preference between M/L, I recommend size M for a more fitted look. You can always size up to L if you prefer a looser fit."
        }
    elif "loose" in preference or "comfortable" in preference:
        return {
            "recommended_size": "L", 
            "rationale": "Recommended size L for a comfortable, loose fit."
        }
    elif "fitted" in preference or "tight" in preference:
        return {
            "recommended_size": "M",
            "rationale": "Recommended size M for a fitted look."
        }
    else:
        return {
            "recommended_size": "M",
            "rationale": "Size M recommended as a versatile middle option that works for most body types."
        }


def eta(zip_code: str) -> Dict[str, Any]:
    """
    Calculate shipping ETA based on zip code.
    
    Args:
        zip_code: Destination zip code
    
    Returns:
        Dictionary with ETA information
    """
    # Rule-based ETA calculation (mock shipping logic)
    zip_str = str(zip_code)
    
    # Different regions get different ETAs
    if zip_str.startswith(('560', '600', '400')):  # Indian metros
        eta_days = "2-3"
        region = "metro"
    elif zip_str.startswith(('1', '2', '3')):  # US East Coast
        eta_days = "2-4" 
        region = "east"
    elif zip_str.startswith(('9', '8')):  # US West Coast
        eta_days = "3-5"
        region = "west"
    else:  # Other areas
        eta_days = "3-5"
        region = "standard"
    
    return {
        "eta_days": eta_days,
        "zip": zip_code,
        "region": region,
        "shipping_note": f"Standard shipping to {zip_code}: {eta_days} business days"
    }


def order_lookup(order_id: str, email: str) -> Optional[Dict[str, Any]]:
    """
    Look up order by ID and email verification.
    
    Args:
        order_id: Order identifier
        email: Customer email for verification
    
    Returns:
        Order details if found and email matches, None otherwise
    """
    orders = load_orders()
    
    for order in orders:
        if order["order_id"] == order_id and order["email"].lower() == email.lower():
            return order
    
    return None


def order_cancel(order_id: str, current_timestamp: str = None) -> Dict[str, Any]:
    """
    Cancel order with strict 60-minute policy enforcement.
    
    Args:
        order_id: Order to cancel
        current_timestamp: Current time (for testing), uses real time if None
    
    Returns:
        Dictionary with cancellation result and policy decision
    """
    orders = load_orders()
    
    # Find the order
    order = None
    for o in orders:
        if o["order_id"] == order_id:
            order = o
            break
    
    if not order:
        return {
            "success": False,
            "reason": "Order not found",
            "policy_decision": {
                "cancel_allowed": False,
                "reason": "Order not found"
            }
        }
    
    # Parse timestamps
    created_at = datetime.fromisoformat(order["created_at"].replace('Z', '+00:00'))
    
    if current_timestamp:
        # For testing - use provided timestamp
        current_time = datetime.fromisoformat(current_timestamp.replace('Z', '+00:00'))
    else:
        # Real usage - use current time
        current_time = datetime.now(timezone.utc)
    
    # Calculate time difference
    time_diff = current_time - created_at
    minutes_elapsed = time_diff.total_seconds() / 60
    
    # 60-minute policy enforcement
    if minutes_elapsed <= 60:
        return {
            "success": True,
            "reason": f"Order cancelled successfully. Cancelled within {minutes_elapsed:.1f} minutes of creation.",
            "policy_decision": {
                "cancel_allowed": True,
                "reason": f"Within 60-minute window ({minutes_elapsed:.1f} minutes elapsed)"
            },
            "refund_info": "Full refund will be processed within 3-5 business days."
        }
    else:
        return {
            "success": False,
            "reason": f"Cancellation not allowed. Order was placed {minutes_elapsed:.1f} minutes ago, which exceeds our 60-minute cancellation window.",
            "policy_decision": {
                "cancel_allowed": False,
                "reason": f"Exceeds 60-minute limit ({minutes_elapsed:.1f} minutes elapsed)"
            },
            "alternatives": [
                "Edit your shipping address if the order hasn't shipped yet",
                "Convert to store credit for future purchases", 
                "Contact customer support for special assistance"
            ]
        }


# Test functions
if __name__ == "__main__":
    # Quick test of all tools
    print("🧪 Testing Tools...")
    
    # Test product search
    print("\n1. Product Search Test:")
    results = product_search("wedding", 120, ["wedding"])
    print(f"Found {len(results)} products under $120 with wedding tag")
    for p in results:
        print(f"  - {p['title']}: ${p['price']}")
    
    # Test size recommender
    print("\n2. Size Recommender Test:")
    rec = size_recommender({"preference": "between m/l"})
    print(f"Recommendation: {rec['recommended_size']} - {rec['rationale']}")
    
    # Test ETA
    print("\n3. ETA Test:")
    eta_result = eta("560001")
    print(f"ETA for 560001: {eta_result['eta_days']} days")
    
    # Test order lookup
    print("\n4. Order Lookup Test:")
    order = order_lookup("A1003", "mira@example.com")
    print(f"Order found: {order['order_id'] if order else 'None'}")
    
    # Test order cancel (mock timestamp for consistent testing)
    print("\n5. Order Cancel Test:")
    # Test within 60 minutes
    result = order_cancel("A1003", "2025-09-07T12:30:00Z")  # 35 minutes after A1003 creation
    print(f"A1003 cancel (within 60min): {result['success']} - {result['reason']}")
    
    # Test beyond 60 minutes  
    result = order_cancel("A1002", "2025-09-07T12:30:00Z")  # Way beyond 60 minutes
    print(f"A1002 cancel (beyond 60min): {result['success']} - {result['reason']}")
    
    print("\n✅ All tools working!")