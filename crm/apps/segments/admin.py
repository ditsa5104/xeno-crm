from django.contrib import admin
from .models import Segment, SegmentMembership, SegmentSnapshot


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'segment_type', 'customer_count', 'ai_generated', 'last_computed')
    list_filter = ('segment_type', 'ai_generated')
    search_fields = ('name', 'description', 'natural_query')


admin.site.register(SegmentMembership)
admin.site.register(SegmentSnapshot)
