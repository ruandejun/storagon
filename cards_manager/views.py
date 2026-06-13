from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from .models import Card
from .serializers import CardSerializer

class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['card_number', 'status']

    def get_queryset(self):
        queryset = Card.objects.all()
        status = self.request.query_params.get('status')
        if status and status != 'Tất cả':
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at', '-id')
