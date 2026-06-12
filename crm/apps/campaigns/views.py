import csv
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Campaign, CampaignTemplate, CommunicationLog
from .serializers import CampaignSerializer, CampaignTemplateSerializer, CommunicationLogSerializer
from .tasks import launch_campaign
from .personaliser import render
from apps.segments.evaluator import SegmentEvaluator


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)

    @action(detail=True, methods=['post'])
    def launch(self, request, pk=None):
        c = self.get_object()
        if c.status not in ('draft', 'scheduled', 'paused'):
            return Response({'error': f'Cannot launch from {c.status}'}, status=400)
        launch_campaign.delay(str(c.id))
        c.status = 'scheduled'
        c.save(update_fields=['status'])
        return Response({'status': 'queued'})

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        c = self.get_object()
        c.status = 'paused'
        c.save(update_fields=['status'])
        return Response({'status': 'paused'})

    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        c = self.get_object()
        if c.status != 'paused':
            return Response({'error': 'Not paused'}, status=400)
        launch_campaign.delay(str(c.id))
        c.status = 'scheduled'
        c.save(update_fields=['status'])
        return Response({'status': 'queued'})

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        c = self.get_object()
        return Response({
            'total': c.stat_total,
            'sent': c.stat_sent,
            'delivered': c.stat_delivered,
            'failed': c.stat_failed,
            'opened': c.stat_opened,
            'read': c.stat_read,
            'clicked': c.stat_clicked,
            'converted': c.stat_converted,
            'revenue_attributed': str(c.stat_revenue_attributed),
            'delivery_rate': c.stat_delivered / c.stat_total if c.stat_total else 0,
            'open_rate': c.stat_opened / c.stat_delivered if c.stat_delivered else 0,
            'click_rate': c.stat_clicked / c.stat_delivered if c.stat_delivered else 0,
            'conversion_rate': c.stat_converted / c.stat_delivered if c.stat_delivered else 0,
        })

    @action(detail=True, methods=['get'], url_path='export-csv')
    def export_csv(self, request, pk=None):
        c = self.get_object()
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="campaign-{c.id}.csv"'
        w = csv.writer(resp)
        w.writerow(['log_id', 'customer', 'channel', 'status', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at', 'converted'])
        for l in CommunicationLog.objects.filter(campaign=c).select_related('customer').iterator():
            w.writerow([l.id, l.customer.name, l.channel, l.status, l.sent_at or '', l.delivered_at or '', l.opened_at or '', l.clicked_at or '', l.converted])
        return resp

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        c = self.get_object()
        new = Campaign.objects.create(
            name=c.name + ' (copy)',
            description=c.description,
            segment=c.segment,
            channel=c.channel,
            message_template=c.message_template,
            send_mode=c.send_mode,
            is_ab_test=c.is_ab_test,
            ab_variants=c.ab_variants,
            status='draft',
            created_by=request.user if request.user.is_authenticated else None,
        )
        return Response(CampaignSerializer(new).data, status=201)

    @action(detail=True, methods=['post'])
    def preflight(self, request, pk=None):
        c = self.get_object()
        audience = SegmentEvaluator().evaluate(c.segment.filter_tree)
        n = audience.count()
        sample = list(audience[:3])
        previews = [render(c.message_template, cust) for cust in sample]
        # Estimate delivery rate: 0.85 baseline, 0.95 for email, penalty above 500
        base = 0.95 if c.channel == 'email' else 0.85
        if n > 500:
            base *= 0.97
        return Response({
            'audience_size': n,
            'channel': c.channel,
            'estimated_delivery_rate': round(base, 3),
            'message_previews': previews,
            'warnings': ([] if n >= 10 else ['Audience is very small (<10).']),
        })


class CommunicationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommunicationLog.objects.select_related('customer', 'campaign').all()
    serializer_class = CommunicationLogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        campaign_id = self.request.query_params.get('campaign')
        if campaign_id:
            qs = qs.filter(campaign_id=campaign_id)
        log_status = self.request.query_params.get('status')
        if log_status:
            qs = qs.filter(status=log_status)
        return qs.order_by('-queued_at')


class CampaignTemplateViewSet(viewsets.ModelViewSet):
    queryset = CampaignTemplate.objects.all()
    serializer_class = CampaignTemplateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
