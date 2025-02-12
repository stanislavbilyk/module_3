"""
URL configuration for online_store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from myapp.views import Login, Register, Logout, ProfileView, ProductListView, ProductView, RefundListView, RefundView, CreatePurchaseView
from rest_framework.authtoken.views import obtain_auth_token
from myapp.api.resources import RegisterAPIView, ProductViewSet, PurchaseViewSet, ProfileViewSet, RefundViewSet, RefundListViewSet
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'purchase', PurchaseViewSet)
router.register(r'profile', ProfileViewSet)
router.register(r'refund', RefundViewSet, basename='refunds')
router.register(r'refund_list', RefundListViewSet, basename='refund-list')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ProductListView.as_view(), name='main'),
    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', Logout.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    # path('search/', SearchProductsView.as_view(), name='search_products'),
    path('product/<int:pk>/', ProductView.as_view(), name='product_id'),
    # path('purchase/<int:pk>/', PurchaseView.as_view(), name='purchase'),
    path('create_purchase/<int:pk>/', CreatePurchaseView.as_view(), name = 'purchase'),
    path('admin_menu/', include('myapp.admin_menu')),
    path('refund', RefundView.as_view(), name='refund'),
    path('api/register/', RegisterAPIView.as_view()),
    path('api/token/', obtain_auth_token),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
