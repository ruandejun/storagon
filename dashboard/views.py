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
from system_configure.controllers.Tool import StandardResultsSetPagination

from servermain.models import UserProfile

from .serializers import DashboardUserSerializer, UserHwidSerializer

from telegram_bot.models import BrowserProfiles, MunProxies, AccountsEmails, AccountsCreated, UserHwid
from telegram_bot.api.TelegramBot_RestfulApi import (
    BrowserProfilesSerializer, MunProxiesSerializer,
    AccountsEmailsSerializer, AccountsCreatedSerializer,
    AccountsCreatedListSerializer
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
        'the_loi': cards_qs.filter(status='Thẻ lỗi').count(),
        'sub_ok': cards_qs.filter(status='Sub OK').count(),
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
    pagination_class = StandardResultsSetPagination
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
    pagination_class = StandardResultsSetPagination
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['profile_name', 'profile_original_name', 'profile_os']


class MunProxiesViewSet(viewsets.ModelViewSet):
    queryset = MunProxies.objects.all().order_by('-id')
    serializer_class = MunProxiesSerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['socks_port', 'control_port', 'bridges_string', 'country_name']


class AccountsEmailsViewSet(viewsets.ModelViewSet):
    serializer_class = AccountsEmailsSerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'type']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return AccountsEmails.objects.all().order_by('-id')
        return AccountsEmails.objects.filter(owner=user).order_by('-id')

    def create(self, request, *args, **kwargs):
        data = request.data
        email_addr = data.get('email', '').strip()
        password = data.get('password', '').strip()
        refresh_token = data.get('refresh_token', '').strip()
        client_id = data.get('client_id', '').strip()
        proxy = data.get('proxy', '').strip()
        socks5 = data.get('socks5', '').strip()
        note = data.get('note', '').strip()

        if not email_addr:
            return Response({'error': 'Email không được để trống.'}, status=400)

        # Detect email type
        email_lower = email_addr.lower()
        if any(dom in email_lower for dom in ['@hotmail.', '@outlook.', '@live.', '@msn.']):
            detected_type = 'hotmail'
        elif '@gmail.' in email_lower:
            detected_type = 'gmail'
        else:
            if '@' in email_lower:
                detected_type = email_lower.split('@')[1].split('.')[0]
            else:
                detected_type = 'gmail'

        from telegram_bot.models import AccountsType
        account_type, _ = AccountsType.objects.get_or_create(
            value=detected_type.lower(),
            defaults={'label': detected_type.title()}
        )

        email_obj = AccountsEmails.objects.filter(email=email_addr, owner=request.user).first()
        if email_obj:
            updated = False
            if password and email_obj.password != password:
                email_obj.password = password
                updated = True
            if refresh_token and email_obj.refresh_token != refresh_token:
                email_obj.refresh_token = refresh_token
                updated = True
            if client_id and email_obj.client_id != client_id:
                email_obj.client_id = client_id
                updated = True
            if email_obj.type != account_type:
                email_obj.type = account_type
                updated = True
            if proxy and email_obj.proxy != proxy:
                email_obj.proxy = proxy
                updated = True
            if socks5 and email_obj.socks5 != socks5:
                email_obj.socks5 = socks5
                updated = True
            if note and email_obj.note != note:
                email_obj.note = note
                updated = True
            if updated:
                email_obj.save()
        else:
            email_obj = AccountsEmails.objects.create(
                email=email_addr,
                password=password,
                refresh_token=refresh_token,
                client_id=client_id,
                type=account_type,
                proxy=proxy,
                socks5=socks5,
                note=note,
                owner=request.user,
                created_by=request.user
            )

        serializer = self.get_serializer(email_obj)
        return Response(serializer.data, status=201)

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

    @action(detail=True, methods=['get'], url_path='read-mailbox')
    def read_mailbox(self, request, pk=None):
        email_obj = self.get_object()
        res = read_single_mailbox_helper(email_obj, request.user)
        if res.get('success'):
            email_obj.refresh_from_db()
            from telegram_bot.api.TelegramBot_RestfulApi import AccountsEmailsSerializer
            serializer = AccountsEmailsSerializer(email_obj)
            return Response({
                'success': True,
                'emails': res.get('emails', []),
                'email_data': serializer.data
            })
        else:
            return Response({'success': False, 'message': res.get('message', 'Không thể đọc hộp thư.')}, status=500)

    @action(detail=False, methods=['get'], url_path='get-graph-config')
    def get_graph_config(self, request):
        return Response({
            'success': True,
            'client_id': get_config('microsoft_graph_client_id', ''),
            'client_secret': get_config('microsoft_graph_client_secret', ''),
            'tenant_id': get_config('microsoft_graph_tenant_id', 'common'),
            'flow': get_config('microsoft_graph_flow', 'ropc')
        })

    @action(detail=False, methods=['post'], url_path='save-graph-config')
    def save_graph_config(self, request):
        data = request.data
        client_id = data.get('client_id', '').strip()
        client_secret = data.get('client_secret', '').strip()
        tenant_id = data.get('tenant_id', 'common').strip()
        flow = data.get('flow', 'ropc').strip()

        set_config('microsoft_graph_client_id', client_id, 'Microsoft Graph API Client ID')
        set_config('microsoft_graph_client_secret', client_secret, 'Microsoft Graph API Client Secret')
        set_config('microsoft_graph_tenant_id', tenant_id, 'Microsoft Graph API Tenant ID')
        set_config('microsoft_graph_flow', flow, 'Microsoft Graph API Auth Flow (client_credentials or ropc)')

        return Response({'success': True, 'message': 'Lưu cấu hình Graph API thành công!'})

    @action(detail=False, methods=['post'], url_path='bulk-read-mailbox')
    def bulk_read_mailbox(self, request):
        accounts = request.data.get('accounts', [])
        if not isinstance(accounts, list) or not accounts:
            return Response({'success': False, 'message': 'Danh sách tài khoản email không hợp lệ.'}, status=400)

        results = {}
        for acc in accounts:
            email_addr = acc.get('email', '').strip()
            password = acc.get('password', '').strip()
            refresh_token = acc.get('refresh_token', '').strip()
            client_id = acc.get('client_id', '').strip()
            
            if not email_addr:
                continue

            # Detect email type
            email_lower = email_addr.lower()
            if any(dom in email_lower for dom in ['@hotmail.', '@outlook.', '@live.', '@msn.']):
                detected_type = 'hotmail'
            elif '@gmail.' in email_lower:
                detected_type = 'gmail'
            else:
                if '@' in email_lower:
                    detected_type = email_lower.split('@')[1].split('.')[0]
                else:
                    detected_type = 'gmail'

            from telegram_bot.models import AccountsType
            account_type, _ = AccountsType.objects.get_or_create(
                value=detected_type.lower(),
                defaults={'label': detected_type.title()}
            )
                
            # Check or create in database
            email_obj = AccountsEmails.objects.filter(email=email_addr, owner=request.user).first()
            if not email_obj:
                email_obj = AccountsEmails.objects.create(
                    email=email_addr,
                    password=password,
                    refresh_token=refresh_token,
                    client_id=client_id,
                    type=account_type,
                    owner=request.user,
                    created_by=request.user
                )
            else:
                updated = False
                if password and email_obj.password != password:
                    email_obj.password = password
                    updated = True
                if refresh_token and email_obj.refresh_token != refresh_token:
                    email_obj.refresh_token = refresh_token
                    updated = True
                if client_id and email_obj.client_id != client_id:
                    email_obj.client_id = client_id
                    updated = True
                if email_obj.type != account_type:
                    email_obj.type = account_type
                    updated = True
                if updated:
                    email_obj.save()

            res = read_single_mailbox_helper(email_obj, request.user)
            results[email_addr] = res

        return Response({'success': True, 'results': results})


