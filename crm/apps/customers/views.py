import csv
import io
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Customer, Order
from .serializers import CustomerSerializer, CustomerListSerializer, OrderSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone', 'city', 'external_id']
    ordering_fields = ['created_at', 'total_spend', 'last_order_at', 'rfm_composite']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer

    @action(detail=False, methods=['post'])
    def bulk(self, request):
        data = request.data.get('customers', [])
        created = []
        for row in data:
            ser = CustomerSerializer(data=row)
            if ser.is_valid():
                ser.save()
                created.append(ser.data)
        return Response({'created': len(created)}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        customer = self.get_object()
        orders = OrderSerializer(customer.orders.all()[:50], many=True).data
        # Communication history
        from apps.campaigns.models import CommunicationLog
        logs = CommunicationLog.objects.filter(customer=customer).order_by('-queued_at')[:50]
        comms = [
            {
                'id': str(l.id),
                'campaign_id': str(l.campaign_id),
                'campaign_name': l.campaign.name,
                'channel': l.channel,
                'status': l.status,
                'queued_at': l.queued_at,
                'sent_at': l.sent_at,
                'delivered_at': l.delivered_at,
                'opened_at': l.opened_at,
                'clicked_at': l.clicked_at,
                'converted': l.converted,
            }
            for l in logs
        ]
        return Response({'orders': orders, 'communications': comms})

    @action(detail=False, methods=['post'], url_path='import-csv')
    def import_csv(self, request):
        f = request.FILES.get('file')
        if not f:
            return Response({'error': 'No file uploaded'}, status=400)
        text = f.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(text))
        n = 0
        for row in reader:
            Customer.objects.update_or_create(
                email=row.get('email') or None,
                defaults={
                    'name': row.get('name', ''),
                    'phone': row.get('phone') or None,
                    'city': row.get('city', ''),
                    'channel_preference': row.get('channel_preference', 'auto'),
                    'gender': row.get('gender', 'unknown'),
                },
            )
            n += 1
        return Response({'imported': n})

    @action(detail=False, methods=['get'], url_path='export-csv')
    def export_csv(self, request):
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="customers.csv"'
        w = csv.writer(resp)
        w.writerow(['id', 'name', 'email', 'phone', 'city', 'rfm_tier', 'total_spend', 'total_orders', 'last_order_at'])
        for c in Customer.objects.all().iterator():
            w.writerow([c.id, c.name, c.email or '', c.phone or '', c.city, c.rfm_tier, c.total_spend, c.total_orders, c.last_order_at or ''])
        return resp
