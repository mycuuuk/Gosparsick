from django.contrib.auth import logout, login, get_user_model
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, viewsets
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .llm_query_expander import expand_request_with_llm
from api.templatetags.menu_content import menu
from .decorators import user_not_authenticated, login_required
from .forms import *
# from .serializers import UserSerializer
from .utils import DataMixin
from django.db.models.query_utils import Q
from django.http import JsonResponse


def ping(request):
    return JsonResponse({'status': 'ok'})


def categories(request):
    return HttpResponse("<h1>Статьи по категориям</h1>")


@user_not_authenticated
def register(request):
    title = "Регистрация"
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            messages.success(request, f'Аккаунт <b>{user}</b> успешно создан. Можете войти.')
            return redirect('login')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserRegistrationForm()

    return render(
        request=request,
        template_name="user/register.html",
        context={"form": form, "menu": menu, "title": title}
        )

def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("user/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    try:
        if email.send():
            messages.success(request, f'Уважаемый(ая) <b>{user}</b>, письмо с ссылкой для активации отправлено на <b>{to_email}</b>. Проверьте папку «Спам» если письмо не пришло.')
        else:
            messages.error(request, f'Не удалось отправить письмо на {to_email}. Проверьте правильность адреса.')
    except Exception as e:
        messages.error(request, f'Ошибка отправки письма: {e}. Обратитесь к администратору.')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Регистрация")
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('home')

class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'user/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('my_orders')

class FakeLoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'user/fake_login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        return dict(list(context.items()) + list(c_def.items()))

def about(request):
    return render(request=request,
                  template_name= 'user/about.html',
                  context={"menu": menu})
def contact(request):
    return render(request=request,
                  template_name= 'user/contacts.html',
                  context={"menu": menu})

def UserHome(request):
    return render(request=request,
                  template_name= 'user/index.html',
                  context={"menu": menu})

def logout_user(request):
    logout(request)
    return redirect('home')


@login_required
def ParseUser(request):
    if request.user.payed_orders > 0:
        if request.method == 'POST':
            form = ParseRequestForm(request.POST)
            if form.is_valid():
                # try:
                    raw_request = form.cleaned_data.get("request", "")
                    expanded_request = expand_request_with_llm(raw_request)
                    form.instance.request = expanded_request
                    form.instance.username = request.user.username
                    form.instance.email = request.user.email
                    form.instance.parse_data = 1
                    form.save()
                    counter = CustomUser.objects.get(id=request.user.id)
                    counter.payed_orders -= 1
                    counter.save()
                    return redirect('my_orders')
                # except:
                    # form.add_error(None, 'Ошибка добавления запроса, пожалуйста проверьте введенные данные или обратитесь к разработчикам!')
        else:
            form = ParseRequestForm()
        return render(request=request,
                      template_name= 'user/parse.html',
                      context={'form': form, "menu": menu, 'title': 'Добавление запроса'})
    else:
        messages.info(request, "Недостаточно доступных заказов для нового запроса.")
        return redirect('my_orders')



def ContactUs(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            try:
                form.instance.UserName = request.user.username
                form.save()
                print(123)
                return redirect('home')
            except:
                form.add_error(None, 'Ошибка добавления поста')

    else:
        form = ParseRequestForm()
    return render(request, 'user/index.html', {'form': form})



def email(request):
    send_mail(
        'Subject here',
        'Here is the message.',
        'from@example.com',
        [request.user.email],
        fail_silently=False,)
    return render(request, 'user/email.html')


def profile(request, username):
    title = "Мой профиль"
    if request.method == "POST":
        user = request.user
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save()
            messages.success(request, f'{user_form.username}, Your profile has been updated!')
            return redirect("profile", user_form.username)

        for error in list(form.errors.values()):
            messages.error(request, error)

    user = get_user_model().objects.filter(username=username).first()
    if user:
        form = UserUpdateForm(instance=user)
        payed_orders = request.user.payed_orders
        return render(
            request=request,
            template_name="user/profile.html",
            context={"form": form, 'payed_orders': payed_orders, "title": title}
        )

    return redirect("home")


@login_required
def password_change(request):
    title = "Смена пароля"
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return render(request, 'user/password_reset_confirm.html', {'form': form, "title": title})


@user_not_authenticated
def password_reset_request(request):
    title = "Восстановление пароля"
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("user/template_reset_password.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                        """
                        <h2>Password reset sent</h2><hr>
                        <p>
                            We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                            You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address 
                            you registered with, and check your spam folder.
                        </p>
                        """
                    )
                else:
                    messages.error(request, "Problem sending reset password email, <b>SERVER PROBLEM</b>")

            return redirect('home')

        for key, error in list(form.errors.items()):
            if key == 'captcha' and error[0] == 'This field is required.':
                messages.error(request, "You must pass the reCAPTCHA test")
                continue

    form = PasswordResetForm()
    return render(
        request=request,
        template_name="user/password_reset_form.html",
        context={"form": form, "title": title}
        )


def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'user/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("home")

@login_required
def My_orders(request):
    title = "Мои заказы"
    data = Order.objects.filter(username=request.user.username)
    data = data[::-1]
    payed_orders = request.user.payed_orders

    return render(request, 'user/my_orders.html', {'data': data, "menu": menu, 'payed_orders': payed_orders, "title": title})


@login_required
def download_result(request, order_id, file_type):
    import mimetypes
    from django.http import FileResponse, Http404

    try:
        order = Order.objects.get(id=order_id, username=request.user.username)
    except Order.DoesNotExist:
        raise Http404

    if file_type == 'pdf':
        filename = order.result_pdf
    elif file_type == 'excel':
        filename = order.result_excel
    else:
        raise Http404

    if not filename:
        raise Http404

    file_path = os.path.join('/home/results', filename)
    if not os.path.exists(file_path):
        raise Http404

    content_type, _ = mimetypes.guess_type(file_path)
    response = FileResponse(open(file_path, 'rb'), content_type=content_type or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response





