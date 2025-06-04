# monitoring_app/management/commands/init_machines.py
from django.core.management.base import BaseCommand
from monitoring_app.models import Machine

class Command(BaseCommand):
    help = 'Initialize machine records for flow meters'

    def handle(self, *args, **kwargs):
        machines = [
            'machine_flow_1',
            'machine_flow_2',
            'machine_flow_3',
        ]
        for name in machines:
            Machine.objects.get_or_create(name=name)
            self.stdout.write(self.style.SUCCESS(f'Machine {name} created or already exists'))