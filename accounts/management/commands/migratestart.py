# * python manage.py migratestart
from django.core.management.base import BaseCommand
from django.core.management import call_command



class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('makemigrations')
        call_command('migrate')
        call_command('runserver')
        return super().handle(*args, **options)