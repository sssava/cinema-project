from datetime import datetime
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def update_session_on_login(sender, user, request, **kwargs):
    last_activity = datetime.now().isoformat()
    print(last_activity)
    request.session['last_activity'] = last_activity
