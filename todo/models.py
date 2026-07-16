from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


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
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
    )
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

    def is_due_soon(self, dt, threshold_hours=24):
        if self.completed or self.due_at is None:
            return False
        return dt <= self.due_at <= dt + timezone.timedelta(hours=threshold_hours)
