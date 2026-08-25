import pytest
from django.urls import reverse

from redirects.models import RedirectRule

pytestmark = pytest.mark.django_db


def test_create_requires_authentication(api_client):
    response = api_client.post(
        reverse("redirect-rule-list"),
        {"redirect_url": "https://example.com", "is_private": False},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_detail_endpoint_requires_authentication(api_client, user, method):
    rule = RedirectRule.objects.create(owner=user, redirect_url="https://a.example.com")

    response = getattr(api_client, method)(
        reverse("redirect-rule-detail", args=[rule.id]),
        {"redirect_url": "https://b.example.com", "is_private": True},
        format="json",
    )

    assert response.status_code == 401


def test_create_sets_owner_and_generates_identifier(auth_client, user):
    response = auth_client.post(
        reverse("redirect-rule-list"),
        {"redirect_url": "https://example.com", "is_private": False},
        format="json",
    )

    assert response.status_code == 201
    rule = RedirectRule.objects.get(id=response.data["id"])
    assert rule.owner == user
    assert rule.redirect_identifier
    assert response.data["redirect_identifier"] == rule.redirect_identifier


def test_create_ignores_client_supplied_identifier(auth_client):
    response = auth_client.post(
        reverse("redirect-rule-list"),
        {
            "redirect_url": "https://example.com",
            "is_private": False,
            "redirect_identifier": "hacked",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["redirect_identifier"] != "hacked"


def test_create_ignores_client_supplied_owner(auth_client, user, other_user):
    response = auth_client.post(
        reverse("redirect-rule-list"),
        {
            "redirect_url": "https://example.com",
            "is_private": False,
            "owner": other_user.id,
        },
        format="json",
    )

    assert response.status_code == 201
    assert RedirectRule.objects.get(id=response.data["id"]).owner == user


def test_update_cannot_reassign_ownership(auth_client, user, other_user):
    rule = RedirectRule.objects.create(owner=user, redirect_url="https://a.example.com")

    response = auth_client.patch(
        reverse("redirect-rule-detail", args=[rule.id]),
        {"owner": other_user.id},
        format="json",
    )

    assert response.status_code == 200
    rule.refresh_from_db()
    assert rule.owner == user


def test_list_returns_only_own_rules(auth_client, other_auth_client, user, other_user):
    RedirectRule.objects.create(owner=user, redirect_url="https://a.example.com")
    RedirectRule.objects.create(owner=other_user, redirect_url="https://b.example.com")

    response = auth_client.get(reverse("redirect-rule-list"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["redirect_url"] == "https://a.example.com"


def test_owner_can_update_own_rule(auth_client, user):
    rule = RedirectRule.objects.create(owner=user, redirect_url="https://a.example.com")

    response = auth_client.patch(
        reverse("redirect-rule-detail", args=[rule.id]),
        {"is_private": True},
        format="json",
    )

    assert response.status_code == 200
    rule.refresh_from_db()
    assert rule.is_private is True


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_other_user_cannot_reach_someone_elses_rule(other_auth_client, user, method):
    rule = RedirectRule.objects.create(owner=user, redirect_url="https://a.example.com")

    response = getattr(other_auth_client, method)(
        reverse("redirect-rule-detail", args=[rule.id]),
        {"redirect_url": "https://hacked.example.com", "is_private": True},
        format="json",
    )

    assert response.status_code == 404
    rule.refresh_from_db()
    assert rule.redirect_url == "https://a.example.com"
    assert rule.is_private is False


def test_owner_can_delete_own_rule(auth_client, user):
    rule = RedirectRule.objects.create(owner=user, redirect_url="https://a.example.com")

    response = auth_client.delete(reverse("redirect-rule-detail", args=[rule.id]))

    assert response.status_code == 204
    assert not RedirectRule.objects.filter(id=rule.id).exists()
