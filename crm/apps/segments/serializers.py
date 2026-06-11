from rest_framework import serializers
from .models import Segment


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = [
            'id', 'name', 'description', 'segment_type', 'filter_tree',
            'natural_query', 'ai_generated', 'customer_count', 'last_computed',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'customer_count', 'last_computed', 'created_at', 'updated_at']


class AIBuildSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    nl_filter = serializers.CharField()
