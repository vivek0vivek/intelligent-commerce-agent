# Intelligent Commerce Agent

A sophisticated AI-powered e-commerce customer service agent built with LangGraph and Google Gemini. The agent provides intelligent product assistance and order management with strict policy enforcement.

## 🎯 Overview

This agent handles two primary workflows:
- **Product Assistance**: Search, compare, size recommendation, and shipping estimates
- **Order Management**: Secure order lookup and policy-aware cancellation handling

### Key Features

- **Intelligent Routing**: Classifies user intent (product_assist, order_help, other)
- **Dynamic Tool Selection**: Calls appropriate tools based on user needs
- **Policy Enforcement**: Strict 60-minute cancellation rule with professional alternatives
- **Professional Responses**: Brand-consistent, helpful customer service
- **Complete Traceability**: JSON traces for every interaction

## 🏗️ Architecture

The agent uses a 4-node LangGraph workflow:

```
User Input → Router → ToolSelector → PolicyGuard → Responder → Final Response
```

### Nodes

1. **Router**: Classifies user intent using LLM
2. **ToolSelector**: Chooses and executes appropriate tools
3. **PolicyGuard**: Enforces business rules and policies
4. **Responder**: Generates customer response and JSON trace

### Tools

- `product_search(query, price_max, tags)` - Product catalog search
- `size_recommender(user_inputs)` - M vs L sizing guidance
- `eta(zip_code)` - Shipping time estimates
- `order_lookup(order_id, email)` - Order verification
- `order_cancel(order_id, timestamp)` - Policy-enforced cancellation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key (free at [ai.google.dev](https://ai.google.dev))

### Installation

```bash
# Clone the repository
git clone https://github.com/vivek0vivek/intelligent-commerce-agent.git
cd intelligent-commerce-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Run Tests

```bash
# Run complete test suite
python -m tests.run_tests

# Quick functionality test
python quick_test.py
```

## 🧪 Test Scenarios

The agent handles 4 key scenarios:

### 1. Product Assistance
```
Input: "Wedding guest, midi, under $120 — I'm between M/L. ETA to 560001?"
Output: Product recommendations + size guidance + shipping estimate
```

### 2. Order Cancellation (Allowed)
```
Input: "Cancel order A1003 — email mira@example.com"
Output: Successful cancellation (within 60-minute window)
```

### 3. Order Cancellation (Blocked)
```
Input: "Cancel order A1002 — email alex@example.com"  
Output: Policy refusal + helpful alternatives
```

### 4. Guardrail Handling
```
Input: "Can you give me a discount code that doesn't exist?"
Output: Professional refusal + legitimate alternatives
```

## 📊 Sample Output

Every response includes a structured JSON trace:

```json
{
  "intent": "product_assist",
  "tools_called": ["product_search", "size_recommender", "eta"],
  "evidence": [
    {"product_id": "P1", "title": "Midi Wrap Dress", "price": 119}
  ],
  "policy_decision": null,
  "final_message": "I found 2 great options for you..."
}
```

## 🗂️ Project Structure

```
├── src/
│   ├── graph.py          # Main LangGraph agent
│   ├── tools.py          # Tool implementations
│   └── prompts.py        # Prompt management
├── data/
│   ├── products.json     # Product catalog
│   └── orders.json       # Order database
├── tests/
│   └── run_tests.py      # Complete test suite
├── prompts/
│   └── system.md         # System prompt
├── requirements.txt      # Dependencies
└── .env.example         # Environment template
```

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Your Google Gemini API key

### Model Configuration

The agent uses Google's `gemini-1.5-flash` model for:
- Intent classification
- Response generation
- Tool selection assistance

## 📈 Performance

- **Response Time**: ~2-3 seconds per request
- **Accuracy**: 100% on test scenarios
- **Policy Compliance**: Strict 60-minute enforcement
- **Cost**: ~$0.001 per request (Gemini pricing)

## 🛡️ Business Rules

### Cancellation Policy
- **Allowed**: Orders ≤60 minutes old
- **Blocked**: Orders >60 minutes old
- **Alternatives**: Address edit, store credit, support handoff

### Product Assistance
- Maximum 2 product recommendations
- Strict price cap enforcement
- No invented product data

### Guardrails
- Refuse non-existent discount codes
- Offer legitimate alternatives
- Professional boundary setting

## 🔍 Development

### Adding New Tools

1. Implement function in `src/tools.py`
2. Add to tool selector logic in `src/graph.py`
3. Update system prompt with usage guidelines
4. Add test coverage

### Extending Functionality

The modular architecture makes it easy to:
- Add new intents
- Implement additional business rules
- Integrate with external APIs
- Enhance tool capabilities

## 📚 API Reference

### EcommerceAgent

```python
from src.graph import EcommerceAgent

agent = EcommerceAgent()
result = agent.process_message("your user input")

# Returns:
{
    "json_trace": {...},    # Structured execution trace
    "final_message": "..."  # Customer-facing response
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://python.langchain.com/docs/langgraph) for agent orchestration
- Powered by [Google Gemini](https://ai.google.dev) for natural language understanding
- Inspired by modern e-commerce customer service best practices