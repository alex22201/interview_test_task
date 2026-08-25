import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_schema_is_available_without_authentication(api_client):
    response = api_client.get(reverse("schema"))

    assert response.status_code == 200


def test_swagger_ui_is_available_without_authentication(api_client):
    response = api_client.get(reverse("swagger-ui"))

    assert response.status_code == 200


def test_schema_documents_all_endpoints(api_client):
    response = api_client.get(reverse("schema"), {"format": "json"})

    paths = response.data["paths"]
    assert "/retrieve-token/" in paths
    assert "/url/" in paths
    assert "/url/{id}/" in paths
    assert "/redirect/public/{redirect_identifier}" in paths
    assert "/redirect/private/{redirect_identifier}" in paths


def test_schema_marks_public_redirect_as_not_requiring_auth(api_client):
    response = api_client.get(reverse("schema"), {"format": "json"})

    operation = response.data["paths"]["/redirect/public/{redirect_identifier}"]["get"]
    assert {} in operation["security"]