def extract_verification_code(subject, body):
    import re
    # Combine subject and body
    text = f"{subject}\n{body}"
    
    # Strip HTML tags
    if "<html" in text.lower() or "<body" in text.lower() or "<div" in text.lower():
        text = re.sub('<[^<]+?>', ' ', text)
        text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
        
    # Search patterns: find numeric / alphanumeric code (4 to 8 characters)
    # preceded by words like code, otp, pin, verify, verify code, confirmation, confirm, mã, xác minh, xác thực, xác nhận
    patterns = [
        r'(?:code|otp|pin|verify|xác minh|xác thực|mã|confirm|xác nhận)\b[^.\n]*?(\b[a-zA-Z0-9-]{4,8}\b)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            code = match.strip()
            if code.isdigit():
                if 4 <= len(code) <= 8:
                    return code
            elif any(c.isdigit() for c in code) and 4 <= len(code) <= 8:
                return code
                
    # Fallback to any 4-8 digit numbers in the subject first
    subj_matches = re.findall(r'\b(\d{4,8})\b', subject)
    if subj_matches:
        return subj_matches[0]
        
    # Fallback: search for any 4-8 digit number anywhere
    fallback_matches = re.findall(r'\b(\d{4,8})\b', text)
    if fallback_matches:
        return fallback_matches[0]
        
    return ""


def update_email_latest_stats(email_obj, latest_email):
    if not latest_email:
        return
    
    from_sender = latest_email.get('from', '')
    date_str = latest_email.get('date', '')
    subject = latest_email.get('subject', '')
    snippet = latest_email.get('snippet', '')
    body = latest_email.get('body', '')
    
    code = extract_verification_code(subject, body)
    
    email_obj.latest_from = from_sender
    email_obj.latest_time = date_str
    email_obj.latest_content = f"{subject} - {snippet}" if subject and snippet else (subject or snippet)
    email_obj.latest_code = code
    email_obj.save(update_fields=['latest_from', 'latest_time', 'latest_content', 'latest_code'])


def read_single_mailbox_helper(email_obj, user):
    import requests
    email_addr = email_obj.email
    password = email_obj.password
    refresh_token = email_obj.refresh_token
    client_id = email_obj.client_id
    
    if not email_addr:
        return {'success': False, 'message': 'Email trống.'}
        
    email_lower = email_addr.lower()
    is_microsoft = any(dom in email_lower for dom in ['@hotmail.', '@live.', '@outlook.', '@msn.'])
    
    parsed_emails = []
    
    if not is_microsoft:
        # Standard IMAP
        import imaplib
        import email as py_email
        from email.header import decode_header
        import re

        def get_imap_host(addr):
            addr = addr.lower()
            if '@gmail.' in addr:
                return 'imap.gmail.com'
            return 'outlook.office365.com'

        try:
            server_host = get_imap_host(email_addr)
            mail = imaplib.IMAP4_SSL(server_host, timeout=10)
            mail.login(email_addr, password)
            mail.select("inbox")
            status, messages = mail.search(None, "ALL")
            if status != "OK":
                return {'success': True, 'emails': []}
            mail_ids = messages[0].split()
            latest_ids = mail_ids[-15:]
            latest_ids.reverse()
            
            for mail_id in latest_ids:
                res_status, msg_data = mail.fetch(mail_id, "(RFC822)")
                if res_status != "OK":
                    continue
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = py_email.message_from_bytes(response_part[1])
                        # decode subject
                        subj_header = msg["Subject"] or ""
                        subject = ""
                        try:
                            decoded = decode_header(subj_header)
                            for part, enc in decoded:
                                if isinstance(part, bytes):
                                    subject += part.decode(enc or "utf-8", errors="ignore")
                                else:
                                    subject += part
                        except Exception:
                            subject = str(subj_header)
                        # decode from
                        from_header = msg["From"] or ""
                        from_sender = ""
                        try:
                            decoded = decode_header(from_header)
                            for part, enc in decoded:
                                if isinstance(part, bytes):
                                    from_sender += part.decode(enc or "utf-8", errors="ignore")
                                else:
                                    from_sender += part
                        except Exception:
                            from_sender = str(from_header)
                        date_str = msg["Date"] or ""
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                                    break
                                elif content_type == "text/html" and "attachment" not in content_disposition:
                                    body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                        else:
                            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore")
                        
                        clean_body = body.strip()
                        if "<html" in clean_body.lower() or "<body" in clean_body.lower() or "<div" in clean_body.lower():
                            clean_body = re.sub('<[^<]+?>', '', clean_body)
                            clean_body = clean_body.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
                        clean_body = re.sub(r'\s+', ' ', clean_body).strip()
                        snippet = clean_body[:200] + ("..." if len(clean_body) > 200 else "")
                        parsed_emails.append({
                            'from': from_sender,
                            'subject': subject,
                            'date': date_str,
                            'snippet': snippet,
                            'body': body
                        })
            try:
                mail.close()
                mail.logout()
            except Exception:
                pass
            
            if parsed_emails:
                update_email_latest_stats(email_obj, parsed_emails[0])
            return {'success': True, 'emails': parsed_emails}
        except Exception as e:
            return {'success': False, 'message': f'Lỗi IMAP: {str(e)}'}

    # Microsoft Account Graph API
    config_client_id = get_config('microsoft_graph_client_id', '').strip()
    config_client_secret = get_config('microsoft_graph_client_secret', '').strip()
    config_tenant_id = get_config('microsoft_graph_tenant_id', 'common').strip()
    config_flow = get_config('microsoft_graph_flow', 'ropc').strip()

    target_refresh_token = refresh_token
    target_client_id = client_id or config_client_id or "9e5f94bc-e8a4-4e73-b8be-63364c29d753"

    if target_refresh_token:
        # OAuth2 Refresh Token Flow
        try:
            token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            res = requests.post(token_url, data={
                'grant_type': 'refresh_token',
                'client_id': target_client_id,
                'refresh_token': target_refresh_token
            }, timeout=10)
            
            if res.status_code == 200:
                res_json = res.json()
                access_token = res_json.get('access_token')
                new_refresh_token = res_json.get('refresh_token')
                
                # Save the rotated refresh token
                if new_refresh_token and new_refresh_token != email_obj.refresh_token:
                    email_obj.refresh_token = new_refresh_token
                    email_obj.save()
                    
                # Fetch messages
                msg_url = "https://graph.microsoft.com/v1.0/me/messages?$top=15"
                msg_res = requests.get(msg_url, headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }, timeout=10)
                
                if msg_res.status_code == 200:
                    emails_list = msg_res.json().get('value', [])
                    parsed_emails = [parse_graph_message(m) for m in emails_list]
                    if parsed_emails:
                        update_email_latest_stats(email_obj, parsed_emails[0])
                    return {'success': True, 'emails': parsed_emails}
                else:
                    return {'success': False, 'message': f'Lỗi Graph API: {msg_res.text}'}
            else:
                try:
                    err_msg = res.json().get("error_description", res.text)
                except Exception:
                    err_msg = res.text
                return {'success': False, 'message': f'Lỗi OAuth Refresh: {err_msg}'}
        except Exception as e:
            return {'success': False, 'message': f'Lỗi kết nối OAuth Refresh: {str(e)}'}

    else:
        # ROPC or Client Credentials
        if config_flow == 'client_credentials':
            if not config_client_id or not config_client_secret:
                return {'success': False, 'message': 'Thiếu Client ID/Secret trong cấu hình App-only.'}
            try:
                token_url = f"https://login.microsoftonline.com/{config_tenant_id}/oauth2/v2.0/token"
                res = requests.post(token_url, data={
                    'grant_type': 'client_credentials',
                    'client_id': config_client_id,
                    'client_secret': config_client_secret,
                    'scope': 'https://graph.microsoft.com/.default'
                }, timeout=10)
                if res.status_code == 200:
                    app_token = res.json().get('access_token')
                    msg_url = f"https://graph.microsoft.com/v1.0/users/{email_addr}/messages?$top=15"
                    msg_res = requests.get(msg_url, headers={
                        'Authorization': f'Bearer {app_token}',
                        'Accept': 'application/json'
                    }, timeout=10)
                    
                    if msg_res.status_code == 200:
                        emails_list = msg_res.json().get('value', [])
                        parsed_emails = [parse_graph_message(m) for m in emails_list]
                        if parsed_emails:
                            update_email_latest_stats(email_obj, parsed_emails[0])
                        return {'success': True, 'emails': parsed_emails}
                    else:
                        return {'success': False, 'message': f'Lỗi Graph API: {msg_res.text}'}
                else:
                    return {'success': False, 'message': f'Lỗi lấy App Token: {res.text}'}
            except Exception as e:
                return {'success': False, 'message': f'Lỗi kết nối Graph API (App): {str(e)}'}

        else:
            if not target_client_id:
                return {'success': False, 'message': 'Thiếu Client ID cho ROPC.'}
            if not password:
                return {'success': False, 'message': 'Mật khẩu email trống.'}
            try:
                token_url = f"https://login.microsoftonline.com/{config_tenant_id}/oauth2/v2.0/token"
                payload = {
                    'grant_type': 'password',
                    'client_id': target_client_id,
                    'username': email_addr,
                    'password': password,
                    'scope': 'https://graph.microsoft.com/Mail.Read'
                }
                if config_client_secret:
                    payload['client_secret'] = config_client_secret
                res = requests.post(token_url, data=payload, timeout=10)
                if res.status_code == 200:
                    user_token = res.json().get('access_token')
                    msg_url = "https://graph.microsoft.com/v1.0/me/messages?$top=15"
                    msg_res = requests.get(msg_url, headers={
                        'Authorization': f'Bearer {user_token}',
                        'Accept': 'application/json'
                    }, timeout=10)
                    if msg_res.status_code == 200:
                        emails_list = msg_res.json().get('value', [])
                        parsed_emails = [parse_graph_message(m) for m in emails_list]
                        if parsed_emails:
                            update_email_latest_stats(email_obj, parsed_emails[0])
                        return {'success': True, 'emails': parsed_emails}
                    else:
                        return {'success': False, 'message': f'Lỗi Graph API: {msg_res.text}'}
                else:
                    try:
                        err_msg = res.json().get("error_description", res.text)
                    except Exception:
                        err_msg = res.text
                    return {'success': False, 'message': f'Lỗi ROPC: {err_msg}'}
            except Exception as e:
                return {'success': False, 'message': f'Lỗi kết nối ROPC: {str(e)}'}


def get_config(key, default=""):
    try:
        from system_configure.models import SystemConfig
        obj = SystemConfig.objects.filter(key=key).first()
        return obj.value if obj else default
    except Exception:
        return default


def set_config(key, value, description=""):
    try:
        from system_configure.models import SystemConfig
        SystemConfig.objects.update_or_create(key=key, defaults={'value': value, 'description': description})
        return True
    except Exception:
        return False


def parse_graph_message(m):
    from_dict = m.get('from', {}) or m.get('sender', {}) or {}
    email_addr = from_dict.get('emailAddress', {}) or {}
    from_name = email_addr.get('name', '')
    from_email = email_addr.get('address', '')
    from_sender = f"{from_name} <{from_email}>" if from_name else from_email

    subject = m.get('subject') or '(Không có tiêu đề)'
    received_time = m.get('receivedDateTime', '')
    
    date_str = received_time
    if 'T' in received_time and 'Z' in received_time:
        try:
            dt = received_time.replace('Z', '').split('.')[0]
            parts = dt.split('T')
            date_str = f"{parts[0]} {parts[1]}"
        except Exception:
            pass

    body_dict = m.get('body', {}) or {}
    body_content = body_dict.get('content', '')
    
    snippet = m.get('bodyPreview', '')
    if not snippet and body_content:
        import re
        clean_body = body_content.strip()
        if "<html" in clean_body.lower() or "<body" in clean_body.lower() or "<div" in clean_body.lower():
            clean_body = re.sub('<[^<]+?>', '', clean_body)
            clean_body = clean_body.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
        clean_body = re.sub(r'\s+', ' ', clean_body).strip()
        snippet = clean_body[:200] + ("..." if len(clean_body) > 200 else "")

    return {
        'from': from_sender,
        'subject': subject,
        'date': date_str,
        'snippet': snippet,
        'body': body_content
    }


