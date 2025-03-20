from django.contrib import admin
from .models import TreeType, PlantingSite, TreePlantingRequest, TreeServiceProvider
from django.utils import timezone
from .utils import award_coins_for_planting
from django.db import transaction

@admin.register(TreeType)
class TreeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(PlantingSite)
class PlantingSiteAdmin(admin.ModelAdmin):
    list_display = ('user', 'site_type', 'location', 'created_at')
    list_filter = ('site_type', 'created_at')
    search_fields = ('location', 'user__username')

@admin.register(TreePlantingRequest)
class TreePlantingRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'tree_type', 'quantity', 'price_per_tree', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'tree_type')
    search_fields = ('user__username', 'tree_type__name')
    actions = ['approve_requests', 'mark_as_completed', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Одобрение выбранных запросов на посадку"""
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} запросов успешно одобрено")
    approve_requests.short_description = "Одобрить выбранные запросы"
    
    def mark_as_completed(self, request, queryset):
        """Отметка запросов как завершенных и начисление коинов"""
        # Только для запросов в статусе 'approved'
        approved_requests = queryset.filter(status='approved')
        count = approved_requests.count()
        
        if count > 0:
            total_coins = 0
            success_count = 0
            
            # Обработка каждого запроса отдельно для корректного начисления коинов
            for planting_request in approved_requests:
                try:
                    with transaction.atomic():
                        # Обновляем статус
                        planting_request.status = 'completed'
                        planting_request.completed_at = timezone.now()
                        planting_request.save()
                        
                        # Начисляем коины
                        coins_awarded = award_coins_for_planting(request, planting_request)
                        total_coins += coins_awarded
                        success_count += 1
                except Exception as e:
                    self.message_user(
                        request, 
                        f"Ошибка при обработке запроса #{planting_request.id}: {str(e)}",
                        level='error'
                    )
            
            self.message_user(
                request, 
                f"{success_count} запросов отмечены как завершенные. Пользователям начислено {total_coins} коинов."
            )
        else:
            self.message_user(
                request, 
                "Нет запросов в статусе 'Одобрено' для отметки завершения."
            )
    mark_as_completed.short_description = "Отметить как завершенные и начислить коины"
    
    def reject_requests(self, request, queryset):
        """Отклонение выбранных запросов"""
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} запросов отклонено")
    reject_requests.short_description = "Отклонить выбранные запросы"

@admin.register(TreeServiceProvider)
class TreeServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'contact_phone', 'created_at')
    search_fields = ('name', 'description', 'user__username', 'contact_phone')

# Регистрируем профиль пользователя в админке
from authentication.models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'coins')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)