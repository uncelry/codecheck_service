import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_user():
    client = APIClient()

    response = client.post(reverse("register"), {
        "email": "test@example.com",
        "password": "sgfdgdfg1234",
        "password2": "sgfdgdfg1234",
    })

    assert response.status_code == 201
    assert response.data["email"] == "test@example.com"


@pytest.mark.django_db
def test_login_user():
    client = APIClient()

    client.post(reverse("register"), {
        "email": "test@example.com",
        "password": "sgfdgdfg1234",
        "password2": "sgfdgdfg1234",
    })

    # теперь логинимся
    response = client.post(reverse("user-login"), {
        "email": "test@example.com",
        "password": "sgfdgdfg1234"
    })

    assert response.status_code == 200
    assert "access" in response.data
