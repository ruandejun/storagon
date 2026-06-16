import json
import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, filters, permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from cards_manager.models import Card
from cards_manager.views import CardViewSet

from servermain.models import UserProfile

from .serializers import DashboardUserSerializer, UserHwidSerializer

from telegram_bot.models import BrowserProfiles, MunProxies, AccountsEmails, AccountsCreated, UserHwid
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
    return render(request, 'dashboard/index.html')

def login_view(request):
    if request.user.is_authenticated:
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
            if user.is_active:
                login(request, user)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Tài khoản đã bị khóa.'}, status=403)
        else:
            return JsonResponse({'success': False, 'message': 'Sai tài khoản hoặc mật khẩu.'}, status=400)
            
    return render(request, 'dashboard/login.html')

def logout_view(request):
    logout(request)
    return redirect('/dashboard/login/')

@csrf_exempt
def register_view(request):
    if request.user.is_authenticated:
        return JsonResponse({'success': True, 'message': 'Đã đăng nhập.'})
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
        except Exception:
            return JsonResponse({'success': False, 'message': 'Dữ liệu không hợp lệ.'}, status=400)
            
        if not username or not email or not password or not confirm_password:
            return JsonResponse({'success': False, 'message': 'Vui lòng điền đầy đủ thông tin.'}, status=400)
            
        if password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Mật khẩu xác nhận không khớp.'}, status=400)
            
        if not re.match(r'^\w[a-zA-Z0-9._]{5,29}$', username):
            return JsonResponse({'success': False, 'message': 'Tên đăng nhập phải từ 6-30 ký tự và không chứa ký tự đặc biệt.'}, status=400)
            
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'Tên đăng nhập đã tồn tại.'}, status=400)
            
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email đã được sử dụng.'}, status=400)
            
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            # Safely get/create UserProfile and set normal status
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.account_status = 0 # AccountStatus.normal
            profile.save()
            
            # Log the user in immediately
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Đăng ký thành công.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Lỗi hệ thống: {str(e)}'}, status=500)
            
    return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ.'}, status=405)

@csrf_exempt
def forgot_password_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
        except Exception:
            return JsonResponse({'success': False, 'message': 'Dữ liệu không hợp lệ.'}, status=400)
            
        if not email:
            return JsonResponse({'success': False, 'message': 'Vui lòng cung cấp email.'}, status=400)
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Email không tồn tại trong hệ thống.'}, status=400)
            
        from servermain.controllers import EmailController
        success = EmailController.sendResetPasswordMail(request, email, user.id)
        if success:
            return JsonResponse({'success': True, 'message': 'Email khôi phục mật khẩu đã được gửi vào hòm thư của bạn.'})
        else:
            return JsonResponse({'success': False, 'message': 'Không thể gửi email lúc này. Vui lòng thử lại sau.'}, status=500)
            
    return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ.'}, status=405)

