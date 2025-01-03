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
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

from myapp.views import Login, Register, Logout, ProfileView, PloductListView, ProductView, RefundListView, PurchaseView, RefundView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', PloductListView.as_view(), name='main'),
    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', Logout.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('search/', views.search_products, name='search_products'),
    path('product/<int:pk>/', ProductView.as_view(), name='product_id'),
    path('purchase', PurchaseView.as_view(), name='purchase'),
    path('admin_menu/', include('myapp.admin_menu')),
    path('refund', RefundView.as_view(), name='refund')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
