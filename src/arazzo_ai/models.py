from typing import List, Optional, Dict, Any, Union
from pydantic import Field
from pydantic import BaseModel

# Assuming DSLModel is a subclass of BaseModel
class DSLModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        anystr_strip_whitespace = True

# 1. ArazzoSpecification Object
class ArazzoSpecification(DSLModel):
    """
    The root Arazzo Specification object.
    """
    arazzo_version: str = Field(
        ...,
        alias="arazzo",
        description="The version number of the Arazzo Specification being used."
    )
    info: "Info" = Field(
        ..., description="Metadata about the workflows in the Arazzo document."
    )
    source_descriptions: List["SourceDescription"] = Field(
        ..., alias="sourceDescriptions",
        description="A list of source descriptions (e.g., OpenAPI descriptions) to be used by workflows."
    )
    workflows: List["Workflow"] = Field(
        ..., description="A list of workflows defined in this Arazzo document."
    )
    components: Optional["Components"] = Field(
        None, description="Holds reusable objects for the Arazzo document."
    )
    plugins: Optional[List["Plugin"]] = Field(
        None, description="A list of plugins to extend CLI functionalities."
    )

# 2. Info Object
class Info(DSLModel):
    """
    Provides metadata about the workflows defined in the Arazzo document.
    """
    title: str = Field(..., description="A human-readable title for the Arazzo Description.")
    summary: Optional[str] = Field(None, description="A short summary of the Arazzo Description.")
    description: Optional[str] = Field(
        None,
        description="A description of the purpose of the workflows defined. Supports CommonMark syntax."
    )
    version: str = Field(..., description="The version identifier of the Arazzo document.")
    author: Optional[str] = Field(None, description="Author of the Arazzo document.")
    contact: Optional[str] = Field(None, description="Contact information for the document maintainer.")

# 3. SourceDescription Object
class SourceDescription(DSLModel):
    """
    Describes a source description that will be referenced by workflows.
    """
    name: str = Field(..., description="A unique name for the source description.")
    url: str = Field(..., description="A URL to the source description.")
    type_: str = Field(
        ..., alias="type",
        description="The type of source description, e.g., 'openapi' or 'arazzo'."
    )
    authentication: Optional["Authentication"] = Field(
        None, description="Authentication details required to access the source."
    )

# 3a. Authentication Object
class Authentication(DSLModel):
    """
    Describes authentication details for accessing a source description.
    """
    type_: str = Field(..., description="The type of authentication, e.g., 'apiKey', 'oauth2'.")
    credentials: Dict[str, Any] = Field(
        ..., description="Credentials required for the authentication type."
    )

# 4. Workflow Object
class Workflow(DSLModel):
    """
    Describes a workflow, including its steps, inputs, and outputs.
    """
    workflow_id: str = Field(
        ..., alias="workflowId",
        description="Unique identifier for the workflow."
    )
    name: Optional[str] = Field(None, description="A human-readable name for the workflow.")
    summary: Optional[str] = Field(None, description="A summary of the workflow's purpose.")
    description: Optional[str] = Field(
        None,
        description="A detailed description of the workflow. Supports CommonMark syntax."
    )
    inputs: Dict[str, Any] = Field(
        ..., description="Input parameters for the workflow, defined as JSON schema."
    )
    depends_on: Optional[List[str]] = Field(
        None, alias="dependsOn",
        description="List of workflow IDs that this workflow depends on."
    )
    steps: List["Step"] = Field(..., description="Ordered list of steps that define the workflow.")
    success_actions: Optional[List[Union["SuccessAction", "ReusableObject"]]] = Field(
        None, alias="successActions",
        description="Actions to take when the workflow succeeds."
    )
    failure_actions: Optional[List[Union["FailureAction", "ReusableObject"]]] = Field(
        None, alias="failureActions",
        description="Actions to take when the workflow fails."
    )
    outputs: Optional[Dict[str, str]] = Field(
        None, description="Mapping of friendly names to output values."
    )
    parameters: Optional[List[Union["Parameter", "ReusableObject"]]] = Field(
        None, description="Parameters applicable to all steps in the workflow."
    )
    ai_models: Optional[List[Union["AIModelConfig", "ReusableObject"]]] = Field(
        None, alias="aiModels",
        description="AI model configurations associated with the workflow."
    )
    monitoring: Optional["MonitoringConfig"] = Field(
        None, description="Configuration for monitoring workflow performance and compliance."
    )

