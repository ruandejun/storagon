from storagon.utils import set_current_user, remove_current_user
from re import sub
from rest_framework.authtoken.models import Token

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        header_token = request.META.get('HTTP_AUTHORIZATION', None)
        if header_token is not None:
            try:
                token = sub('Token ', '', request.META.get('HTTP_AUTHORIZATION', None))
                token_obj = Token.objects.get(key=token)
                request.user = token_obj.user
            except Token.DoesNotExist:
                pass
        set_current_user(getattr(request, 'user', None))

        response = self.get_response(request)

        remove_current_user()
        # Code to be executed for each request/response after
        # the view is called.

        return response
