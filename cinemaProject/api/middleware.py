from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.authtoken.models import Token


class AutoInvalidTokenMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith('/api/'):
            if "Authorization" in request.headers:
                try:
                    user_token = request.headers['Authorization'].split()[1]
                    token = Token.objects.get(key=user_token)
                    user = token.user
                except Exception as e:
                    return JsonResponse(data={"error": "Invalid Token"})
                if not user.is_staff:
                    last_request = user.last_request
                    if datetime.now() - last_request > timedelta(minutes=1):
                        logout(request)
                        token.delete()
                    else:
                        user.last_request = datetime.now()
                        user.save()
