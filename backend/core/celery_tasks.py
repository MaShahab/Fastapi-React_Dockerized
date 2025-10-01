from .celery_conf import celery_app
import time
import datetime

@celery_app.task(name="core.add")
def add(x, y):
    time.sleep(5)
    return x + y

@celery_app.task
def print_hello():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Hello! Current time: {now}")
