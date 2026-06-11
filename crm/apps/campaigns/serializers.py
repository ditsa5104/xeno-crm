from rest_framework import serializers
from .models import Campaign, CampaignTemplate, CommunicationLog


class CampaignTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignTemplate
        fields = ['id', 'name', 'description', 'channel', 'message_template', 'use_count', 'created_at']
        read_only_fields = ['id', 'use_count', 'created_at']


class CampaignSerializer(serializers.ModelSerializer):
    segment_name = serializers.CharField(source='segment.name', read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'description', 'status', 'segment', 'segment_name',
            'channel', 'message_template', 'ai_generated_copy',
            'send_mode', 'scheduled_at', 'wave_config',
            'is_ab_test', 'ab_variants', 'ab_winner_variant', 'ab_decided_at',
            'stat_total', 'stat_sent', 'stat_delivered', 'stat_failed',
            'stat_opened', 'stat_read', 'stat_clicked', 'stat_converted',
            'stat_revenue_attributed',
            'launched_at', 'completed_at', 'created_at',
        ]
        read_only_fields = [
            'id', 'status', 'segment_name', 'ab_winner_variant', 'ab_decided_at',
            'stat_total', 'stat_sent', 'stat_delivered', 'stat_failed',
            'stat_opened', 'stat_read', 'stat_clicked', 'stat_converted',
            'stat_revenue_attributed',
            'launched_at', 'completed_at', 'created_at',
        ]


class CommunicationLogSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = CommunicationLog
        fields = [
            'id', 'campaign', 'customer', 'customer_name', 'channel',
            'message_body', 'variant_label', 'status', 'failure_reason',
            'retry_count', 'converted', 'conversion_at',
            'queued_at', 'sent_at', 'delivered_at', 'opened_at', 'read_at', 'clicked_at',
        ]