@login_required(login_url='/dashboard/login/')
def dashboard_stats_api(request):
    user = request.user
    if user.is_staff:
        cards_qs = Card.objects.all()
    else:
        cards_qs = Card.objects.filter(owner=user)

    # Cards Stats
    total_cards = cards_qs.count()
    status_counts = {
        'chua_su_dung': cards_qs.filter(status='Chưa sử dụng').count(),
        'dang_su_dung': cards_qs.filter(status='Đang sử dụng').count(),
        'da_su_dung': cards_qs.filter(status='Đã sử dụng').count(),
        'the_chet': cards_qs.filter(status='Thẻ chết').count(),
        'the_song': cards_qs.filter(status='Thẻ sống').count(),
        'the_tot': cards_qs.filter(status='Thẻ tốt').count(),
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
    for c in cards_qs.order_by('-updated_at')[:5]:
        recent_cards.append({
            'card_number': c.card_number[:4] + ' **** **** ' + c.card_number[-4:] if len(c.card_number) >= 8 else c.card_number,
            'status': c.status,
            'updated_at': c.updated_at.strftime('%Y-%m-%d %H:%M:%S') if c.updated_at else '-'
        })
        
    # Recent Users - Only for staff
    recent_users = []
    if request.user.is_staff:
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Security checks: Do not delete superusers or yourself
        if instance.is_superuser:
            return Response({'success': False, 'message': 'Không thể xóa tài khoản Admin hệ thống.'}, status=400)
        if instance == request.user:
            return Response({'success': False, 'message': 'Không thể tự xóa chính tài khoản của bạn.'}, status=400)

        from django.apps import apps
        from django.db import transaction

        try:
            with transaction.atomic():
                # Loop through all models in the project to clean up ForeignKey and OneToOne references to User
                for model in apps.get_models():
                    for field in model._meta.fields:
                        if field.related_model == User:
                            filter_kwargs = {field.name: instance}
                            if model.objects.filter(**filter_kwargs).exists():
                                if field.null:
                                    update_kwargs = {field.name: None}
                                    model.objects.filter(**filter_kwargs).update(**update_kwargs)
                                else:
                                    model.objects.filter(**filter_kwargs).delete()

                # Clean up UserProfile just in case
                from servermain.models import UserProfile
                UserProfile.objects.filter(user=instance).delete()

                # Delete the user itself
                instance.delete()

            return Response({'success': True, 'message': 'Đã xóa người dùng thành công!'})
        except Exception as e:
            return Response({'success': False, 'message': f'Lỗi khi xóa người dùng: {str(e)}'}, status=500)


class BrowserProfilesViewSet(viewsets.ModelViewSet):
    queryset = BrowserProfiles.objects.all().order_by('-id')
    serializer_class = BrowserProfilesSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['profile_name', 'profile_original_name', 'profile_os']


class MunProxiesViewSet(viewsets.ModelViewSet):
    queryset = MunProxies.objects.all().order_by('-id')
    serializer_class = MunProxiesSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['socks_port', 'control_port', 'bridges_string', 'country_name']


class AccountsEmailsViewSet(viewsets.ModelViewSet):
    queryset = AccountsEmails.objects.all().order_by('-id')
    serializer_class = AccountsEmailsSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'type']

    @action(detail=True, methods=['post'], url_path='add-to-system')
    def add_to_system(self, request, pk=None):
        email_obj = self.get_object()
        
        # 1. Create a default browser profile
        import random
        profile_name = email_obj.email.split('@')[0] if email_obj.email else 'profile'
        profile_name = re.sub(r'[^a-zA-Z0-9]', '', profile_name)
        
        profile = BrowserProfiles.objects.create(
            profile_owner=request.user,
            profile_name=profile_name,
            profile_os='Window',
            profile_browser='Chrome',
            profile_version='102.0.5005.63',
            profile_resolution='1920×1080',
            profile_cpu='8',
            profile_canvas='Noise',
            profile_rects='Noise',
            profile_font='Noise',
            profile_audio='Noise',
            profile_webgl='Noise',
            profile_time_zone=2, # Follow IP
            profile_webrtc=2,    # Follow IP
            profile_geo=2,       # Follow IP
            profile_vendor='Google Inc. (ATI Technologies Inc.)',
            profile_renderer='ANGLE (Intel(R) G41 Express Chipset (Microsoft Corporation - WDDM 1.1) Direct3D9Ex vs_3_0 ps_3_0)',
            profile_start_url='https://iphey.com'
        )
        
        # 2. Create the AccountsCreated record
        account = AccountsCreated.objects.create(
            owner=request.user,
            created_by=request.user,
            email=email_obj.email,
            password=email_obj.password,
            type=email_obj.type,
            browser_profiles=profile,
            accounts_emails=email_obj,
            signup_ip=email_obj.signup_ip or '',
            phone_number=email_obj.phone_number or '',
            note=email_obj.note or ''
        )
        
        # 3. Mark the email as used
        email_obj.used = 1
        email_obj.save()
        
        return Response({'success': True, 'message': 'Đã thêm tài khoản vào hệ thống thành công!'})


