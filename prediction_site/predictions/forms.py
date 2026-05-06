from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta: #внутр класс с настройками
        model = UserProfile
        fields = ['bio', 'birth_date', 'avatar', 'favorite_category']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }