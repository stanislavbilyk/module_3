from rest_framework.permissions import BasePermission

from myapp.models import Purchase


class RefundOnlyOwner(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            purchase_id = request.data.get("purchase")
            if not purchase_id:
                return False
            try:
                purchase = Purchase.objects.get(id=purchase_id)
            except Purchase.DoesNotExist:
                return False
            return purchase.user == request.user
        return True


    def has_object_permission(self, request, view, obj):
        return obj.purchase.user == request.user