# 4a. MonitoringConfig Object
class MonitoringConfig(DSLModel):
    """
    Configuration for monitoring workflow performance and compliance.
    """
    performance: Optional["PerformanceMonitoring"] = Field(
        None, description="Performance monitoring settings."
    )
    compliance: Optional["ComplianceMonitoring"] = Field(
        None, description="Compliance monitoring settings."
    )

# 4b. PerformanceMonitoring Object
class PerformanceMonitoring(DSLModel):
    """
    Settings for performance monitoring.
    """
    enabled: bool = Field(..., description="Enable or disable performance monitoring.")
    metrics: List[str] = Field(..., description="List of performance metrics to monitor.")

# 4c. ComplianceMonitoring Object
class ComplianceMonitoring(DSLModel):
    """
    Settings for compliance monitoring.
    """
    enabled: bool = Field(..., description="Enable or disable compliance monitoring.")
    rules: List["ComplianceRule"] = Field(..., description="List of compliance rules to enforce.")

# 4d. ComplianceRule Object
class ComplianceRule(DSLModel):
    """
    Describes a compliance rule to enforce.
    """
    rule_id: str = Field(..., alias="ruleId", description="Unique identifier for the compliance rule.")
    description: str = Field(..., description="Description of the compliance rule.")

# 5. Step Object
class Step(DSLModel):
    """
    Represents a single step in a workflow.
    """
    step_id: str = Field(
        ..., alias="stepId",
        description="Unique identifier for the step."
    )
    name: Optional[str] = Field(None, description="A human-readable name for the step.")
    description: Optional[str] = Field(
        None, description="A description of what the step does."
    )
    operation_id: Optional[str] = Field(
        None,
        alias="operationId",
        description="The operation ID to execute, as defined in the source descriptions."
    )
    operation_path: Optional[str] = Field(
        None,
        alias="operationPath",
        description="The path to the operation, if the operationId is not used."
    )
    workflow_id: Optional[str] = Field(
        None,
        alias="workflowId",
        description="Reference to another workflow to execute as part of this step."
    )
    parameters: Optional[List[Union["Parameter", "ReusableObject"]]] = Field(
        None, description="Parameters to pass into the operation or workflow."
    )
    request_body: Optional["RequestBody"] = Field(
        None,
        alias="requestBody",
        description="The request body for the operation."
    )
    success_criteria: List["Criterion"] = Field(
        ..., alias="successCriteria",
        description="Conditions that must be met for the step to be considered successful."
    )
    on_success: Optional[List[Union["SuccessAction", "ReusableObject"]]] = Field(
        None, alias="onSuccess",
        description="Actions to take when the step succeeds."
    )
    on_failure: Optional[List[Union["FailureAction", "ReusableObject"]]] = Field(
        None, alias="onFailure",
        description="Actions to take when the step fails."
    )
    outputs: Optional[Dict[str, str]] = Field(
        None, description="Output values from the step."
    )
    human_task: Optional["HumanTask"] = Field(
        None, alias="humanTask",
        description="Human-in-the-loop task associated with the step."
    )
    code: Optional[str] = Field(
        None, description="Custom code to execute during the step."
    )
    callable_: Optional[str] = Field(
        None, alias="callable",
        description="Callable function to execute during the step."
    )
    resources: Optional["ResourceConfig"] = Field(
        None, description="Resource allocation for the step."
    )

# 6. Parameter Object
class Parameter(DSLModel):
    """
    Describes a parameter for a workflow step.
    """
    name: str = Field(..., description="The name of the parameter.")
    in_: str = Field(
        ..., alias="in",
        description="The location of the parameter (e.g., 'path', 'query', 'header', 'cookie', 'body')."
    )
    value: Any = Field(..., description="The value to pass in the parameter.")
    type_: Optional[str] = Field(
        None, alias="type",
        description="The data type of the parameter (e.g., 'string', 'integer')."
    )
    required: Optional[bool] = Field(
        None, description="Indicates if the parameter is required."
    )

# 7. RequestBody Object
class RequestBody(DSLModel):
    """
    Describes the request body for an operation.
    """
    content_type: str = Field(
        ..., alias="contentType",
        description="The Content-Type of the request body."
    )
    payload: Any = Field(..., description="The content of the request body.")
    replacements: Optional[List["PayloadReplacement"]] = Field(
        None,
        description="List of locations and values to replace in the payload."
    )
    schema: Optional[Dict[str, Any]] = Field(
        None, description="JSON Schema defining the structure of the request body for validation purposes."
    )