class AccountsCreatedViewSet(viewsets.ModelViewSet):
    serializer_class = AccountsCreatedSerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'type']

    def get_serializer_class(self):
        if self.action == 'list':
            return AccountsCreatedListSerializer
        return AccountsCreatedSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            qs = AccountsCreated.objects.all()
        else:
            from django.db.models import Q
            qs = AccountsCreated.objects.filter(
                Q(owner=user) | Q(created_by=user) | Q(subscription_owner=user.username)
            )
        
        type_param = self.request.query_params.get('type')
        if type_param:
            qs = qs.filter(type__value=type_param.lower())
            
        created_by_param = self.request.query_params.get('created_by')
        if not created_by_param and hasattr(self.request, 'data') and isinstance(self.request.data, dict):
            created_by_param = self.request.data.get('created_by')
        if created_by_param:
            qs = qs.filter(created_by__username=created_by_param)
            
        return qs.select_related('owner', 'created_by', 'customer', 'type', 'browser_profiles', 'modified_by').order_by('-id')

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
        deleted_count, _ = self.get_queryset().filter(pk__in=ids).delete()
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
        
        updated_count = self.get_queryset().filter(pk__in=ids).update(status=status_int)
        return Response({'success': True, 'message': f'Đã cập nhật trạng thái cho {updated_count} tài khoản!'})

    @action(detail=False, methods=['get'], url_path='users-list')
    def users_list(self, request):
        users = User.objects.filter(is_active=True).order_by('username')
        user_data = [{'id': u.id, 'username': u.username} for u in users]
        return Response(user_data)

    @action(detail=True, methods=['get'], url_path='get-2fa')
    def get_2fa_code(self, request, pk=None):
        instance = self.get_object()
        secret = (instance.two_factor_auth or '').strip()
        if not secret:
            return Response({'success': False, 'message': 'Tài khoản không có cấu hình 2FA Secret Key.'}, status=400)
        
        import urllib.request
        import json
        
        secret_clean = secret.replace(' ', '')
        try:
            url = f"https://2fa.live/tok/{secret_clean}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = response.read().decode('utf-8')
                res_json = json.loads(res_data)
                token = res_json.get('token')
                if token:
                    return Response({'success': True, 'token': token})
                else:
                    return Response({'success': False, 'message': 'Không thể lấy mã code từ API. Phản hồi không đúng định dạng.'}, status=500)
        except Exception as e:
            return Response({'success': False, 'message': f'Lỗi khi lấy mã code: {str(e)}'}, status=500)

    @action(detail=False, methods=['post'], url_path='bulk-sub-owner')
    def bulk_sub_owner(self, request):
        ids = request.data.get('ids', [])
        sub_owner = request.data.get('subscription_owner')
        if not isinstance(ids, list):
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.'}, status=400)
        
        sub_owner_str = (sub_owner or '').strip()
        updated_count = self.get_queryset().filter(pk__in=ids).update(subscription_owner=sub_owner_str)
        return Response({'success': True, 'message': f'Đã gán sở hữu sub cho {updated_count} tài khoản!'})


class UserHwidViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for managing UserHwid — controls which machines can use MunLogin tool."""
    serializer_class = UserHwidSerializer
    pagination_class = StandardResultsSetPagination
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
