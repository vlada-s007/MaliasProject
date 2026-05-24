from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User

from maliasStore.models import Customer, UserRating, CartItems, Delivery, Contact


class RegistrationForm(UserCreationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    password1 = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))

    password2 = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))

    newsletter = forms.BooleanField(widget=forms.CheckboxInput(attrs={
    }))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2', 'newsletter')


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))

    password = forms.CharField(min_length=3, widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))


class UserChangeForm(forms.ModelForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')


class CustomerAccountChangeForm(forms.ModelForm):
    phone = forms.CharField(required=False, widget=forms.TelInput(attrs={
        'class': 'form-control'
    }))

    street = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    home = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    flat = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    newsletter = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
    }))

    fax = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    note = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': "3"
    }))

    postal_code = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    company = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = Customer
        # fields = ('phone', 'region', 'city', 'street', 'newsletter', 'fax',
        #           'note', 'postal_code', 'company', 'home', 'flat')
        exclude = ('user',)
        widgets = {
            'region': forms.Select(
                attrs={'class': 'form-control'}),
            'city': forms.Select(
                attrs={'class': 'form-control'}),
        }

class DeliveryForm(forms.ModelForm):
    first_name = forms.CharField(required=False, widget=forms.TelInput(attrs={
        'class': 'form-control'
    }))

    last_name = forms.CharField(required=False, widget=forms.TelInput(attrs={
        'class': 'form-control'
    }))

    phone = forms.CharField(required=False, widget=forms.TelInput(attrs={
        'class': 'form-control'
    }))

    street = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    home = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    flat = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    comment_delivery = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': "8"
    }))

    comment_payment = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': "8"
    }))

    fax = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    postal_code = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    company = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    # online_payment = forms.BooleanField(required=False, widget=forms.RadioSelect)
    #
    # door_to_door = forms.BooleanField(required=False, widget=forms.RadioSelect)

    class Meta:
        model = Delivery
        exclude = ('customer', 'created_at', 'status')

        widgets = {
            'region': forms.Select(
                attrs={'class': 'form-control'}),
            'city': forms.Select(
                attrs={'class': 'form-control'}),
            'online_payment': forms.RadioSelect(),
            'door_to_door': forms.RadioSelect()
        }


class DeliveryEstimation(forms.Form):
    class Meta:
        widgets = {
            'region': forms.Select(
                attrs={'class': 'form-control'}),
            'city': forms.Select(
                attrs={'class': 'form-control'}),}

class ContactForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    phone = forms.CharField(widget=forms.TelInput(attrs={
        'class': 'form-control'
    }))

    text = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 10
    }))

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = Contact
        exclude = ('created_at',)


