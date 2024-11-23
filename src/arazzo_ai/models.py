from pathlib import Path
from dslmodel import DSLModel, Field


from typing import Any, Dict, List, Optional, Union
from enum import Enum


# Enums for fixed value fields
class SourceDescriptionType(str, Enum):
    openapi = 'openapi'
    arazzo = 'arazzo'


class InEnum(str, Enum):
    path = 'path'
    query = 'query'
    header = 'header'
    cookie = 'cookie'
    body = 'body'


class CriterionType(str, Enum):
    simple = 'simple'
    regex = 'regex'
    jsonpath = 'jsonpath'
    xpath = 'xpath'


class SuccessActionType(str, Enum):
    end = 'end'
    goto = 'goto'


class FailureActionType(str, Enum):
    end = 'end'
    retry = 'retry'
    goto = 'goto'


# Models

class Info(DSLModel):
    title: str = Field(..., description="A human-readable title of the Arazzo Description.")
    summary: Optional[str] = Field(None, description="A short summary of the Arazzo Description.")
    description: Optional[str] = Field(None, description="A description of the purpose of the workflows defined. Supports CommonMark syntax.")
    version: str = Field(..., description="The version identifier of the Arazzo document (distinct from the Arazzo Specification version).")


class SourceDescription(DSLModel):
    name: str = Field(..., pattern=r'^[A-Za-z0-9_\-]+$', description="Unique name for the source description. Should conform to the regular expression `[A-Za-z0-9_\\-]+`.")
    url: str = Field(..., description="A URL to a source description. If a relative reference is used, it must follow URI-reference format as defined by RFC3986.")
    type_: SourceDescriptionType = Field(..., alias='type', description="The type of source description. Possible values are 'openapi' or 'arazzo'.")


class Parameter(DSLModel):
    name: str = Field(..., description="The name of the parameter. Parameter names are case sensitive.")
    in_: Optional[InEnum] = Field("", alias='in', description="The location of the parameter. Possible values are 'path', 'query', 'header', 'cookie', or 'body'.")
    value: Any = Field(..., description="The value to pass in the parameter. Can be a constant or a runtime expression.")


class ReusableObject(DSLModel):
    reference: str = Field(..., description="A runtime expression used to reference the desired reusable component.")
    value: Optional[Any] = Field(None, description="Sets a value of the referenced parameter. Applicable only for parameter object references.")


class CriterionExpressionType(DSLModel):
    type_: str = Field(..., alias='type', description="The type of condition to be applied. Allowed values: 'jsonpath' or 'xpath'.")
    version: str = Field(..., description="A shorthand string representing the version of the expression type being used (e.g., 'draft-goessner-dispatch-jsonpath-00').")


class Criterion(DSLModel):
    context: Optional[str] = Field(None, description="A runtime expression used to set the context for the condition.")
    condition: str = Field(..., description="The condition to apply. Can be simple, regex, JSONPath, or XPath expressions.")
    type_: Optional[Union[CriterionType, CriterionExpressionType]] = Field(None, alias='type', description="The type of condition to be applied. Defaults to 'simple' if not specified.")


class SuccessAction(DSLModel):
    name: str = Field(..., description="The name of the success action. Names are case sensitive.")
    type_: SuccessActionType = Field(..., alias='type', description="The type of action to take upon success. Possible values: 'end' or 'goto'.")
    workflow_id: Optional[str] = Field(None, alias='workflowId', description="The workflowId to transfer to upon success. Required if type is 'goto' and the target is a workflow.")
    step_id: Optional[str] = Field(None, alias='stepId', description="The stepId to transfer to upon success. Required if type is 'goto' and the target is a step.")
    criteria: Optional[List[Criterion]] = Field(None, description="A list of assertions to determine if this action shall be executed.")


class FailureAction(DSLModel):
    name: str = Field(..., description="The name of the failure action. Names are case sensitive.")
    type_: FailureActionType = Field(..., alias='type', description="The type of action to take upon failure. Possible values: 'end', 'retry', or 'goto'.")
    workflow_id: Optional[str] = Field(None, alias='workflowId', description="The workflowId to transfer to upon failure. Required if type is 'goto' or 'retry'.")
    step_id: Optional[str] = Field(None, alias='stepId', description="The stepId to transfer to upon failure. Required if type is 'goto' or 'retry'.")
    retry_after: Optional[float] = Field(None, alias='retryAfter', description="Seconds to delay after step failure before retrying. Applicable only if type is 'retry'.")
    retry_limit: Optional[int] = Field(None, alias='retryLimit', description="Number of attempts to retry the step before failing. Applicable only if type is 'retry'.")
    criteria: Optional[List[Criterion]] = Field(None, description="A list of assertions to determine if this action shall be executed.")


class PayloadReplacement(DSLModel):
    target: str = Field(..., description="A JSON Pointer or XPath Expression to locate the replacement target within the payload.")
    value: Any = Field(..., description="The value to set at the specified target location.")