# 8. Criterion Object
class Criterion(DSLModel):
    """
    Represents a condition for evaluating the success or failure of a step.
    """
    context: Optional[str] = Field(
        None,
        description="The runtime expression context for the condition."
    )
    condition: str = Field(
        ...,
        description="The condition expression."
    )
    type_: Optional[Union[str, "CriterionExpressionType"]] = Field(
        None, alias="type",
        description="The type of the condition (e.g., 'simple', 'jsonpath', 'regex', 'xpath')."
    )
    message: Optional[str] = Field(
        None,
        description="Message to display if the condition is not met."
    )

# 8a. CriterionExpressionType Object
class CriterionExpressionType(DSLModel):
    """
    Describes the type and version of an expression used in a Criterion.
    """
    type_: str = Field(
        ..., description="The type of condition, either 'jsonpath' or 'xpath'."
    )
    version: str = Field(
        ..., description="Version of the expression type being used."
    )

# 9. SuccessAction and FailureAction Objects
class SuccessAction(DSLModel):
    """
    Describes an action to take upon successful execution of a step.
    """
    name: str = Field(..., description="The name of the success action.")
    type_: str = Field(
        ..., alias="type",
        description="The type of action to take (e.g., 'goto', 'end', 'notify')."
    )
    workflow_id: Optional[str] = Field(
        None, alias="workflowId",
        description="The workflow ID to jump to if the action type is 'goto'."
    )
    step_id: Optional[str] = Field(
        None, alias="stepId",
        description="The step ID to jump to if the action type is 'goto'."
    )
    notification_id: Optional[str] = Field(
        None, alias="notificationId",
        description="The notification ID to use if the action type is 'notify'."
    )
    criteria: Optional[List["Criterion"]] = Field(
        None,
        description="Criteria to determine if this success action should be executed."
    )

class FailureAction(DSLModel):
    """
    Describes an action to take upon failure of a step.
    """
    name: str = Field(..., description="The name of the failure action.")
    type_: str = Field(
        ..., alias="type",
        description="The type of action to take (e.g., 'goto', 'retry', 'end', 'notify')."
    )
    workflow_id: Optional[str] = Field(
        None, alias="workflowId",
        description="The workflow ID to jump to if the action type is 'goto' or 'retry'."
    )
    step_id: Optional[str] = Field(
        None, alias="stepId",
        description="The step ID to jump to if the action type is 'goto' or 'retry'."
    )
    retry_after: Optional[int] = Field(
        None, alias="retryAfter",
        description="Delay in seconds before retrying the step."
    )
    retry_limit: Optional[int] = Field(
        None, alias="retryLimit",
        description="The maximum number of retries."
    )
    notification_id: Optional[str] = Field(
        None, alias="notificationId",
        description="The notification ID to use if the action type is 'notify'."
    )
    criteria: Optional[List["Criterion"]] = Field(
        None,
        description="Criteria to determine if this failure action should be executed."
    )

# 10. PayloadReplacement Object
class PayloadReplacement(DSLModel):
    """
    Describes a location in the payload to replace with a value.
    """
    target: str = Field(..., description="The JSON Pointer or XPath for the replacement target.")
    value: Any = Field(..., description="The value to replace at the target location.")
    condition: Optional["Criterion"] = Field(
        None, description="Condition under which the replacement should occur."
    )

# 11. Components Object
class Components(DSLModel):
    """
    Holds reusable objects for the Arazzo document.
    """
    inputs: Optional[Dict[str, Any]] = Field(
        None, description="Reusable JSON Schema objects for workflow inputs."
    )
    parameters: Optional[Dict[str, "Parameter"]] = Field(
        None, description="Reusable parameters."
    )
    success_actions: Optional[Dict[str, Union["SuccessAction", "ReusableObject"]]] = Field(
        None, alias="successActions", description="Reusable success actions."
    )
    failure_actions: Optional[Dict[str, Union["FailureAction", "ReusableObject"]]] = Field(
        None, alias="failureActions", description="Reusable failure actions."
    )
    notifications: Optional[Dict[str, "Notification"]] = Field(
        None, alias="notifications", description="Reusable notification configurations."
    )
    ai_models: Optional[Dict[str, "AIModelConfig"]] = Field(
        None, alias="aiModels", description="Reusable AI model configurations."
    )

# 12. Plugin Object
class Plugin(DSLModel):
    """
    Describes a plugin to extend CLI functionalities.
    """
    name: str = Field(..., description="The name of the plugin.")
    version: str = Field(..., description="The version of the plugin.")
    description: Optional[str] = Field(None, description="A description of the plugin's functionality.")
    config: Optional[Dict[str, Any]] = Field(
        None, description="Configuration settings for the plugin."
    )

