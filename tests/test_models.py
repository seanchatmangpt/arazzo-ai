from pathlib import Path
from arazzo_ai.models import ArazzoSpecification


def test_bnpl():
    yaml = Path("bnpl-arazzo.yaml").read_text()
    spec = ArazzoSpecification.from_yaml(yaml)
    assert spec.workflows[0].workflow_id == "ApplyForLoanAtCheckout"


def test_extended():
    yaml = Path("ExtendedParametersExample.arazzo.yaml").read_text()
    spec = ArazzoSpecification.from_yaml(yaml)
    assert spec.workflows[0].workflow_id == "animal-workflow"

def test_fapi():
    yaml = Path("FAPI-PAR.arazzo.yaml").read_text()
    spec = ArazzoSpecification.from_yaml(yaml)
    assert spec.workflows[0].workflow_id == "OIDC-PAR-AuthzCode"

def test_login():
    yaml = Path("LoginAndRetrievePets.arazzo.yaml").read_text()
    spec = ArazzoSpecification.from_yaml(yaml)
    assert spec.workflows[0].workflow_id == "loginUserRetrievePet"

def test_oauth():
    yaml = Path("oath.arazzo.yaml").read_text()
    spec = ArazzoSpecification.from_yaml(yaml)
    assert spec.workflows[0].workflow_id == "refresh-token-flow"
