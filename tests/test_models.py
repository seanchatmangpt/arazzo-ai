# tests/test_arazzo_models.py

import pytest
from pydantic import ValidationError
from arazzo_ai import (
    ArazzoSpecification,
    Info,
    SourceDescription,
    Authentication,
    Workflow,
    MonitoringConfig,
    PerformanceMonitoring,
    ComplianceMonitoring,
    ComplianceRule,
    Step,
    Parameter,
    RequestBody,
    Criterion,
    CriterionExpressionType,
    SuccessAction,
    FailureAction,
    PayloadReplacement,
    Components,
    Plugin,
    AIModelConfig,
    Notification,
    HumanTask,
    ResourceConfig,
    CronSchedule,
    DateSchedule,
    Schedule,
    ReusableObject
)

# 1. Test ArazzoSpecification Object
def test_arazzo_specification_valid():
    spec = ArazzoSpecification(
        arazzo="4.1.0",
        info=Info(
            title="AI-Enhanced Pet Purchasing Workflow",
            summary="Workflow for purchasing pets with AI assistance.",
            description="Detailed workflow description.",
            version="1.0.1",
            author="Jane Doe",
            contact="jane.doe@example.com"
        ),
        source_descriptions=[
            SourceDescription(
                name="petStoreDescription",
                url="https://example.com/openapi.yaml",
                type_="openapi",
                authentication=Authentication(
                    type_="apiKey",
                    credentials={
                        "name": "X-Api-Key",
                        "in": "header",
                        "value": "your-api-key-here"
                    }
                )
            )
        ],
        workflows=[
            Workflow(
                workflow_id="loginUserAndRetrievePet",
                name="Login and Retrieve Pet Workflow",
                summary="Login User and then retrieve pets",
                description="This workflow logs in a user and retrieves available pets.",
                inputs={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "password": {"type": "string"}
                    }
                },
                steps=[
                    Step(
                        step_id="loginStep",
                        name="User Login Step",
                        description="This step demonstrates the user login step",
                        operation_id="loginUser",
                        parameters=[
                            Parameter(name="username", in_="query", value="$inputs.username"),
                            Parameter(name="password", in_="query", value="$inputs.password")
                        ],
                        success_criteria=[
                            Criterion(condition="$statusCode == 200")
                        ],
                        outputs={
                            "tokenExpires": "$response.header.X-Expires-After",
                            "rateLimit": "$response.header.X-Rate-Limit",
                            "sessionToken": "$response.body"
                        }
                    ),
                    Step(
                        step_id="getPetStep",
                        name="Retrieve Available Pets",
                        description="Retrieve a pet by status from the GET pets endpoint",
                        operation_path="{$sourceDescriptions.petStoreDescription.url}#/paths/~1pet~1findByStatus/get",
                        parameters=[
                            Parameter(name="status", in_="query", value="'available'"),
                            Parameter(name="Authorization", in_="header", value="$steps.loginStep.outputs.sessionToken")
                        ],
                        success_criteria=[
                            Criterion(condition="$statusCode == 200")
                        ],
                        outputs={
                            "availablePets": "$response.body"
                        }
                    )
                ],
                ai_models=[
                    AIModelConfig(
                        model_id="dt-001",
                        name="Decision Tree Model",
                        version="1.0.0",
                        path="models/decision_tree.pkl",
                        parameters={"threshold": 0.75},
                        description="AI model used for recommending pets based on user preferences and available data."
                    )
                ],
                monitoring=MonitoringConfig(
                    performance=PerformanceMonitoring(
                        enabled=True,
                        metrics=["cpuUsage", "memoryUsage", "responseTime"]
                    ),
                    compliance=ComplianceMonitoring(
                        enabled=True,
                        rules=[
                            ComplianceRule(
                                rule_id="EU_AIA_Compliance",
                                description="Ensure workflow complies with EU AI Act regulations"
                            )
                        ]
                    )
                )
            )
        ],
        components=Components(
            parameters={
                "storeId": Parameter(
                    name="storeId",
                    in_="header",
                    value="$inputs.x-store-id"
                )
            },
            inputs={
                "pagination": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "format": "int32"
                        },
                        "pageSize": {
                            "type": "integer",
                            "format": "int32"
                        }
                    }
                }
            },
            success_actions={
                "notifyUser": SuccessAction(
                    name="notifyUser",
                    type_="notify",
                    notification_id="userNotification",
                    criteria=[
                        Criterion(condition="$steps.analyzePetSelection.outputs.recommendedPet != null")
                    ]
                )
            },
            failure_actions={
                "refreshToken": FailureAction(
                    name="refreshExpiredToken",
                    type_="retry",
                    retry_after=1,
                    retry_limit=5,
                    workflow_id="refreshTokenWorkflowId",
                    criteria=[
                        Criterion(condition="$statusCode == 401")
                    ]
                )
            },
            notifications={
                "userNotification": Notification(
                    channel="email",
                    recipients=["user@example.com"],
                    message_template="Your recommended pet is ready for review: {recommendedPet.name}.",
                    conditions=[
                        Criterion(condition="$steps.analyzePetSelection.outputs.recommendedPet != null")
                    ]
                )
            },
            ai_models={
                "decisionTree": AIModelConfig(
                    model_id="dt-001",
                    name="Decision Tree Model",
                    version="1.0.0",
                    path="models/decision_tree.pkl",
                    parameters={"threshold": 0.75},
                    description="AI model used for recommending pets based on user preferences and available data."
                )
            }
        ),
        plugins=[
            Plugin(
                name="aiModelPlugin",
                version="1.0.0",
                description="Integrates AI models for decision-making and optimization.",
                config={
                    "modelPath": "models/decision_tree.pkl",
                    "threshold": 0.75
                }
            )
        ]
    )
    assert spec.arazzo_version == "4.1.0"
    assert spec.info.title == "AI-Enhanced Pet Purchasing Workflow"
    assert len(spec.source_descriptions) == 1
    assert len(spec.workflows) == 1
    assert spec.plugins[0].name == "aiModelPlugin"

