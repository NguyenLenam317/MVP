from celery import Celery
from ..core.config import settings

app = Celery(
    'tasks',
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}',
    backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}'
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks
    beat_schedule={
        'daily_aggregations': {
            'task': 'app.tasks.aggregation.daily_aggregations',
            'schedule': 3600.0  # Every hour
        },
        'weekly_aggregations': {
            'task': 'app.tasks.aggregation.weekly_aggregations',
            'schedule': 86400.0  # Every day
        },
        'monthly_aggregations': {
            'task': 'app.tasks.aggregation.monthly_aggregations',
            'schedule': 604800.0  # Every week
        },
        'data_cleanup': {
            'task': 'app.tasks.cleanup.data_cleanup',
            'schedule': 86400.0  # Every day
        }
    }
)
