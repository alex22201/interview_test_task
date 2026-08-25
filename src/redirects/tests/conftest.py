import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="s3cret-pass")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="bob", password="s3cret-pass")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def other_auth_client(other_user):
    client = APIClient()
    client.force_authenticate(user=other_user)
    return client
