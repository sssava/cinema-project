from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class StaffRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('no-permission')
        return super().dispatch(request, *args, **kwargs)