class AccountsCreatedViewSet(viewsets.ModelViewSet):
    queryset = AccountsCreated.objects.all().order_by('-id')
    serializer_class = AccountsCreatedSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'type']

    @action(detail=False, methods=['post'], url_path='add-manual')
    def add_manual(self, request):
        data = request.data
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        type_str = data.get('type', 'Amazon').strip()
        profile_id = data.get('profile_id')
        two_factor_auth = data.get('two_factor_auth', '').strip()
        cookies = data.get('cookies', '').strip()
        note = data.get('note', '').strip()
        subscription = data.get('subscription', '').strip()
        subscription_owner = data.get('subscription_owner', '').strip()

        if not email or not password:
            return Response({'success': False, 'message': 'Email và Mật khẩu không được để trống.'}, status=400)

        # 1. Resolve or create type
        from telegram_bot.models import AccountsType
        account_type, _ = AccountsType.objects.get_or_create(value=type_str.lower())

        # 2. Resolve profile
        profile = None
        if profile_id == 'auto':
            # Create a default profile
            profile_name = email.split('@')[0] if email else 'profile'
            profile_name = re.sub(r'[^a-zA-Z0-9]', '', profile_name)
            profile = BrowserProfiles.objects.create(
                profile_owner=request.user,
                profile_name=profile_name,
                profile_os='Window',
                profile_browser='Chrome',
                profile_version='102.0.5005.63',
                profile_resolution='1920×1080',
                profile_cpu='8',
                profile_canvas='Noise',
                profile_rects='Noise',
                profile_font='Noise',
                profile_audio='Noise',
                profile_webgl='Noise',
                profile_time_zone=2, # Follow IP
                profile_webrtc=2,    # Follow IP
                profile_geo=2,       # Follow IP
                profile_vendor='Google Inc. (ATI Technologies Inc.)',
                profile_renderer='ANGLE (Intel(R) G41 Express Chipset (Microsoft Corporation - WDDM 1.1) Direct3D9Ex vs_3_0 ps_3_0)',
                profile_start_url='https://iphey.com'
            )
        elif profile_id and profile_id != 'none':
            try:
                profile_qs = BrowserProfiles.objects.filter(pk=int(profile_id))
                if profile_qs.exists():
                    profile = profile_qs[0]
            except (ValueError, TypeError):
                pass

        # 3. Create the AccountsCreated record
        account = AccountsCreated.objects.create(
            owner=request.user,
            created_by=request.user,
            email=email,
            password=password,
            type=account_type,
            browser_profiles=profile,
            two_factor_auth=two_factor_auth,
            cookies=cookies,
            note=note,
            subscription=subscription,
            subscription_owner=subscription_owner
        )

        return Response({'success': True, 'message': 'Đã thêm tài khoản mới thành công!'})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        if 'email' in data:
            instance.email = data.get('email', '').strip()
        if 'password' in data:
            instance.password = data.get('password', '').strip()
        
        if 'type' in data:
            type_str = data.get('type', '').strip()
            if type_str:
                from telegram_bot.models import AccountsType
                account_type, _ = AccountsType.objects.get_or_create(value=type_str.lower())
                instance.type = account_type
            else:
                instance.type = None

        if 'profile_id' in data:
            profile_id = data.get('profile_id')
            if profile_id == 'auto':
                profile_name = instance.email.split('@')[0] if instance.email else 'profile'
                profile_name = re.sub(r'[^a-zA-Z0-9]', '', profile_name)
                profile = BrowserProfiles.objects.create(
                    profile_owner=request.user,
                    profile_name=profile_name,
                    profile_os='Window',
                    profile_browser='Chrome',
                    profile_version='102.0.5005.63',
                    profile_resolution='1920×1080',
                    profile_cpu='8',
                    profile_canvas='Noise',
                    profile_rects='Noise',
                    profile_font='Noise',
                    profile_audio='Noise',
                    profile_webgl='Noise',
                    profile_time_zone=2, # Follow IP
                    profile_webrtc=2,    # Follow IP
                    profile_geo=2,       # Follow IP
                    profile_vendor='Google Inc. (ATI Technologies Inc.)',
                    profile_renderer='ANGLE (Intel(R) G41 Express Chipset (Microsoft Corporation - WDDM 1.1) Direct3D9Ex vs_3_0 ps_3_0)',
                    profile_start_url='https://iphey.com'
                )
                instance.browser_profiles = profile
            elif profile_id == 'none':
                instance.browser_profiles = None
            elif profile_id:
                try:
                    profile_qs = BrowserProfiles.objects.filter(pk=int(profile_id))
                    if profile_qs.exists():
                        instance.browser_profiles = profile_qs[0]
                except (ValueError, TypeError):
                    pass

        if 'two_factor_auth' in data:
            instance.two_factor_auth = data.get('two_factor_auth', '').strip()
        if 'cookies' in data:
            instance.cookies = data.get('cookies', '').strip()
        if 'note' in data:
            instance.note = data.get('note', '').strip()
        if 'subscription' in data:
            instance.subscription = data.get('subscription', '').strip()
        if 'subscription_owner' in data:
            instance.subscription_owner = data.get('subscription_owner', '').strip()
        if 'status' in data:
            try:
                instance.status = int(data.get('status'))
            except (ValueError, TypeError):
                pass

        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response({'success': False, 'message': 'Danh sách ID không hợp lệ.'}, status=400)
        deleted_count, _ = AccountsCreated.objects.filter(pk__in=ids).delete()
        return Response({'success': True, 'message': f'Đã xóa thành công {deleted_count} tài khoản!'})

    @action(detail=False, methods=['post'], url_path='bulk-status')
    def bulk_status(self, request):
        ids = request.data.get('ids', [])
        status_val = request.data.get('status')
        if not isinstance(ids, list) or status_val is None:
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.'}, status=400)
        
        try:
            status_int = int(status_val)
        except (ValueError, TypeError):
            return Response({'success': False, 'message': 'Trạng thái không hợp lệ.'}, status=400)
        
        updated_count = AccountsCreated.objects.filter(pk__in=ids).update(status=status_int)
        return Response({'success': True, 'message': f'Đã cập nhật trạng thái cho {updated_count} tài khoản!'})

    @action(detail=False, methods=['get'], url_path='users-list')
    def users_list(self, request):
        users = User.objects.filter(is_active=True).order_by('username')
        user_data = [{'id': u.id, 'username': u.username} for u in users]
        return Response(user_data)


class UserHwidViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for managing UserHwid — controls which machines can use MunLogin tool."""
    serializer_class = UserHwidSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]  # Admin only
    filter_backends = [filters.SearchFilter]
    search_fields = ['value', 'user__username', 'user__email', 'note']

    def get_queryset(self):
        qs = UserHwid.objects.all().select_related('user').order_by('-created')
        # Filter by user_id param
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
        # Filter by status
        hwid_status = self.request.query_params.get('status')
        if hwid_status is not None:
            qs = qs.filter(status=hwid_status)
        return qs

    @action(detail=False, methods=['delete'], url_path='reset-user')
    def reset_user_hwid(self, request):
        """DELETE /api/hwids/reset-user/?user_id=X  — removes ALL HWIDs for a user."""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'success': False, 'message': 'user_id is required'}, status=400)
        deleted_count, _ = UserHwid.objects.filter(user_id=user_id).delete()
        return Response({
            'success': True,
            'message': f'Đã xóa {deleted_count} HWID của user ID={user_id}. User có thể đăng nhập bằng máy mới.'
        })

    @action(detail=True, methods=['post'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        """POST /api/hwids/{id}/toggle-status/ — enable/disable a specific HWID."""
        obj = self.get_object()
        # Toggle: 0=active → 1=suspended, 1=suspended → 0=active
        obj.status = 1 if obj.status == 0 else 0
        obj.save()
        label = 'Đã kích hoạt' if obj.status == 0 else 'Đã tạm khóa'
        return Response({'success': True, 'message': label, 'status': obj.status})
