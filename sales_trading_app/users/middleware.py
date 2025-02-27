
from django.utils.deprecation import MiddlewareMixin
from .authentication import CookieJWTAuthentication

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        jwt_auth = CookieJWTAuthentication()
        auth_result = jwt_auth.authenticate(request)
        if auth_result:
            request.user, _ = auth_result