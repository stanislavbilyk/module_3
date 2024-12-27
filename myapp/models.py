from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, username, first_name, last_name, wallet_balance = 10000.00, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username (Email) must be set")
        if wallet_balance is None:
            wallet_balance = 10000.00
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, first_name=first_name, last_name=last_name, wallet_balance=wallet_balance, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            wallet_balance=0.00,
            password=password,
            **extra_fields
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.username


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    quantity_on_storage = models.IntegerField(validators=[MinValueValidator(0)])

class Purchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='purchases', null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='products', null=True)
    quantity_of_purchase = models.IntegerField(validators=[MinValueValidator(0)])
    time_of_purchase = models.DateTimeField(auto_now_add=True)

class Refund(models.Model):
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, related_name='refund', null=True)
    time_of_refund = models.DateTimeField(auto_now_add=True)

