from django import forms
from .models import UserProfile
from datetime import date

class UserProfileForm(forms.ModelForm):
    class Meta: #внутр класс с настройками
        model = UserProfile
        fields = ['bio', 'birth_date', 'avatar', 'favorite_category']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')

        if birth_date:
            today = date.today()
            age = today.year - birth_date.year

            if today.month < birth_date.month or (
                    today.month == birth_date.month and today.day < birth_date.day
            ):
                age -= 1

            if age < 13:
                raise forms.ValidationError(
                    'Минимальный возраст для регистрации — 13 лет. '
                    f'Вам {age} лет, извините!'
                )

            if age > 120:
                raise forms.ValidationError(
                    'Проверьте дату рождения. Возраст не может быть больше 120 лет.'
                )

        return birth_date
