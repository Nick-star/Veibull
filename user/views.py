from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


class CreateUserForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'passwordInput'}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'passwordConfirmInput'}))
    is_staff = forms.BooleanField(required=False, label='Is Staff')


@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = form.cleaned_data['is_staff']
            user.save()
            return JsonResponse({'message': 'Пользователь был успешно создан', 'user_id': user.id})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = CreateUserForm()

    return render(request, 'create_user.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def change_password(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        form = SetPasswordForm(User.objects.get(pk=user_id), request.POST)
        if form.is_valid():
            user = form.save()
            return JsonResponse({'message': 'Пароль был успешно изменен'})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = SetPasswordForm(User())
        users = User.objects.all()
        return render(request, 'change_password.html', {'form': form, 'users': users})


@login_required
def profile(request):
    context = {
        'is_superuser': request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'username': request.user.username,
    }
    return render(request, 'profile.html', context)


@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        User.objects.filter(id=user_id).delete()
        return JsonResponse({'message': 'Пользователь удалён'})
    else:
        return JsonResponse({'error': 'Invalid request'})

@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    users = User.objects.all()
    return render(request, 'manage_users.html', {'users': users})