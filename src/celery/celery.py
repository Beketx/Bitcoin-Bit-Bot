from __future__ import absolute_import

from celery import Celery

app = Celery('src.celery',
             broker='redis://localhost:6379/0',
             include=['src.recycler'])

app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Executes every Monday morning at 7:30 a.m.
    # 'add-every-monday-morning': {
        # 'task': 'core.ex_views.view_bp12.autostart',
    #     'task': 'smart_remont.tasks.startbp12',
    #     'schedule': crontab(hour=15, minute=50, day_of_week=5)
    # },
    "run-me-every-ten-seconds": {
        "task": "src.recycler.periodic",
        "schedule": 10.0
    }
}

if __name__ == '__main__':
    app.start()