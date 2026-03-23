from celery import shared_task
from django.core.management import call_command

@shared_task
def sync_user_search_task():
    call_command('sync_user_search')