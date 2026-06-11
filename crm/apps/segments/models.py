import uuid
from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel
from apps.customers.models import Customer


SEGMENT_TYPE_CHOICES = [('dynamic', 'Dynamic'), ('static', 'Static')]


class Segment(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    segment_type = models.CharField(max_length=10, choices=SEGMENT_TYPE_CHOICES, default='dynamic')
    filter_tree = models.JSONField(default=dict)
    natural_query = models.TextField(blank=True)
    ai_generated = models.BooleanField(default=False)
    customer_count = models.IntegerField(default=0)
    last_computed = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    customers = models.ManyToManyField(Customer, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class SegmentMembership(TimestampedModel):
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, related_name='memberships')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='segment_memberships')
    entered_at = models.DateTimeField(auto_now_add=True)
    exited_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('segment', 'customer')


class SegmentSnapshot(TimestampedModel):
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, related_name='snapshots')
    customer_count = models.IntegerField(default=0)
    taken_at = models.DateTimeField(auto_now_add=True)
