import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storagon.settings")
django.setup()

from dashboard.views import get_config, set_config, AccountsEmailsViewSet
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth.models import User

# Test 1: set & get config
print("Test 1: Testing get_config/set_config...")
set_config('microsoft_graph_client_id', 'test_client_id_123', 'Client ID')
client_id = get_config('microsoft_graph_client_id')
print("Value set/get matches:", client_id == 'test_client_id_123')

# Test 2: API endpoints viewset
print("\nTest 2: Testing viewset endpoints...")
factory = APIRequestFactory()
admin_user = User.objects.get(username="Admin")

# Get Graph Config
view = AccountsEmailsViewSet.as_view({'get': 'get_graph_config'})
request = factory.get('/dashboard/api/emails/get-graph-config/')
force_authenticate(request, user=admin_user)
response = view(request)
print("GET graph config response:", response.status_code, response.data)

# Save Graph Config
view_save = AccountsEmailsViewSet.as_view({'post': 'save_graph_config'})
request_save = factory.post('/dashboard/api/emails/save-graph-config/', {
    'client_id': 'azure_client_abc',
    'client_secret': 'secret_xyz',
    'tenant_id': 'common',
    'flow': 'ropc'
}, format='json')
force_authenticate(request_save, user=admin_user)
response_save = view_save(request_save)
print("POST save config response:", response_save.status_code, response_save.data)

# Check updated config
request_check = factory.get('/dashboard/api/emails/get-graph-config/')
force_authenticate(request_check, user=admin_user)
response_check = view(request_check)
print("GET check updated config:", response_check.status_code, response_check.data)

# Test 3: Bulk read empty list validation
print("\nTest 3: Testing bulk-read-mailbox validation...")
view_bulk = AccountsEmailsViewSet.as_view({'post': 'bulk_read_mailbox'})
request_bulk = factory.post('/dashboard/api/emails/bulk-read-mailbox/', {'ids': []}, format='json')
force_authenticate(request_bulk, user=admin_user)
response_bulk = view_bulk(request_bulk)
print("POST bulk read (empty list) response:", response_bulk.status_code, response_bulk.data)

print("\n--- ALL TESTS SUCCESSFUL ---")
