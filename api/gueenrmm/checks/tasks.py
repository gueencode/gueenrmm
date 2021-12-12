import datetime as dt
import random
from time import sleep
from typing import Union

from django.utils import timezone as djangotime

from gueenrmm.celery import app


@app.task
def handle_check_email_alert_task(pk, alert_interval: Union[float, None] = None) -> str:
    from alerts.models import Alert

    alert = Alert.objects.get(pk=pk)

    # first time sending email
    if not alert.email_sent:
        sleep(random.randint(1, 10))
        alert.assigned_check.send_email()
        alert.email_sent = djangotime.now()
        alert.save(update_fields=["email_sent"])
    else:
        if alert_interval:
            # send an email only if the last email sent is older than alert interval
            delta = djangotime.now() - dt.timedelta(days=alert_interval)
            if alert.email_sent < delta:
                sleep(random.randint(1, 10))
                alert.assigned_check.send_email()
                alert.email_sent = djangotime.now()
                alert.save(update_fields=["email_sent"])

    return "ok"


@app.task
def handle_check_sms_alert_task(pk, alert_interval: Union[float, None] = None) -> str:
    from alerts.models import Alert

    alert = Alert.objects.get(pk=pk)

    # first time sending text
    if not alert.sms_sent:
        sleep(random.randint(1, 3))
        alert.assigned_check.send_sms()
        alert.sms_sent = djangotime.now()
        alert.save(update_fields=["sms_sent"])
    else:
        if alert_interval:
            # send a text only if the last text sent is older than 24 hours
            delta = djangotime.now() - dt.timedelta(days=alert_interval)
            if alert.sms_sent < delta:
                sleep(random.randint(1, 3))
                alert.assigned_check.send_sms()
                alert.sms_sent = djangotime.now()
                alert.save(update_fields=["sms_sent"])

    return "ok"


@app.task
def handle_resolved_check_sms_alert_task(pk: int) -> str:
    from alerts.models import Alert

    alert = Alert.objects.get(pk=pk)

    # first time sending text
    if not alert.resolved_sms_sent:
        sleep(random.randint(1, 3))
        alert.assigned_check.send_resolved_sms()
        alert.resolved_sms_sent = djangotime.now()
        alert.save(update_fields=["resolved_sms_sent"])

    return "ok"


@app.task
def handle_resolved_check_email_alert_task(pk: int) -> str:
    from alerts.models import Alert

    alert = Alert.objects.get(pk=pk)

    # first time sending email
    if not alert.resolved_email_sent:
        sleep(random.randint(1, 10))
        alert.assigned_check.send_resolved_email()
        alert.resolved_email_sent = djangotime.now()
        alert.save(update_fields=["resolved_email_sent"])

    return "ok"


@app.task
def prune_check_history(older_than_days: int) -> str:
    from .models import CheckHistory

    CheckHistory.objects.filter(
        x__lt=djangotime.make_aware(dt.datetime.today())
        - djangotime.timedelta(days=older_than_days)
    ).delete()

    return "ok"
