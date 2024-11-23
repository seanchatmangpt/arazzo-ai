import pytest
from arazzo_ai.condition import ConditionEvaluator


@pytest.fixture
def sample_context():
    return {
        "inputs": {
            "username": "john_doe",
            "password": "supersecure"
        },
        "response": {
            "body": {
                "status": "success",
                "pets": [
                    {"id": 1, "name": "Fluffy"},
                    {"id": 2, "name": "Whiskers"}
                ],
                "totalAmount": 150.0
            },
            "header": {
                "Location": "https://example.com/redirect"
            }
        },
        "statusCode": 200,
        "steps": {
            "loginStep": {
                "outputs": {
                    "sessionToken": "abcd1234"
                }
            }
        }
    }


def test_simple_condition_evaluation(sample_context):
    evaluator = ConditionEvaluator(sample_context)
    assert evaluator.evaluate("$statusCode == 200", condition_type='simple') is True


def test_regex_condition_evaluation(sample_context):
    evaluator = ConditionEvaluator(sample_context)
    assert evaluator.evaluate("^success$", context="$response.body.status", condition_type='regex') is True


def test_jsonpath_condition_evaluation(sample_context):
    evaluator = ConditionEvaluator(sample_context)
    # Check if a JSONPath query finds the 'pets' array
    assert evaluator.evaluate("$.pets", context="$response.body", condition_type='jsonpath') is not None
    # Check if a JSONPath query can find a specific pet by ID
    assert evaluator.evaluate("$.pets[?(@.id == 1)]", context="$response.body", condition_type='jsonpath') is not None


def test_step_output_access(sample_context):
    evaluator = ConditionEvaluator(sample_context)
    # Accessing the output of a previous step
    assert evaluator.evaluate("$steps.loginStep.outputs.sessionToken", condition_type='simple') == "abcd1234"


def test_jsonpath_filtering(sample_context):
    evaluator = ConditionEvaluator(sample_context)
    # Checking if a JSONPath filter can find a pet by name
    assert evaluator.evaluate("$.pets[?(@.name == 'Fluffy')]", context="$response.body",
                              condition_type='jsonpath') is not None
