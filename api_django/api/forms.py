import datetime
from datetime import datetime
from django import forms
from django.contrib.auth import password_validation, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.forms import CheckboxInput
from django.core.exceptions import ValidationError
from .models import *


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(help_text='A valid email address, please.', required=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        return user


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class ParseRequestForm(forms.ModelForm):
    year_start = forms.ChoiceField(
        label="Введите год начала периода отчета",
        widget=forms.Select(attrs={'class': 'my-dropdown'}),
        choices=[],
    )
    year_end = forms.ChoiceField(
        label="Введите год окончания периода отчета",
        widget=forms.Select(attrs={'class': 'my-dropdown'}),
        choices=[],
    )
    class Meta:
        model = Order
        fields = ['request', 'year_start', 'year_end', 'ktru_plots', 'customers_plots', 'regions_plots', 'mnn_plots',
                ]
        widgets = {
            'request': forms.TextInput(attrs={'class': 'big_text'}),
            'year_start': forms.Select(attrs={'class': 'my-dropdown'}),
            'year_end': forms.Select(attrs={'class': 'my-dropdown'}),
            'ktru_plots': CheckboxInput(attrs={'class': 'required checkbox form-control'}),
            'customers_plots': CheckboxInput(attrs={'class': 'required checkbox form-control'}),
            'regions_plots': CheckboxInput(attrs={'class': 'required checkbox form-control'}),
            'mnn_plots': CheckboxInput(attrs={'class': 'required checkbox form-control'}),\
        }

    def clean(self):
        cleaned_data = super().clean()
        request = cleaned_data.get('request')
        # year_start = cleaned_data.get('year_start')
        # year_end = cleaned_data.get('year_end')
        if len(request) < 5:
            raise ValidationError("Вы ввели слишком короткий запрос, мы боимся, что это может негативно сказаться на "
                                  "работе нашей системы. Попробуйте уточнить запрос или свяжитесь с нами перейдя по "
                                  "вкладке Обратная связь")
        else:
            return cleaned_data



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Генерация выборов для поля "year_start" от 2010 до текущего года
        current_year = datetime.now().year
        year_start_choices = [(year, year) for year in range(2010, current_year + 1)]
        self.fields['year_start'].choices = year_start_choices

        # Проверка значения "year_start" и генерация выборов для поля "year_end"
        year_start_value = self.data.get('year_start') or self.initial.get('year_start') or self.instance.year_start
        if year_start_value:
            year_end_choices = [(year, year) for year in range(int(year_start_value), current_year + 1)]
        else:
            year_end_choices = []
        self.fields['year_end'].choices = year_end_choices

        self.fields['request'].help_text = 'Введите поисковый запрос по которому будет производиться поиск закупок на сайте zakupki.gov.ru. Если интересующих вас продукт может содержать в названии различные комбинации слов, то разделите их ; Рекомедуется вводить слова без окончаний, если окончание не является значимым Пример: Тест полос глюкоз; набор глюкоз ИВД.'
        self.fields['year_start'].help_text = 'Не раньше 2010'
        self.fields['year_end'].help_text = 'Не позже нынешнего года'
        self.fields['ktru_plots'].help_text = 'Доступен только КТРУ для медицинских изделий'
        self.fields['customers_plots'].help_text = 'В отчете будут построены диаграммы отображающие объемы закупок РФ/Импорт для этих учреждений.'
        # self.fields['regions_plots'].help_text = 'Подсказка для поля 1'
        self.fields['mnn_plots'].help_text = 'Рекомендуется, если вас интересуют лекарственные препараты'
        # self.fields['parse_data'].help_text = 'Подсказка для поля 1'


class ContactUsForm(forms.ModelForm):
    content = forms.CharField(max_length=255)


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']


class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

        self.fields['new_captcha_name'] = ReCaptchaField(
            widget=ReCaptchaV2Checkbox(attrs={'placeholder': 'Введите капчу'}),
            label='Докажите что вы не робот',
    )


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label='Почта')

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']