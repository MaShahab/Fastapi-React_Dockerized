from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/3")

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["core.celery_tasks"],  # <-- corrected path
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


celery_app.conf.update(
    timezone="UTC",
    beat_schedule={
        "print-hello-every-minute": {
            "task": "core.celery_tasks.print_hello",
            "schedule": 30.0, #every 30 secs
        }
    }
)
