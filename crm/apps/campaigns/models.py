import uuid
from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel
from apps.customers.models import Customer, Order, CHANNEL_CHOICES
from apps.segments.models import Segment


CAMPAIGN_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('scheduled', 'Scheduled'),
    ('running', 'Running'),
    ('paused', 'Paused'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
]

SEND_MODE_CHOICES = [
    ('immediate', 'Immediate'),
    ('scheduled', 'Scheduled'),
    ('multi_wave', 'Multi-Wave'),
]

LOG_STATUS_CHOICES = [
    ('queued', 'Queued'),
    ('sent', 'Sent'),
    ('delivered', 'Delivered'),
    ('failed', 'Failed'),
    ('opened', 'Opened'),
    ('read', 'Read'),
    ('clicked', 'Clicked'),
]

EVENT_CHOICES = [
    ('queued', 'Queued'),
    ('sent', 'Sent'),
    ('delivered', 'Delivered'),
    ('failed', 'Failed'),
    ('opened', 'Opened'),
    ('read', 'Read'),
    ('clicked', 'Clicked'),
    ('converted', 'Converted'),
]


class CampaignTemplate(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    message_template = models.TextField()
    use_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Campaign(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=CAMPAIGN_STATUS_CHOICES, default='draft', db_index=True)
    segment = models.ForeignKey(Segment, on_delete=models.PROTECT, related_name='campaigns')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    message_template = models.TextField()
    ai_generated_copy = models.BooleanField(default=False)
    send_mode = models.CharField(max_length=20, choices=SEND_MODE_CHOICES, default='immediate')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    wave_config = models.JSONField(null=True, blank=True)

    is_ab_test = models.BooleanField(default=False)
    ab_variants = models.JSONField(default=list)
    ab_winner_variant = models.CharField(max_length=50, blank=True)
    ab_decided_at = models.DateTimeField(null=True, blank=True)

    stat_total = models.IntegerField(default=0)
    stat_sent = models.IntegerField(default=0)
    stat_delivered = models.IntegerField(default=0)
    stat_failed = models.IntegerField(default=0)
    stat_opened = models.IntegerField(default=0)
    stat_read = models.IntegerField(default=0)
    stat_clicked = models.IntegerField(default=0)
    stat_converted = models.IntegerField(default=0)
    stat_revenue_attributed = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    launched_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CommunicationLog(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='logs')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='logs')
    channel = models.CharField(max_length=20)
    message_body = models.TextField()
    variant_label = models.CharField(max_length=50, blank=True)
    stub_message_id = models.CharField(max_length=255, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=LOG_STATUS_CHOICES, default='queued', db_index=True)
    failure_reason = models.CharField(max_length=100, blank=True)
    retry_count = models.IntegerField(default=0)
    converted = models.BooleanField(default=False)
    conversion_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    conversion_at = models.DateTimeField(null=True, blank=True)
    queued_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-queued_at']
        indexes = [
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['customer', '-queued_at']),
        ]


class CommunicationEvent(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    log = models.ForeignKey(CommunicationLog, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    occurred_at = models.DateTimeField()
    metadata = models.JSONField(default=dict)

    class Meta:
        unique_together = ('log', 'event_type')
        ordering = ['occurred_at']