# 13. AIModelConfig Object
class AIModelConfig(DSLModel):
    """
    Configuration for an AI model used within a workflow.
    """
    model_id: str = Field(..., alias="modelId", description="Unique identifier for the AI model.")
    name: str = Field(..., description="Name of the AI model.")
    version: str = Field(..., description="Version of the AI model.")
    path: str = Field(..., description="Path or URL to the AI model.")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Parameters for configuring the AI model."
    )
    description: Optional[str] = Field(
        None, description="Description of the AI model's purpose."
    )

# 14. Notification Object
class Notification(DSLModel):
    """
    Describes a notification configuration.
    """
    channel: str = Field(..., description="Notification channel (e.g., 'email', 'slack', 'sms').")
    recipients: List[str] = Field(..., description="List of recipients for the notification.")
    message_template: str = Field(
        ..., alias="messageTemplate",
        description="Template for the notification message. Can include runtime expressions."
    )
    conditions: Optional[List["Criterion"]] = Field(
        None, description="Conditions under which the notification should be sent."
    )

# 15. HumanTask Object
class HumanTask(DSLModel):
    """
    Describes a human-in-the-loop task associated with a workflow step.
    """
    assigned_to: str = Field(..., alias="assignedTo", description="User or team assigned to the task.")
    task_type: str = Field(..., alias="taskType", description="Type of task (e.g., 'approval', 'review').")
    instructions: str = Field(..., description="Instructions for the human performing the task.")
    deadline: Optional[str] = Field(
        None, description="Deadline for task completion in ISO 8601 format."
    )
    priority: Optional[str] = Field(
        None, description="Priority level of the task (e.g., 'high', 'medium', 'low')."
    )

# 16. Condition Object
# Already defined as Criterion; no separate model needed unless different

# 17. ResourceConfig Object
class ResourceConfig(DSLModel):
    """
    Defines resource allocation for a workflow step.
    """
    cpu: Optional[str] = Field(
        None, description="CPU allocation (e.g., '2', '500m')."
    )
    memory: Optional[str] = Field(
        None, description="Memory allocation (e.g., '4Gi', '512Mi')."
    )
    gpu: Optional[str] = Field(
        None, description="GPU allocation if required (e.g., '1')."
    )
    storage: Optional[str] = Field(
        None, description="Storage allocation (e.g., '10Gi')."
    )
    environment: Optional[Dict[str, str]] = Field(
        None, description="Environment variables for the step."
    )

# 18. Schedule Models
class CronSchedule(DSLModel):
    """
    Represents a Cron schedule for workflow execution.
    """
    cron: str = Field(..., description="Cron expression defining the schedule.")
    timezone: Optional[str] = Field(
        None, description="Timezone for the Cron schedule. Defaults to 'UTC'."
    )

class DateSchedule(DSLModel):
    """
    Represents a specific date and time to execute the workflow.
    """
    run_date: str = Field(..., alias="runDate",
                           description="The date and time to run the workflow in ISO 8601 format or 'now' to execute immediately.")
    timezone: Optional[str] = Field(
        None, description="Timezone for the run date. Defaults to 'UTC'."
    )

class Schedule(DSLModel):
    """
    Union of possible schedule types for workflow execution.
    """
    cron: Optional[CronSchedule] = Field(
        None, description="Cron-based schedule."
    )
    date: Optional[DateSchedule] = Field(
        None, description="Date-based schedule."
    )

# 19. ReusableObject
class ReusableObject(DSLModel):
    """
    A simple object to reference reusable components.
    """
    reference: str = Field(..., description="A runtime expression used to reference the desired object.")
    value: Optional[str] = Field(
        None, description="Sets a value of the referenced parameter. Applicable for parameter object references."
    )

# Register forward references
ArazzoSpecification.update_forward_refs()
Info.update_forward_refs()
SourceDescription.update_forward_refs()
Authentication.update_forward_refs()
Workflow.update_forward_refs()
MonitoringConfig.update_forward_refs()
PerformanceMonitoring.update_forward_refs()
ComplianceMonitoring.update_forward_refs()
ComplianceRule.update_forward_refs()
Step.update_forward_refs()
Parameter.update_forward_refs()
RequestBody.update_forward_refs()
Criterion.update_forward_refs()
CriterionExpressionType.update_forward_refs()
SuccessAction.update_forward_refs()
FailureAction.update_forward_refs()
PayloadReplacement.update_forward_refs()
Components.update_forward_refs()
Plugin.update_forward_refs()
AIModelConfig.update_forward_refs()
Notification.update_forward_refs()
HumanTask.update_forward_refs()
ResourceConfig.update_forward_refs()
CronSchedule.update_forward_refs()
DateSchedule.update_forward_refs()
Schedule.update_forward_refs()
ReusableObject.update_forward_refs()
