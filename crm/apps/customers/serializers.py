from rest_framework import serializers
from .models import Customer, Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'total_amount', 'currency', 'status',
            'channel', 'items', 'ordered_at', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class CustomerSerializer(serializers.ModelSerializer):
    recent_orders = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'external_id', 'name', 'email', 'phone',
            'channel_preference', 'city', 'gender', 'tags',
            'rfm_recency_score', 'rfm_frequency_score', 'rfm_monetary_score',
            'rfm_composite', 'rfm_tier', 'churn_risk_score',
            'predicted_send_hour', 'ltv_estimate',
            'last_order_at', 'total_orders', 'total_spend',
            'created_at', 'updated_at',
            'recent_orders',
        ]
        read_only_fields = [
            'id', 'rfm_recency_score', 'rfm_frequency_score', 'rfm_monetary_score',
            'rfm_composite', 'rfm_tier', 'churn_risk_score',
            'predicted_send_hour', 'ltv_estimate',
            'last_order_at', 'total_orders', 'total_spend',
            'created_at', 'updated_at',
        ]

    def get_recent_orders(self, obj):
        recent = obj.orders.all()[:5]
        return OrderSerializer(recent, many=True).data


class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'city', 'channel_preference',
            'rfm_tier', 'rfm_composite', 'churn_risk_score',
            'total_orders', 'total_spend', 'last_order_at',
        ]


class BulkCustomerSerializer(serializers.Serializer):
    customers = CustomerSerializer(many=True)
