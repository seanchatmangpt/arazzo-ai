import pytest

from arazzo_ai.evaluate import ExpressionEvaluator


@pytest.fixture
def sample_context():
    return {
        "inputs": {
            "customer": {
                "firstName": "John",
                "lastName": "Doe",
                "dateOfBirth": "1990-01-01T00:00:00Z",
                "postalCode": "12345"
            },
            "products": [
                {"productCode": "123", "purchaseAmount": {"currency": "USD", "amount": 100.00}},
                {"productCode": "456", "purchaseAmount": {"currency": "USD", "amount": 50.00}}
            ]
        },
        "response": {
            "body": {
                "eligibilityCheckRequired": True,
                "products": [{"productCode": "123", "eligible": True}],
                "existingCustomerNotEligible": False,
                "totalAmount": 150.00,
                "redirectAuthToken": "auth-token-123",
                "links": {"self": "https://example.com/transaction/123"}
            },
            "header": {
                "Location": "https://example.com/redirect"
            }
        },
        "components": {
            "parameters": {
                "storeId": "store_001"
            }
        },
        "sourceDescriptions": {
            "petStoreDescription": {
                "type": "openapi",
                "url": "https://github.com/swagger-api/swagger-petstore/blob/master/src/main/resources/openapi.yaml"
            }
        },
        "url": "https://example.com/api",
        "method": "POST",
        "statusCode": 200
    }


def test_json_pointer_support(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    assert evaluator("$response.body#/totalAmount") == 150.00
    assert evaluator("$response.body#/links/self") == "https://example.com/transaction/123"
    assert evaluator("$response.body#/products/0/productCode") == "123"


def test_all_bases(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    assert evaluator("$url") == "https://example.com/api"
    assert evaluator("$method") == "POST"
    assert evaluator("$statusCode") == 200
    assert evaluator("$components.parameters.storeId") == "store_001"
    assert evaluator(
        "$sourceDescriptions.petStoreDescription.url") == "https://github.com/swagger-api/swagger-petstore/blob/master/src/main/resources/openapi.yaml"


def test_embedded_expressions(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    assert evaluator("Hello, {$inputs.customer.firstName}!") == "Hello, John!"
    assert evaluator("Total amount is {$response.body.totalAmount} USD.") == "Total amount is 150.0 USD."
    assert evaluator("Visit us at {$url}") == "Visit us at https://example.com/api"

    # Multiple embedded expressions
    assert evaluator(
        "Hello, {$inputs.customer.firstName} {$inputs.customer.lastName}, your total is {$response.body.totalAmount} USD.") == "Hello, John Doe, your total is 150.0 USD."


def test_embedded_expressions_with_json_pointer(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    result = evaluator("Your order can be tracked here: {$response.body#/links/self}")
    assert result == "Your order can be tracked here: https://example.com/transaction/123"


def test_json_pointer_on_nonexistent_path(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    result = evaluator("$response.body#/nonexistent/path")
    assert result is None


def test_dot_notation_fallback(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    # Should fallback to dot notation if not using JSON Pointer
    assert evaluator("$response.body.links.self") == "https://example.com/transaction/123"


def test_components_access(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    assert evaluator("$components.parameters.storeId") == "store_001"


def test_source_descriptions_access(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    assert evaluator("$sourceDescriptions.petStoreDescription.type") == "openapi"
    assert evaluator(
        "$sourceDescriptions.petStoreDescription.url") == "https://github.com/swagger-api/swagger-petstore/blob/master/src/main/resources/openapi.yaml"
