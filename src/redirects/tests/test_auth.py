import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_retrieve_token_with_valid_credentials(api_client, user):
    url = reverse("retrieve-token")
    response = api_client.post(
        url, {"username": "alice", "password": "s3cret-pass"}, format="json"
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


def test_retrieve_token_with_invalid_credentials(api_client, user):
    url = reverse("retrieve-token")
    response = api_client.post(
        url, {"username": "alice", "password": "wrong-password"}, format="json"
    )

    assert response.status_code == 401


def test_refresh_token_returns_a_new_access_token(api_client, user):
    tokens = api_client.post(
        reverse("retrieve-token"),
        {"username": "alice", "password": "s3cret-pass"},
        format="json",
    ).data

    response = api_client.post(
        reverse("refresh-token"), {"refresh": tokens["refresh"]}, format="json"
    )

    assert response.status_code == 200
    assert "access" in response.data


def test_bearer_token_is_accepted_in_the_authorization_header(api_client, user):
    """Covers the real header path, which the force_authenticate fixtures bypass."""
    access = api_client.post(
        reverse("retrieve-token"),
        {"username": "alice", "password": "s3cret-pass"},
        format="json",
    ).data["access"]

    response = api_client.get(reverse("redirect-rule-list"), HTTP_AUTHORIZATION=f"Bearer {access}")

    assert response.status_code == 200
