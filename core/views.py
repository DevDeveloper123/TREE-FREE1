from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.utils import timezone
from .models import TreeType, PlantingSite, TreePlantingRequest, TreeServiceProvider
from .forms import (
    TreeSelectionForm, PlantingSiteForm, TreePriceForm, TreeQuantityForm,
    ServiceProviderForm
)

def home(request):
    """Главная страница с тремя основными кнопками"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    """Личный кабинет пользователя с основной информацией"""
    # Получаем статистику пользователя
    completed_requests_count = TreePlantingRequest.objects.filter(
        user=request.user, status='completed'
    ).count()
    
    total_trees_planted = TreePlantingRequest.objects.filter(
        user=request.user, status='completed'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    pending_requests_count = TreePlantingRequest.objects.filter(
        user=request.user, status='pending'
    ).count()
    
    planting_sites_count = PlantingSite.objects.filter(
        user=request.user
    ).count()
    
    # Получаем последние запросы пользователя
    recent_requests = TreePlantingRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Получаем последние участки пользователя
    recent_sites = PlantingSite.objects.filter(
        user=request.user
    ).order_by('-created_at')[:4]
    
    context = {
        'completed_requests_count': completed_requests_count,
        'total_trees_planted': total_trees_planted,
        'pending_requests_count': pending_requests_count,
        'planting_sites_count': planting_sites_count,
        'recent_requests': recent_requests,
        'recent_sites': recent_sites
    }
    
    return render(request, 'core/dashboard.html', context)

# === Раздел "Я хочу посадить дерево" ===

@login_required
def plant_tree(request):
    """Страница с кнопками для процесса посадки дерева"""
    return render(request, 'core/plant_tree.html')

@login_required
def select_tree_type(request):
    """Выбор вида дерева для посадки"""
    tree_types = TreeType.objects.all()
    
    if request.method == 'POST':
        form = TreeSelectionForm(request.POST)
        if form.is_valid():
            # Сохраняем выбор в сессии для дальнейшего использования
            request.session['selected_tree_type_id'] = form.cleaned_data['tree_type'].id
            messages.success(request, f'Вы выбрали {form.cleaned_data["tree_type"].name}')
            return redirect('select_planting_site')
    else:
        form = TreeSelectionForm()
    
    return render(request, 'core/select_tree_type.html', {
        'form': form,
        'tree_types': tree_types
    })

@login_required
def select_planting_site(request):
    """Выбор или добавление участка для посадки"""
    if request.method == 'POST':
        form = PlantingSiteForm(request.POST, request.FILES)
        if form.is_valid():
            site = form.save(commit=False)
            site.user = request.user
            site.save()
            
            request.session['selected_planting_site_id'] = site.id
            messages.success(request, 'Участок успешно добавлен')
            return redirect('set_tree_price')
    else:
        form = PlantingSiteForm()
    
    return render(request, 'core/select_planting_site.html', {
        'form': form
    })

@login_required
def set_tree_price(request):
    """Установка цены дерева"""
    if request.method == 'POST':
        form = TreePriceForm(request.POST)
        if form.is_valid():
            request.session['tree_price'] = float(form.cleaned_data['price'])
            messages.success(request, f'Цена установлена: {form.cleaned_data["price"]}')
            return redirect('set_tree_quantity')
    else:
        form = TreePriceForm()
    
    return render(request, 'core/set_tree_price.html', {
        'form': form
    })

@login_required
def set_tree_quantity(request):
    """Установка количества деревьев"""
    if request.method == 'POST':
        form = TreeQuantityForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            request.session['tree_quantity'] = quantity
            
            # Создаем запись о запросе на посадку
            tree_type = get_object_or_404(TreeType, id=request.session.get('selected_tree_type_id'))
            planting_site = get_object_or_404(PlantingSite, id=request.session.get('selected_planting_site_id'))
            
            TreePlantingRequest.objects.create(
                user=request.user,
                tree_type=tree_type,
                planting_site=planting_site,
                quantity=quantity,
                price_per_tree=request.session.get('tree_price', 0),
                status='pending'
            )
            
            # Очищаем сессию
            for key in ['selected_tree_type_id', 'selected_planting_site_id', 'tree_price', 'tree_quantity']:
                if key in request.session:
                    del request.session[key]
            
            messages.success(request, f'Заявка на посадку {quantity} деревьев создана')
            return redirect('planting_requests')
    else:
        form = TreeQuantityForm()
    
    return render(request, 'core/set_tree_quantity.html', {
        'form': form
    })

# === Раздел "У меня есть участок для посадки деревьев" ===

@login_required
def my_land(request):
    """Страница для пользователей с участком для посадки"""
    return render(request, 'core/my_land.html')

@login_required
def add_planting_site(request):
    """Добавление участка для посадки"""
    if request.method == 'POST':
        form = PlantingSiteForm(request.POST, request.FILES)
        if form.is_valid():
            site = form.save(commit=False)
            site.user = request.user
            site.save()
            
            request.session['land_planting_site_id'] = site.id
            messages.success(request, 'Участок успешно добавлен')
            return redirect('land_select_tree_type')
    else:
        form = PlantingSiteForm()
    
    return render(request, 'core/add_planting_site.html', {
        'form': form
    })

@login_required
def land_select_tree_type(request):
    """Выбор вида дерева для участка"""
    tree_types = TreeType.objects.all()
    
    if request.method == 'POST':
        form = TreeSelectionForm(request.POST)
        if form.is_valid():
            request.session['land_tree_type_id'] = form.cleaned_data['tree_type'].id
            messages.success(request, f'Вы выбрали {form.cleaned_data["tree_type"].name}')
            return redirect('land_set_tree_price')
    else:
        form = TreeSelectionForm()
    
    return render(request, 'core/land_select_tree_type.html', {
        'form': form,
        'tree_types': tree_types
    })

@login_required
def land_set_tree_price(request):
    """Установка цены дерева для участка"""
    if request.method == 'POST':
        form = TreePriceForm(request.POST)
        if form.is_valid():
            request.session['land_tree_price'] = float(form.cleaned_data['price'])
            messages.success(request, f'Цена установлена: {form.cleaned_data["price"]}')
            return redirect('land_set_tree_quantity')
    else:
        form = TreePriceForm()
    
    return render(request, 'core/land_set_tree_price.html', {
        'form': form
    })

@login_required
def land_set_tree_quantity(request):
    """Установка количества деревьев для участка"""
    if request.method == 'POST':
        form = TreeQuantityForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            # Создаем запись о запросе на посадку
            tree_type = get_object_or_404(TreeType, id=request.session.get('land_tree_type_id'))
            planting_site = get_object_or_404(PlantingSite, id=request.session.get('land_planting_site_id'))
            
            TreePlantingRequest.objects.create(
                user=request.user,
                tree_type=tree_type,
                planting_site=planting_site,
                quantity=quantity,
                price_per_tree=request.session.get('land_tree_price', 0),
                status='pending'
            )
            
            # Очищаем сессию
            for key in ['land_planting_site_id', 'land_tree_type_id', 'land_tree_price']:
                if key in request.session:
                    del request.session[key]
            
            messages.success(request, 'Ваш участок добавлен для озеленения')
            return redirect('planting_requests')
    else:
        form = TreeQuantityForm()
    
    return render(request, 'core/land_set_tree_quantity.html', {
        'form': form
    })

# === Дополнительные представления для управления запросами ===

@login_required
def planting_requests(request):
    """Список всех запросов пользователя на посадку деревьев"""
    # Получаем параметры фильтрации из GET-запроса
    status = request.GET.get('status')
    tree_type_id = request.GET.get('tree_type')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Базовый QuerySet
    requests_queryset = TreePlantingRequest.objects.filter(user=request.user)
    
    # Применяем фильтры, если они указаны
    if status:
        requests_queryset = requests_queryset.filter(status=status)
    
    if tree_type_id:
        requests_queryset = requests_queryset.filter(tree_type_id=tree_type_id)
    
    # Сортировка
    requests_queryset = requests_queryset.order_by(sort_by)
    
    # Пагинация
    paginator = Paginator(requests_queryset, 10)  # 10 запросов на страницу
    page_number = request.GET.get('page')
    planting_requests = paginator.get_page(page_number)
    
    # Получаем список всех видов деревьев для фильтра
    tree_types = TreeType.objects.all()
    
    context = {
        'planting_requests': planting_requests,
        'tree_types': tree_types
    }
    
    return render(request, 'core/planting_requests.html', context)

@login_required
def planting_request_detail(request, request_id):
    """Детальная информация о запросе на посадку"""
    planting_request = get_object_or_404(TreePlantingRequest, id=request_id, user=request.user)
    
    # Вычисляем общую стоимость
    total_price = planting_request.price_per_tree * planting_request.quantity
    
    context = {
        'planting_request': planting_request,
        'total_price': total_price
    }
    
    return render(request, 'core/planting_request_detail.html', context)

@login_required
def cancel_planting_request(request, request_id):
    """Отмена запроса на посадку"""
    planting_request = get_object_or_404(TreePlantingRequest, id=request_id, user=request.user)
    
    # Проверяем, что запрос находится в статусе "В ожидании"
    if planting_request.status != 'pending':
        messages.error(request, 'Можно отменить только запросы в статусе "В ожидании"')
        return redirect('planting_request_detail', request_id=request_id)
    
    # Меняем статус на "Отклонено"
    planting_request.status = 'rejected'
    planting_request.save()
    
    messages.success(request, 'Запрос успешно отменен')
    return redirect('planting_requests')

@login_required
def planting_sites(request):
    """Список всех участков пользователя"""
    # Получаем параметры фильтрации из GET-запроса
    site_type = request.GET.get('site_type')
    search_query = request.GET.get('search')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Базовый QuerySet
    sites_queryset = PlantingSite.objects.filter(user=request.user)
    
    # Применяем фильтры, если они указаны
    if site_type:
        sites_queryset = sites_queryset.filter(site_type=site_type)
    
    if search_query:
        sites_queryset = sites_queryset.filter(location__icontains=search_query)
    
    # Сортировка
    sites_queryset = sites_queryset.order_by(sort_by)
    
    # Пагинация
    paginator = Paginator(sites_queryset, 8)  # 8 участков на страницу
    page_number = request.GET.get('page')
    planting_sites = paginator.get_page(page_number)
    
    context = {
        'planting_sites': planting_sites
    }
    
    return render(request, 'core/planting_sites.html', context)

# === Раздел "Продаю и сажаю деревья" ===

@login_required
def sell_trees(request):
    """Страница для продавцов/поставщиков услуг"""
    if request.method == 'POST':
        form = ServiceProviderForm(request.POST)
        if form.is_valid():
            # Проверяем, есть ли уже профиль поставщика услуг у пользователя
            try:
                provider = TreeServiceProvider.objects.get(user=request.user)
                # Обновляем существующий профиль
                form = ServiceProviderForm(request.POST, instance=provider)
                form.save()
                messages.success(request, 'Информация о ваших услугах обновлена')
            except TreeServiceProvider.DoesNotExist:
                # Создаем новый профиль
                provider = form.save(commit=False)
                provider.user = request.user
                provider.save()
                messages.success(request, 'Ваши услуги добавлены на платформу')
            
            return redirect('service_provider_profile')
    else:
        # Проверяем, есть ли уже профиль поставщика услуг у пользователя
        try:
            provider = TreeServiceProvider.objects.get(user=request.user)
            form = ServiceProviderForm(instance=provider)
        except TreeServiceProvider.DoesNotExist:
            form = ServiceProviderForm()
    
    return render(request, 'core/sell_trees.html', {
        'form': form
    })

@login_required
def service_provider_profile(request):
    """Профиль поставщика услуг"""
    try:
        provider = TreeServiceProvider.objects.get(user=request.user)
    except TreeServiceProvider.DoesNotExist:
        messages.error(request, 'У вас нет профиля поставщика услуг')
        return redirect('sell_trees')
    
    # Получаем запросы, связанные с этим поставщиком
    related_requests = TreePlantingRequest.objects.filter(
        Q(status='approved') | Q(status='completed'),
        planting_site__user=request.user
    ).order_by('-created_at')
    
    # Подсчитываем статистику
    completed_requests_count = related_requests.filter(status='completed').count()
    total_trees_planted = related_requests.filter(status='completed').aggregate(total=Sum('quantity'))['total'] or 0
    
    context = {
        'provider': provider,
        'related_requests': related_requests,
        'completed_requests_count': completed_requests_count,
        'total_trees_planted': total_trees_planted
    }
    
    return render(request, 'core/service_provider_profile.html', context)

@login_required
def service_providers_list(request):
    """Список всех поставщиков услуг"""
    # Получаем параметры фильтрации из GET-запроса
    search_query = request.GET.get('search')
    
    # Базовый QuerySet
    providers_queryset = TreeServiceProvider.objects.all()
    
    # Применяем поиск, если он указан
    if search_query:
        providers_queryset = providers_queryset.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Сортировка
    providers_queryset = providers_queryset.order_by('name')
    
    # Пагинация
    paginator = Paginator(providers_queryset, 6)  # 6 поставщиков на страницу
    page_number = request.GET.get('page')
    providers = paginator.get_page(page_number)
    
    context = {
        'providers': providers
    }
    
    return render(request, 'core/service_providers_list.html', context)

@login_required
def contact_provider(request, provider_id):
    """Отправка сообщения поставщику услуг"""
    provider = get_object_or_404(TreeServiceProvider, id=provider_id)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        
        if message:
            # Здесь можно реализовать отправку сообщения (например, через email или внутреннюю систему сообщений)
            # В данной версии просто показываем уведомление об успешной отправке
            
            messages.success(request, f'Ваше сообщение успешно отправлено поставщику {provider.name}')
        else:
            messages.error(request, 'Пожалуйста, введите текст сообщения')
    
    return redirect('service_providers_list')

@login_required
def complete_planting_request(request, request_id):
    """Отметка запроса на посадку как выполненного"""
    planting_request = get_object_or_404(TreePlantingRequest, id=request_id)
    
    # Проверяем, что текущий пользователь является владельцем участка для посадки
    if planting_request.planting_site.user != request.user:
        messages.error(request, 'У вас нет прав для выполнения этого действия')
        return redirect('service_provider_profile')
    
    # Проверяем, что запрос находится в статусе "Одобрено"
    if planting_request.status != 'approved':
        messages.error(request, 'Можно завершить только запросы в статусе "Одобрено"')
        return redirect('service_provider_profile')
    
    # Обновляем статус запроса
    planting_request.status = 'completed'
    
    # Добавляем примечания, если они есть
    notes = request.POST.get('notes')
    if notes:
        planting_request.notes = notes
    
    planting_request.save()
    
    messages.success(request, f'Запрос на посадку {planting_request.quantity} {planting_request.tree_type.name} успешно завершен')
    return redirect('service_provider_profile')
