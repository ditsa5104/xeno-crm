from django.contrib import admin
from .models import Campaign, CampaignTemplate, CommunicationLog, CommunicationEvent


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'segment', 'channel', 'stat_total', 'stat_delivered', 'stat_clicked', 'launched_at')
    list_filter = ('status', 'channel', 'is_ab_test')
    search_fields = ('name',)


@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'campaign', 'customer', 'status', 'channel', 'queued_at', 'delivered_at')
    list_filter = ('status', 'channel')
    search_fields = ('campaign__name', 'customer__name', 'customer__email')


admin.site.register(CampaignTemplate)
admin.site.register(CommunicationEvent)
