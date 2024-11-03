from datetime import datetime
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import message
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode

from proveedor.forms import VendorForm
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test

from django.core.exceptions import PermissionDenied
from proveedor.models import Vendor
from django.template.defaultfilters import slugify
# from orders.models import Order
import datetime


# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Ya has iniciado sesión!')
        return redirect('dashboard')
    elif request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()

            # Send verification email
            mail_subject = 'Por favor activa tu cuenta'
            email_template = 'cuentas/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, '¡Su cuenta ha sido registrada exitosamente! ')
            return redirect('registerUser')
        else:
            print('Formulario inválido')
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'cuentas/registerUser.html', context)


# PROVEEDOR REGISTRO
def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('dashboard')
    elif request.method == 'POST':
        # store the data and create the user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        if form.is_valid() and v_form.is_valid:
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # Send verification email
            mail_subject = 'Por favor activa tu cuenta'
            email_template = 'cuentas/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, '¡Su cuenta ha sido registrada con éxito! Espere la aprobación.')
            return redirect('registerVendor')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form': form,
        'v_form': v_form,
    }

    return render(request, 'cuentas/registerVendor.html', context)


# ACTIVATE ACCOUNT
def activate(request, uidb64, token):
    # Active al usuario estableciendo el estado is_active en True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, '¡Enhorabuena! Tu cuenta está activada.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Enlace de activación no válido')
        return redirect('myAccount')
        


# LOGIN
def login(request):
    if request.user.is_authenticated:
        messages.warning(request, '¡Ya has iniciado sesión!')
        return redirect('dashboard')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Has iniciado sesión')
            return redirect('myAccount')
        else:
            messages.error(request, 'Credenciales de inicio de sesión no válidas')
            return redirect('login')
    return render(request, 'cuentas/login.html')

# LOGOUT
def logout(request):
    auth.logout(request)
    messages.info(request, 'Has cerrado la sesión')
    return redirect('login')


@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request, "cuentas/custDashboard.html")


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    # orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('created_at')
    # recent_orders = orders[:10]

    # # current month's revenue
    # current_month = datetime.datetime.now().month
    # current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    # current_month_revenue = 0
    # for i in current_month_orders:
    #     current_month_revenue += i.get_total_by_vendor()['grand_total']
    

    # # total revenue
    # total_revenue = 0
    # for i in orders:
    #     total_revenue += i.get_total_by_vendor()['grand_total']
    context = {
        # 'orders': orders,
        # 'orders_count': orders.count(),
        # 'recent_orders': recent_orders,
        # 'total_revenue': total_revenue,
        # 'current_month_revenue': current_month_revenue,
        'vendor': vendor
    }
    return render(request, "cuentas/vendorDashboard.html", context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # enviar correo electrónico para restablecer contraseña
            mail_subject = 'Restablecer su contraseña'
            email_template = 'cuentas/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Se envió un enlace de restablecimiento a su correo')
            return redirect('login')
        else:
            messages.error(request, 'La cuenta no existe')
            return redirect('forgot_password')
    return render(request, 'cuentas/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Por favor restablezca su contraseña')
        return redirect('reset_password')
    else:
        messages.error(request, '¡Este enlace ha expirado!')
        return redirect('myAccount')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Restablecimiento de contraseña exitosa')
            return redirect('login')
        else:
            messages.error(request, '¡La contraseña no coincide!')
            return redirect('reset_password')
    return render(request, 'cuentas/reset_password.html')