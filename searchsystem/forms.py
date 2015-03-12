from .models import Account
from django import forms

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Account
        fields = ('username', 'email', 'password')