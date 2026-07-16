from django.db import models
from django.utils import timezone


# Create your models here.
class Task(models.Model):
    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "低"),
        (PRIORITY_MEDIUM, "中"),
        (PRIORITY_HIGH, "高"),
    ]

    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(
        max_length=6,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt
