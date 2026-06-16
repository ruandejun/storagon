from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Card
from .serializers import CardSerializer
from system_configure.controllers import Tool

class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [filters.SearchFilter]
    search_fields = ['card_number', 'status']
    pagination_class = Tool.StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'bulk_assign']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            queryset = Card.objects.all()
        else:
            queryset = Card.objects.filter(owner=user)

        status = self.request.query_params.get('status')
        if status and status != 'Tất cả':
            queryset = queryset.filter(status=status)

        owner = self.request.query_params.get('owner')
        if owner:
            if owner == 'unassigned':
                queryset = queryset.filter(owner__isnull=True)
            elif owner != 'all':
                try:
                    queryset = queryset.filter(owner_id=int(owner))
                except ValueError:
                    pass
        return queryset.order_by('-created_at', '-id')

    def perform_update(self, serializer):
        user = self.request.user
        card = serializer.instance
        if not user.is_staff:
            serializer.save(
                card_number=card.card_number,
                expiry_date=card.expiry_date,
                cvv=card.cvv,
                extra_info=card.extra_info,
                owner=card.owner,
                used_by=user
            )
        else:
            serializer.save()

    @action(detail=False, methods=['post'], url_path='bulk-assign', permission_classes=[IsAdminUser])
    def bulk_assign(self, request):
        card_ids = request.data.get('card_ids', [])
        owner_id = request.data.get('owner_id')
        
        if not card_ids:
            return Response({'success': False, 'message': 'Không có thẻ nào được chọn.'}, status=400)
            
        owner = None
        if owner_id:
            try:
                owner = User.objects.get(id=owner_id)
            except User.DoesNotExist:
                return Response({'success': False, 'message': 'Người dùng không tồn tại.'}, status=404)
                
        Card.objects.filter(id__in=card_ids).update(owner=owner)
        return Response({'success': True, 'message': f'Đã gán sở hữu thành công cho {len(card_ids)} thẻ.'})
