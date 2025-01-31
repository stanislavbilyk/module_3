import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import UserCreationForm, AddNewProductForm, ProductUpdateForm, \
    PurchaseCreateForm
from .mixins import SuperUserPassesTestMixin
from .models import Product, CustomUser, Purchase, Refund


class Login(LoginView):
    next_page = 'profile'
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy(self.next_page)


class Register(CreateView):
    form_class = UserCreationForm
    template_name = 'register.html'
    success_url = '/profile/'


class Logout(LoginRequiredMixin, LogoutView):
    next_page = '/'
    login_url = 'login/'


class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    login_url = '/login/'
    template_name = 'profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchases'] = self.request.user.purchases.all()
        return context


class ProductListView(ListView):
    model = Product
    template_name = 'main.html'
    extra_context = {"purchase_form": PurchaseCreateForm(initial={'quantity_of_purchase': 1})}

    def get_queryset(self):
        query = self.request.GET.get('query', '')
        query_param = Q()
        if query:
            query_param = Q(name__icontains=query) | Q(description__icontains=query)
        return Product.objects.filter(query_param)


class ProductView(DetailView):
    model = Product
    template_name = 'product_id.html'


class ProductUpdate(UpdateView):
    model = Product
    form_class = ProductUpdateForm
    template_name = 'product_update_form.html'
    success_url = '/'


class CreatePurchaseView(SuccessMessageMixin, CreateView):
    model = Purchase
    http_method_names = ['post']
    form_class = PurchaseCreateForm
    success_url = reverse_lazy('main')
    success_message = "Purchase was created successfully"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['product'] = self.get_product()
        return kwargs

    def get_product(self):
        return get_object_or_404(Product, id=self.kwargs['pk'])

    def form_valid(self, form):
        product = self.get_product()
        quantity = form.cleaned_data['quantity_of_purchase']
        user = self.request.user
        product.quantity_on_storage -= quantity
        user.wallet_balance -= product.price * quantity
        with transaction.atomic():
            product.save()
            user.save()
            purchase = form.save(commit=False)
            purchase.user = user
            purchase.product = product
            purchase.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect(reverse_lazy('main'))



class RefundView(View):
    def post(self, request, *args, **kwargs):
        purchase_id = request.POST.get('purchase_id')

        try:
            purchase_id = int(purchase_id)
            purchase = Purchase.objects.get(id=purchase_id)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid purchase_id format'}, status=400)
        except Purchase.DoesNotExist:
            return JsonResponse({'error': 'Purchase not found'}, status=404)

        time_of_purchase = request.POST.get('purchase_time_of_purchase')
        if not time_of_purchase:
            return JsonResponse({'error': 'Missing time_of_purchase'}, status=400)

        try:
            time_of_purchase = float(time_of_purchase)
        except ValueError:
            return JsonResponse({'error': 'Invalid time_of_purchase'}, status=400)

        current_time = time.time()
        if current_time - time_of_purchase < 90:
            Refund.objects.create(purchase=purchase)
            return JsonResponse({'success': 'Refund processed'}, status=200)
        else:
            return JsonResponse({'error': 'Sorry, but you can no longer return the product'}, status=400)


class RefundListView(SuperUserPassesTestMixin, ListView):
    model = Refund
    template_name = 'view_refunds.html'


class RefundAcceptView(SuperUserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        refund_id = request.POST.get('refund_id')
        refund = get_object_or_404(Refund, id=refund_id)
        purchase = refund.purchase

        with transaction.atomic():
            product = purchase.product
            product.quantity_on_storage += purchase.quantity_of_purchase
            product.save()

            user = purchase.user
            user.wallet_balance += product.price * purchase.quantity_of_purchase
            user.save()

            refund.delete()
            purchase.delete()
        return JsonResponse({'message': 'Refund accepted successfully'}, status=200)


class RefundDeclineView(SuperUserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        refund_id = request.POST.get('refund_id')
        refund = get_object_or_404(Refund, id=refund_id)

        refund.delete()
        return JsonResponse({'message': 'Refund declined successfully'}, status=200)


class AdminMenuListView(SuperUserPassesTestMixin, ListView):
    model = Product
    template_name = 'admin_menu.html'


class AddNewProduct(SuperUserPassesTestMixin, CreateView):
    model = Product
    template_name = 'add_new_product.html'
    form_class = AddNewProductForm
    success_url = '/'
