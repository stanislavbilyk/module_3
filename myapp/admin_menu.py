from django.urls import path
from myapp.views import AdminMenuListView, AddNewProduct, RefundListView, RefundAcceptView, RefundDeclineView, ProductUpdate


urlpatterns = [
    path('', AdminMenuListView.as_view(), name='admin_menu'),
    path('add_new_product/', AddNewProduct.as_view(), name='add_new_product'),
    path('view_refunds', RefundListView.as_view(), name='view_refunds'),
    path('refund_accept', RefundAcceptView.as_view(), name='refund_accept'),
    path('refund_decline', RefundDeclineView.as_view(), name='refund_decline'),
    path('product_update_form/<int:pk>/', ProductUpdate.as_view(), name='product_update'),
]