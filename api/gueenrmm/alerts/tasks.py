from django.utils import timezone as djangotime
from gueenrmm.celery import app


@app.task
def unsnooze_alerts() -> str:
    from .models import Alert

    Alert.objects.filter(snoozed=True, snooze_until__lte=djangotime.now()).update(
        snoozed=False, snooze_until=None
    )

    return "ok"


@app.task
def cache_agents_alert_template():
    from agents.models import Agent

    for agent in Agent.objects.only("pk"):
        agent.set_alert_template()

    return "ok"


@app.task
def prune_resolved_alerts(older_than_days: int) -> str:
    from .models import Alert

    Alert.objects.filter(resolved=True).filter(
        alert_time__lt=djangotime.now() - djangotime.timedelta(days=older_than_days)
    ).delete()

    return "ok"
