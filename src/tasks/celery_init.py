from celery import Celery

from src.config import settings

# celery -A src.tasks.celery_init:celery_app worker --loglevel=INFO
# celery -A src.tasks.celery_init:celery_app flower --port=5555


celery_app = Celery(
    'tasks',
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}',
    include=['src.tasks.tasks']
)

