from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseForbidden


class SuperUserPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return super().test_func() and self.request.user.is_superuser

    def handle_no_permission(self):
        return HttpResponseForbidden("Access denied: You must be a superuser to access this page.")
