from django.core.management.base import BaseCommand

from gueenrmm.utils import reload_nats


class Command(BaseCommand):
    help = "Reload Nats"

    def handle(self, *args, **kwargs):
        reload_nats()
