from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm
from core.models import TreePlantingRequest, PlantingSite

def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'authentication/register.html', {'form': form})

@login_required
def profile(request):
    """Страница профиля пользователя"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Ваш профиль обновлен!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        
    # Получаем запросы на посадку деревьев пользователя
    planting_requests = TreePlantingRequest.objects.filter(user=request.user).order_by('-created_at')
    # Получаем участки пользователя
    planting_sites = PlantingSite.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'u_form': u_form,
        'planting_requests': planting_requests,
        'planting_sites': planting_sites
    }
    
    return render(request, 'authentication/profile.html', context)

def logout_view(request):
    """Выход из аккаунта с перенаправлением на главную страницу"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из аккаунта')
    return redirect('home')
