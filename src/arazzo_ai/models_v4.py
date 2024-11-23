from pathlib import Path
from dslmodel import DSLModel, Field
from typing import Any, Dict, List, Optional, Union
from enum import Enum


# Enums for fixed value fields
class InEnum(str, Enum):
    path = 'path'
    query = 'query'
    header = 'header'
    cookie = 'cookie'
    body = 'body'


class CriterionTypeEnum(str, Enum):
    simple = 'simple'
    regex = 'regex'
    jsonpath = 'jsonpath'
    xpath = 'xpath'


class SuccessActionTypeEnum(str, Enum):
    end = 'end'
    goto = 'goto'
    notify = 'notify'


class FailureActionTypeEnum(str, Enum):
    end = 'end'
    retry = 'retry'
    goto = 'goto'
    notify = 'notify'


class JsonPathVersionEnum(str, Enum):
    draft_goessner_dispatch_jsonpath_00 = 'draft-goessner-dispatch-jsonpath-00'


class XPathVersionEnum(str, Enum):
    xpath_30 = 'xpath-30'
    xpath_20 = 'xpath-20'
    xpath_10 = 'xpath-10'


# Models

class Info(DSLModel):
    title: str = Field(..., description="A human-readable title of the Arazzo Description.")
    summary: Optional[str] = Field(None, description="A short summary of the Arazzo Description.")
    description: Optional[str] = Field(None, description="A description of the purpose of the workflows defined. Supports CommonMark syntax.")
    version: str = Field(..., description="The version identifier of the Arazzo document (distinct from the Arazzo Specification version).")
    author: Optional[str] = Field(None, description="Author of the Arazzo document.")
    contact: Optional[str] = Field(None, description="Contact information for the document maintainer.")


class Credentials(DSLModel):
    name: str = Field(..., description="Name of the credential.")
    in_: str = Field(..., alias='in', description="Location of the credential (e.g., 'header', 'query').")
    value: str = Field(..., description="Value of the credential.")


class Authentication(DSLModel):
    type_: str = Field(..., alias='type', description="Authentication type (e.g., 'apiKey', 'oauth2').")
    credentials: Credentials = Field(..., description="Credentials required for authentication.")


class SourceDescription(DSLModel):
    name: str = Field(..., pattern=r'^[A-Za-z0-9_\-]+$',
                      description="Unique name for the source description. Should conform to the regular expression `[A-Za-z0-9_\\-]+`.")
    url: str = Field(..., description="A URL to a source description to be used by a workflow.")
    type_: Optional[str] = Field(None, alias='type',
                                 description='The type of source description. Possible values are "openapi", "arazzo", or other types as extended through Specification Extensions.')
    authentication: Optional[Authentication] = Field(None, description="Authentication details required to access the source.")


class CriterionExpressionType(DSLModel):
    type_: str = Field(..., alias='type', description="The type of condition to be applied. Allowed values: 'jsonpath' or 'xpath'.")
    version: str = Field(..., description="A shorthand string representing the version of the expression type being used (e.g., 'draft-goessner-dispatch-jsonpath-00').")


class Criterion(DSLModel):
    context: Optional[str] = Field(None, description="A runtime expression used to set the context for the condition.")
    condition: str = Field(..., description="The condition to apply.")
    type_: Optional[Union[CriterionTypeEnum, CriterionExpressionType]] = Field(None, alias='type',
                                                                              description="The type of condition to be applied. Defaults to 'simple' if not specified.")
    message: Optional[str] = Field(None, description="Message to display if the condition is not met.")


class PayloadReplacement(DSLModel):
    target: str = Field(..., description="A JSON Pointer or XPath Expression to locate the replacement target within the payload.")
    value: Any = Field(..., description="The value to set at the specified target location.")
    condition: Optional[Criterion] = Field(None, description="Condition under which the replacement should occur.")


