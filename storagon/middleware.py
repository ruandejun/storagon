from storagon.utils import set_current_user, remove_current_user
from rest_framework.decorators import api_view
@api_view(['GET', 'POST', 'PUT'])
class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):

        set_current_user(getattr(request, 'user', None))

        response = self.get_response(request)

        remove_current_user()
        # Code to be executed for each request/response after
        # the view is called.

        return response
