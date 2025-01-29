import time

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, resolve_url, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.deprecation import MiddlewareMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView, FormView, TemplateView
from django.db import transaction
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from .forms import AuthenticationForm, UserCreationForm, ProductSearchForm, AddNewProductForm, ProductUpdateForm, \
    PurchaseCreateForm
from django.contrib.auth import login, logout
from django.views import View

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

class ProductView(DetailView):
    model = Product
    template_name = 'product_id.html'

class ProductUpdate(UpdateView):
    model = Product
    form_class = ProductUpdateForm
    template_name = 'product_update_form.html'
    success_url = '/'

   
class SearchProductsView(ListView):
    template_name = 'search_results.html'
    form_class = ProductSearchForm
    queryset = Product.objects.all()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query', '')
        if query:
            context['products'] = Product.objects.filter(name__icontains=query)
            context['products'] = Product.objects.filter(description__icontains=query)
        else:
            context['products'] = Product.objects.none()
        return context


class PurchaseView(DetailView):
    model = Product
    template_name = 'purchase.html'
    context_object_name = 'product'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quantity = self.request.GET.get('quantity', 1)  # Значение по умолчанию 1
        try:
            context['quantity'] = int(quantity)
        except ValueError:
            context['quantity'] = 1  # Если некорректный ввод, ставим 1
        return context


class CreatePurchaseView(CreateView):
    model = Purchase
    http_method_names = ['get', 'post']
    template_name = 'create_purchase.html'
    success_url = 'profile.html'
    form_class = PurchaseCreateForm

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        product_id = form.cleaned_data['product_id']
        quantity = form.cleaned_data['quantity_of_purchase']
        try:
            quantity = int(quantity)
            if quantity < 1:
                messages.error(self.request, 'Invalid quantity')
        except (TypeError, ValueError):
            messages.error(self.request, 'Invalid quantity format')

        user = self.object.user
        product = get_object_or_404(Product, id=product_id)

        if product.quantity_on_storage < quantity:
            messages.error(self.request, 'Not enough stock')
        if user.wallet_balance < product.price * quantity:
            messages.error(self.request, 'Insufficient balance')

        with transaction.atomic():
            product.quantity_on_storage -= quantity
            product.save()

            user.wallet_balance -= product.price * quantity
            user.save()

            purchase = form.save(commit=False)
            purchase.user = user
            purchase.product = product
            purchase.save()
        messages.success(self.request, f'You purchased {quantity} {product.name}')


        return redirect(self.get_success_url())



# class PurchaseView(View):
#     def post(self, request, *args, **kwargs):
#         product_id = request.POST.get('product_id')
#         quantity = request.POST.get('quantity')
#
#         try:
#             quantity = int(quantity)
#             if quantity < 1:
#                 return JsonResponse({'error': 'Invalid quantity'}, status=400)
#         except (TypeError, ValueError):
#             return JsonResponse({'error': 'Invalid quantity format'}, status=400)
#
#         user = request.user
#         product = get_object_or_404(Product, id=product_id)
#
#         if product.quantity_on_storage < quantity:
#             return JsonResponse({'error': 'Not enough stock'}, status=400)
#         if user.wallet_balance < product.price * quantity:
#             return JsonResponse({'error': 'Insufficient balance'}, status=400)
#
#         with transaction.atomic():
#             product.quantity_on_storage -= quantity
#             product.save()
#
#             user.wallet_balance -= product.price * quantity
#             user.save()
#
#             Purchase.objects.create(user=user, product=product, quantity_of_purchase=quantity)
#         return JsonResponse({'success': f'You purchased {quantity} {product.name}'}, status=200)


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


class RefundListView(UserPassesTestMixin, ListView):
    model = Refund
    template_name = 'view_refunds.html'
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied: You must be a superuser to access this page.")

class RefundAcceptView(UserPassesTestMixin, View):
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
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied: You must be a superuser to access this page.")


class RefundDeclineView(UserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        refund_id = request.POST.get('refund_id')
        refund = get_object_or_404(Refund, id=refund_id)

        refund.delete()
        return JsonResponse({'message': 'Refund declined successfully'}, status=200)
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied: You must be a superuser to access this page.")

class AdminMenuListView(UserPassesTestMixin, ListView):
    model = Product
    template_name = 'admin_menu.html'
    
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied: You must be a superuser to access this page.")

class AddNewProduct(UserPassesTestMixin, CreateView):
    model = Product
    template_name = 'add_new_product.html'
    form_class = AddNewProductForm
    success_url = '/'
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied: You must be a superuser to access this page.")









