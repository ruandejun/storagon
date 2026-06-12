import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, filters, permissions
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.models import User
from cards_manager.models import Card
from cards_manager.views import CardViewSet

from .serializers import DashboardUserSerializer

from telegram_bot.models import BrowserProfiles, MunProxies, AccountsEmails, AccountsCreated
from telegram_bot.api.TelegramBot_RestfulApi import (
    BrowserProfilesSerializer, MunProxiesSerializer,
    AccountsEmailsSerializer, AccountsCreatedSerializer
)

# Wrap MongoDB imports to handle failures gracefully
try:
    from servermain.mongo_models import Session
    from storagon.enum import SessionStatus
except Exception:
    Session = None
    SessionStatus = None

@login_required(login_url='/dashboard/login/')
def dashboard_index(request):
    if not request.user.is_staff:
        return redirect('/dashboard/login/?error=unauthorized')
    return render(request, 'dashboard/index.html')

def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/dashboard/')
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except Exception:
            return JsonResponse({'success': False, 'message': 'Dữ liệu không hợp lệ.'}, status=400)
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Tài khoản không có quyền truy cập.'}, status=403)
        else:
            return JsonResponse({'success': False, 'message': 'Sai tài khoản hoặc mật khẩu.'}, status=400)
            
    return render(request, 'dashboard/login.html')

def logout_view(request):
    logout(request)
    return redirect('/dashboard/login/')

@login_required(login_url='/dashboard/login/')
def dashboard_stats_api(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    # Cards Stats
    total_cards = Card.objects.count()
    status_counts = {
        'chua_su_dung': Card.objects.filter(status='Chưa sử dụng').count(),
        'dang_su_dung': Card.objects.filter(status='Đang sử dụng').count(),
        'da_su_dung': Card.objects.filter(status='Đã sử dụng').count(),
        'the_chet': Card.objects.filter(status='Thẻ chết').count(),
        'the_song': Card.objects.filter(status='Thẻ sống').count(),
        'the_tot': Card.objects.filter(status='Thẻ tốt').count(),
    }
    
    # Users Stats
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    # Active sessions from MongoDB
    active_sessions = 0
    if Session is not None:
        try:
            active_sessions = Session.objects.count()
        except Exception:
            pass
            
    # Recent Cards
    recent_cards = []
    for c in Card.objects.all().order_by('-updated_at')[:5]:
        recent_cards.append({
            'card_number': c.card_number[:4] + ' **** **** ' + c.card_number[-4:] if len(c.card_number) >= 8 else c.card_number,
            'status': c.status,
            'updated_at': c.updated_at.strftime('%Y-%m-%d %H:%M:%S') if c.updated_at else '-'
        })
        
    # Recent Users
    recent_users = []
    for u in User.objects.all().order_by('-date_joined')[:5]:
        recent_users.append({
            'username': u.username,
            'email': u.email,
            'date_joined': u.date_joined.strftime('%Y-%m-%d %H:%M:%S') if u.date_joined else '-'
        })
        
    return JsonResponse({
        'total_cards': total_cards,
        'status_counts': status_counts,
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'active_sessions': active_sessions,
        'recent_cards': recent_cards,
        'recent_users': recent_users
    })

class DashboardUserViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardUserSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'profile__full_name']

    def get_queryset(self):
        queryset = User.objects.all().order_by('-id')
        status = self.request.query_params.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        role = self.request.query_params.get('role')
        if role == 'admin':
            queryset = queryset.filter(is_superuser=True)
        elif role == 'staff':
            queryset = queryset.filter(is_staff=True, is_superuser=False)
        elif role == 'user':
            queryset = queryset.filter(is_staff=False, is_superuser=False)
            
        return queryset


class BrowserProfilesViewSet(viewsets.ModelViewSet):
    queryset = BrowserProfiles.objects.all().order_by('-id')
    serializer_class = BrowserProfilesSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['profile_name', 'profile_original_name', 'profile_os']


class MunProxiesViewSet(viewsets.ModelViewSet):
    queryset = MunProxies.objects.all().order_by('-id')
    serializer_class = MunProxiesSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['socks_port', 'control_port', 'bridges_string', 'country_name']


class AccountsEmailsViewSet(viewsets.ModelViewSet):
    queryset = AccountsEmails.objects.all().order_by('-id')
    serializer_class = AccountsEmailsSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'type']


class AccountsCreatedViewSet(viewsets.ModelViewSet):
    queryset = AccountsCreated.objects.all().order_by('-id')
    serializer_class = AccountsCreatedSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'type']
