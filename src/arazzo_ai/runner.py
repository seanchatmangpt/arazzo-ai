import json
from pathlib import Path
from typing import Dict, Any, Optional
from arazzo_ai.models import ArazzoSpecification, Step, Criterion
from arazzo_ai.evaluate import ExpressionEvaluator  # Assuming the evaluator is imported from this module


def load_arazzo_spec(yaml_path: str) -> ArazzoSpecification:
    """Load the Arazzo specification from the given YAML file."""
    content = Path(yaml_path).read_text()
    return ArazzoSpecification.from_yaml(content)


def simulate_response(step: Step, context: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate an API response for a given step."""
    print(f"Simulating response for step: {step.step_id}")
    # Example response for simulation; adjust as needed.
    return {
        "statusCode": 200,
        "body": {
            "existingCustomerNotEligible": False,
            "products": [{"productCode": "PRD123", "eligible": True}],
            "eligibilityCheckRequired": True,
            "redirectAuthToken": "dummyAuthToken",
            "links": {"self": "https://api.example.com/customer/12345"},
            "totalAmount": 1000.0
        },
        "headers": {
            "Location": "https://auth.example.com/redirect"
        }
    }


def evaluate_criteria(criteria: Criterion, context: Dict[str, Any], evaluator: ExpressionEvaluator) -> bool:
    """Evaluate a single criterion against the context using the evaluator."""
    try:
        result = evaluator(criteria.condition)
        # For conditions that should return a boolean directly, like simple conditions
        return bool(result)
    except Exception as e:
        print(f"Error evaluating condition '{criteria.condition}': {e}")
        return False


def execute_step(step: Step, context: Dict[str, Any], evaluator: ExpressionEvaluator) -> Dict[str, Any]:
    """Execute a step and update the context with simulated responses."""
    print(f"\nExecuting step: {step.step_id} - {step.description}")
    response = simulate_response(step, context)
    context.update({
        "statusCode": response["statusCode"],
        "response": response["body"],
        "headers": response["headers"]
    })
    print(f"Simulated API response: {json.dumps(response, indent=2)}")

    # Extract outputs based on the response.
    for output_key, output_expression in step.outputs.items():
        result = evaluator(output_expression)
        context[output_key] = result
        print(f"Evaluating output expression '{output_expression}' => {result}")
        print(f"Extracted output - {output_key}: {context[output_key]}")

    return context



def transition_to_next_step(current_step: Step, context: Dict[str, Any], steps_by_id: Dict[str, Step], evaluator: ExpressionEvaluator) -> Optional[Step]:
    """Determine the next step based on the success criteria and actions."""
    for action in current_step.on_success:
        if all(evaluate_criteria(criterion, context, evaluator) for criterion in action.criteria):
            print(f"Action '{action.name}' met criteria. Transitioning to step: {action.step_id}")
            if action.type_ == "goto":
                return steps_by_id.get(action.step_id)
            elif action.type_ == "end":
                print(f"Action '{action.name}' indicates workflow should end.")
                return None
            break
    print("No further steps; ending workflow execution.")
    return None


def run_workflow(workflow: ArazzoSpecification, input_data: Dict[str, Any]):
    """Run a workflow by iterating over its steps and evaluating conditions."""
    context = {"inputs": input_data, "steps": {}, "outputs": {}}
    evaluator = ExpressionEvaluator(context)
    workflow_instance = workflow.workflows[0]

    # Index steps by their ID for easy lookup.
    steps_by_id = {step.step_id: step for step in workflow_instance.steps}

    # Determine the starting step dynamically.
    current_step = next(iter(steps_by_id.values()), None)

    while current_step:
        context = execute_step(current_step, context, evaluator)
        current_step = transition_to_next_step(current_step, context, steps_by_id, evaluator)

    print("\nWorkflow execution completed.")
    print("Final Workflow Outputs:")
    print(json.dumps(context.get("outputs", {}), indent=2))


def main():
    yaml_path = "bnpl-arazzo.yaml"  # Adjust this path to your local YAML file.
    spec = load_arazzo_spec(yaml_path)

    example_inputs = {
        "customer": {
            "firstName": "Jane",
            "lastName": "Doe",
            "dateOfBirth": "1990-01-01",
            "postalCode": "12345"
        },
        "products": [
            {
                "productCode": "PRD123",
                "purchaseAmount": {
                    "currency": "USD",
                    "amount": 500
                }
            }
        ]
    }

    run_workflow(spec, example_inputs)


if __name__ == '__main__':
    main()
