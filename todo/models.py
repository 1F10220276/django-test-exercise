from django.db import models
from django.utils import timezone


# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt

    def is_due_soon(self, dt, threshold_hours=24):
        if self.completed or self.due_at is None:
            return False
        return dt <= self.due_at <= dt + timezone.timedelta(hours=threshold_hours)
