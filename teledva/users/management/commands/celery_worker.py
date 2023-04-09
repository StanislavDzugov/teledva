import shlex
import subprocess

from django.core.management.base import BaseCommand
from django.utils import autoreload


def restart_celery():
    cmd = 'pkill -9 celery'

    subprocess.call(shlex.split(cmd))
    subprocess.call(shlex.split('celery -A teledva worker --loglevel=info'))


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Starting celery worker with autoreload...')
        autoreload.run_with_reloader(restart_celery)
