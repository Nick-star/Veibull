from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse
from django import forms
from django.contrib import messages

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


@login_required
def profile(request):
    context = {
        'is_staff': request.user.is_staff,
        'username': request.user.username,
    }
    return render(request, 'profile.html', context)