from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.Form):
    # BASIC USER DATA
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()

    # EXTRA DATA (Profile)
    phone = forms.CharField(max_length=15)
    id_number = forms.CharField(max_length=20)

    ID_CHOICES = [
        ('ID', 'ID'),
        ('Passport', 'Passport'),
    ]
    id_type = forms.ChoiceField(choices=ID_CHOICES)

    # PASSWORDS
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    # 🔐 VALIDATE EMAIL
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")

        return email

    # 🔐 VALIDATE PASSWORD MATCH
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data