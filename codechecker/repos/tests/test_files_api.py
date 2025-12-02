import io
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from repos.models import SourceFile


@pytest.mark.django_db
def authenticated_client(email: str = "some@email.com", password: str = "dsfsf1234"):
    """Вспомогательная функция для создания залогиненного клиента"""
    client = APIClient()

    client.post(reverse("register"), {
        "email": email,
        "password": password,
        "password2": password
    })

    login = client.post(reverse("user-login"), {
        "email": email,
        "password": password
    })

    token = login.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    return client


@pytest.mark.django_db
def test_upload_python_file():
    client = authenticated_client()

    file_content = io.BytesIO(b"print('hello')")
    file_content.name = "test.py"

    response = client.post(
        reverse("files-list"),
        {"file": file_content},
        format="multipart"
    )

    assert response.status_code == 201
    assert SourceFile.objects.count() == 1


@pytest.mark.django_db
def test_cannot_upload_non_python_file():
    client = authenticated_client()

    file_content = io.BytesIO(b"not python")
    file_content.name = "bad.txt"

    response = client.post(
        reverse("files-list"),
        {"file": file_content},
        format="multipart"
    )

    assert response.status_code == 400
    assert "Only .py files are allowed" in str(response.data)


@pytest.mark.django_db
def test_user_sees_only_his_files():
    client1 = authenticated_client()

    # загрузим файл пользователю 1
    file_content = io.BytesIO(b"print('hi')")
    file_content.name = "a.py"

    client1.post(reverse("files-list"), {"file": file_content}, format="multipart")

    # создаём второго пользователя
    client2 = authenticated_client(email="other@email.com", password="dsffdsff12444")

    # пользователь 2 не должен видеть файл пользователя 1
    list_response = client2.get(reverse("files-list"))
    assert list_response.status_code == 200
    assert list_response.data == []


@pytest.mark.django_db
def test_rerun_check():
    client = authenticated_client()

    file_content = io.BytesIO(b"print('hi')")
    file_content.name = "a.py"

    upload = client.post(
        reverse("files-list"),
        {"file": file_content},
        format="multipart"
    )

    file_id = upload.data["id"]

    response = client.post(reverse("files-rerun", kwargs={"pk": file_id}))

    assert response.status_code == 200
    assert response.data["result"] == "ok"
    assert response.data["message"] == "file under testing"
