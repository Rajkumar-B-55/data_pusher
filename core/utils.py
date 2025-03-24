from django.utils.timezone import now
from .models import Log, Account


def create_log(event_id: str, account: Account, received_data: dict, status: str = "processing"):
    return Log.objects.create(
        event_id=event_id,
        account=account,
        received_timestamp=now(),
        processed_timestamp=None,
        destination=None,
        received_data=received_data,
        status=status
    )
