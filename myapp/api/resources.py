import time

from django.db import transaction
from rest_framework import viewsets

from myapp.api.permissions import RefundOnlyOwner
from myapp.api.serializers import ProductSerializer, PurchaseSerializer, RefundSerializer
from myapp.models import CustomUser, Product, Purchase, Refund
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
# from myapp.api.permissions import DeleteOnlyAdmin

from myapp.api.serializers import CustomUserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


class RegisterAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny, ]


class ProfileViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch']
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]




class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    http_method_names = ['get', 'post']
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity_of_purchase"]

        with transaction.atomic():
            product.quantity_on_storage -= quantity
            product.save()
            user.wallet_balance -= product.price * quantity
            user.save()

        serializer.save(user=user, product=product)


    def list(self, request, *args, **kwargs):
        queryset = Purchase.objects.all().filter(user=self.request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class BaseRefundViewSet(viewsets.ModelViewSet):
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer

class RefundViewSet(BaseRefundViewSet):
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated, RefundOnlyOwner]

    def list(self, request, *args, **kwargs):
        queryset = Refund.objects.filter(purchase__user=self.request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        purchase = serializer.validated_data["purchase"]

        serializer.save(purchase=purchase)

class RefundAcceptViewSet(viewsets.ModelViewSet):
    queryset = Refund.objects.all()
    http_method_names = ['delete']
    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated] #issuperuser
    def destroy(self, request, *args, **kwargs):
        refund = self.request("refund")


class RefundListViewSet(BaseRefundViewSet):
    http_method_names = ['get']
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)