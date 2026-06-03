"""Celery application configuration for BudgetBites background workers."""

from celery import Celery

from app.core.config import settings

celery_app = Celery("budgetbites")

celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Autodiscover tasks from the app.tasks package so that decorated tasks
# in sibling modules (meal_tasks.py, report_tasks.py, etc.) are registered
# automatically when the worker starts.
celery_app.autodiscover_tasks(["app.tasks"])
