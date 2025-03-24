import json
import uuid
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from unittest.mock import patch
from core.models import Account, Destination, Log
from core.tasks import send_data_to_destination


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="testuser", password="test123")


@pytest.fixture
def test_account(db, test_user):
    return Account.objects.create(
        name="Test Account",
        app_secret_token=str(uuid.uuid4()),
        created_by=test_user,
        updated_by=test_user,
    )


@pytest.fixture
def test_destination(db, test_account, test_user):
    return Destination.objects.create(
        account=test_account,
        url="https://bb6f-103-226-186-140.ngrok-free.app/api/webhook-test/",
        http_method="POST",
        headers={"Content-Type": "application/json"},
        created_by=test_user,
        updated_by=test_user,
    )


@pytest.mark.django_db
def test_incoming_data_api(api_client, test_account, test_destination):
    url = "/api/server/incoming_data/"
    headers = {
        "CL-X-TOKEN": test_account.app_secret_token,
        "Content-Type": "application/json",
    }
    payload = {"user_id": 123, "action": "update"}

    response = api_client.post(url, data=json.dumps(payload), headers=headers, content_type="application/json")

    assert response.status_code == 202
    assert response.json()["message"] == "Data Received"


@pytest.mark.django_db
@patch("requests.request")
def test_send_data_to_destination(mock_request, test_destination):
    event_id = "test-event-123"
    data = json.dumps({"user_id": 123, "action": "update"})

    mock_request.return_value.status_code = 200

    send_data_to_destination(test_destination.id, event_id, data)

    log = Log.objects.filter(event_id=event_id, destination=test_destination).first()
    assert log is not None
    assert log.status == "success"
