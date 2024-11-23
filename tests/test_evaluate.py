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
        "steps": {
            "checkLoanCanBeProvided": {
                "outputs": {
                    "eligibilityCheckRequired": True,
                    "eligibleProducts": [{"productCode": "123", "eligible": True}],
                    "totalLoanAmount": 150.00
                }
            },
            "initiateBnplTransaction": {
                "outputs": {
                    "loanTransactionId": "123",
                    "loanTransactionResourceUrl": "https://example.com/transaction/123",
                    "redirectAuthToken": "auth-token-123"
                }
            }
        },
        "method": "POST",
        "statusCode": 200
    }


def test_simple_expression(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    assert evaluator("$inputs.customer.firstName") == "John"
    assert evaluator("$inputs.customer.postalCode") == "12345"
    assert evaluator("$method") == "POST"
    assert evaluator("$statusCode") == 200


def test_nested_expression(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    assert evaluator("$response.body.totalAmount") == 150.00
    assert evaluator("$steps.checkLoanCanBeProvided.outputs.totalLoanAmount") == 150.00
    assert evaluator("$response.body.links.self") == "https://example.com/transaction/123"


def test_array_expression(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    assert evaluator("$inputs.products.0.productCode") == "123"
    assert evaluator("$inputs.products.1.purchaseAmount.amount") == 50.00


def test_embedded_expression(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    result = evaluator("Hello, {$inputs.customer.firstName}!")
    assert result == "Hello, John!"

    result = evaluator("Your order total is {$response.body.totalAmount} USD.")
    assert result == "Your order total is 150.0 USD."


def test_embedded_expression_with_nonexistent_value(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    result = evaluator("Hello, {$inputs.customer.middleName}!")
    assert result == "Hello, None!"  # Expecting "None" if the value is not found.


def test_partial_path_resolution(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    assert evaluator("$inputs.products.0") == {"productCode": "123",
                                               "purchaseAmount": {"currency": "USD", "amount": 100.00}}


def test_path_with_invalid_index(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    result = evaluator("$inputs.products.5.productCode")
    assert result is None  # Index out of range should return None


def test_expression_with_empty_path(sample_context):
    evaluator = ExpressionEvaluator(sample_context)
    assert evaluator("$method") == "POST"
    assert evaluator("$response") == sample_context["response"]


