from celery import Celery

from app.core.config import settings

celery_app = Celery("ghostwriter", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    imports=("app.services.tasks",),
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_queue="ghostwriter",
    task_default_exchange="ghostwriter",
    task_default_routing_key="ghostwriter.default",
)
