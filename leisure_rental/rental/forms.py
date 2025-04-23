from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Equipment, Rental, User
from django.contrib.auth import get_user_model



# --------- Rental Form ---------
class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['equipment', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available equipment in dropdown
        self.fields['equipment'].queryset = self.fields['equipment'].queryset.filter(available=True)


# --------- Equipment Form (Admin) ---------
class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'type', 'daily_rate', 'available', 'condition', 'image']


# --------- Custom Signup Form ---------
User = get_user_model()  # Ensures correct custom model is used

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'CUSTOMER'  # Assign default role
        if commit:
            user.save()
        return user
