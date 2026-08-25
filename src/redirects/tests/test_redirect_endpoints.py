import pytest
from django.urls import reverse

from redirects.models import RedirectRule

pytestmark = pytest.mark.django_db


def test_public_redirect_returns_302(api_client, user):
    rule = RedirectRule.objects.create(
        owner=user, redirect_url="https://example.com", is_private=False
    )

    response = api_client.get(reverse("redirect-public", args=[rule.redirect_identifier]))

    assert response.status_code == 302
    assert response.url == "https://example.com"


def test_public_redirect_unknown_identifier_returns_404(api_client):
    response = api_client.get(reverse("redirect-public", args=["doesnotexist"]))

    assert response.status_code == 404


def test_public_redirect_rejects_private_rule(api_client, user):
    rule = RedirectRule.objects.create(
        owner=user, redirect_url="https://example.com", is_private=True
    )

    response = api_client.get(reverse("redirect-public", args=[rule.redirect_identifier]))

    assert response.status_code == 404


def test_private_redirect_requires_authentication(api_client, user):
    rule = RedirectRule.objects.create(
        owner=user, redirect_url="https://example.com", is_private=True
    )

    response = api_client.get(reverse("redirect-private", args=[rule.redirect_identifier]))

    assert response.status_code == 401


def test_private_redirect_returns_302_when_authenticated(other_auth_client, user):
    rule = RedirectRule.objects.create(
        owner=user, redirect_url="https://example.com", is_private=True
    )

    response = other_auth_client.get(reverse("redirect-private", args=[rule.redirect_identifier]))

    assert response.status_code == 302
    assert response.url == "https://example.com"
