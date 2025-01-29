from django.contrib.auth import authenticate
from django import forms

from .models import CustomUser, Product, Purchase


class AuthenticationForm(forms.Form):
    username = forms.CharField(max_length=254)
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput)
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            self.user = authenticate(username = username, password = password)
            if self.user is None:
                raise forms.ValidationError("Incorrect username/password")


class UserCreationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=("Enter the same password as above for verification."))
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name']
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ProductSearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label='Search', widget=forms.TextInput(attrs={'placeholder':'Search product...', 'class':'form-control'}))

class AddNewProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'quantity_on_storage']

class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'quantity_on_storage']

class PurchaseCreateForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ('product', 'quantity_of_purchase')


