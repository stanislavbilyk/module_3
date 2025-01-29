from rest_framework import serializers
from django.core.validators import MinValueValidator

from online_store.myapp.models import Product, CustomUser, Purchase, Refund


def greater_than_zero(value):
    if value < 0:
        raise serializers.ValidationError("Value must be greater than zero.")
class CustomUserSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.BooleanField(read_only=True, validators=[greater_than_zero])
    is_staff = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'wallet_balance', 'is_staff', 'is_active', 'purchases')


class ProductSerializer(serializers.ModelSerializer):
    quantity_on_store = serializers.IntegerField(validators=[greater_than_zero])
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'image', 'quantity_on_storage')

class PurchaseSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    quantity_of_purchase = serializers.IntegerField(validators=[greater_than_zero])
    time_of_purchase = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Purchase
        fields = ('user', 'product', 'quantity_of_purchase', 'time_of_purchase')

class RefundSerializer(serializers.ModelSerializer):
    purchase = PurchaseSerializer(read_only=True)
    time_of_refund = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Refund
        fields = ('purchase', 'time_of_refund')


