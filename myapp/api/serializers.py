from django.shortcuts import get_object_or_404
from rest_framework import serializers
import time
from django.core.validators import MinValueValidator

from myapp.models import Product, CustomUser, Purchase, Refund


def greater_than_zero(value):
    if value < 0:
        raise serializers.ValidationError("Value must be greater than zero.")

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    wallet_balance = serializers.DecimalField(read_only=True, validators=[greater_than_zero], max_digits=10, decimal_places=2, default=10000.00)
    is_staff = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'wallet_balance', 'is_staff', 'is_active')

        def create(self, validated_data):
            user = CustomUser.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password']
            )
            return user


class ProductSerializer(serializers.ModelSerializer):
    quantity_on_storage = serializers.IntegerField(validators=[greater_than_zero])
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'image', 'quantity_on_storage')

class PurchaseSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), error_messages={"does_not_exist": "This product doesn't exist."})
    quantity_of_purchase = serializers.IntegerField(validators=[greater_than_zero])
    time_of_purchase = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Purchase
        fields = ('id', 'user', 'product', 'quantity_of_purchase', 'time_of_purchase')
    def validate(self, data):
        user = self.context['request'].user
        product = data['product']
        quantity = data['quantity_of_purchase']
        print(f'Purchased product: {product}')
        print(f'Quantity: {quantity}')
        if user.wallet_balance < product.price * quantity:
            raise serializers.ValidationError({"user": "Insufficient balance"})
        if product.quantity_on_storage < quantity:
            raise serializers.ValidationError({"product": "Not enough on storage"})
        return data



class RefundSerializer(serializers.ModelSerializer):
    purchase = serializers.PrimaryKeyRelatedField(queryset=Purchase.objects.all(), error_messages={"does_not_exist": "This purchase doesn't exist."})
    time_of_refund = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Refund
        fields = ('id', 'purchase', 'time_of_refund')
    def validate(self, data):
        purchase = data['purchase']

        if Refund.objects.filter(purchase=purchase).exists():
            raise serializers.ValidationError({"purchase": "This purchase already refunded"})

        time_of_purchase = purchase.time_of_purchase.timestamp()
        current_time = time.time()
        if current_time - time_of_purchase > 90:
            raise serializers.ValidationError({"time": "Sorry, but you can no longer return the product"})

        return data




