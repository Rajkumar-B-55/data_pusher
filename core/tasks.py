import json
import logging

from celery import shared_task
import requests
from django.utils.timezone import now
from .models import Destination, Log

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def send_data_to_destination(self, destination_id, event_id, data):
    try:

        logger.info(f"Starting task for destination {destination_id}, event {event_id}")

        with open("celery_debug.log", "a") as f:
            f.write(f"Received Task: destination_id={destination_id}, event_id={event_id}, data={data}\n")

        try:
            destination = Destination.objects.get(id=destination_id)
        except Destination.DoesNotExist:
            print(f"Destination with ID {destination_id} not found.")
            return

        try:
            data = json.loads(data)

            headers = destination.headers
            if destination.http_method == "GET":
                response = requests.get(destination.url, headers=headers, params=data)
            else:
                response = requests.request(destination.http_method, destination.url, headers=headers, json=data)

            log, created = Log.objects.get_or_create(event_id=event_id, account=destination.account, defaults={
                "received_timestamp": now(),
                "processed_timestamp": now(),
                "destination": destination,
                "received_data": data,
                "status": "success" if response.status_code == 200 else "failed",
            })

            if not created:
                log.processed_timestamp = now()
                log.destination = destination
                log.status = "success" if response.status_code == 200 else "failed"
                log.save()

        except Exception as e:

            Log.objects.create(
                event_id=event_id,
                account=destination.account,
                received_timestamp=now(),
                processed_timestamp=now(),
                destination=destination,
                received_data=data,
                status="failed"
            )
            logger.error(f"Error sending data to {destination.url}: {e}")
    except Exception as e:
        logger.error(f"Task failed completely: {str(e)}", exc_info=True)
        raise