class RequestBody(DSLModel):
    content_type: Optional[str] = Field(None, alias='contentType', description="The Content-Type for the request content.")
    payload: Optional[Any] = Field(None, description="A value representing the request body payload.")
    replacements: Optional[List[PayloadReplacement]] = Field(None, description="A list of locations and values to set within the payload.")
    schema: Optional[Any] = Field(None, description="JSON Schema defining the structure of the request body for validation purposes.")


class Parameter(DSLModel):
    name: str = Field(..., description="The name of the parameter. Parameter names are case sensitive.")
    in_: Optional[InEnum] = Field(None, alias='in', description="The location of the parameter.")
    value: Any = Field(..., description="The value to pass in the parameter.")
    type_: Optional[str] = Field(None, alias='type', description="The data type of the parameter (e.g., 'string', 'integer').")
    required: Optional[bool] = Field(False, description="Indicates if the parameter is required. Defaults to false.")


class ReusableObject(DSLModel):
    reference: str = Field(..., description="A runtime expression used to reference the desired object.")
    value: Optional[Any] = Field(None, description="Sets a value of the referenced parameter. Applicable only for parameter object references.")


class OutputsType(Dict[str, Any]):
    """Ensures keys match the regex '^[a-zA-Z0-9\\._-]+$'"""


class Notification(DSLModel):
    channel: str = Field(..., description="Notification channel (e.g., 'email', 'slack', 'sms').")
    recipients: List[str] = Field(..., description="List of recipients for the notification.")
    message_template: str = Field(..., alias='messageTemplate', description="Template for the notification message.")
    conditions: Optional[List[Criterion]] = Field(None, description="Conditions under which the notification should be sent.")


class SuccessAction(DSLModel):
    name: str = Field(..., description="The name of the success action. Names are case sensitive.")
    type_: SuccessActionTypeEnum = Field(..., alias='type', description="The type of action to take upon success.")
    workflow_id: Optional[str] = Field(None, alias='workflowId',
                                       description="The workflowId to transfer to upon success. Required if type is 'goto'.")
    step_id: Optional[str] = Field(None, alias='stepId',
                                   description="The stepId to transfer to upon success. Required if type is 'goto'.")
    notification_id: Optional[str] = Field(None, alias='notificationId',
                                           description="The notificationId to use when the action type is 'notify'.")
    criteria: Optional[List[Criterion]] = Field(None, description="A list of assertions to determine if this action shall be executed.")


class FailureAction(DSLModel):
    name: str = Field(..., description="The name of the failure action. Names are case sensitive.")
    type_: FailureActionTypeEnum = Field(..., alias='type', description="The type of action to take upon failure.")
    workflow_id: Optional[str] = Field(None, alias='workflowId',
                                       description="The workflowId to transfer to upon failure. Required if type is 'goto' or 'retry'.")
    step_id: Optional[str] = Field(None, alias='stepId',
                                   description="The stepId to transfer to upon failure. Required if type is 'goto' or 'retry'.")
    retry_after: Optional[float] = Field(None, alias='retryAfter',
                                         description="Seconds to delay after step failure before retrying. Applicable when type is 'retry'.")
    retry_limit: Optional[int] = Field(None, alias='retryLimit',
                                       description="Number of attempts to retry the step before failing. Applicable when type is 'retry'.")
    notification_id: Optional[str] = Field(None, alias='notificationId',
                                           description="The notificationId to use when the action type is 'notify'.")
    criteria: Optional[List[Criterion]] = Field(None, description="A list of assertions to determine if this action shall be executed.")


class AIModelConfig(DSLModel):
    model_id: str = Field(..., alias='modelId', description="Unique identifier for the AI model.")
    name: str = Field(..., description="Name of the AI model.")
    version: str = Field(..., description="Version of the AI model.")
    path: str = Field(..., description="Path or URL to the AI model.")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for configuring the AI model.")
    description: Optional[str] = Field(None, description="Description of the AI model's purpose.")