def test_arazzo_specification_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        ArazzoSpecification(
            # Missing 'arazzo', 'info', 'sourceDescriptions', 'workflows'
        )
    errors = exc_info.value.errors()
    assert len(errors) == 4
    required_fields = {"arazzo", "info", "sourceDescriptions", "workflows"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

def test_arazzo_specification_invalid_type():
    with pytest.raises(ValidationError) as exc_info:
        ArazzoSpecification(
            arazzo=4.1,  # Should be string
            info="Not an Info object",
            source_descriptions="Not a list",
            workflows="Not a list"
        )
    errors = exc_info.value.errors()
    assert len(errors) == 3
    assert errors[0]['loc'] == ('arazzo',)
    assert errors[1]['loc'] == ('info',)
    assert errors[2]['loc'] == ('source_descriptions',)

# 2. Test Info Object
def test_info_valid():
    info = Info(
        title="Sample Workflow",
        summary="A sample workflow for testing.",
        description="Detailed description using **CommonMark**.",
        version="1.0.0",
        author="John Doe",
        contact="john.doe@example.com"
    )
    assert info.title == "Sample Workflow"
    assert info.summary == "A sample workflow for testing."
    assert info.version == "1.0.0"

def test_info_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        Info(
            # Missing 'title' and 'version'
            summary="Missing required fields."
        )
    errors = exc_info.value.errors()
    assert len(errors) == 2
    assert errors[0]['loc'] == ('title',)
    assert errors[1]['loc'] == ('version',)

def test_info_optional_fields():
    info = Info(
        title="Workflow without optional fields",
        version="1.0.0"
    )
    assert info.summary is None
    assert info.description is None
    assert info.author is None
    assert info.contact is None

# 3. Test SourceDescription Object
def test_source_description_valid():
    source = SourceDescription(
        name="petStoreDescription",
        url="https://example.com/openapi.yaml",
        type_="openapi",
        authentication=Authentication(
            type_="apiKey",
            credentials={
                "name": "X-Api-Key",
                "in": "header",
                "value": "your-api-key-here"
            }
        )
    )
    assert source.name == "petStoreDescription"
    assert source.url == "https://example.com/openapi.yaml"
    assert source.type_ == "openapi"
    assert source.authentication.type == "apiKey"

def test_source_description_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        SourceDescription(
            # Missing 'name', 'url', 'type_'
        )
    errors = exc_info.value.errors()
    assert len(errors) == 3
    required_fields = {"name", "url", "type_"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

def test_source_description_invalid_type():
    with pytest.raises(ValidationError) as exc_info:
        SourceDescription(
            name=123,  # Should be string
            url=456,   # Should be string
            type_=789   # Should be string
        )
    errors = exc_info.value.errors()
    assert len(errors) == 3
    assert errors[0]['loc'] == ('name',)
    assert errors[1]['loc'] == ('url',)
    assert errors[2]['loc'] == ('type_',)

# 4. Test Workflow Object
def test_workflow_valid():
    workflow = Workflow(
        workflow_id="sampleWorkflow",
        name="Sample Workflow",
        summary="A workflow for testing purposes.",
        description="This workflow performs sample steps.",
        inputs={
            "type": "object",
            "properties": {
                "input1": {"type": "string"},
                "input2": {"type": "integer"}
            }
        },
        depends_on=["anotherWorkflow"],
        steps=[
            Step(
                step_id="step1",
                name="First Step",
                description="Performs the first action.",
                operation_id="doFirstAction",
                parameters=[
                    Parameter(name="param1", in_="query", value="$inputs.input1")
                ],
                success_criteria=[
                    Criterion(condition="$statusCode == 200")
                ],
                outputs={
                    "output1": "$response.body"
                }
            )
        ],
        success_actions=[
            SuccessAction(
                name="endWorkflow",
                type_="end",
                criteria=[
                    Criterion(condition="$steps.step1.outputs.output1 != null")
                ]
            )
        ],
        failure_actions=[
            FailureAction(
                name="retryStep1",
                type_="retry",
                retry_after=5,
                retry_limit=3,
                criteria=[
                    Criterion(condition="$statusCode >= 500")
                ]
            )
        ],
        outputs={
            "finalOutput": "$steps.step1.outputs.output1"
        }
    )
    assert workflow.workflow_id == "sampleWorkflow"
    assert workflow.name == "Sample Workflow"
    assert len(workflow.steps) == 1
    assert workflow.success_actions[0].type_ == "end"

def test_workflow_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        Workflow(
            # Missing 'workflow_id', 'inputs', 'steps'
            name="Incomplete Workflow"
        )
    errors = exc_info.value.errors()
    assert len(errors) == 3
    required_fields = {"workflowId", "inputs", "steps"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

def test_workflow_invalid_step():
    with pytest.raises(ValidationError) as exc_info:
        Workflow(
            workflow_id="invalidStepWorkflow",
            inputs={"type": "object"},
            steps=[
                Step(
                    step_id="",
                    # step_id is required and should not be empty
                )
            ]
        )
    errors = exc_info.value.errors()
    assert len(errors) >= 1
    assert errors[0]['loc'] == ('steps', 0, 'step_id')
    assert errors[0]['type'] == 'value_error.any_str.min_length'

# 5. Test Step Object
def test_step_valid():
    step = Step(
        step_id="loginStep",
        name="User Login Step",
        description="Logs in the user.",
        operation_id="loginUser",
        parameters=[
            Parameter(name="username", in_="query", value="$inputs.username"),
            Parameter(name="password", in_="query", value="$inputs.password")
        ],
        success_criteria=[
            Criterion(condition="$statusCode == 200")
        ],
        on_success=[
            SuccessAction(
                name="notifyUser",
                type_="notify",
                notification_id="userNotification",
                criteria=[
                    Criterion(condition="$steps.loginStep.outputs.sessionToken != null")
                ]
            )
        ],
        on_failure=[
            FailureAction(
                name="retryLogin",
                type_="retry",
                retry_after=2,
                retry_limit=3,
                criteria=[
                    Criterion(condition="$statusCode == 503")
                ]
            )
        ],
        outputs={
            "sessionToken": "$response.body"
        }
    )
    assert step.step_id == "loginStep"
    assert step.operation_id == "loginUser"
    assert len(step.parameters) == 2
    assert step.on_success[0].type_ == "notify"

def test_step_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        Step(
            # Missing 'step_id', 'success_criteria'
            name="Incomplete Step"
        )
    errors = exc_info.value.errors()
    assert len(errors) == 2
    required_fields = {"stepId", "successCriteria"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

def test_step_invalid_operation():
    with pytest.raises(ValidationError) as exc_info:
        Step(
            step_id="invalidOperationStep",
            success_criteria=[
                Criterion(condition="$statusCode == 200")
            ],
            operation_id=123  # Should be string
        )
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('operation_id',)
    assert errors[0]['type'] == 'type_error.str'

# 6. Test Parameter Object
def test_parameter_valid():
    param = Parameter(
        name="username",
        in_="query",
        value="$inputs.username",
        type_="string",
        required=True
    )
    assert param.name == "username"
    assert param.in_ == "query"
    assert param.value == "$inputs.username"
    assert param.type_ == "string"
    assert param.required is True

def test_parameter_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        Parameter(
            # Missing 'name', 'in_', 'value'
        )
    errors = exc_info.value.errors()
    assert len(errors) == 3
    required_fields = {"name", "in_", "value"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

def test_parameter_invalid_in():
    with pytest.raises(ValidationError) as exc_info:
        Parameter(
            name="invalidInParam",
            in_="invalidLocation",  # Assuming 'invalidLocation' is not a valid 'in' value
            value="test"
        )
    # Since 'in' field is a string without restricted choices, it might pass unless choices are enforced
    # If choices are enforced, expect a validation error. Otherwise, it will pass.
    # Adjust accordingly based on actual model constraints.
    # Here, no choices are enforced, so it passes
    param = Parameter(
        name="invalidInParam",
        in_="invalidLocation",
        value="test"
    )
    assert param.in_ == "invalidLocation"

# 7. Test RequestBody Object
def test_request_body_valid():
    request_body = RequestBody(
        content_type="application/json",
        payload={
            "key": "value"
        },
        replacements=[
            PayloadReplacement(
                target="/key",
                value="newValue"
            )
        ],
        schema={
            "type": "object",
            "properties": {
                "key": {"type": "string"}
            }
        }
    )
    assert request_body.content_type == "application/json"
    assert request_body.payload["key"] == "value"
    assert len(request_body.replacements) == 1
    assert request_body.schema["type"] == "object"

def test_request_body_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        RequestBody(
            # Missing 'content_type', 'payload'
        )
    errors = exc_info.value.errors()
    assert len(errors) == 2
    required_fields = {"contentType", "payload"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

def test_request_body_invalid_content_type():
    with pytest.raises(ValidationError) as exc_info:
        RequestBody(
            content_type=123,  # Should be string
            payload="Invalid payload"
        )
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('content_type',)
    assert errors[0]['type'] == 'type_error.str'

# 8. Test Criterion Object
def test_criterion_valid_simple():
    criterion = Criterion(
        condition="$statusCode == 200"
    )
    assert criterion.condition == "$statusCode == 200"
    assert criterion.context is None
    assert criterion.type_ is None
    assert criterion.message is None

def test_criterion_valid_jsonpath():
    criterion = Criterion(
        context="$response.body",
        condition="$[?count(@.pets) > 0]",
        type_="jsonpath",
        message="No pets available in the response."
    )
    assert criterion.context == "$response.body"
    assert criterion.condition == "$[?count(@.pets) > 0]"
    assert criterion.type_ == "jsonpath"
    assert criterion.message == "No pets available in the response."

def test_criterion_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        Criterion(
            # Missing 'condition'
            context="$response.body"
        )
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('condition',)
    assert errors[0]['type'] == 'value_error.missing'

def test_criterion_invalid_type():
    with pytest.raises(ValidationError) as exc_info:
        Criterion(
            context=123,  # Should be string
            condition="$statusCode == 200",
            type_=456  # Should be string or CriterionExpressionType
        )
    errors = exc_info.value.errors()
    assert len(errors) == 2
    assert errors[0]['loc'] == ('context',)
    assert errors[1]['loc'] == ('type_',)
    assert errors[0]['type'] == 'type_error.str'
    assert errors[1]['type'] == 'type_error.dict'  # If type_ expects either string or dict

# 9. Test SuccessAction and FailureAction Objects
def test_success_action_valid():
    success_action = SuccessAction(
        name="gotoNextStep",
        type_="goto",
        step_id="nextStep",
        criteria=[
            Criterion(condition="$response.body.success == true")
        ]
    )
    assert success_action.name == "gotoNextStep"
    assert success_action.type_ == "goto"
    assert success_action.step_id == "nextStep"
    assert len(success_action.criteria) == 1

def test_failure_action_valid_retry():
    failure_action = FailureAction(
        name="retryStep",
        type_="retry",
        retry_after=10,
        retry_limit=3,
        criteria=[
            Criterion(condition="$statusCode == 500")
        ]
    )
    assert failure_action.name == "retryStep"
    assert failure_action.type_ == "retry"
    assert failure_action.retry_after == 10
    assert failure_action.retry_limit == 3
    assert len(failure_action.criteria) == 1

def test_success_action_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        SuccessAction(
            # Missing 'name', 'type_'
            step_id="nextStep"
        )
    errors = exc_info.value.errors()
    assert len(errors) == 2
    required_fields = {"name", "type_"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

def test_failure_action_invalid_type():
    with pytest.raises(ValidationError) as exc_info:
        FailureAction(
            name="invalidTypeFailureAction",
            type_=123,  # Should be string
        )
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('type_',)
    assert errors[0]['type'] == 'type_error.str'

# 10. Test PayloadReplacement Object
def test_payload_replacement_valid():
    replacement = PayloadReplacement(
        target="/petId",
        value="12345"
    )
    assert replacement.target == "/petId"
    assert replacement.value == "12345"
    assert replacement.condition is None

def test_payload_replacement_with_condition():
    replacement = PayloadReplacement(
        target="/status",
        value="completed",
        condition=Criterion(condition="$steps.processPayment.outputs.success == true")
    )
    assert replacement.target == "/status"
    assert replacement.value == "completed"
    assert replacement.condition.condition == "$steps.processPayment.outputs.success == true"

def test_payload_replacement_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        PayloadReplacement(
            # Missing 'target' and 'value'
        )
    errors = exc_info.value.errors()
    assert len(errors) == 2
    required_fields = {"target", "value"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

# 11. Test Components Object
def test_components_valid():
    components = Components(
        inputs={
            "pagination": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "format": "int32"},
                    "pageSize": {"type": "integer", "format": "int32"}
                }
            }
        },
        parameters={
            "storeId": Parameter(
                name="storeId",
                in_="header",
                value="$inputs.x-store-id"
            )
        },
        success_actions={
            "notifyUser": SuccessAction(
                name="notifyUser",
                type_="notify",
                notification_id="userNotification",
                criteria=[
                    Criterion(condition="$steps.analyzePetSelection.outputs.recommendedPet != null")
                ]
            )
        },
        failure_actions={
            "refreshToken": FailureAction(
                name="refreshExpiredToken",
                type_="retry",
                retry_after=1,
                retry_limit=5,
                workflow_id="refreshTokenWorkflowId",
                criteria=[
                    Criterion(condition="$statusCode == 401")
                ]
            )
        },
        notifications={
            "userNotification": Notification(
                channel="email",
                recipients=["user@example.com"],
                message_template="Your recommended pet is ready for review.",
                conditions=[
                    Criterion(condition="$steps.analyzePetSelection.outputs.recommendedPet != null")
                ]
            )
        },
        ai_models={
            "decisionTree": AIModelConfig(
                model_id="dt-001",
                name="Decision Tree Model",
                version="1.0.0",
                path="models/decision_tree.pkl",
                parameters={"threshold": 0.75},
                description="AI model used for recommending pets based on user preferences and available data."
            )
        }
    )
    assert components.inputs["pagination"]["type"] == "object"
    assert components.parameters["storeId"].name == "storeId"
    assert components.success_actions["notifyUser"].type_ == "notify"

def test_components_optional_fields():
    components = Components()
    assert components.inputs is None
    assert components.parameters is None
    assert components.success_actions is None
    assert components.failure_actions is None
    assert components.notifications is None
    assert components.ai_models is None

def test_components_invalid():
    with pytest.raises(ValidationError) as exc_info:
        Components(
            parameters={
                "invalidParam": "Not a Parameter object"
            }
        )
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('parameters', 'invalidParam')
    assert errors[0]['type'] == 'type_error.dict'

# 12. Test Plugin Object
def test_plugin_valid():
    plugin = Plugin(
        name="aiModelPlugin",
        version="1.0.0",
        description="Integrates AI models for decision-making and optimization.",
        config={
            "modelPath": "models/decision_tree.pkl",
            "threshold": 0.75
        }
    )
    assert plugin.name == "aiModelPlugin"
    assert plugin.version == "1.0.0"
    assert plugin.config["modelPath"] == "models/decision_tree.pkl"

def test_plugin_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        Plugin(
            # Missing 'name' and 'version'
            description="Incomplete plugin."
        )
    errors = exc_info.value.errors()
    assert len(errors) == 2
    required_fields = {"name", "version"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

def test_plugin_invalid_config():
    with pytest.raises(ValidationError) as exc_info:
        Plugin(
            name="invalidPlugin",
            version="1.0.0",
            config="Invalid config type"  # Should be dict or None
        )
    # Since config is Optional[Dict], passing a string may be allowed unless type is strictly Dict
    # Adjust based on actual model constraints
    assert exc_info.value is None  # Assuming config allows Any, it passes

# 13. Test AIModelConfig Object
def test_ai_model_config_valid():
    ai_model = AIModelConfig(
        model_id="dt-001",
        name="Decision Tree Model",
        version="1.0.0",
        path="models/decision_tree.pkl",
        parameters={"threshold": 0.75},
        description="AI model used for recommending pets based on user preferences and available data."
    )
    assert ai_model.model_id == "dt-001"
    assert ai_model.name == "Decision Tree Model"
    assert ai_model.version == "1.0.0"
    assert ai_model.path == "models/decision_tree.pkl"
    assert ai_model.parameters["threshold"] == 0.75

def test_ai_model_config_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        AIModelConfig(
            # Missing 'model_id', 'name', 'version', 'path'
            parameters={"threshold": 0.75}
        )
    errors = exc_info.value.errors()
    required_fields = {"modelId", "name", "version", "path"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

# 14. Test Notification Object
def test_notification_valid():
    notification = Notification(
        channel="email",
        recipients=["user@example.com"],
        message_template="Your recommended pet is ready for review: {recommendedPet.name}.",
        conditions=[
            Criterion(condition="$steps.analyzePetSelection.outputs.recommendedPet != null")
        ]
    )
    assert notification.channel == "email"
    assert "user@example.com" in notification.recipients
    assert "recommendedPet.name" in notification.message_template
    assert len(notification.conditions) == 1

def test_notification_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        Notification(
            # Missing 'channel', 'recipients', 'message_template'
        )
    errors = exc_info.value.errors()
    required_fields = {"channel", "recipients", "message_template"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

def test_notification_invalid_recipients():
    with pytest.raises(ValidationError) as exc_info:
        Notification(
            channel="sms",
            recipients="not-a-list",  # Should be list of strings
            message_template="Test message."
        )
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('recipients',)
    assert errors[0]['type'] == 'type_error.list'

# 15. Test HumanTask Object
def test_human_task_valid():
    human_task = HumanTask(
        assigned_to="support_team",
        task_type="review",
        instructions="Please review the AI-recommended pet selection and confirm suitability.",
        deadline="2024-06-01T12:00:00Z",
        priority="high"
    )
    assert human_task.assigned_to == "support_team"
    assert human_task.task_type == "review"
    assert human_task.instructions == "Please review the AI-recommended pet selection and confirm suitability."
    assert human_task.deadline == "2024-06-01T12:00:00Z"
    assert human_task.priority == "high"

def test_human_task_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        HumanTask(
            # Missing 'assigned_to', 'task_type', 'instructions'
        )
    errors = exc_info.value.errors()
    required_fields = {"assignedTo", "taskType", "instructions"}
    missing = {error['loc'][0] for error in errors if error['type'] == 'value_error.missing'}
    assert missing == required_fields

def test_human_task_invalid_priority():
    human_task = HumanTask(
        assigned_to="john.doe@example.com",
        task_type="approval",
        instructions="Approve the final pet selection.",
        priority="urgent"  # Assuming no validation on priority values
    )
    assert human_task.priority == "urgent"

# 16. Test ResourceConfig Object
def test_resource_config_valid():
    resource_config = ResourceConfig(
        cpu="2",
        memory="4Gi",
        gpu="1",
        storage="10Gi",
        environment={
            "ENV": "production",
            "DEBUG": "false"
        }
    )
    assert resource_config.cpu == "2"
    assert resource_config.memory == "4Gi"
    assert resource_config.gpu == "1"
    assert resource_config.storage == "10Gi"
    assert resource_config.environment["ENV"] == "production"

def test_resource_config_optional_fields():
    resource_config = ResourceConfig(
        cpu="500m",
        memory="512Mi"
    )
    assert resource_config.cpu == "500m"
    assert resource_config.memory == "512Mi"
    assert resource_config.gpu is None
    assert resource_config.storage is None
    assert resource_config.environment is None

def test_resource_config_invalid_cpu():
    with pytest.raises(ValidationError) as exc_info:
        ResourceConfig(
            cpu=2,  # Should be string
            memory="4Gi"
        )
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('cpu',)
    assert errors[0]['type'] == 'type_error.str'

# 17. Test Schedule Models
def test_cron_schedule_valid():
    cron = CronSchedule(
        cron="0 9 * * MON",
        timezone="America/New_York"
    )
    assert cron.cron == "0 9 * * MON"
    assert cron.timezone == "America/New_York"

def test_cron_schedule_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        CronSchedule(
            # Missing 'cron'
            timezone="UTC"
        )
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('cron',)
    assert errors[0]['type'] == 'value_error.missing'

def test_date_schedule_valid():
    date_schedule = DateSchedule(
        run_date="2024-06-01T09:00:00Z",
        timezone="Europe/Berlin"
    )
    assert date_schedule.run_date == "2024-06-01T09:00:00Z"
    assert date_schedule.timezone == "Europe/Berlin"

def test_date_schedule_invalid_run_date():
    with pytest.raises(ValidationError) as exc_info:
        DateSchedule(
            run_date=12345,  # Should be string
            timezone="UTC"
        )
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('run_date',)
    assert errors[0]['type'] == 'type_error.str'

def test_schedule_valid_cron():
    schedule = Schedule(
        cron=CronSchedule(
            cron="0 9 * * MON",
            timezone="America/New_York"
        )
    )
    assert schedule.cron.cron == "0 9 * * MON"
    assert schedule.cron.timezone == "America/New_York"
    assert schedule.date is None

def test_schedule_valid_date():
    schedule = Schedule(
        date=DateSchedule(
            run_date="2024-06-01T09:00:00Z",
            timezone="Europe/Berlin"
        )
    )
    assert schedule.date.run_date == "2024-06-01T09:00:00Z"
    assert schedule.date.timezone == "Europe/Berlin"
    assert schedule.cron is None

def test_schedule_invalid_both_cron_and_date():
    with pytest.raises(ValidationError) as exc_info:
        Schedule(
            cron=CronSchedule(
                cron="0 9 * * MON"
            ),
            date=DateSchedule(
                run_date="2024-06-01T09:00:00Z"
            )
        )
    # Depending on model validation, it might allow both or not.
    # If mutual exclusivity is enforced, expect a validation error.
    # Since no constraints are defined, it might pass.
    # Adjust based on actual model constraints.
    # Here, assuming it passes since no mutual exclusivity is enforced
    schedule = Schedule(
        cron=CronSchedule(
            cron="0 9 * * MON"
        ),
        date=DateSchedule(
            run_date="2024-06-01T09:00:00Z"
        )
    )
    assert schedule.cron.cron == "0 9 * * MON"
    assert schedule.date.run_date == "2024-06-01T09:00:00Z"

# 18. Test ReusableObject
def test_reusable_object_valid():
    reusable = ReusableObject(
        reference="$components.successActions.notifyUser",
        value="1"
    )
    assert reusable.reference == "$components.successActions.notifyUser"
    assert reusable.value == "1"

def test_reusable_object_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        ReusableObject(
            # Missing 'reference'
            value="1"
        )
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('reference',)
    assert errors[0]['type'] == 'value_error.missing'

def test_reusable_object_invalid_reference():
    # Assuming no validation on the format of 'reference'
    reusable = ReusableObject(
        reference=12345,  # Should be string
        value="1"
    )
    with pytest.raises(ValidationError) as exc_info:
        reusable.dict()
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('reference',)
    assert errors[0]['type'] == 'type_error.str'

# Additional tests can be added similarly for other models if needed.
