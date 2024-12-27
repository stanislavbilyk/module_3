from django.urls import path
from myapp.views import AdminMenuListView, AddNewProduct, RefundListView


urlpatterns = [
    path('', AdminMenuListView.as_view(), name='admin_menu'),
    path('add_new_product/', AddNewProduct.as_view(), name='add_new_product'),
    path('view_refunds', RefundListView.as_view(), name='view_refunds'),
]