class HumanTask(DSLModel):
    assigned_to: str = Field(..., alias='assignedTo', description="User or team assigned to the task.")
    task_type: str = Field(..., alias='taskType', description="Type of task (e.g., 'approval', 'review', 'verification').")
    instructions: str = Field(..., description="Instructions for the human performing the task.")
    deadline: Optional[str] = Field(None, description="Deadline for task completion in ISO 8601 format.")
    priority: Optional[str] = Field(None, description="Priority level of the task (e.g., 'high', 'medium', 'low').")


class ResourceConfig(DSLModel):
    cpu: Optional[str] = Field(None, description="CPU allocation (e.g., '2', '500m').")
    memory: Optional[str] = Field(None, description="Memory allocation (e.g., '4Gi', '512Mi').")
    gpu: Optional[str] = Field(None, description="GPU allocation if required (e.g., '1').")
    storage: Optional[str] = Field(None, description="Storage allocation (e.g., '10Gi').")
    environment: Optional[Dict[str, str]] = Field(None, description="Environment variables for the step.")


class ComplianceRule(DSLModel):
    rule_id: str = Field(..., alias='ruleId', description="Identifier of the compliance rule.")
    description: Optional[str] = Field(None, description="Description of the compliance rule.")


class ComplianceMonitoring(DSLModel):
    enabled: bool = Field(..., description="Indicates if compliance monitoring is enabled.")
    rules: Optional[List[ComplianceRule]] = Field(None, description="List of compliance rules to enforce.")


class PerformanceMonitoring(DSLModel):
    enabled: bool = Field(..., description="Indicates if performance monitoring is enabled.")
    metrics: Optional[List[str]] = Field(None, description="List of performance metrics to monitor.")


class MonitoringConfig(DSLModel):
    performance: Optional[PerformanceMonitoring] = Field(None, description="Configuration for performance monitoring.")
    compliance: Optional[ComplianceMonitoring] = Field(None, description="Configuration for compliance monitoring.")


class Plugin(DSLModel):
    name: str = Field(..., description="The name of the plugin.")
    version: str = Field(..., description="The version of the plugin.")
    description: Optional[str] = Field(None, description="A description of the plugin's functionality.")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration settings for the plugin.")


class Step(DSLModel):
    description: Optional[str] = Field(None, description="A description of the step.")
    step_id: str = Field(..., alias='stepId', pattern=r'^[A-Za-z0-9_\-]+$',
                         description="Unique string to represent the step.")
    name: Optional[str] = Field(None, description="A human-readable name for the step.")
    operation_id: Optional[str] = Field(None, alias='operationId',
                                        description="The name of a resolvable operation defined in the source description.")
    operation_path: Optional[str] = Field(None, alias='operationPath', description="A reference to an operation using a JSON Pointer.")
    workflow_id: Optional[str] = Field(None, alias='workflowId',
                                       description="The workflowId referencing another workflow within the Arazzo Description.")
    parameters: Optional[List[Union[Parameter, ReusableObject]]] = Field(None,
                                                                         description="A list of parameters to pass to an operation or workflow.")
    request_body: Optional[RequestBody] = Field(None, alias='requestBody', description="The request body to pass to an operation.")
    success_criteria: Optional[List[Criterion]] = Field(None, alias='successCriteria',
                                                        description="A list of assertions to determine the success of the step.")
    on_success: Optional[List[Union[SuccessAction, ReusableObject]]] = Field(None, alias='onSuccess',
                                                                             description="An array of success action objects.")
    on_failure: Optional[List[Union[FailureAction, ReusableObject]]] = Field(None, alias='onFailure',
                                                                             description="An array of failure action objects.")
    outputs: Optional[OutputsType] = Field(None, description="A map between a friendly name and a dynamic output value.")
    human_task: Optional[HumanTask] = Field(None, alias='humanTask',
                                            description="Human-in-the-loop task associated with the step.")
    code: Optional[str] = Field(None, description="Custom code to execute during the step.")
    callable_: Optional[str] = Field(None, alias='callable', description="Callable function to execute during the step.")
    resources: Optional[ResourceConfig] = Field(None, description="Resource allocation for the step.")
    ai_model: Optional[str] = Field(None, alias='aiModel',
                                    description="AI model reference to integrate AI-driven decision-making within the step.")