class RequestBody(DSLModel):
    content_type: Optional[str] = Field(None, alias='contentType', description="The Content-Type for the request content.")
    payload: Optional[Any] = Field(None, description="A value representing the request body payload. Can include runtime expressions.")
    replacements: Optional[List[PayloadReplacement]] = Field(None, description="A list of locations and values to set within the payload.")


OutputsType = Dict[str, str]  # Ensures keys match the regex '^[a-zA-Z0-9\.\-_]+$'


class Step(DSLModel):
    description: Optional[str] = Field(None, description="A description of the step. Supports CommonMark syntax.")
    step_id: str = Field(..., alias='stepId', pattern=r'^[A-Za-z0-9_\-]+$', description="Unique string to represent the step.")
    operation_id: Optional[str] = Field(None, alias='operationId', description="The name of a resolvable operation defined in the source description.")
    operation_path: Optional[str] = Field(None, alias='operationPath', description="A reference to an operation using a JSON Pointer.")
    workflow_id: Optional[str] = Field(None, alias='workflowId', description="The workflowId referencing another workflow within the Arazzo Description.")
    parameters: Optional[List[Union[Parameter, ReusableObject]]] = Field(None, description="A list of parameters to pass to an operation or workflow. Can include reusable references.")
    request_body: Optional[RequestBody] = Field(None, alias='requestBody', description="The request body to pass to an operation.")
    success_criteria: Optional[List[Criterion]] = Field(None, alias='successCriteria', description="A list of assertions to determine the success of the step.")
    on_success: Optional[List[Union[SuccessAction, ReusableObject]]] = Field(None, alias='onSuccess', description="An array of success action objects applicable to the step.")
    on_failure: Optional[List[Union[FailureAction, ReusableObject]]] = Field(None, alias='onFailure', description="An array of failure action objects applicable to the step.")
    outputs: Optional[OutputsType] = Field(None, description="A map between a friendly name and a dynamic output value.")


class Workflow(DSLModel):
    workflow_id: str = Field(..., alias='workflowId', pattern=r'^[A-Za-z0-9_\-]+$', description="Unique string to represent the workflow.")
    summary: Optional[str] = Field(None, description="A summary of the workflow's purpose or objective.")
    description: Optional[str] = Field(None, description="A description of the workflow. Supports CommonMark syntax.")
    inputs: Optional[Any] = Field(None, description="A JSON Schema object representing the input parameters used by this workflow.")
    depends_on: Optional[List[str]] = Field(None, alias='dependsOn', description="A list of workflowIds that must be completed before this workflow can be processed.")
    steps: List[Step] = Field(..., description="An ordered list of steps in the workflow.")
    success_actions: Optional[List[Union[SuccessAction, ReusableObject]]] = Field(None, alias='successActions', description="A list of success actions applicable to all steps in the workflow.")
    failure_actions: Optional[List[Union[FailureAction, ReusableObject]]] = Field(None, alias='failureActions', description="A list of failure actions applicable to all steps in the workflow.")
    outputs: Optional[OutputsType] = Field(None, description="A map between a friendly name and a dynamic output value produced by the workflow.")
    parameters: Optional[List[Union[Parameter, ReusableObject]]] = Field(None, description="A list of parameters applicable for all steps in the workflow. Can include reusable references.")


class Components(DSLModel):
    inputs: Optional[Dict[str, Any]] = Field(None, description="An object to hold reusable JSON Schema objects for workflow inputs.")
    parameters: Optional[Dict[str, Parameter]] = Field(None, description="An object to hold reusable Parameter objects.")
    success_actions: Optional[Dict[str, SuccessAction]] = Field(None, alias='successActions', description="An object to hold reusable Success Action objects.")
    failure_actions: Optional[Dict[str, FailureAction]] = Field(None, alias='failureActions', description="An object to hold reusable Failure Action objects.")


class ArazzoSpecification(DSLModel):
    arazzo: str = Field(..., description="The version number of the Arazzo Specification that the Arazzo Description uses.")
    info: Info = Field(..., description="Provides metadata about the workflows contained within the Arazzo Description.")
    source_descriptions: List[SourceDescription] = Field(..., alias='sourceDescriptions', description="A list of source descriptions that this Arazzo Description applies to.")
    workflows: List[Workflow] = Field(..., description="A list of workflows defined in the Arazzo Description.")
    components: Optional[Components] = Field(None, description="An element to hold various reusable schemas and components for the Arazzo Description.")


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()
    # arazzo = Path("/Users/sac/dev/arazzo-ai/examples/1.0.0/pet-coupons.arazzo.yaml").read_text()
    arazzo = Path("/Users/sac/dev/arazzo-ai/examples/1.0.0/LoginAndRetrievePets.arazzo.yaml").read_text()
    spec = ArazzoSpecification.from_yaml(arazzo)
    print(spec)

if __name__ == '__main__':
    main()
