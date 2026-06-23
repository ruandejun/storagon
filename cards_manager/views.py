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

    def create(self, request, *args, **kwargs):
        card_number = request.data.get('card_number')
        if not card_number:
            return Response({'success': False, 'message': 'Thiếu số thẻ.'}, status=400)

        card_obj = Card.objects.filter(card_number=card_number).first()
        if card_obj:
            # Update info if provided in request to keep it in sync and prevent duplicates
            updated = False
            expiry_date = request.data.get('expiry_date')
            cvv = request.data.get('cvv')
            status = request.data.get('status')
            extra_info = request.data.get('extra_info')
            owner_id = request.data.get('owner')

            if expiry_date and card_obj.expiry_date != expiry_date:
                card_obj.expiry_date = expiry_date
                updated = True
            if cvv and card_obj.cvv != cvv:
                card_obj.cvv = cvv
                updated = True
            if status and card_obj.status != status:
                card_obj.status = status
                updated = True
            if extra_info and card_obj.extra_info != extra_info:
                card_obj.extra_info = extra_info
                updated = True
            if owner_id is not None:
                try:
                    owner_val = int(owner_id) if owner_id else None
                except ValueError:
                    owner_val = None
                if card_obj.owner_id != owner_val:
                    card_obj.owner_id = owner_val
                    updated = True
                    if owner_val:
                        try:
                            from dashboard.models import Notification
                            target_user = User.objects.get(id=owner_val)
                            Notification.objects.create(
                                user=target_user,
                                message=f"Bạn đã được gán quyền sở hữu thẻ {card_obj.card_number} (CVV: {card_obj.cvv})."
                            )
                        except Exception:
                            pass

            if updated:
                card_obj.save()

            serializer = self.get_serializer(card_obj)
            return Response(serializer.data)

        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_authenticated:
            instance.used_by = request.user
            instance.save(update_fields=['used_by'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
            if ',' in status:
                status_list = [s.strip() for s in status.split(',')]
                queryset = queryset.filter(status__in=status_list)
            else:
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
        return queryset.select_related('owner', 'used_by').order_by('-created_at', '-id')

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
            old_instance = self.get_object()
            old_owner = old_instance.owner
            old_status = old_instance.status
            old_extra = old_instance.extra_info
            serializer.save()
            new_instance = serializer.instance
            new_owner = new_instance.owner
            
            try:
                from dashboard.models import Notification
                if old_owner != new_owner and new_owner:
                    Notification.objects.create(
                        user=new_owner,
                        message=f"Bạn đã được gán quyền sở hữu thẻ {new_instance.card_number} (CVV: {new_instance.cvv})."
                    )
                if new_owner:
                    changes = []
                    if old_status != new_instance.status:
                        changes.append(f"trạng thái từ '{old_status}' sang '{new_instance.status}'")
                    if old_extra != new_instance.extra_info:
                        changes.append("thông tin bổ sung")
                    if changes:
                        Notification.objects.create(
                            user=new_owner,
                            message=f"Thẻ {new_instance.card_number} của bạn đã thay đổi: {', '.join(changes)}."
                        )
            except Exception as e:
                print(f"Error creating card notification: {e}")

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
                
        cards_to_notify = list(Card.objects.filter(id__in=card_ids))
        Card.objects.filter(id__in=card_ids).update(owner=owner)
        
        if owner:
            try:
                from dashboard.models import Notification
                for card in cards_to_notify:
                    if card.owner != owner:
                        Notification.objects.create(
                            user=owner,
                            message=f"Bạn đã được gán quyền sở hữu thẻ {card.card_number} (CVV: {card.cvv}) qua gán hàng loạt."
                        )
            except Exception as e:
                print(f"Error creating bulk card notification: {e}")
                
        return Response({'success': True, 'message': f'Đã gán sở hữu thành công cho {len(card_ids)} thẻ.'})

    @action(detail=False, methods=['post'], url_path='bulk-status')
    def bulk_status(self, request):
        card_ids = request.data.get('card_ids', [])
        status = request.data.get('status')
        
        if not card_ids or not status:
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.'}, status=400)
            
        queryset = self.get_queryset().filter(id__in=card_ids)
        cards_to_notify = list(queryset)
        updated_count = queryset.update(status=status)
        
        if request.user.is_staff:
            try:
                from dashboard.models import Notification
                for card in cards_to_notify:
                    if card.owner:
                        Notification.objects.create(
                            user=card.owner,
                            message=f"Thẻ {card.card_number} đã được cập nhật trạng thái thành '{status}' bởi quản trị viên."
                        )
            except Exception:
                pass
                
        return Response({'success': True, 'message': f'Đã cập nhật trạng thái cho {updated_count} thẻ.'})