class Components(DSLModel):
    inputs: Optional[Dict[str, Any]] = Field(None, description="An object to hold reusable JSON Schema objects for workflow inputs.")
    parameters: Optional[Dict[str, Parameter]] = Field(None, description="An object to hold reusable Parameter objects.")
    success_actions: Optional[Dict[str, SuccessAction]] = Field(None, alias='successActions',
                                                                description="An object to hold reusable Success Action objects.")
    failure_actions: Optional[Dict[str, FailureAction]] = Field(None, alias='failureActions',
                                                                description="An object to hold reusable Failure Action objects.")
    notifications: Optional[Dict[str, Notification]] = Field(None, description="An object to hold reusable Notification objects.")
    ai_models: Optional[Dict[str, AIModelConfig]] = Field(None, alias='aiModels',
                                                          description="An object to hold reusable AI Model configurations.")


class Workflow(DSLModel):
    workflow_id: str = Field(..., alias='workflowId', pattern=r'^[A-Za-z0-9_\-]+$',
                             description="Unique string to represent the workflow.")
    name: Optional[str] = Field(None, description="A human-readable name for the workflow.")
    summary: Optional[str] = Field(None, description="A summary of the purpose or objective of the workflow.")
    description: Optional[str] = Field(None, description="A description of the workflow. Supports CommonMark syntax.")
    inputs: Optional[Any] = Field(None, description="A JSON Schema object representing the input parameters used by this workflow.")
    depends_on: Optional[List[str]] = Field(None, alias='dependsOn',
                                            description="A list of workflows that must be completed before this workflow can be processed.")
    steps: List[Step] = Field(..., description="An ordered list of steps in the workflow.")
    success_actions: Optional[List[Union[SuccessAction, ReusableObject]]] = Field(None, alias='successActions',
                                                                                  description="A list of success actions applicable to all steps in the workflow.")
    failure_actions: Optional[List[Union[FailureAction, ReusableObject]]] = Field(None, alias='failureActions',
                                                                                  description="A list of failure actions applicable to all steps in the workflow.")
    outputs: Optional[OutputsType] = Field(None, description="A map between a friendly name and a dynamic output value produced by the workflow.")
    parameters: Optional[List[Union[Parameter, ReusableObject]]] = Field(None,
                                                                         description="A list of parameters applicable for all steps in the workflow.")
    ai_models: Optional[List[Union[AIModelConfig, ReusableObject]]] = Field(None, alias='aiModels',
                                                                            description="A list of AI model configurations associated with this workflow.")
    monitoring: Optional[MonitoringConfig] = Field(None, description="Configuration for monitoring workflow performance and compliance.")


class ArazzoSpecification(DSLModel):
    arazzo: str = Field(...,
                        description="This string MUST be the version number of the Arazzo Specification that the Arazzo Description uses.")
    info: Info = Field(..., description="Provides metadata about the workflows contained within the Arazzo Description.")
    source_descriptions: List[SourceDescription] = Field(..., alias='sourceDescriptions',
                                                         description="A list of source descriptions that this Arazzo Description applies to.")
    workflows: List[Workflow] = Field(..., description="A list of workflows defined in the Arazzo Description.")
    components: Optional[Components] = Field(None,
                                             description="An element to hold various reusable schemas and components for the Arazzo Description.")
    plugins: Optional[List[Plugin]] = Field(None, description="A list of plugins to extend CLI functionalities.")


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()
    # Replace with the actual path to your Arazzo Description file
    arazzo_file_path = "arazzo_4_1_0.yaml"
    arazzo_content = Path(arazzo_file_path).read_text()

    try:
        spec = ArazzoSpecification.from_yaml(arazzo_content)
        print("Arazzo Specification parsed successfully:")
        print(spec)
    except Exception as e:
        print(f"Error parsing Arazzo Specification: {e}")


if __name__ == '__main__':
    main()
