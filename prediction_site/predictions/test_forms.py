# Проверяем регистрацию и валидацию пользователей
import pytest
from users.forms import CustomUserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


# ТЕСТЫ ДЛЯ ФОРМЫ РЕГИСТРАЦИИ CUSTOMUSERCREATIONFORM

@pytest.mark.django_db
class TestCustomUserCreationForm:
    def test_valid_registration_form(self):
        """
        Тест: регистрация с валидными данными
        Проверяет: форма принимает правильные данные
        """
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',  # пароль повторён правильно
        }
        form = CustomUserCreationForm(data=form_data)

        # Форма должна быть валидной
        assert form.is_valid() == True

    def test_passwords_mismatch(self):
        """
        Тест: пароли не совпадают
        Проверяет: форма возвращает ошибку, если password1 != password2
        """
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass456!',  # не совпадает с password1
        }
        form = CustomUserCreationForm(data=form_data)

        # Форма должна быть НЕ валидной
        assert form.is_valid() == False
        # В ошибках должно быть поле password2
        assert 'password2' in form.errors

    def test_duplicate_username(self, user):
        """
        Тест: имя пользователя уже существует
        Проверяет: форма не позволяет создать пользователя с существующим username
        """
        # user уже создан фикстурой с username='testuser'
        form_data = {
            'username': user.username,  # username уже существует!
            'email': 'another@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        form = CustomUserCreationForm(data=form_data)

        # Форма должна быть НЕвалидной
        assert form.is_valid() == False
        # В ошибках должно быть поле username
        assert 'username' in form.errors

    def test_blank_username(self):
        """
        Тест: пустое имя пользователя
        Проверяет: форма не допускает пустой username
        """
        form_data = {
            'username': '',  # пустое имя
            'email': 'test@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        form = CustomUserCreationForm(data=form_data)

        # Форма должна быть НЕвалидной
        assert form.is_valid() == False
        # В ошибках должно быть поле username
        assert 'username' in form.errors

    def test_invalid_email(self):
        """
        Тест: неправильный формат email
        Проверяет: форма проверяет корректность email
        """
        form_data = {
            'username': 'newuser',
            'email': 'not-an-email',  # неправильный email
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        form = CustomUserCreationForm(data=form_data)

        # Форма должна быть НЕвалидной
        assert form.is_valid() == False
        # В ошибках должно быть поле email
        assert 'email' in form.errors

    def test_too_short_password(self):
        """
        Тест: слишком короткий пароль
        Проверяет: форма проверяет минимальную длину пароля
        """
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': '123',  # слишком короткий пароль
            'password2': '123',
        }
        form = CustomUserCreationForm(data=form_data)

        # Форма должна быть НЕвалидной
        assert form.is_valid() == False
        # В ошибках должно быть поле password2 (или password1)
        assert 'password2' in form.errors or 'password1' in form.errors

    def test_form_creates_user_when_valid(self):
        """
        Тест: при валидной форме пользователь создаётся
        Проверяет: form.save() действительно сохраняет пользователя в БД
        """
        form_data = {
            'username': 'brandnewuser',
            'email': 'brandnew@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        form = CustomUserCreationForm(data=form_data)

        # Проверяем, что форма валидна
        assert form.is_valid() == True

        # Сохраняем пользователя
        user = form.save()

        # Проверяем, что пользователь появился в базе
        assert User.objects.filter(username='brandnewuser').exists() == True
        assert user.email == 'brandnew@example.com'

