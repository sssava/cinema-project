from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                last_activity = request.session.get('last_activity')
                last_activity_from_iso = datetime.fromisoformat(last_activity)
                if last_activity_from_iso and datetime.now() - last_activity_from_iso > timedelta(seconds=10):
                    logout(request)
                    return redirect('/login/')
                else:
                    current_time_iso = datetime.now().isoformat()
                    request.session['last_activity'] = current_time_iso
