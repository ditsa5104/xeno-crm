from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Segment, SegmentSnapshot
from .serializers import SegmentSerializer, AIBuildSerializer
from .evaluator import SegmentEvaluator
from .ai_segmenter import nl_to_filter_tree, SegmenterError
from apps.customers.serializers import CustomerListSerializer
from apps.customers.models import Customer


class SegmentViewSet(viewsets.ModelViewSet):
    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        seg = serializer.save(
            created_by=self.request.user if self.request.user.is_authenticated else None,
        )
        self._recompute_count(seg)

    def perform_update(self, serializer):
        seg = serializer.save()
        self._recompute_count(seg)

    @staticmethod
    def _recompute_count(seg):
        try:
            qs = SegmentEvaluator().evaluate(seg.filter_tree)
            seg.customer_count = qs.count()
            seg.last_computed = timezone.now()
            seg.save(update_fields=['customer_count', 'last_computed'])
        except ValueError:
            pass

    @action(detail=False, methods=['post'], url_path='ai-build')
    def ai_build(self, request):
        ser = AIBuildSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        nl = ser.validated_data['nl_filter']
        try:
            tree = nl_to_filter_tree(nl)
        except SegmenterError as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        seg = Segment.objects.create(
            name=ser.validated_data['name'],
            description=ser.validated_data.get('description', ''),
            segment_type='dynamic',
            filter_tree=tree,
            natural_query=nl,
            ai_generated=True,
            created_by=request.user if request.user.is_authenticated else None,
        )
        self._recompute_count(seg)
        return Response(SegmentSerializer(seg).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        seg = self.get_object()
        tree = request.data.get('filter_tree') or seg.filter_tree
        try:
            qs = SegmentEvaluator().evaluate(tree)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        sample = CustomerListSerializer(qs[:25], many=True).data
        return Response({'count': qs.count(), 'sample': sample})

    @action(detail=True, methods=['post'])
    def snapshot(self, request, pk=None):
        seg = self.get_object()
        qs = SegmentEvaluator().evaluate(seg.filter_tree)
        count = qs.count()
        SegmentSnapshot.objects.create(segment=seg, customer_count=count)
        seg.customer_count = count
        seg.last_computed = timezone.now()
        seg.save(update_fields=['customer_count', 'last_computed'])
        return Response({'customer_count': count})

    @action(detail=True, methods=['get'])
    def health(self, request, pk=None):
        seg = self.get_object()
        snaps = seg.snapshots.order_by('-taken_at')[:30]
        return Response([
            {'taken_at': s.taken_at, 'customer_count': s.customer_count}
            for s in snaps
        ])

    @action(detail=False, methods=['post'])
    def lookalike(self, request):
        """Find customers similar to a seed segment using simple feature-vector cosine similarity."""
        seed_segment_id = request.data.get('segment_id')
        n = int(request.data.get('n', 50))
        if not seed_segment_id:
            return Response({'error': 'segment_id required'}, status=400)
        try:
            seed = Segment.objects.get(id=seed_segment_id)
        except Segment.DoesNotExist:
            return Response({'error': 'Segment not found'}, status=404)
        seed_qs = SegmentEvaluator().evaluate(seed.filter_tree)
        if not seed_qs.exists():
            return Response({'error': 'Seed segment is empty'}, status=400)

        def vec(c):
            return (
                float(c.rfm_composite),
                float(c.total_spend),
                c.total_orders,
                c.rfm_recency_score,
            )

        seed_vecs = [vec(c) for c in seed_qs[:200]]
        if not seed_vecs:
            return Response({'error': 'No seed vectors'}, status=400)
        # Centroid
        cn = len(seed_vecs)
        centroid = tuple(sum(v[i] for v in seed_vecs) / cn for i in range(4))

        def cos(a, b):
            dot = sum(a[i] * b[i] for i in range(4))
            na = sum(a[i] ** 2 for i in range(4)) ** 0.5
            nb = sum(b[i] ** 2 for i in range(4)) ** 0.5
            return dot / (na * nb + 1e-9)

        seed_ids = set(seed_qs.values_list('id', flat=True))
        candidates = Customer.objects.exclude(id__in=seed_ids)[:5000]
        scored = sorted(
            [(c, cos(vec(c), centroid)) for c in candidates],
            key=lambda x: -x[1],
        )[:n]
        return Response({
            'centroid': centroid,
            'lookalikes': [
                {**CustomerListSerializer(c).data, 'similarity': round(s, 4)}
                for c, s in scored
            ],
        })
