import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.core.models import TimestampedModel


CHANNEL_CHOICES = [
    ('whatsapp', 'WhatsApp'),
    ('sms', 'SMS'),
    ('email', 'Email'),
    ('rcs', 'RCS'),
    ('auto', 'Auto'),
]

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
    ('unknown', 'Unknown'),
]


class Customer(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(max_length=255, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True, unique=True)
    channel_preference = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='auto')
    city = models.CharField(max_length=100, blank=True, db_index=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='unknown')
    date_of_birth = models.DateField(null=True, blank=True, db_index=True)
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)

    rfm_recency_score = models.IntegerField(default=0)
    rfm_frequency_score = models.IntegerField(default=0)
    rfm_monetary_score = models.IntegerField(default=0)
    rfm_composite = models.FloatField(default=0.0)
    rfm_tier = models.CharField(max_length=30, default='Unscored', db_index=True)
    churn_risk_score = models.FloatField(default=0.0)
    predicted_send_hour = models.IntegerField(default=10)
    ltv_estimate = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    last_order_at = models.DateTimeField(null=True, blank=True, db_index=True)
    total_orders = models.IntegerField(default=0)
    total_spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rfm_tier', '-total_spend']),
            models.Index(fields=['-last_order_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.email or self.phone or self.id})"


ORDER_STATUS_CHOICES = [
    ('placed', 'Placed'),
    ('fulfilled', 'Fulfilled'),
    ('returned', 'Returned'),
    ('cancelled', 'Cancelled'),
]

ORDER_CHANNEL_CHOICES = [
    ('online', 'Online'),
    ('in_store', 'In Store'),
    ('app', 'App'),
]


class Order(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=100, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='placed')
    channel = models.CharField(max_length=20, choices=ORDER_CHANNEL_CHOICES, default='online')
    product_category = models.CharField(max_length=100, blank=True, db_index=True)
    items = models.JSONField(default=list)
    ordered_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ['-ordered_at']
        indexes = [
            models.Index(fields=['customer', '-ordered_at']),
        ]

    def __str__(self):
        return f"Order {self.order_number} ({self.customer_id})"
