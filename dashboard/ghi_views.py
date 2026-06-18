import random
import string
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import QuickNote

def generate_random_note_id(length=6):
    chars = string.ascii_lowercase + string.digits
    while True:
        note_id = ''.join(random.choice(chars) for _ in range(length))
        if not QuickNote.objects.filter(note_id=note_id).exists():
            return note_id

def ghi_redirect(request):
    note_id = generate_random_note_id()
    return redirect(f'/{note_id}/')

@ensure_csrf_cookie
def ghi_editor(request, note_id):
    # Ensure note_id is alphanumeric
    if not note_id.isalnum():
        raise Http404("Đường dẫn ghi chú không hợp lệ")

    note, created = QuickNote.objects.get_or_create(note_id=note_id)

    # Check if password-protected
    if note.password:
        session_key = f'note_verified_{note_id}'
        if not request.session.get(session_key):
            return render(request, 'dashboard/ghi_password.html', {'note_id': note_id})

    return render(request, 'dashboard/ghi.html', {
        'note': note,
        'has_password': bool(note.password)
    })

def ghi_get_api(request, note_id):
    try:
        note = QuickNote.objects.get(note_id=note_id)
    except QuickNote.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Ghi chú không tồn tại'}, status=404)

    if note.password:
        session_key = f'note_verified_{note_id}'
        if not request.session.get(session_key):
            return JsonResponse({'success': False, 'message': 'Yêu cầu mật khẩu', 'password_required': True}, status=403)

    return JsonResponse({
        'success': True,
        'content': note.content,
        'has_password': bool(note.password),
        'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    })

def ghi_save_api(request, note_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Chỉ chấp nhận phương thức POST'}, status=405)

    try:
        note = QuickNote.objects.get(note_id=note_id)
    except QuickNote.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Ghi chú không tồn tại'}, status=404)

    # Validate note access permissions
    if note.password:
        session_key = f'note_verified_{note_id}'
        if not request.session.get(session_key):
            return JsonResponse({'success': False, 'message': 'Quyền truy cập bị từ chối'}, status=403)

    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Dữ liệu JSON không hợp lệ'}, status=400)

    # Save content if provided
    if 'content' in data:
        note.content = data['content']

    # Update or remove password
    if 'set_password' in data:
        pwd = data['set_password']
        if pwd:
            note.password = make_password(pwd)
            # Mark verified in current session
            request.session[f'note_verified_{note_id}'] = True
        else:
            note.password = None
            if f'note_verified_{note_id}' in request.session:
                del request.session[f'note_verified_{note_id}']

    note.save()
    return JsonResponse({
        'success': True,
        'has_password': bool(note.password),
        'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    })

def ghi_verify_password(request, note_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Chỉ chấp nhận phương thức POST'}, status=405)

    try:
        note = QuickNote.objects.get(note_id=note_id)
    except QuickNote.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Ghi chú không tồn tại'}, status=404)

    try:
        data = json.loads(request.body)
        password = data.get('password', '')
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Dữ liệu JSON không hợp lệ'}, status=400)

    if not note.password:
        return JsonResponse({'success': True, 'message': 'Ghi chú không có mật khẩu'})

    if check_password(password, note.password):
        request.session[f'note_verified_{note_id}'] = True
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Mật khẩu không chính xác'}, status=400)
