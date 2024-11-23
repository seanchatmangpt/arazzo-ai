# Mock context for debugging
from arazzo_ai.evaluate import ExpressionEvaluator

context = {
    "response": {
        "body": {
            "eligibilityCheckRequired": True,
            "products": [{"productCode": "PRD123", "eligible": True}],
            "existingCustomerNotEligible": False,
            "totalAmount": 1000.0,
            "redirectAuthToken": "dummyAuthToken",
            "links": {"self": "https://api.example.com/customer/12345"}
        },
        "header": {"Location": "https://auth.example.com/redirect"}
    },
    "statusCode": 200
}

evaluator = ExpressionEvaluator(context)

print(evaluator("$statusCode == 200"))  # Should return True
